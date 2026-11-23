#!/usr/bin/env python3
"""Fetch the operational KPIs for one report quarter — deterministically.

CR-2026-11-18-operativa-nyckeltal-deterministisk-hamtning (Financial repo).

    ~/.weasy/bin/python fetch_kpis.py <period-dir> --period-end 2026-09-30 \
        --sales-analysis "<period-dir>/Underlag - dataserier/sales_analysis_2026-10-31.xlsx" \
        [--dry-run] [--partial] [--overwrite] [--allow-jump]

The quarter and its months are derived from --period-end; nothing else decides which row is
written. Writes the quarter's row in seven Grafkälldata CSVs and .current/.source for arr,
aktiva_betalande_kunder and cac_kr in data.json. Never writes comparatives (.prior), never
writes yoy_pct, never writes XX, never guesses. A missing value stops the run; --partial writes
PENDING instead so a draft can render (guard 25 still stops a release).

ARR and kunder need the finops API: FINOPS_API_URL and FINOPS_API_TOKEN in the environment
(VPN up). No token file is ever read.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PENDING = "PENDING"
MON = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
# sales_analysis 'Data' sheet: column of 2025-05 (1-based), header row with month dates.
SA_BASE_COL, SA_BASE = 169, (2025, 5)
SA_HEADER_ROW = 8
SA_ROWS = {"nya": [534], "cac": [703], "premium": [755, 756], "business": [777, 778],
           "telefon": [838, 839, 840]}
JUMP_LIMIT = 0.08          # kunder vs previous quarter — backstop, see CR
PUBLISHED_TOL = 0.05       # MSEK, ARR bar vs a published amount


class FetchError(RuntimeError):
    pass


# ----------------------------------------------------------------------------- period

def quarter_of(period_end: dt.date):
    if period_end.month % 3 or (period_end + dt.timedelta(days=1)).day != 1:
        raise FetchError(f"--period-end {period_end} is not a quarter end")
    q = period_end.month // 3
    months = [(period_end.year, period_end.month - 2 + i) for i in range(3)]
    label = f"Q{q} {period_end.year % 100:02d}"
    period = f"Q{q} {MON[months[0][1]-1]}-{MON[months[2][1]-1]} {period_end.year}"
    return label, period, months


def prev_quarter_label(label: str) -> str:
    q, yy = int(label[1]), int(label[3:])
    return f"Q{q-1} {yy:02d}" if q > 1 else f"Q4 {yy-1:02d}"


# ----------------------------------------------------------------------------- sources

def read_sales_analysis(path: Path, months):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb["Data"]
    needed = sorted({r for rows in SA_ROWS.values() for r in rows} | {SA_HEADER_ROW})
    rows = {r: list(ws.iter_rows(min_row=r, max_row=r, values_only=True))[0] for r in needed}
    cols = {}
    for (y, m) in months:
        c = SA_BASE_COL + (y - SA_BASE[0]) * 12 + (m - SA_BASE[1])
        h = rows[SA_HEADER_ROW][c - 1] if c - 1 < len(rows[SA_HEADER_ROW]) else None
        if not isinstance(h, (dt.datetime, dt.date)) or (h.year, h.month) != (y, m):
            raise FetchError(f"{path.name}: column {c} header is {h!r}, expected {y}-{m:02d}. "
                             f"Stopping rather than reading the wrong month.")
        cols[(y, m)] = c

    def cell(r, ym):
        v = rows[r][cols[ym] - 1]
        if v is None:
            raise FetchError(f"{path.name}: r{r} is empty for {ym[0]}-{ym[1]:02d}. The workbook "
                             f"must be opened and saved in Excel so formula values are cached.")
        return float(v)

    last = months[-1]
    src = lambda rr, ms: f"{path.name} Data r{'+'.join(map(str, rr))}, kol " + \
        ",".join(str(cols[m]) for m in ms)
    out = {
        "telefon": (round(sum(cell(r, last) for r in SA_ROWS["telefon"])), src(SA_ROWS["telefon"], [last])),
        "premium": (round(sum(cell(r, last) for r in SA_ROWS["premium"])), src(SA_ROWS["premium"], [last])),
        "business": (round(sum(cell(r, last) for r in SA_ROWS["business"])), src(SA_ROWS["business"], [last])),
        "nya": (round(sum(cell(534, m) for m in months)), src([534], months) + " (summa tre månader)"),
        "cac": (round(sum(cell(703, m) for m in months) / 3), src([703], months) +
                " (snitt tre månader; samma metod som halvårsrapporten jan-jun 2026)"),
    }
    return out


def _get_json(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


_RATES: dict[str, float] = {}


def _riksbank_load(start: dt.date, end: dt.date):
    """One call for the whole range — the API rate-limits (429) a call per quarter."""
    import time
    url = f"https://api.riksbank.se/swea/v1/Observations/SEKUSDPMI/{start}/{end}"
    for attempt in range(4):
        try:
            for o in _get_json(url):
                if o.get("value") is not None:
                    _RATES[o["date"]] = float(o["value"])
            return
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 3:
                raise FetchError(f"Riksbank SWEA: HTTP {e.code} for {url}") from e
            time.sleep(10 * (attempt + 1))


def riksbank_rate(day: dt.date) -> tuple[float, dt.date]:
    """SEK per USD, Riksbank SEKUSDPMI, on `day` or the last banking day before it."""
    if not any(dt.date.fromisoformat(k) <= day and (day - dt.date.fromisoformat(k)).days <= 10
               for k in _RATES):
        _riksbank_load(day - dt.timedelta(days=10), day)
    cands = [k for k in _RATES if dt.date.fromisoformat(k) <= day
             and (day - dt.date.fromisoformat(k)).days <= 10]
    if not cands:
        raise FetchError(f"Riksbank: no SEKUSDPMI observation in the 10 days to {day}")
    k = max(cands)
    return _RATES[k], dt.date.fromisoformat(k)


def _finops():
    url, tok = os.environ.get("FINOPS_API_URL"), os.environ.get("FINOPS_API_TOKEN")
    if not url or not tok:
        raise FetchError("FINOPS_API_URL / FINOPS_API_TOKEN not set (VPN + token needed for ARR and kunder)")
    return url.rstrip("/"), {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def _payload(body):
    # api_success_response wraps the payload; accept both wrapped and bare.
    return body.get("data") if isinstance(body, dict) and isinstance(body.get("data"), dict) else body


def finops_arr_usd(day: dt.date) -> tuple[float, str]:
    base, h = _finops()
    q = urllib.parse.urlencode({"metric": "arr_total", "granularity": "daily",
                                "start_date": str(day), "end_date": str(day)})
    p = _payload(_get_json(f"{base}/api/v1/metrics/trend?{q}", h))
    pts = [d for d in (p.get("data") or []) if d.get("date") == str(day)]
    if len(pts) != 1 or pts[0].get("value") is None:
        raise FetchError(f"finops arr_total: expected one value for {day}, got {pts!r}")
    return float(pts[0]["value"]) / 1e6, f"finops GET /api/v1/metrics/trend?metric=arr_total {day}"


def finops_kunder(period_end: dt.date) -> tuple[int, str]:
    base, h = _finops()
    ym = f"{period_end.year}-{period_end.month:02d}"
    pq = f"/mnt/financial-ops-storage/data/raw/subscriptions/{ym}/data.parquet"
    # ENTERPRISEID read as text: mixed int/str counted 5048380 and '5048380' twice (2026-06/07, +11 %).
    sql = (f"SELECT COUNT(DISTINCT TRIM(CAST(ENTERPRISEID AS VARCHAR))) AS n "
           f"FROM read_parquet('{pq}') WHERE ACCOUNT_STATUS = 'A'")
    body = json.dumps({"sql": sql, "dataset_type": "subscriptions", "period": ym}).encode()
    p = _payload(_get_json(f"{base}/api/v1/analytics/query", h, body))
    rows = p.get("data") or []
    if len(rows) != 1 or rows[0].get("n") is None:
        raise FetchError(f"finops subscriptions: unexpected result {rows!r}")
    return int(rows[0]["n"]), (f"finops subscriptions {ym}: COUNT(DISTINCT ENTERPRISEID som text) "
                               f"WHERE ACCOUNT_STATUS='A'")


# ----------------------------------------------------------------------------- CSV writing

class Sheet:
    """A Grafkälldata CSV: header, data rows (until the first blank line), footer."""

    def __init__(self, path: Path):
        self.path = path
        rows = list(csv.reader(path.open(encoding="utf-8")))
        self.header = rows[0]
        i = 1
        while i < len(rows) and any(c.strip() for c in rows[i]):
            i += 1
        self.data, self.footer = rows[1:i], rows[i:]

    def col(self, substr: str) -> int:
        for i, h in enumerate(self.header):
            if substr in h:
                return i
        raise FetchError(f"{self.path.name}: no column containing '{substr}'")

    def row(self, label):
        return next((r for r in self.data if r and r[0] == label), None)

    def upsert(self, label, period, values: dict[str, object], source: str, overwrite: bool,
               notes: list[str]):
        """values: {column substring: value or PENDING}."""
        r = self.row(label)
        if r is None:
            last = self.data[-1][0] if self.data else None
            if last and last != prev_quarter_label(label):
                raise FetchError(f"{self.path.name}: last row is {last}, cannot append {label} "
                                 f"out of order")
            r = [""] * len(self.header)
            r[0], r[1] = label, period
            self.data.append(r)
        wrote = False
        for sub, v in values.items():
            c = self.col(sub)
            old = (r[c] if c < len(r) else "").strip()
            new = str(v)
            if old and old not in ("XX", PENDING) and v != PENDING:
                try:
                    same = abs(float(old.replace(",", ".").replace(" ", "")) - float(v)) < 1e-9
                except ValueError:
                    same = False
                if not same and not overwrite:
                    raise FetchError(f"{self.path.name} {label} '{self.header[c]}': has {old}, "
                                     f"fetched {v}. Use --overwrite to replace.")
            if v == PENDING and old and old not in ("XX", PENDING):
                continue                        # never replace a real value with PENDING
            r[c] = new
            wrote = wrote or v != PENDING or old in ("", "XX", PENDING)
        if wrote:                               # a kept value keeps its source text
            r[-1] = source
        notes.append(f"{self.path.name}: {label} {values}")

    def save(self):
        with self.path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.header)
            w.writerows(self.data)
            w.writerows(self.footer)


def num(s: str):
    try:
        return float(s.replace(",", ".").replace(" ", ""))
    except (ValueError, AttributeError):
        return None


# ----------------------------------------------------------------------------- ARR sheet

def arr_sheet(sheet: Sheet, label, period, usd, period_end, overwrite, notes):
    """One method for every bar: USD x Riksbank day rate at that quarter's end (CR decision b).
    Migrates the old single-rate layout once; checks bars against PUBLICERAT amounts."""
    if "Kurs SEK/USD" not in sheet.header:
        usd_c = sheet.col("MUSD")
        sheet.header = ["Kvartal", "Period", "ARR (MUSD)", "Kurs SEK/USD", "ARR (MSEK)",
                        "Publicerat belopp", "Källa"]
        sheet.data = [[r[0], r[1], r[usd_c], "", "", "", r[-1]] for r in sheet.data]
        sheet.footer = [f for f in sheet.footer if not (f and f[0].startswith("SEK-konvertering"))]
        sheet.footer.append(["SEK-konvertering", "Varje kvartal till Riksbankens dagskurs (SEKUSDPMI) vid "
                             "kvartalets slut, eller närmast föregående bankdag. Beslut Henrik 2026-11-18 "
                             "(CR-2026-11-18). Halvårsrapporten jan-jun 2026 räknade om alla kvartal till "
                             "9,73626 — metodbyte från och med jul-sep 2026."])
    if usd is not None:
        sheet.upsert(label, period, {"MUSD": f"{usd:.4f}"}, sheet.row(label)[-1] if sheet.row(label)
                     else "", overwrite, notes)
    else:   # upsert never replaces a real number with PENDING, but does replace XX
        sheet.upsert(label, period, {"MUSD": PENDING, "ARR (MSEK)": PENDING}, PENDING, False, notes)
    errors = []
    firsts = [r[0] for r in sheet.data if r and len(r[0]) == 5]
    if firsts:
        q0, y0 = int(firsts[0][1]), 2000 + int(firsts[0][3:])
        _riksbank_load(dt.date(y0, q0 * 3 - 2, 1), period_end)
    for r in sheet.data:
        u = num(r[2])
        if u is None:
            r[3] = r[4] = PENDING
            continue
        q, yy = int(r[0][1]), 2000 + int(r[0][3:])
        qend = (dt.date(yy, q * 3 % 12 + 1, 1) if q < 4 else dt.date(yy + 1, 1, 1)) - dt.timedelta(days=1)
        rate, rdate = riksbank_rate(qend)
        r[3], r[4] = f"{rate:.5f}", f"{u * rate:.1f}"
        pub = num(r[5])
        if pub is not None and abs(u * rate - pub) > PUBLISHED_TOL:
            errors.append(f"{r[0]}: {u:.4f} MUSD x {rate:.5f} ({rdate}) = {u*rate:.2f} MSEK, "
                          f"published {pub}")
        if r[0] == label:
            r[-1] = f"finops arr_total {period_end} x Riksbank SEKUSDPMI {rdate}"
    if errors:
        raise FetchError("ARR bar deviates from a published amount (>0,05 MSEK):\n  " + "\n  ".join(errors))
    row = sheet.row(label)
    return (num(row[4]), num(row[3]), num(row[2])) if row and num(row[4]) is not None else (None, None, None)


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("period_dir", type=Path)
    ap.add_argument("--period-end", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--sales-analysis", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--partial", action="store_true", help="write PENDING for what could not be fetched")
    ap.add_argument("--overwrite", action="store_true", help="replace an existing different number")
    ap.add_argument("--allow-jump", action="store_true", help=f"allow kunder to move > ±{JUMP_LIMIT:.0%}")
    a = ap.parse_args()

    label, period, months = quarter_of(a.period_end)
    g = a.period_dir / "Grafkälldata"
    print(f"[fetch] {label} ({period}), months {months}")

    sa = read_sales_analysis(a.sales_analysis, months)
    missing, ext = [], {}
    for key, fn in (("arr_usd", lambda: finops_arr_usd(a.period_end)),
                    ("kunder", lambda: finops_kunder(a.period_end))):
        try:
            ext[key] = fn()
        except Exception as e:                      # noqa: BLE001 — reported, not swallowed
            missing.append(f"{key}: {e}")
            ext[key] = (None, None)
    if missing and not a.partial:
        raise FetchError("Could not fetch:\n  " + "\n  ".join(missing) +
                         "\nFix access, or run with --partial for a draft.")

    notes: list[str] = []
    sheets = {n: Sheet(g / f"{n}_per_kvartal_källdata.csv") for n in
              ("arr", "kunder", "telefonnummer", "premium", "nya_kunder", "cac", "premium_andel")}
    sheets["telefonnummer"].upsert(label, period, {"Antal": sa["telefon"][0]}, sa["telefon"][1], a.overwrite, notes)
    sheets["premium"].upsert(label, period, {"Antal": sa["premium"][0]}, sa["premium"][1], a.overwrite, notes)
    sheets["nya_kunder"].upsert(label, period, {"Antal": sa["nya"][0]}, sa["nya"][1], a.overwrite, notes)
    sheets["cac"].upsert(label, period, {"CAC": sa["cac"][0]}, sa["cac"][1], a.overwrite, notes)

    kunder, ksrc = ext["kunder"]
    if kunder is not None:
        prev = sheets["kunder"].row(prev_quarter_label(label))
        pv = num(prev[2]) if prev else None
        if pv and abs(kunder / pv - 1) > JUMP_LIMIT and not a.allow_jump:
            raise FetchError(f"kunder {kunder} vs {pv:.0f} in {prev[0]} = {kunder/pv-1:+.1%}. "
                             f"Check for the ENTERPRISEID double count; --allow-jump if real.")
    sheets["kunder"].upsert(label, period, {"Antal": kunder if kunder is not None else PENDING},
                            ksrc or PENDING, a.overwrite, notes)
    pb = sa["premium"][0] + sa["business"][0]
    sheets["premium_andel"].upsert(label, period, {
        "Premium": sa["premium"][0], "Business": sa["business"][0], "Premium+Business": pb,
        "Kunder": kunder if kunder is not None else PENDING,
        "Andel": f"{100 * pb / kunder:.1f}" if kunder else PENDING},
        f"{a.sales_analysis.name} r755+756, r777+778; kunder: {ksrc or PENDING}", a.overwrite, notes)

    usd = ext["arr_usd"][0]
    arr_msek, rate, arr_usd = arr_sheet(sheets["arr"], label, period, usd, a.period_end, a.overwrite, notes)

    # data.json — .current and .source only
    dp = a.period_dir / "data.json"
    d = json.loads(dp.read_text(encoding="utf-8"))
    def setk(key, cur, src):
        k = d["kpis"][key]
        if cur is None:
            return
        keep = k.get("source", "")
        keep = keep[keep.find("Jämförelsetal"):] if "Jämförelsetal" in keep else ""
        k["current"] = cur
        k["source"] = (src + (". " + keep if keep else "")).strip()
    setk("cac_kr", sa["cac"][0], sa["cac"][1])
    setk("aktiva_betalande_kunder", kunder, ksrc)
    if arr_msek is not None:
        notes.append(f"arr_per_kvartal_källdata.csv: {label} {arr_usd:.4f} MUSD x {rate:.5f} = {arr_msek} MSEK")
        d["kpis"].setdefault("arr_musd", {"current": None, "prior": None, "unit": "MUSD", "yoy_pct": None})
        setk("arr_musd", round(arr_usd, 4), f"finops arr_total {a.period_end}")
        setk("arr", arr_msek, f"finops arr_total {a.period_end} = {arr_usd:.4f} MUSD x {rate:.5f} "
                              f"(Riksbank SEKUSDPMI)")

    print("\n".join("  " + n for n in notes))
    for m in missing:
        print(f"  [PENDING] {m}")
    if a.dry_run:
        print("[fetch] dry run — nothing written")
        return
    for s in sheets.values():
        s.save()
    dp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[fetch] wrote 7 CSVs and data.json{' (partial)' if missing else ''}")


if __name__ == "__main__":
    try:
        main()
    except FetchError as e:
        print(f"\n[FAIL] {e}", file=sys.stderr)
        sys.exit(2)
