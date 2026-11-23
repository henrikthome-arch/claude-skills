#!/usr/bin/env python3
"""Deck coverage check: what should be in this board deck, what is, and who owes the rest.

Run from a meeting folder (the one holding agenda/ and slides/):

    python3 ~/.claude/skills/board-slides/scripts/coverage.py            # print + write slides/COVERAGE.md
    python3 ~/.claude/skills/board-slides/scripts/coverage.py --no-probe # skip network probes (fast)

Two checks:
  1. STANDING slides from ../standing-slides.json — the slides every deck is expected to carry.
  2. AGENDA items that render a divider but have no slides and no external deck.

Exit 0 only when nothing is missing. A deck is not "done" while this exits non-zero (SKILL.md §57).

WHY THIS EXISTS: in Sep 2026 the web-traffic and SaaS40 slides silently fell out of the
meeting #8 deck. Nothing was broken — their data just had not been pulled, and nothing listed
what the deck was supposed to contain, so a missing slide looked exactly like a slide nobody
wanted. This file is that list, and COVERAGE.md is what the next session reads to chase.
"""
import argparse, glob, json, os, re, sys, urllib.request
from datetime import date
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = SKILL / "standing-slides.json"
FINOPS_BASE = os.environ.get("FINOPS_BASE", "http://44.194.218.109:8000/api/v1")
FINOPS_TOKEN = Path.home() / "Library/CloudStorage/Dropbox/Workspace/financial-ops/mcp-api-token.txt"
SONETEL = Path.home() / "Library/CloudStorage/Dropbox/Sonetel"
ACTION_LOG = SONETEL / "Board/Board action log/Board Action Log {year}.xlsx"
SF_DATALESS = 0x40000000   # macOS st_flags bit: Dropbox "online-only" placeholder

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]


# ---------------------------------------------------------------- periods
def month_back(d, n):
    y, m = d.year, d.month - n
    while m <= 0:
        y, m = y - 1, m + 12
    return f"{y}-{m:02d}"


def period_from_title(title):
    t = (title or "").lower()
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{4})", t)
    if m:
        return f"{m.group(2)}-{MONTHS.index(m.group(1)) + 1:02d}"
    m = re.search(r"\((\d{4})-(\d{2})\)", t)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def period_from_file(path):
    """Newest YYYY-MM found anywhere in a data_ref file's series."""
    try:
        text = path.read_text()
    except Exception:
        return None
    found = re.findall(r'"(?:month|date)"\s*:\s*"(\d{4}-\d{2})', text)
    return max(found) if found else None


# ---------------------------------------------------------------- probes
def dataless(p):
    try:
        return bool(os.stat(p).st_flags & SF_DATALESS)
    except (FileNotFoundError, AttributeError):
        return False


def finops_latest_booked():
    """Newest period of the newest fiscal year loaded in Finops ('YYYY-MM'), or None."""
    try:
        tok = FINOPS_TOKEN.read_text().strip()
        h = {"Authorization": f"Bearer {tok}"}
        fys = json.loads(urllib.request.urlopen(urllib.request.Request(
            FINOPS_BASE + "/group-pl/fiscal-years", headers=h), timeout=8).read())["data"]["fiscal_years"]
        newest = max(fys, key=lambda f: f["end_date"])
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            FINOPS_BASE + f"/group-pl/{newest['id']}", headers=h), timeout=15).read())
        d = d.get("data", d)
        return max(d.get("periods") or []) or None
    except Exception:
        return None


def probe_finops():
    try:
        tok = FINOPS_TOKEN.read_text().strip()
        req = urllib.request.Request(FINOPS_BASE + "/group-pl/fiscal-years",
                                     headers={"Authorization": f"Bearer {tok}"})
        urllib.request.urlopen(req, timeout=5).read(1)
        return True, "reachable"
    except Exception as e:
        return False, f"unreachable ({type(e).__name__}) — VPN on?"


def probe_neon():
    try:
        import importlib.util, psycopg2
        spec = importlib.util.spec_from_file_location("bnm", SKILL / "scripts/build_neon_metrics.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        psycopg2.connect(m.get_url(), connect_timeout=5).close()
        return True, "reachable"
    except SystemExit as e:
        return False, str(e)
    except Exception as e:
        return False, f"unreachable ({type(e).__name__})"


def probe_action_log(year):
    p = Path(str(ACTION_LOG).format(year=year))
    if not p.exists():
        return False, f"not found: {p}"
    if dataless(p):
        return False, "online-only in Dropbox — right-click → Make Available Offline"
    return True, "readable"


def newest_published_quarter():
    """(label, path) of the newest quarterly report with a tables.json, e.g. ('Q2 2026', ...)."""
    best = None
    for tp in glob.glob(str(SONETEL / "Financial/*/Quarter/*/*/tables.json")):
        parts = Path(tp).parts
        year, q = parts[-5], parts[-3]
        m = re.match(r"Q(\d)$", q)
        if not (m and re.fullmatch(r"\d{4}", year)):
            continue
        key = (int(year), int(m.group(1)))
        if best is None or key > best[0]:
            best = (key, f"Q{key[1]} {key[0]}", tp)
    return (best[1], best[2]) if best else (None, None)


# ---------------------------------------------------------------- matching
def matches(slide, rule):
    if slide.get("type") != rule["type"]:
        return False
    if "title_re" in rule and not re.search(rule["title_re"], slide.get("title") or "", re.I):
        return False
    if "data_ref_re" in rule and not re.search(rule["data_ref_re"], slide.get("data_ref") or ""):
        return False
    if "layout_key" in rule:
        # a chart names its series in `key`, a STACKED one in `keys` — read both, or a stacked
        # slide that is present reads as missing (the payer-source slide did, 2026-09-14)
        keys = set()
        for c in slide.get("trends_layout") or []:
            if c.get("key"):
                keys.add(c["key"])
            keys.update(c.get("keys") or [])
        if not keys & set(rule["layout_key"]):
            return False
    return True


def extra_checks(sid, slide, folder):
    """Required parts a slide can be present without. Returns a list of problems."""
    probs = []
    if sid == "cash_flow_forecast":
        ref = folder / (slide.get("data_ref") or "financials-data/cash-flow-forecast.json")
        try:
            d = json.loads(ref.read_text())
            blob = json.dumps(d)
            if re.search(r'rationale"\s*:\s*null', blob):
                probs.append("revenue-assumption rationale is null (mandatory, §40)")
            # The curated top-items panel is OPTIONAL (Henrik 2026-09-12: the candidates were all
            # recurring costs). Only flag it when the data file asks for one.
            if d.get("top_items_wanted") and not d.get("top_forecast_items"):
                probs.append("top-items panel requested but empty (§31 — never the API's ranked list)")
        except Exception:
            probs.append(f"cannot read {ref.name}")
    if sid == "saas40" and re.search(r"pre-audit|not yet published|indicative",
                                     slide.get("notes") or "", re.I):
        probs.append("a quarter is still marked pre-audit — check whether it is now published")
    if sid == "cash_position" and slide.get("data_ref"):
        try:
            pend = json.loads((folder / slide["data_ref"]).read_text()).get("_pending_confirmation") or []
            probs += [f"to confirm: {p}" for p in pend]
        except Exception:
            pass
    if sid == "key_messages":
        # the opening summary must sit in items["0"] (after the cover, before the agenda — §70)
        if slide.get("_item") not in (None, "0"):
            probs.append('must be under items["0"] so it opens the deck (§70)')
        if not 3 <= len(slide.get("bullets") or []) <= 5:
            probs.append("needs 4–5 key messages (§70)")
    if sid == "action_log" and not slide.get("actions"):
        probs.append("no open items listed")
    return probs


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=".")
    ap.add_argument("--no-probe", action="store_true")
    args = ap.parse_args()
    folder = Path(args.folder).resolve()

    agenda = json.loads((folder / "agenda/agenda.json").read_text())
    data = json.loads((folder / "slides/data.json").read_text())
    manifest = json.loads(MANIFEST.read_text())
    meet = agenda["meeting"]
    mdate = date.fromisoformat(meet["date"])
    kind = "board_update" if "update" in meet.get("title", "").lower() else "quarterly"
    complete, booked = month_back(mdate, 1), month_back(mdate, 2)
    items = agenda["agenda_items"]
    slides = [(str(k), {**s, "_item": str(k)}) for k, v in data["items"].items() for s in v]

    probes = {}
    if not args.no_probe:
        probes["finops"] = probe_finops()
        probes["neon"] = probe_neon()
        # Latest month actually SIE-booked in Finops. "Meeting month −2" is only the usual case:
        # on 2026-10-04 August was not loaded yet and the P&L showed as STALE/Claude when it was
        # really WAIT/Henrik (BDO). If Finops says an older month is the latest, that is `booked`.
        fb = finops_latest_booked()
        if fb and fb < booked:
            print(f"[coverage] Finops latest booked month is {fb}, not {booked} — BDO upload pending", file=sys.stderr)
            probes["finops_booked_lag"] = (False, f"latest booked in Finops is {fb}; {booked} not loaded yet (BDO)")
    probes["action_log_xlsx"] = probe_action_log(mdate.year)
    pub_label, pub_path = newest_published_quarter()
    probes["published_quarter"] = (pub_label is not None, pub_label or "none found")
    probes["henrik"] = (False, "needs Henrik")

    def section_item(section):
        rx = manifest["sections"][section]
        for it in items:
            if re.search(rx, it["title"], re.I):
                return it["number"]
        return None

    rows = []
    for e in manifest["slides"]:
        if kind not in e["applies_to"]:
            continue
        hit = next(((k, s) for k, s in slides if matches(s, e["match"])), None)
        src_ok, src_msg = probes.get(e["source"], (None, "not probed"))
        want = {"booked": booked, "complete": complete}.get(e.get("period"))
        fmt = lambda c: c.format(booked=booked, complete=complete) if c else ""
        item_no = hit[0] if hit else section_item(e["section"])

        if hit:
            k, s = hit
            got = None
            if e.get("period_from") == "title":
                got = period_from_title(s.get("title"))
            elif e.get("period_from") == "data_ref" and s.get("data_ref"):
                got = period_from_file(folder / s["data_ref"])
            probs = extra_checks(e["id"], s, folder)
            if e["id"] == "saas40" and pub_label:
                # the newest PUBLISHED quarter must be on the slide; a later booked-months-only
                # point after it (e.g. "Q3 2026 (Jul)", Henrik 2026-09-10) is allowed
                labels = [p.get("label", "") for p in s.get("periods") or []]
                if not any(pub_label in l for l in labels):
                    probs.append(f"newest published quarter {pub_label} is not on the slide (has: {', '.join(labels)})")
            if want and got and got < want:
                status, why = "STALE", f"shows {got}, {want} is expected"
            elif probs:
                status, why = "INCOMPLETE", "; ".join(probs)
            else:
                status, why = "OK", got or ""
            owner = e.get("blocked_owner", e["owner"]) if status == "INCOMPLETE" else e["owner"]
        else:
            if e.get("optional"):
                status, why, owner = "ASK", "optional — does this deck want it?", "Henrik"
            elif e["source"] == "henrik":
                status, why, owner = "WRITE", e.get("note", ""), e["owner"]
            elif e["source"] == "action_log_xlsx":
                status = "WAIT" if not src_ok else "WRITE"
                why, owner = src_msg if not src_ok else "file readable — collect Henrik's status per item", "Henrik"
            elif e.get("local_file") and (folder / e["local_file"]).exists():
                # data already pulled: the source being down no longer matters
                probs = extra_checks(e["id"], {"data_ref": e["local_file"]}, folder)
                got = period_from_file(folder / e["local_file"])
                if probs:
                    status, why, owner = "WAIT", f"{e['local_file']} on disk; " + "; ".join(probs), \
                        e.get("blocked_owner", e["owner"])
                else:
                    status, why, owner = "BUILD", f"{e['local_file']} on disk ({got or 'period ?'}); add the slide", e["owner"]
            elif src_ok is False:
                status, why, owner = "WAIT", f"{e['source']}: {src_msg}", e.get("blocked_owner", e["owner"])
            else:
                status, why, owner = "BUILD", fmt(e.get("build")), e["owner"]
        rows.append(dict(id=e["id"], title=e["title"], item=item_no, status=status,
                         why=why, owner=owner, note=e.get("note", "")))

    # agenda items with no content
    ext = {it["number"] for it in items if it.get("external_deck")}
    have = {int(k) for k, _ in slides}
    for it in items:
        n = it["number"]
        if it.get("section_header") is False or it.get("type") == "procedural" or n in ext or n in have:
            continue
        rows.append(dict(id=f"item-{n}", title=it["title"], item=n, status="WRITE",
                         why="agenda item has no slides", owner=it.get("presenter") or "Henrik",
                         note=""))

    # ------------------------------------------------------------ output
    ICON = {"OK": "✅", "STALE": "🟠", "INCOMPLETE": "🟠", "BUILD": "🔧",
            "WAIT": "⏳", "WRITE": "✍️", "ASK": "❓"}
    gaps = [r for r in rows if r["status"] != "OK"]
    lines = [f"# Deck coverage — {meet['title']}, {meet['date']}",
             "",
             f"Generated {date.today().isoformat()} by `board-slides/scripts/coverage.py`. "
             f"Deck type: **{kind}**. Latest complete month **{complete}**, latest booked month **{booked}**.",
             "Re-run after every data pull; the deck is not done while anything below is not ✅.",
             "",
             "## Sources",
             ""]
    for name, (ok, msg) in probes.items():
        if name == "henrik":
            continue
        lines.append(f"- {'✅' if ok else '❌'} **{name}** — {msg}")
    lines += ["", "## Standing slides and agenda items", "",
              "| | Slide | Item | Status | Detail | Owner |", "|---|---|---:|---|---|---|"]
    for r in rows:
        lines.append(f"| {ICON[r['status']]} | {r['title']} | {r['item'] or '—'} | {r['status']} "
                     f"| {r['why'].replace('|', '/')} | {r['owner']} |")
    lines += ["", "## Chase list", ""]
    if not gaps:
        lines.append("Nothing outstanding.")
    by_owner = {}
    for r in gaps:
        # "Henrik (curated top items)" -> group under Henrik, keep the parenthetical as the ask
        m = re.match(r"([^(]+?)\s*\((.*)\)$", r["owner"])
        name, ask = (m.group(1), m.group(2)) if m else (r["owner"], "")
        by_owner.setdefault(name, []).append((r, ask))
    for owner, rs in by_owner.items():
        lines.append(f"**{owner}**")
        for r, ask in rs:
            lines.append(f"- {ICON[r['status']]} {r['title']} (item {r['item'] or '?'}) — {r['why']}"
                         + (f" → **needs: {ask}**" if ask else ""))
        lines.append("")
    md = "\n".join(lines).rstrip() + "\n"
    (folder / "slides/COVERAGE.md").write_text(md, encoding="utf-8")
    print(md)
    sys.exit(1 if gaps else 0)


if __name__ == "__main__":
    main()
