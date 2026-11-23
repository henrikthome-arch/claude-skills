#!/usr/bin/env python3
"""Deterministic generator for the Sonetel board-deck FINANCIALS P&L from Finops.

WHY THIS EXISTS
---------------
The board P&L must be the CONSOLIDATED koncern result, but the financial-ops
`group-pl/{fy}` endpoint does NOT serve koncern figures per line. It returns
*pre-consolidation* category lines (parent + India aggregated) PLUS India
intra-group markup adjustments that must be applied to reach the koncern numbers
that reconcile to `consolidated_profit`:

    india_support_markup (20%)  -> add to Personal-/övriga rörelsekostnader (opex)
    india_rd_markup (10.9%)     -> add to Av/nedskrivningar (depreciation)

(Dividend from the India subsidiary is also eliminated, but only fires in some
months and never affects the operating lines — it's already inside
`consolidated_profit`; we reconcile against that as the ground truth.)

The BUDGET is koncern-level (confirmed by Henrik 2026-06-08) and is only exposed
for cogs / gross_profit / ebitda / depreciation. We derive the rest:
    net_sales budget = gross_profit_budget - cogs_budget
    opex budget      = ebitda_budget - gross_profit_budget
    ebit budget      = ebitda_budget + depreciation_budget
Financial items and Resultat före skatt have NO Finops budget (must come from
Henrik's FY plan) -> emitted as null.

Deriving all this by hand each cycle is brittle and error-prone (e.g. a wrong
adjustment key silently drops the depreciation markup). Hence this script.

NOTE: CLOSED SaaS40 quarters are NOT generated here — their EBITDA is the *published
statutory* basis (Rörelse + avskrivningar), which does NOT reconcile to Finops
(the gap is non-constant and sign-changing). Those stay published-report figures.
The OPEN current quarter, however, gets an INDICATIVE quarter-to-date point via
`--saas40 --period YYYY-QN` (Finops consolidated basis, labelled "(QTD)" + caveat) —
additive, never overwrites a published period. See SKILL.md §33.

USAGE
-----
  FINOPS_TOKEN=... python build_financials.py --period 2026-04            # month
  python build_financials.py --period 2026-Q1                            # quarter
  python build_financials.py --period 2026-04 --reconcile                # show PBT check
  python build_financials.py --period 2026-04 --ytd                      # add YTD + Δ YTD-YoY columns (7-col)
  python build_financials.py --period 2026-04 --write path/to/data.json  # patch pnl_table in place
  python build_financials.py --period 2026-04 --breakeven                 # pulse breakeven vs latest actual revenue

Token resolution order: --token, $FINOPS_TOKEN, then the file
~/Library/CloudStorage/Dropbox/Workspace/financial-ops/mcp-api-token.txt
"""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.request
from pathlib import Path

BASE = os.environ.get("FINOPS_BASE", "http://44.194.218.109:8000/api/v1")
TOKEN_FILE = Path.home() / "Library/CloudStorage/Dropbox/Workspace/financial-ops/mcp-api-token.txt"

# condensed-P&L row labels (Swedish, koncern) in order
LABELS = [
    ("ns",     "Nettoomsättning",                       False),
    ("cogs",   "Direkta kostnader sålda tjänster",      False),
    ("gp",     "Bruttoresultat",                        True),
    ("merged", "Personal- och övriga rörelsekostnader", False),
    ("eb",     "EBITDA",                                True),
    ("dep",    "Av/nedskrivningar",                     False),
    ("ebit",   "Rörelseresultat",                       True),
    ("fin",    "Finansiella poster",                    False),
    ("pbt",    "Resultat före skatt",                   True),
]


def get_token(arg_token: str | None) -> str:
    if arg_token:
        return arg_token
    if os.environ.get("FINOPS_TOKEN"):
        return os.environ["FINOPS_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    sys.exit("No Finops token: pass --token, set $FINOPS_TOKEN, or provide %s" % TOKEN_FILE)


def fetch(path: str, token: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def month_index(token: str) -> dict[str, tuple[dict, int]]:
    """Map 'YYYY-MM' -> (group_pl_data, period_index). Caches one fetch per fiscal year."""
    fys = fetch("/group-pl/fiscal-years", token)["fiscal_years"]
    out: dict[str, tuple[dict, int]] = {}
    for fy in fys:
        data = fetch(f"/group-pl/{fy['id']}", token)
        for i, p in enumerate(data.get("periods", [])):
            out[p] = (data, i)  # latest-loaded wins; FYs don't overlap monthly
    return out


def cons_month(data: dict, i: int) -> dict:
    """Consolidated koncern P&L lines for one month index."""
    c, cal = data["categories"], data["calculated"]

    def adj(key: str) -> float:
        for a in data.get("consolidation_adjustments", []):
            if a.get("key") == key:
                return a["values"][i] or 0.0
        return 0.0

    ns = c["net_sales"]["values"][i]
    cogs = c["cogs"]["values"][i]
    gp = cal["gross_profit"]["values"][i]
    # Opex is DERIVED as "every category that does not have an explicit home below",
    # not an enumerated list. An enumerated list silently drops any category Finops
    # adds: financial-ops CR-2026-08-20 introduced `other_operating_costs`
    # (BAS 7900-7999, realised FX losses) and every month of FY2026 then overstated
    # EBITDA/EBIT/PBT by exactly that line — 907 kSEK cumulative Jan-Jul — because
    # this sum still listed only four keys. Deriving it mirrors Finops' own EBITDA
    # formula and self-heals on the next category addition.
    HOMED = {"net_sales", "cogs", "depreciation", "financial_income", "financial_expense"}
    opex = sum(c[k]["values"][i] for k in c if k not in HOMED and k != "other_income")
    merged = opex + c["other_income"]["values"][i] + adj("india_support_markup")
    dep = c["depreciation"]["values"][i] + adj("india_rd_markup")
    # Dividend from the India subsidiary is financial income to the parent; consolidation
    # eliminates it -> it lands on the Finansiella poster line. Fires only in some months
    # (e.g. January) — missing it silently breaks any quarter/period that includes one.
    fin = c["financial_income"]["values"][i] + c["financial_expense"]["values"][i] + adj("india_dividend")
    eb = gp + merged
    ebit = eb + dep
    pbt = ebit + fin
    return dict(ns=ns, cogs=cogs, gp=gp, merged=merged, eb=eb, dep=dep, ebit=ebit, fin=fin, pbt=pbt,
                _cons_profit=data["consolidated_profit"][i])


_MONTHS = ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]


def _month_label(ym: str) -> str:
    y, m = ym.split("-")
    return f"{_MONTHS[int(m)]} {y}"


def pnl_header(period: str, ytd: bool) -> tuple[list[dict], dict]:
    """Two-row P&L header: a group label over each set of columns, plain labels beneath.
    Henrik 2026-10-04: "hard to understand what each column shows" with ACTUAL / PRIOR YEAR /
    Δ YOY / BUDGET / Δ VS BUDGET / YTD / Δ YTD. Grouping says WHICH period each number is for.
    Keys in pnl_columns stay unchanged (the template picks cell values by them)."""
    if "-Q" in period.upper():
        y, q = period.upper().split("-Q"); y, q = int(y), int(q)
        name, last = f"Q{q}", q * 3
    else:
        y, m = (int(x) for x in period.split("-"))
        name, last = _MONTHS[m], m
    groups = [{"label": name, "span": 3}, {"label": f"{name} budget", "span": 2}]
    labels = {"Actual": str(y), "Prior year": str(y - 1), "Δ YoY": "Change",
              "Budget": "Budget", "Δ vs budget": "Actual vs budget"}
    if ytd:
        groups.append({"label": f"January–{_MONTHS[last]}" if last > 1 else "January", "span": 2})
        labels.update({"YTD": str(y), "Δ YTD": f"vs {y - 1}"})  # no prior-year YTD column, so "Change" read as ambiguous (Henrik 2026-10-04)
    return groups, labels


def fetch_actual_revenue(token: str, usd_sek: float | None) -> tuple[float, str]:
    """Latest COMPLETED month's actual net revenue → (MSEK, 'YYYY-MM').
    Source = /analytics/revenue/trends (SUM net_revenue_usd from customer_monthly_revenue),
    i.e. exactly what Finops' get_month_actual_revenue uses.

    FX: `usd_sek=None` (the default) pulls THAT MONTH's actual rate from the monthly pulse
    (`fx_info.actual_rate`). A hardcoded default used to sit here (9.336) and silently understated
    August 2026 by ~42,600 SEK — the actual rate was 9.50895 — which put the breakeven slide's
    headroom at 4.2% instead of 6.2% in a deck already sent to the board (2026-09-14). Revenue is
    ~95% non-SEK, so a stale rate is never a rounding error. Pass --usd-sek only to override.
    """
    trends = [t for t in fetch("/analytics/revenue/trends", token).get("trends", []) if t.get("net_revenue_usd")]
    last = trends[-1]
    period = last["period"][:7]
    if usd_sek is None:
        fx = (fetch(f"/pulse/monthly?month={period}", token).get("fx_info") or {}).get("actual_rate")
        if not fx:
            sys.exit(f"No fx_info.actual_rate for {period} — pass --usd-sek explicitly.")
        usd_sek = float(fx)
        print(f"[fx] {period}: using pulse actual_rate {usd_sek:.5f} USD/SEK", file=sys.stderr)
    return last["net_revenue_usd"] * usd_sek / 1e6, period


def fetch_cashflow_forecast(token: str) -> dict:
    """Pull /cash-flow/forecast and shape the deck's Daily Cash Balance Projection
    1:1 with the Finops UI (portal/templates/analytics/cash_flow.html).

    KEY: plot the absolute `running_balance` series VERBATIM — do NOT re-derive it
    (the old deck re-based to 0 and used net-of-COGS revenue, sinking the line to
    -1.14M instead of the true -859,749). Reference lines are stored as SIGNED plot
    values exactly as the Finops UI draws them: 0, the WARNING line hardcoded at
    -650,000 (UI hardcodes this — cash_flow.html line ~1416, not derived from
    buffer_sek), and the CREDIT line at -credit_line_sek. Assumed-revenue display is
    the GROSS run_rate_daily (84,000/day = 2.52 MSEK/month), matching the UI label.
    `top_forecast_items` is a curated board view (recurring removed, repayment-to-
    Henrik added) and is PRESERVED by the writer — never overwritten from the API's
    amount-ranked top_cost_items (which would re-introduce the recurring India bundle).
    """
    d = fetch("/cash-flow/forecast", token)
    days = d.get("days") or []
    daily = [{"date": x["day"], "balance_sek": round(x["running_balance"], 2),
              "is_actual": bool(x.get("revenue_is_actual"))} for x in days if x.get("running_balance") is not None]
    rr_day = d.get("run_rate_daily")  # gross SEK/day, the UI's displayed assumption
    credit = d.get("credit_line_sek")
    last_actual = (d.get("actual_revenue_summary") or {}).get("last_date")
    return {
        "as_of_date": d.get("start_date"),
        "start_date": d.get("start_date"),
        "assumed_revenue_msek_month": round(rr_day * 30 / 1e6, 2) if rr_day else None,
        "assumed_revenue_sek_day": rr_day,
        "revenue_growth_pct_monthly": d.get("revenue_growth_pct_monthly"),  # compounding, Finops CR-2026-08-25
        "growth_anchor_month": d.get("growth_anchor_month"),
        "revenue_assumption_rationale": None,  # drop the net-of-COGS clutter banner
        "actuals_through_date": last_actual,
        "credit_line_sek": -abs(credit) if credit is not None else None,  # signed: floor
        "warning_line_sek": -650000.0,  # Finops UI hardcoded warning threshold
        "minimum_projected_balance_sek": round(d["min_balance"], 2) if d.get("min_balance") is not None else None,
        "minimum_projected_date": d.get("min_balance_date"),
        "starting_cash_sek": round(d["starting_cash"], 2) if d.get("starting_cash") is not None else None,
        "starting_cash_source": "Finops /cash-flow/forecast starting_cash (EOM prior balance)",
        "forecast_horizon_days": d.get("forecast_days"),
        "daily_balance": daily,
        "flat_scenario": fetch_flat_scenario(token, d),
        "_metadata": {"source": "Finops GET /api/v1/cash-flow/forecast",
                      "run_rate_source": d.get("run_rate_source"),
                      "min_balance": d.get("min_balance"), "min_date": d.get("min_balance_date")},
    }


def fetch_flat_scenario(token: str, base: dict) -> dict | None:
    """No-growth line next to the growth line (Annika, board call 2026-11-09; Henrik: "always in
    the presentations moving forward"). Finops CR-2026-11-09b: GET ?revenue_growth_pct_monthly=0
    overrides the rate for that one request and saves nothing.
    NEVER send the 0 with POST: that deletes the stored rate for every user (Finops warning).
    Returns None when the stored growth is already 0 (then there is only one line)."""
    if not base.get("revenue_growth_pct_monthly"):
        return None
    f = fetch("/cash-flow/forecast?revenue_growth_pct_monthly=0", token)
    if f.get("revenue_growth_pct_monthly") not in (0, 0.0):
        sys.exit(f"/cash-flow/forecast ignored the 0% override (got {f.get('revenue_growth_pct_monthly')!r}) — "
                 "Finops CR-2026-11-09b not deployed? Do not draw a flat line from growth data")
    days = [x for x in (f.get("days") or []) if x.get("running_balance") is not None]
    return {"label": "No growth",
            "daily_balance": [{"date": x["day"], "balance_sek": round(x["running_balance"], 2)} for x in days],
            "minimum_projected_balance_sek": round(f["min_balance"], 2) if f.get("min_balance") is not None else None,
            "minimum_projected_date": f.get("min_balance_date"),
            "end_balance_sek": round(days[-1]["running_balance"], 2) if days else None}


def build_kpis(token: str, period: str) -> dict:
    """Build the KPI-snapshot cells from the Finops Monthly Business Pulse, 1:1 with
    the Finops UI (portal/templates/analytics/pulse_monthly.html). Pulls the
    pre-computed pulse VERBATIM from GET /api/v1/pulse/monthly?month=YYYY-MM (added by
    CR-2026-06-08-monthly-pulse-api) — do NOT reconstruct it from piecemeal endpoints:
    the pulse uses net revenue (not MRR), per-MONTH SEK rates (so SEK deltas ≠ USD
    deltas), subscription_monthly active counts, budget comparison, and an April-EBITDA
    fallback — all of which a hand-rebuild gets wrong (it did, on the first attempt).
    """
    from datetime import date
    UM = "−"  # Unicode minus, matches the rest of the deck
    def pct0(x): return None if x is None else f"{x:+.0f}%".replace("-", UM)
    def pct1(x): return None if x is None else f"{x:+.1f}%".replace("-", UM)
    def pp1(x):  return None if x is None else f"{x:+.1f} pp".replace("-", UM)
    def tone(x): return "neutral" if x is None else ("positive" if x >= 0 else "negative")
    def ksek(v):
        if v is None: return None
        return f"{v/1e6:.1f} MSEK" if abs(v) >= 1e6 else f"{v/1e3:.0f} KSEK"
    def budget_line(c):
        if c.get("budget_sek") is None: return None
        dev = c.get("budget_dev_pct")
        if dev is None: return f"Budget {ksek(c['budget_sek'])}"
        return f"Budget {ksek(c['budget_sek'])} · {pct1(dev)} {'ahead' if dev >= 0 else 'behind'}"
    def delta_line(mom, yoy, *, lead=None):
        """Join MoM/YoY, dropping whichever is missing. The pulse legitimately returns a null
        mom_pct (e.g. EBITDA when the prior month isn't SIE-booked); interpolating it straight
        into an f-string printed a literal 'MoM None' on the board slide."""
        parts = [p for p in (f"MoM {mom}" if mom else None, f"YoY {yoy}" if yoy else None) if p]
        if not parts: return None
        return " · ".join(([lead] if lead else []) + parts)
    def curr_line(c, disp_key):
        d = c.get(disp_key)
        if not d or d == "N/A": return None
        suf = "_usd" if disp_key == "display" else "_sek"
        return delta_line(pct0(c.get('mom_pct'+suf)), pct0(c.get('yoy_pct'+suf)), lead=d)

    d = fetch(f"/pulse/monthly?month={period}", token)
    k = d["kpis"]
    cells = []
    for key, label in (("arr", "ARR"), ("revenue", "Revenue")):
        c = k[key]
        cells.append({"label": label, "value": pct0(c["yoy_pct_usd"]), "tone": tone(c["yoy_pct_usd"]),
                      "lines": [l for l in [curr_line(c, "display"), curr_line(c, "display_sek"), budget_line(c)] if l]})
    ca = k["customer_acquisition"]
    ws, wos = ca.get("with_subscription"), ca.get("without_subscription")
    cells.append({"label": "Customer acquisition", "value": pct0(ca["yoy_pct"]), "tone": tone(ca["yoy_pct"]),
                  "lines": [l for l in [
                      f"{ca['daily_avg']} / day · {ca['total_mtd']:,} MTD" if ca.get("total_mtd") else (f"{ca['daily_avg']} / day" if ca.get("daily_avg") else None),
                      delta_line(pct0(ca.get('mom_pct')), pct0(ca.get('yoy_pct'))),
                      f"{ws:,} with sub / {wos:,} without" if ws is not None and wos is not None else None,
                  ] if l]})
    ch = k["churn"]
    cells.append({"label": "Net churn", "tone": "neutral",
                  "value": f"{ch['rate_pct']:.1f}%" if ch.get("rate_pct") is not None else "N/A",
                  "lines": [l for l in [delta_line(pp1(ch.get('mom_pp_change')), pp1(ch.get('yoy_pp_change')))] if l]})
    s = k["subscribers"]
    cells.append({"label": "Subscribers", "value": pct0(s["yoy_pct"]), "tone": tone(s["yoy_pct"]),
                  "lines": [l for l in [s.get("display"), delta_line(pct0(s.get('mom_pct')), pct0(s.get('yoy_pct')))] if l]})
    e = k["ebitda"]
    am = e.get("actual_month")
    cells.append({"label": f"EBITDA ({am})" if am and am != period else "EBITDA",
                  "value": pct0(e["yoy_pct"]), "tone": tone(e["yoy_pct"]),
                  "lines": [l for l in [e.get("display"), delta_line(pct0(e.get('mom_pct')), pct0(e.get('yoy_pct')))] if l]})

    y, m = int(period[:4]), int(period[5:7])
    pm = (y, m - 1) if m > 1 else (y - 1, 12)
    title = f"{date(y, m, 1).strftime('%B %Y')} — KPI snapshot"
    subtitle = f"MoM = {date(*pm, 1).strftime('%b %Y')} · YoY = {date(y - 1, m, 1).strftime('%b %Y')}"
    return {"title": title, "subtitle": subtitle, "kpis": cells}


def breakeven_from_pl(data: dict, actual_msek=None, actual_month=None, fx_factor: float = 1.0) -> dict:
    """Finops monthly-pulse "Breakeven & profitability" targets
    (GroupPLService.calculate_breakeven_runrate), from the latest booked month:
        breakeven = fixed_costs / GM%;  cashflow-neutral = breakeven − |depreciation| × (1 − GM%)
    fixed_costs = gross_profit − adjusted_profit (adjusted_profit = `runrate_profit`).
    Depreciation is the PRE-consolidation `categories.depreciation` line. `fx_factor` adjusts the
    targets for the FX move between the cost month and the actual-revenue month
    (≈ 1 + opex_foreign_pct(0.6) × (rate_now/rate_pl − 1)).

    The "actual" is the **latest completed month's ACTUAL net revenue** (`fetch_actual_revenue`),
    NOT the pulse's forward run-rate and NOT booked MRR. (Henrik 2026-06-08: the breakeven slide
    compares the breakeven point against actual revenue, e.g. May actual revenue.)"""
    cat, cal, ns = data["categories"], data["calculated"], data["categories"]["net_sales"]["values"]
    i = max(j for j in range(len(data["periods"])) if ns[j])
    rev = ns[i]; gp = cal["gross_profit"]["values"][i]; dep = cat["depreciation"]["values"][i]
    fixed = gp - data["runrate_profit"][i]
    gm = gp / rev
    be = fixed / gm * fx_factor
    cf = (fixed / gm - abs(dep) * (1 - gm)) * fx_factor
    cost_month = data["periods"][i]
    rev_lbl = _month_label(actual_month) if actual_month else "actual"
    out = {"based_on_month": cost_month, "gross_margin_pct": round(gm * 100, 2),
           "fixed_costs": round(fixed), "breakeven_msek": round(be / 1e6, 3), "cashflow_msek": round(cf / 1e6, 3),
           "subtitle": f"Breakeven from {_month_label(cost_month)} costs · actual = {rev_lbl} revenue"}
    if actual_msek is not None:
        be_m, cf_m = be / 1e6, cf / 1e6
        # Gaps and status from the UNROUNDED actual — rounding first overstated the gap % (QC 2026-10-04).
        a = actual_msek
        out["breakeven_boxes"] = [
            {"label": "Breakeven", "target_msek": round(be_m, 2), "actual_msek": round(a, 2),
             "gap_msek": round(a - be_m, 2), "gap_pct": round((a - be_m) / be_m * 100, 1),
             "status": "ok" if a >= be_m else "critical",
             # fixed_costs come from profit AFTER financial items, so interest is in both targets;
             # loan amortisation is a balance-sheet item and is in neither (verified 2026-11-03).
             "scope": "Profit after interest"},
            {"label": "Cash flow positive", "target_msek": round(cf_m, 2), "actual_msek": round(a, 2),
             "gap_msek": round(a - cf_m, 2), "gap_pct": round((a - cf_m) / cf_m * 100, 1),
             "status": "ok" if a >= cf_m else "critical",
             "scope": "Includes interest. Excludes loan repayments."},
        ]
    return out


def breakeven_from_api(token: str, actual_msek: float, actual_month: str | None) -> dict:
    """Breakeven slide from Finops GET /pulse/breakeven (CR-2026-11-03b, financial-ops), the same
    figures as the Pulse page — never re-derive them here.
      Box 1 "Breakeven": target from the last 12 booked months (FX-adjusted by Finops), compared with
            the latest completed month's ACTUAL revenue (Henrik 2026-06-08, §37) — not the API run rate.
      Box 2 "Cash-flow positive": monthly sales needed for positive cash over the next 12 months
            (Finops sales_needed_sek) vs the same actual. Finops status green/amber/red -> ok/warn/critical.
    Amounts are shown to 2 decimals: at a thin margin, 1 decimal reads 2.5 vs 2.6 with a +0.1 gap."""
    d = fetch("/pulse/breakeven", token)
    be, cf = d["breakeven"], d["cash_forward"]
    if not be.get("available"):
        sys.exit(f"/pulse/breakeven: breakeven unavailable ({be.get('reason')})")
    tgt = be["breakeven"]["target_msek"]
    gap = actual_msek - tgt
    boxes = [{"label": "Breakeven", "status": "ok" if gap >= 0 else "critical",
              "rows": [["Target", f"{tgt:.2f} MSEK"], ["Actual", f"{actual_msek:.2f} MSEK"],
                       ["Gap", f"{gap:+.2f} MSEK ({gap / tgt * 100:+.0f}%)"]],
              "scope": "Target = average monthly costs over the last 12 months, including interest."}]
    if cf.get("available"):
        # Box 2 mirrors box 1 (financial-ops CR-2026-11-03b follow-up, 2026-11-04): the monthly sales
        # needed to cover every payment of the next 12 months (average, incl. planned cost increases,
        # loan repayments and interest; late bills excluded) vs the same actual revenue as box 1.
        # Replaces the three-balance box: one measure per box, same Target/Actual/Gap shape.
        need = cf["sales_needed_sek"] / 1e6
        g2 = actual_msek - need
        boxes.append({"label": "Cash-flow positive",
                      "status": {"green": "ok", "amber": "warn", "red": "critical"}[cf["status"]],
                      "rows": [["Target", f"{need:.2f} MSEK"], ["Actual", f"{actual_msek:.2f} MSEK"],
                               ["Gap", f"{g2:+.2f} MSEK ({g2 / need * 100:+.1f}%)"]],
                      "scope": "Target = average monthly payments over the next 12 months, including planned cost increases, loan repayments and interest."})
    m0, m1 = be["basis"].split(": ", 1)[1].split(" \u2013 ")
    rev_lbl = _month_label(actual_month) if actual_month else "actual"
    out = {"breakeven_boxes": boxes,
           "subtitle": f"Actual = {rev_lbl} revenue",
           "note": (f"Cash dips to {cf['min_balance_sek'] / 1e6:.2f} MSEK on {_day_label(cf['min_balance_date'])}"
                    f"{', below the ' + format(cf['warning_line_sek'] / 1e6, '.2f') + ' MSEK warning line' if cf['min_balance_sek'] < cf['warning_line_sek'] else ''}."
                    ).replace("-", "\u2212") if cf.get("available") else None,
           "based_on_month": be.get("based_on_month"),
           "_source": {"endpoint": "/pulse/breakeven", "reference_date": d.get("reference_date"),
                       "breakeven": be, "cash_forward": cf}}
    return out


# Balance sheet rows for the board slide: (label, [line keys summed], emphasis). Zero lines
# (tangible, receivables, reserves, provisions) are dropped; small current items are grouped.
BS_ROWS = [
    ("Fixed assets", ["total_fixed_assets"], False),
    ("Receivables and prepaid", ["accounts_receivable", "other_receivables", "prepaid_accrued_income"], False),
    ("Cash and bank", ["cash"], False),
    ("Total assets", ["total_assets"], True),
    ("Equity", ["total_equity"], False),
    ("Loans, long and short term", ["long_term_liabilities", "liabilities_credit_institutions"], False),
    ("Accounts payable", ["accounts_payable"], False),
    ("Other liabilities", ["tax_liabilities", "other_current_liabilities", "accrued_expenses",
                                         "provisions", "untaxed_reserves"], False),
    ("Total equity and liabilities", ["total_equity_and_liabilities"], True),
]


def build_balance_sheet(token: str, period: str, scope: str = "group") -> dict:
    """Balance sheet slide from Finops GET /balance-sheet. scope="group" (default since 2026-11-05):
    Sonetel AB + India subsidiary, BDO's consolidation method; scope="parent": Sonetel AB only
    (CR-2026-11-04b). A group column with estimate=true (markup elimination estimated until BDO's
    quarterly figures) gets a * on its label and a footnote line.
    Reporting month = the month, or the quarter's last month; compared with three months
    earlier and twelve months earlier. Refuses numbers unless Finops says they balance.
    Equity is TOTAL equity (Finops note: 'Profit for the period' resets at a year-end)."""
    from datetime import date as _d
    period = period.upper()
    if "-Q" in period:
        y, q = period.split("-Q"); y, m = int(y), int(q) * 3
    else:
        y, m = map(int, period.split("-"))
    def back(n):
        t = y * 12 + (m - 1) - n
        return f"{t // 12}-{t % 12 + 1:02d}"
    # Reporting month, a quarter back, the last year-end (when it isn't already one of them; Henrik
    # 2026-11-04: the Dec 2025 loan peak was invisible without it), and a year back.
    ye = f"{y - 1}-12" if m != 12 else None
    pers = [f"{y}-{m:02d}", back(3)] + ([ye] if ye and ye not in (back(3), back(12)) else []) + [back(12)]
    d = fetch(f"/balance-sheet?scope={scope}&periods={','.join(pers)}", token)
    if d.get("scope_key", "parent") != scope:
        sys.exit(f"/balance-sheet: asked for scope={scope}, got {d.get('scope_key')!r}")
    est = [bool(c.get("estimate")) for c in d["columns"]]
    if not d.get("balances"):
        sys.exit(f"/balance-sheet: does not balance for {pers} — do not use ({d.get('columns')})")
    if any(c.get("status") != "ok" for c in d["columns"]):
        sys.exit(f"/balance-sheet: column status not ok: {d['columns']}")
    L = {l["key"]: l["values"] for l in d["lines"]}
    k = lambda v: f"{v / 1e3:,.0f}".replace(",", " ").replace("-", "\u2212")
    dk = lambda v: ("+" if v > 0 else "") + k(v) if round(v / 1e3) != 0 else "0"
    lbl = lambda ym: _d(int(ym[:4]), int(ym[5:]), 1).strftime("%b %Y")
    n = len(pers)
    # Every balance line must land in exactly one row: the rows must add up to Finops' totals.
    for tot, part in (("total_assets", ["total_fixed_assets", "accounts_receivable", "other_receivables",
                                        "prepaid_accrued_income", "cash"]),
                      ("total_equity_and_liabilities", [x for _, ks, e in BS_ROWS if not e and ks[0] not in
                       ("total_fixed_assets", "accounts_receivable", "cash") for x in ks])):
        for i in range(n):
            gap = L[tot][i] - sum(L[x][i] or 0 for x in part)
            if abs(gap) > 1:
                sys.exit(f"/balance-sheet: rows miss {gap:,.0f} SEK of {tot} in {pers[i]} — a line is not mapped in BS_ROWS")
    rows = []
    for name, keys, emph in BS_ROWS:
        v = [sum(L[x][i] or 0 for x in keys) for i in range(n)]
        rows.append({"cells": [name] + [k(x) for x in v] + [dk(v[0] - v[1]), dk(v[0] - v[-1])],
                     **({"emphasis": True} if emph else {})})
    who = {"group": ("group", "Sonetel group (incl. India)"), "parent": ("parent company", "Sonetel AB")}[scope]
    sub = f"{who[1]}, KSEK, at month-end."
    if any(est):
        sub += " * Estimate until BDO's quarterly figures."  # keep short: a 2-line subtitle pushes the note off
    return {"type": "data_table", "dense": True, "title": f"Balance sheet — {who[0]}",
            "subtitle": sub,
            "columns": [{"label": "", "align": "left"}] + [{"label": lbl(x) + ("*" if e else "")} for x, e in zip(pers, est)]
                       + [{"label": "vs " + lbl(pers[1])[:3]}, {"label": "vs " + lbl(pers[-1])}],
            "rows": rows, "_source": {"endpoint": "/balance-sheet", "scope": scope, "periods": pers}}


# Spot values Finops verified on 2026-11-09 after the subscriber double-count fix (SNTLRND-9836).
# month -> (new/day, lost/day, net/day). If the API ever disagrees, the data has regressed: stop.
SUB_FLOW_KNOWN = {"2025-05": (186.6, 109.5, 77.1), "2026-06": (100.6, 125.7, -25.1),
                  "2026-10": (97.7, 94.8, 2.9)}
SUB_COUNT_KNOWN = {"2026-06": 32133}   # 36,623 = the double-counted value before the fix


def build_subscriber_flow(token: str, start: str, end: str) -> dict:
    """"Paying customers with subscriptions" per day: new, lost (churn) and net increase.
    Henrik 2026-11-09, spec from Finops. All from the API (never the sales_analysis Excel):
      new(m)  = GET /metrics/trend?metric=customers_new_paying_monthly_total (monthly)
      subs(m) = GET /monthly-metrics?metric_name=subscriptions_positive_balance (month-end)
      new/day = round(new(m) / days, 1); net/day = (subs(m) - subs(m-1)) / days;
      lost/day = new/day - net/day.
    The month before `start` is fetched too: May needs April's count."""
    import calendar
    def prev(ym):
        y, m = int(ym[:4]), int(ym[5:])
        return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"
    y2, m2 = int(end[:4]), int(end[5:])
    last = calendar.monthrange(y2, m2)[1]
    tr = fetch(f"/metrics/trend?metric=customers_new_paying_monthly_total&granularity=monthly"
               f"&start_date={start}-01&end_date={end}-{last:02d}", token)
    new = {x["date"][:7]: x["value"] for x in tr["data"]}
    mm = fetch(f"/monthly-metrics?metric_name=subscriptions_positive_balance&from={prev(start)}&to={end}", token)
    subs = {x["year_month"]: x["value"] for x in mm["metrics"]}
    for ym, v in SUB_COUNT_KNOWN.items():
        if ym in subs and subs[ym] != v:
            sys.exit(f"subscriptions_positive_balance {ym} = {subs[ym]}, expected {v} — "
                     "the SNTLRND-9836 correction is missing or regressed; do not build")
    months, ym = [], start
    while ym <= end:
        months.append(ym)
        y, m = int(ym[:4]), int(ym[5:])
        ym = f"{y + 1}-01" if m == 12 else f"{y}-{m + 1:02d}"
    missing = [m for m in months if m not in new or m not in subs or prev(m) not in subs]
    if missing:
        sys.exit(f"subscriber flow: no data for {missing}")
    ser = {"new_per_day": [], "lost_per_day": [], "net_per_day": []}
    for m in months:
        d = calendar.monthrange(int(m[:4]), int(m[5:]))[1]
        npd = round(new[m] / d, 1)
        net = (subs[m] - subs[prev(m)]) / d
        lost = npd - net
        if m in SUB_FLOW_KNOWN:
            exp = SUB_FLOW_KNOWN[m]
            if any(abs(a - b) > 0.06 for a, b in zip((npd, lost, net), exp)):
                sys.exit(f"subscriber flow {m}: got new {npd} lost {lost:.1f} net {net:.1f}, "
                         f"Finops verified {exp} — stop and report to Finops")
        ser["new_per_day"].append({"month": m, "value": npd})
        ser["lost_per_day"].append({"month": m, "value": round(lost, 1)})
        ser["net_per_day"].append({"month": m, "value": round(net, 1)})
    return {"title": "Paying customers with subscriptions", "series": ser,
            "_source": {"new": "/metrics/trend customers_new_paying_monthly_total",
                        "subs": "/monthly-metrics subscriptions_positive_balance",
                        "window": [start, end], "subs_month_end": {m: subs[m] for m in [prev(start)] + months}}}


def _day_label(iso: str) -> str:
    from datetime import date as _d
    x = _d.fromisoformat(iso)
    return f"{x.day} {x.strftime('%b')}"


def budget_month(data: dict, i: int) -> dict:
    cb = data["categories"]["cogs"].get("budget")
    db = data["categories"]["depreciation"].get("budget")
    gb = data["calculated"]["gross_profit"].get("budget")
    eb = data["calculated"]["ebitda"].get("budget")
    if not all(isinstance(x, list) and x[i] is not None for x in (cb, db, gb, eb)):
        return {k: None for k, _, _ in LABELS}
    c, d, g, e = cb[i], db[i], gb[i], eb[i]
    return dict(ns=g - c, cogs=c, gp=g, merged=e - g, eb=e, dep=d, ebit=e + d, fin=None, pbt=None)


def agg(dicts: list[dict]) -> dict:
    keys = [k for k, _, _ in LABELS] + ["_cons_profit"]
    out = {}
    for k in keys:
        vals = [d.get(k) for d in dicts]
        out[k] = None if any(v is None for v in vals) else sum(vals)
    return out


def pct(x, base):
    # A % change across zero is meaningless: Aug 2026 PBT −4,785 vs budget +171,796 printed
    # "−102.8%" and Henrik asked "that is impossible?" (2026-10-12). Show "—" instead.
    if x is None or base in (None, 0) or (x < 0) != (base < 0):
        return None
    return round((x - base) / abs(base) * 100, 1)


def resolve_months(period: str) -> tuple[list[str], list[str], str]:
    """Return (current_months, prior_year_months, subtitle) for 'YYYY-MM' or 'YYYY-QN'."""
    period = period.upper()
    if "-Q" in period:
        y, q = period.split("-Q")
        y, q = int(y), int(q)
        m0 = (q - 1) * 3 + 1
        cur = [f"{y}-{m:02d}" for m in range(m0, m0 + 3)]
        prior = [f"{y-1}-{m:02d}" for m in range(m0, m0 + 3)]
        sub = f"Q{q} {y} vs Q{q} {y-1}, koncernen (SEK)"
    else:
        y, m = period.split("-")
        cur = [f"{int(y)}-{int(m):02d}"]
        prior = [f"{int(y)-1}-{int(m):02d}"]
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        sub = f"{months[int(m)]} {y} vs {months[int(m)]} {int(y)-1}, koncernen (SEK)"
    return cur, prior, sub


def resolve_ytd(period: str) -> tuple[list[str], list[str]]:
    """YTD = Jan..(last month of the period) for the calendar year, and the same for prior year."""
    period = period.upper()
    if "-Q" in period:
        y, q = period.split("-Q"); y = int(y); last = int(q) * 3
    else:
        y, m = period.split("-"); y = int(y); last = int(m)
    cur = [f"{y}-{mm:02d}" for mm in range(1, last + 1)]
    pri = [f"{y-1}-{mm:02d}" for mm in range(1, last + 1)]
    return cur, pri


def build_rows(period: str, token: str, reconcile: bool = False,
               fin_budget=None, pbt_budget=None, ytd: bool = False) -> tuple[list[dict], str, list[str]]:
    idx = month_index(token)
    cur_m, py_m, subtitle = resolve_months(period)
    ytd_c_m, ytd_p_m = (resolve_ytd(period) if ytd else ([], []))
    for m in list(cur_m) + list(py_m) + ytd_c_m + ytd_p_m:
        if m not in idx:
            sys.exit(f"Period {m} not found in Finops group-pl (not booked / no fiscal year loaded).")

    cur = agg([cons_month(*idx[m]) for m in cur_m])
    pri = agg([cons_month(*idx[m]) for m in py_m])
    bud = agg([budget_month(*idx[m]) for m in cur_m])
    yc = agg([cons_month(*idx[m]) for m in ytd_c_m]) if ytd else None
    yp = agg([cons_month(*idx[m]) for m in ytd_p_m]) if ytd else None

    # Finansiella poster + Resultat före skatt budget are NOT on the sparse group-pl API —
    # they live in group_pl_budget / get_budget_display (the UI) and stay null here until
    # CR-2026-06-08-group-pl-full-budget ships (then read them from the API and drop these args).
    if fin_budget is not None:
        bud["fin"] = fin_budget
    if pbt_budget is not None:
        bud["pbt"] = pbt_budget

    # The reconciliation is ALWAYS run and ALWAYS fatal on failure. It used to be
    # opt-in and merely printed to stderr — so when financial-ops CR-2026-08-20 added
    # a cost category this script did not read, seven months of overstated EBITDA
    # sailed through unnoticed. A number bound for a board paper does not get a
    # warning it can outrun.
    residual = cur["pbt"] - cur["_cons_profit"]
    ok = abs(residual) < 1
    print(f"[reconcile] {period}: computed PBT {cur['pbt']:,.0f} vs consolidated_profit "
          f"{cur['_cons_profit']:,.0f}  {'OK' if ok else '*** MISMATCH ***'}", file=sys.stderr)
    if not ok:
        sys.exit(
            f"\nRECONCILIATION FAILED for {period}: off by {residual:,.2f} SEK.\n"
            "The computed koncern P&L disagrees with Finops' own consolidated_profit, so one\n"
            "of the lines is wrong. Do NOT put these figures on a slide.\n"
            "Most likely cause: Finops has added a `categories` key this script does not map.\n"
            "Compare data['categories'].keys() against cons_month()'s HOMED set.")

    rows = []
    for key, label, summa in LABELS:
        r = {"label": label, "actual": round(cur[key]), "prior_year": round(pri[key]),
             "variance_yoy_pct": pct(cur[key], pri[key]),
             "budget": (round(bud[key]) if bud[key] is not None else None),
             "variance_pct": pct(cur[key], bud[key])}
        if ytd:
            r["ytd"] = round(yc[key])
            r["variance_ytd_yoy_pct"] = pct(yc[key], yp[key])
        if summa:
            r["summa"] = True
        rows.append(r)
    cols = (["Actual", "Prior year", "Δ YoY", "Budget", "Δ vs budget", "YTD", "Δ YTD"] if ytd
            else ["Actual", "Prior year", "Δ YoY", "Budget", "Δ vs budget"])
    return rows, subtitle, cols


def build_saas40_qtd(period: str, token: str) -> dict:
    """Indicative quarter-to-date SaaS40 for a quarter 'YYYY-QN', from the BOOKED months only.
    growth = net-revenue YoY %; margin = EBITDA/net-revenue %; saas40 = growth + margin.
    Finops CONSOLIDATED basis (= Rörelse + avskrivningar). This is INDICATIVE / pre-audit —
    NOT the published BDO statutory SaaS40 used for closed periods (the Finops↔statutory gap
    is non-constant, so this typically overstates margin; growth is basis-independent)."""
    period = period.upper()
    if "-Q" not in period:
        sys.exit("--saas40 needs a quarter period, e.g. --period 2026-Q2")
    idx = month_index(token)
    cur_m, py_m, _ = resolve_months(period)
    booked = [(c, p) for c, p in zip(cur_m, py_m) if c in idx and p in idx]
    if not booked:
        sys.exit(f"No booked months in group-pl for {period}")
    cur = agg([cons_month(*idx[c]) for c, _ in booked])
    pri = agg([cons_month(*idx[p]) for _, p in booked])
    growth = (cur["ns"] / pri["ns"] - 1) * 100
    margin = (cur["eb"] / cur["ns"]) * 100
    y, q = period.split("-Q")
    full = len(booked) == 3
    mon = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    used = [int(c.split("-")[1]) for c, _ in booked]
    rng = mon[used[0]] if len(used) == 1 else f"{mon[used[0]]}–{mon[used[-1]]}"
    return {
        "label": f"Q{q} {y}" + ("" if full else " (QTD)"),
        "growth_pct": round(growth, 1),
        "margin_pct": round(margin, 1),
        "saas40_pct": round(growth + margin),
        "indicative": not full,
        "months_label": f"{rng} {y}",
        "months_used": [c for c, _ in booked],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--period", default=None, help="YYYY-MM (month) or YYYY-QN (quarter)")
    ap.add_argument("--token", default=None)
    ap.add_argument("--cashflow", action="store_true",
                    help="pull the Daily Cash Balance Projection from /cash-flow/forecast (verbatim running_balance)")
    ap.add_argument("--cashflow-out", default=None,
                    help="path to cash-flow-forecast.json to update in place (preserves top_forecast_items)")
    ap.add_argument("--kpis", action="store_true",
                    help="build the KPI snapshot from the Monthly Business Pulse (GET /pulse/monthly), matching the Finops UI")
    ap.add_argument("--saas40", action="store_true",
                    help="compute the INDICATIVE quarter-to-date SaaS40 (needs --period YYYY-QN) from booked months, Finops consolidated basis; upserts the quarter's period on the saas40 slide")
    ap.add_argument("--balance-sheet", action="store_true",
                    help="balance sheet slide (needs --period); --write replaces the existing one or inserts it after the P&L")
    ap.add_argument("--bs-scope", choices=["group", "parent"], default="group",
                    help="balance sheet scope: group (default, consolidated incl. India) or parent (Sonetel AB only)")
    ap.add_argument("--subscriber-flow", nargs=2, metavar=("FROM", "TO"),
                    help="new / lost / net paying subscription customers per day, YYYY-MM YYYY-MM "
                         "(board view: 18 months); writes JSON to --out or stdout")
    ap.add_argument("--out", default=None, help="output path for --subscriber-flow")
    ap.add_argument("--reconcile", action="store_true", help="print PBT-vs-consolidated_profit check to stderr")
    ap.add_argument("--fin-items-budget", type=float, default=None,
                    help="Finansiella poster budget (group_pl_budget — until CR-2026-06-08 exposes it on the API)")
    ap.add_argument("--pbt-budget", type=float, default=None,
                    help="Resultat före skatt budget (group_pl_budget — until CR-2026-06-08 exposes it on the API)")
    ap.add_argument("--ytd", action=argparse.BooleanOptionalAction, default=True,
                    help="YTD + Δ YTD-vs-prior-year columns (7-col layout). ON by default (board standard); use --no-ytd to drop.")
    ap.add_argument("--breakeven", action="store_true",
                    help="compute the monthly-pulse breakeven/profitability vs latest actual revenue, instead of the P&L")
    ap.add_argument("--actual-msek", type=float, default=None,
                    help="override the breakeven 'actual' revenue MSEK (default: latest completed month from the API)")
    ap.add_argument("--usd-sek", type=float, default=None,
                    help="USD→SEK rate for the actual net revenue (default: that month's actual rate "
                         "from the monthly pulse — never hardcode one, see fetch_actual_revenue)")
    ap.add_argument("--fx-factor", type=float, default=1.0,
                    help="FX adjustment on the breakeven targets (cost month vs actual-revenue month; ~1.005)")
    ap.add_argument("--write", default=None, help="patch the first pnl_table slide in this data.json in place")
    args = ap.parse_args()
    token = get_token(args.token)

    if args.cashflow:
        cf = fetch_cashflow_forecast(token)
        if args.cashflow_out:
            p = Path(args.cashflow_out)
            existing = json.loads(p.read_text()) if p.exists() else {}
            cf["top_forecast_items"] = existing.get("top_forecast_items", [])  # preserve curated board view
            cf["revenue_assumption_rationale"] = existing.get("revenue_assumption_rationale")  # preserve curated note
            p.write_text(json.dumps(cf, ensure_ascii=False, indent=2) + "\n")
            print(f"Patched cash-flow forecast: {len(cf['daily_balance'])} days "
                  f"{cf['start_date']}→{cf['daily_balance'][-1]['date']}, "
                  f"min {cf['minimum_projected_balance_sek']:,.0f} on {cf['minimum_projected_date']}, "
                  f"credit {cf['credit_line_sek']:,.0f}.", file=sys.stderr)
        else:
            print(json.dumps(cf, ensure_ascii=False, indent=2))
        return

    if args.subscriber_flow:
        sf = build_subscriber_flow(token, *args.subscriber_flow)
        txt = json.dumps(sf, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            Path(args.out).write_text(txt)
            n = sf["series"]["net_per_day"]
            print(f"Wrote {args.out}: {n[0]['month']}..{n[-1]['month']}, net/day last {n[-1]['value']}.", file=sys.stderr)
        else:
            print(txt)
        return

    if args.balance_sheet:
        if not args.period:
            sys.exit("--balance-sheet needs --period YYYY-MM or YYYY-QN")
        sl = build_balance_sheet(token, args.period, args.bs_scope)
        if args.write:
            p = Path(args.write); data = json.loads(p.read_text())
            for slides in (data.get("items") or {}).values():
                old = [i for i, x in enumerate(slides) if (x.get("_source") or {}).get("endpoint") == "/balance-sheet"]
                pnl = [i for i, x in enumerate(slides) if x.get("type") == "pnl_table"]
                if old:
                    if slides[old[0]].get("notes"):
                        sl["notes"] = slides[old[0]]["notes"]  # preserve the curated note
                    slides[old[0]] = sl; break
                if pnl:
                    slides.insert(pnl[0] + 1, sl); break
            else:
                sys.exit("No pnl_table slide found in %s" % args.write)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Patched balance sheet {sl['_source']['periods']}.", file=sys.stderr)
        else:
            print(json.dumps(sl, ensure_ascii=False, indent=2))
        return

    if args.saas40:
        if not args.period:
            sys.exit("--saas40 needs --period YYYY-QN")
        res = build_saas40_qtd(args.period, token)
        if args.write:
            p = Path(args.write); data = json.loads(p.read_text()); patched = False
            base = res["label"].replace(" (QTD)", "")
            for slides in (data.get("items") or {}).values():
                for s in slides:
                    if s.get("type") == "saas40" and not patched:
                        pers = [pp for pp in (s.get("periods") or [])
                                if not str(pp.get("label", "")).startswith(base)]
                        pers.append({"label": res["label"], "growth_pct": res["growth_pct"],
                                     "margin_pct": res["margin_pct"], "saas40_pct": res["saas40_pct"]})
                        s["periods"] = pers
                        if res["indicative"]:
                            s["notes"] = (f"{res['label']} is quarter-to-date ({res['months_label']}), "
                                          "indicative — Finops consolidated basis, pre-audit.")
                        patched = True
            if not patched:
                sys.exit("No saas40 slide found in %s" % args.write)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Patched saas40 ({res['label']}): growth {res['growth_pct']} + "
                  f"margin {res['margin_pct']} = {res['saas40_pct']}.", file=sys.stderr)
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if not args.period:
        sys.exit("--period is required (unless --cashflow)")

    if args.kpis:
        try:
            res = build_kpis(token, args.period)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                sys.exit("/pulse/monthly not on the API yet — needs CR-2026-06-08-monthly-pulse-api "
                         "(GET /api/v1/pulse/monthly?month=YYYY-MM) implemented in financial-ops first.")
            raise
        if args.write:
            p = Path(args.write); data = json.loads(p.read_text()); patched = False
            for slides in (data.get("items") or {}).values():
                for s in slides:
                    if s.get("type") == "kpi_grid" and not patched:
                        s["title"], s["subtitle"], s["kpis"] = res["title"], res["subtitle"], res["kpis"]
                        patched = True
            if not patched:
                sys.exit("No kpi_grid slide found in %s" % args.write)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Patched kpi_grid ({args.period}): {len(res['kpis'])} cells.", file=sys.stderr)
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if args.breakeven:
        # CR-2026-11-03b: targets come from Finops /pulse/breakeven (12-month basis + 12-month
        # cash forecast). The old one-month breakeven_from_pl path is kept only for reference.
        if args.actual_msek is not None:
            actual, rev_month = args.actual_msek, None
        else:
            actual, rev_month = fetch_actual_revenue(token, args.usd_sek)
        res = breakeven_from_api(token, actual, rev_month)
        if args.write:
            p = Path(args.write); data = json.loads(p.read_text()); patched = False
            for slides in (data.get("items") or {}).values():
                for s in slides:
                    if s.get("type") == "breakeven" and not patched:
                        s["breakeven_boxes"] = res["breakeven_boxes"]
                        s["subtitle"] = res["subtitle"]
                        s.setdefault("title", "Breakeven & profitability")
                        s["breakeven_note"] = res["note"]
                        patched = True
            if not patched:
                sys.exit("No breakeven slide found in %s" % args.write)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Patched breakeven (based on {res['based_on_month']}).", file=sys.stderr)
        else:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    rows, subtitle, cols = build_rows(args.period, token, reconcile=args.reconcile,
                                      fin_budget=args.fin_items_budget, pbt_budget=args.pbt_budget,
                                      ytd=args.ytd)

    if args.write:
        p = Path(args.write)
        data = json.loads(p.read_text())
        patched = False
        for slides in (data.get("items") or {}).values():
            for s in slides:
                if s.get("type") == "pnl_table" and not patched:
                    s["pnl_columns"] = cols
                    s["pnl_rows"] = rows
                    s["pnl_column_groups"], s["pnl_column_labels"] = pnl_header(args.period, "YTD" in cols)
                    s["subtitle"] = "Koncernen, SEK"   # the group headers now carry the periods
                    # Title carries the month too; patching only the subtitle left "July 2026 — …" on an August P&L (2026-10-04).
                    # A quarter period gets "Q3 2026 — …" (board-slides §69: quarter view at quarter close).
                    if re.match(r"^([A-Z][a-z]+|Q\d) \d{4} — ", s.get("title") or ""):
                        qm = re.fullmatch(r"(\d{4})-Q(\d)", args.period)
                        label = f"Q{qm.group(2)} {qm.group(1)}" if qm else _month_label(args.period)
                        s["title"] = re.sub(r"^([A-Z][a-z]+|Q\d) \d{4}", label, s["title"])
                    patched = True
        if not patched:
            sys.exit("No pnl_table slide found in %s" % args.write)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"Patched pnl_table in {args.write} ({args.period}).", file=sys.stderr)
    else:
        print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
