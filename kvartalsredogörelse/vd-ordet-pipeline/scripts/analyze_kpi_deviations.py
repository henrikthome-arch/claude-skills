#!/usr/bin/env python3
"""
Identify KPIs and income-statement rows whose YoY change is material enough
to require commentary in VD-ordet. Surfaces flagged items with "WHY?" prompts
so the user can supply underlying factors before drafting the brief.

Usage:
  python3 analyze_kpi_deviations.py <period-folder>

Reads:
  <period-folder>/data.json

Writes:
  <period-folder>/vd-ordet/briefs/kpi-deviations.md
  Also prints the report to stdout.

Flagging rules (any one triggers a flag):
  - SIGN FLIP   — current and prior have different signs (positive ↔ negative)
  - PCT CHANGE  — abs((current - prior) / prior) >= 15%  (or 5pp for percent KPIs)
  - ABS DELTA   — abs(current - prior) >= 0.30 MSEK (catches large moves on small bases)

KPIs whose current OR prior is null are listed separately as "MISSING — fill in".
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

PCT_THRESHOLD = 0.15           # 15% relative change on absolute-value KPIs
PERCENT_PP_THRESHOLD = 5       # 5pp on percent-valued KPIs (margin, ratio)
MSEK_THRESHOLD_SEK = 300_000   # 0.30 MSEK absolute swing
MSEK_DIVISOR = 1_000_000

# Map kpis.* keys to display names + format hint
KPI_DISPLAY = {
    "nettoomsattning": ("Nettoomsättning", "msek"),
    "bruttomarginal_pct": ("Bruttomarginal", "pp"),
    "ebitda_pct": ("EBITDA-marginal", "pp"),
    "rorelseresultat": ("Rörelseresultat", "msek"),
    "resultat_fore_skatt": ("Resultat före skatt", "msek"),
    "kassaflode_loepande": ("Kassaflöde löpande", "msek"),
    "likvida_medel_eom": ("Likvida medel EoM", "msek"),
    "soliditet_pct": ("Soliditet", "pp"),
    "arr": ("ARR", "msek"),
    "saas40_pct": ("SaaS 40", "pp"),
    "aktiva_betalande_kunder": ("Antal betalande kunder", "count"),
    "cac_kr": ("CAC", "kr"),
    "anstallda_snitt": ("Genomsnittligt antal anställda", "count"),
}


def signs_differ(a: float, b: float) -> bool:
    if a == 0 or b == 0:
        return False  # zero → "no sign", don't flag as flip
    return (a > 0) != (b > 0)


def pct_change(current: float, prior: float) -> float | None:
    if prior == 0:
        return None
    return (current - prior) / abs(prior)


def fmt_value(v, kind: str) -> str:
    if v is None:
        return "—"
    if kind == "pp":
        return f"{v:.0f}%"
    if kind == "msek":
        return f"{v:+.2f} MSEK"
    if kind == "kr":
        return f"{v:,.0f} kr".replace(",", " ")
    if kind == "count":
        return f"{v:,.0f}".replace(",", " ")
    return str(v)


def analyze_kpis(kpis: dict) -> tuple[list[dict], list[dict]]:
    """Returns (flagged, missing)."""
    flagged = []
    missing = []
    for key, val in kpis.items():
        if not isinstance(val, dict):
            continue
        cur = val.get("current")
        prior = val.get("prior")
        display_name, kind = KPI_DISPLAY.get(key, (key, "msek"))

        if cur is None or prior is None:
            missing.append({"key": key, "name": display_name})
            continue

        reasons = []
        if signs_differ(cur, prior):
            reasons.append("SIGN FLIP")
        delta = cur - prior
        if kind == "pp":
            if abs(delta) >= PERCENT_PP_THRESHOLD:
                reasons.append(f"{delta:+.1f}pp")
        else:
            pct = pct_change(cur, prior)
            if pct is not None and abs(pct) >= PCT_THRESHOLD:
                reasons.append(f"{pct*100:+.0f}%")
            if kind == "msek" and abs(delta) >= MSEK_THRESHOLD_SEK / MSEK_DIVISOR:
                reasons.append(f"{delta:+.2f} MSEK swing")

        if reasons:
            flagged.append({
                "key": key,
                "name": display_name,
                "current": fmt_value(cur, kind),
                "prior": fmt_value(prior, kind),
                "reasons": reasons,
            })
    return flagged, missing


def analyze_income_statement(table: dict) -> list[dict]:
    """
    Flag rows in resultatrakning where current vs prior column differs materially.
    Columns convention: [current_period, prior_period, ytd_current, ytd_prior]
    """
    flagged = []
    rows = table.get("rows", [])
    for row in rows:
        if row.get("section_header"):
            continue
        vals = row.get("values") or []
        if len(vals) < 2:
            continue
        cur_sek = vals[0]
        prior_sek = vals[1]
        if cur_sek is None or prior_sek is None:
            continue
        cur = cur_sek / MSEK_DIVISOR
        prior = prior_sek / MSEK_DIVISOR

        reasons = []
        if signs_differ(cur, prior):
            reasons.append("SIGN FLIP")
        delta = cur - prior
        pct = pct_change(cur, prior)
        if pct is not None and abs(pct) >= PCT_THRESHOLD:
            reasons.append(f"{pct*100:+.0f}%")
        if abs(delta) >= MSEK_THRESHOLD_SEK / MSEK_DIVISOR:
            reasons.append(f"{delta:+.2f} MSEK")

        if reasons:
            flagged.append({
                "label": row["label"],
                "current": f"{cur:+.2f} MSEK",
                "prior": f"{prior:+.2f} MSEK",
                "reasons": reasons,
                "is_subtotal": bool(row.get("subtotal") or row.get("total")),
            })
    return flagged


def render_report(period_label: str, kpi_flagged, kpi_missing, is_flagged) -> str:
    out = []
    out.append(f"# KPI deviations — {period_label}\n")
    out.append("Items that need explicit commentary in VD-ordet because they moved materially YoY.\n")
    out.append("**For each flagged item, supply the underlying factor (the WHY).** This drives the VD-ordet brief.\n")

    if not kpi_flagged and not is_flagged and not kpi_missing:
        out.append("\n_No material deviations and no missing values._ Move on.\n")
        return "".join(out)

    if is_flagged:
        out.append("\n## Resultaträkning — material YoY deviations\n")
        for f in is_flagged:
            marker = " 🔴 SUBTOTAL" if f["is_subtotal"] else ""
            reasons = " · ".join(f["reasons"])
            out.append(f"- **{f['label']}**{marker}: {f['current']} vs {f['prior']} (`{reasons}`)\n")
            out.append(f"  - **WHY?** _<— fill in underlying driver(s)>_\n")

    if kpi_flagged:
        out.append("\n## KPIs — material YoY deviations\n")
        for f in kpi_flagged:
            reasons = " · ".join(f["reasons"])
            out.append(f"- **{f['name']}**: {f['current']} vs {f['prior']} (`{reasons}`)\n")
            out.append(f"  - **WHY?** _<— fill in underlying driver(s)>_\n")

    if kpi_missing:
        out.append("\n## KPIs — MISSING values (need to be filled)\n")
        for m in kpi_missing:
            out.append(f"- **{m['name']}** (`kpis.{m['key']}`): no value supplied → KPI tile / body shows `XX`\n")

    out.append("\n---\n")
    out.append("Once you've filled in the WHY rows above, paste this file's content into `vd-ordet/transcript.txt` "
               "(or attach as additional underlag) before composing the drafter brief.\n")
    return "".join(out)


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    period_root = Path(sys.argv[1]).resolve()
    data_json = period_root / "data.json"
    if not data_json.exists():
        print(f"[error] {data_json} does not exist", file=sys.stderr)
        sys.exit(2)

    data = json.loads(data_json.read_text())
    period_label = data.get("meta", {}).get("period_label", period_root.name)

    kpi_flagged, kpi_missing = analyze_kpis(data.get("kpis", {}))
    is_table = data.get("tables", {}).get("resultatrakning_koncern", {})
    is_flagged = analyze_income_statement(is_table)

    report = render_report(period_label, kpi_flagged, kpi_missing, is_flagged)

    out_dir = period_root / "vd-ordet" / "briefs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "kpi-deviations.md"
    out_file.write_text(report)

    print(report)
    print(f"\n[wrote] {out_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
