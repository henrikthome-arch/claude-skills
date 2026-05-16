# Financial data shapes

The Finops agent produces four JSON files in the meeting's `financials-data/` folder. These are the canonical shapes — keep the agent prompt aligned with them so render.py adapters don't break.

## 1. `q1-budget-vs-actual.json`

Quarterly P&L with actual + budget per line. Renders into a `pnl_table` slide.

```json
{
  "period": "2026 Q1 (Jan-Mar)",
  "currency": "SEK",
  "rows": [
    {
      "label": "Nettoomsättning",
      "actual": 7460106,
      "budget": 7943362.0,
      "variance_abs": -483256.0,
      "variance_pct": -6.08
    },
    {
      "label": "Personalkostnader",
      "actual": -2479308,
      "budget": null,
      "variance_abs": null,
      "variance_pct": null,
      "_note": "parent-company budget doesn't map 1:1 to consolidated KR label"
    }
  ],
  "source": {
    "actuals": "<path to KR data.json>",
    "budget": "Finops table group_pl_budget (fiscal_year_id=N) summed over periods YYYYMM-YYYYMM"
  }
}
```

**Important**: Some rows may have `budget: null` if the budget structure doesn't map cleanly. The renderer handles this — it shows "—" in the budget column.

Currently `pnl_table` slides inline these `rows` into the slide's `pnl_rows` (no `data_ref` adapter yet — manual copy). To be improved.

## 2. `april-kpis.json`

Monthly Pulse KPIs. Currently transformed manually into a `kpi_grid` slide (no adapter yet).

```json
{
  "period": "2026-04",
  "comparison": {"mom": "2026-03", "yoy": "2025-04"},
  "kpis": {
    "arr": {
      "current_usd": 2681746.93,
      "current_sek": 24822412.9,
      "mom_pct_usd": -1.51,
      "mom_pct_sek": -2.09,
      "yoy_pct_usd": 6.26,
      "yoy_pct_sek": 0.47,
      "budget_sek": 29464831.64,
      "budget_dev_pct": -15.8
    },
    "revenue":     {...},
    "acquisition": {"daily_avg": 109, "total_mtd": 3257, "with_subscription": 2267, "without_subscription": 990, "mom_pct": ..., "yoy_pct": ...},
    "net_churn":   {"rate_pct": 7.54, "mom_pp_change": -0.78, "yoy_pp_change": 0.21},
    "subscribers": {"total": 33570, "mom_pct": ..., "yoy_pct": ...},
    "ebitda":      {"value_sek": 736858.96, "actual_month": "2026-03", "mom_pct": ..., "yoy_pct": ..., "note": "April SIE not yet booked"}
  },
  "_metadata": {"sek_rate_usd_per_sek": {...}, "source": "..."}
}
```

When constructing the kpi_grid slide manually:
- The big `value` on each card is the YoY USD-basis % (e.g. "+6%", "−8%"). Format with the special Unicode minus `−`, not ASCII hyphen.
- `tone`: positive for + delta, negative for − delta, neutral for absolute rates (net churn).
- `lines` (up to 3): primary breakdown, secondary currency, budget delta.

## 3. `april-breakeven.json`

```json
{
  "period": "2026-04",
  "note": "P&L expense levels (fixed costs, gross margin) are from 2026-03 (latest SIE-booked).",
  "pl_data_month": "2026-03",
  "revenue_msek": 2.61,
  "breakeven": {"target_msek": 2.57, "actual_msek": 2.61, "gap_msek": 0.04, "gap_pct": 1.7, "status": "achieved"},
  "cash_flow": {"target_msek": 2.34, "actual_msek": 2.61, "gap_msek": 0.28, "gap_pct": 11.8, "status": "positive"}
}
```

Maps to a `breakeven` slide. Status mapping for the slide's left-border color:
- `"achieved"` / `"positive"` → `status: "ok"` (green border)
- `"missed"` / negative gap → `status: "critical"` (red border)
- otherwise → `status: "warn"` (amber border)

## 4. `13-month-trends.json`

```json
{
  "period_label": "13-Month Trends · Apr 2025 – Apr 2026",
  "series": {
    "net_revenue_usd":              [{"month": "2025-04", "value": 308559.01}, ... 13 entries],
    "net_revenue_sek":              [...],
    "arr_usd":                      [...],
    "new_customers_per_day_with_sub":    [...],
    "new_customers_per_day_without_sub": [...],
    "net_churn_rate_pct":           [...],
    "total_subscribers":            [...]
  }
}
```

This file has a `data_ref` adapter in `render.py:expand_data_refs()`. The slide's `trends_layout` tells the renderer which series to plot, with what `kind` (`bar`, `line`, `stacked_bar`) and `y_format`.

Supported `y_format` values: `auto`, `percent`, `thousands`, `thousands_sek`, `msek`, `usd_k`, `usd_m`, `k`.

Stacked bars combine two series — pass `keys: [a, b]` instead of `key: a`. The renderer auto-labels with "With subscription" / "Without subscription" for customer acquisition charts.

Auto-color rules in `render_chart()`:
- `bar` → light teal `#7BC4C4`
- `stacked_bar` → dark teal `#3D7B81` + light teal `#7BC4C4`
- `line` + `y_format: "percent"` → red `#E15454` (churn convention)
- `line` other → light teal `#7BC4C4` with 18% alpha area fill
- Override with `"color": "#hex"` in the layout entry if needed.

## 5. `cash-position.json`

Drives the `cash_position` slide. Pairs a 6-month EOM cash trend with "drivers outside monthly run-rate" — quarterly/annual obligations that fired in the latest month and explain the deviation from the typical monthly cash flow.

```json
{
  "period_label": "EOM Cash Position · Nov 2025 – Apr 2026",
  "currency": "SEK",
  "trend": [
    {"month": "2025-11", "value": 517766},
    {"month": "2025-12", "value": 61058},
    {"month": "2026-01", "value": -576604},
    {"month": "2026-02", "value": -621768},
    {"month": "2026-03", "value": -650434},
    {"month": "2026-04", "value": -755967}
  ],
  "april_change_msek": -0.11,
  "april_drivers": [
    {
      "label": "Skatteverket MOSS/OSS Q1 EU VAT",
      "amount_sek": -206000,
      "note": "Quarterly EU VAT (Jan/Apr/Jul/Oct). Grows with EU revenue."
    },
    {
      "label": "Forvis Mazars annual audit fee (a conto)",
      "amount_sek": -100000,
      "note": "Annual audit fee, booked April only (recurring_payment.annual_month=4)."
    }
  ]
}
```

**Driver classification** (the rule the Finops agent must apply):
- Include only drivers *outside the recurring monthly cost base* — i.e. one-off costs, quarterly recurring (typical Q1/Q4 EU VAT, Certified Advisor fees), or annual recurring (audit fees).
- If the dominant cause is *declining revenue*, list "Declining revenue" as a driver with a SEK estimate of the gap vs. trailing-3-month average revenue.
- Top 3 drivers maximum on the slide. Sub-materiality items (<5K SEK) omitted.

**Identification method** (recorded in `_metadata.method`):
1. Query `recurring_payment` for items with `annual_month == target_month` or `quarter_months` containing `target_month` — these are obligations that fire outside the monthly run-rate.
2. Confirm against `cash-flow forecast top_cost_items` whose descriptions reference the target-month actuals.
3. Where available, cross-check `bank_outflow_transaction` for transaction-level confirmation (often unavailable if bank CSV import lags).

The renderer's `expand_data_refs()` reshapes the file into the slide's `cash_trend` (TrendSeries) and `cash_drivers` (list).

## 6. `cash-flow-forecast.json`

Drives the `cash_flow_forecast` slide. 90 daily balance points + top-5 non-recurring items.

```json
{
  "as_of_date": "2026-05-14",
  "assumed_revenue_msek_month": 2.6,
  "assumed_revenue_sek_day": 86667,
  "revenue_assumption_rationale": "<one paragraph — why this number, e.g. manual override CR-2026-04-06>",
  "actuals_through_date": "2026-05-12",
  "credit_line_sek": -1000000,
  "warning_line_sek": -650000,
  "minimum_projected_balance_sek": -814398.58,
  "minimum_projected_date": "2026-05-28",
  "starting_cash_sek": -755966.75,
  "starting_cash_source": "EOM April 2026 bank snapshot",
  "forecast_horizon_days": 90,
  "daily_balance": [
    {"date": "2026-05-01", "balance_sek": -774691.46, "is_actual": true},
    ...104 entries...
    {"date": "2026-08-12", "balance_sek": 64861.58, "is_actual": false}
  ],
  "top_forecast_items": [
    {
      "label": "Revenue assumption: 2.6 MSEK/month manual override",
      "amount_sek": 2600000,
      "kind": "assumption",
      "expected_date": "monthly (recurring)",
      "note": "<rationale>"
    },
    {
      "label": "Skatteverket — MOSS/OSS EU VAT (Q2 quarterly)",
      "amount_sek": -206000,
      "expected_date": "2026-07-30",
      "kind": "quarterly",
      "note": "<one line>"
    },
    ... up to 5 items total ...
  ],
  "_metadata": {
    "source_endpoints": [
      "POST /api/v1/cash-flow/forecast (start_date=YYYY-MM-DD, forecast_days=N)",
      "GET /api/v1/cash-flow/recurring (to identify monthly run-rate items to exclude)"
    ],
    "method": "Daily balance from CashFlowForecastService.generate_forecast. Top items filtered for kind != 'monthly_recurring' over the forecast window. is_actual=true for dates ≤ actuals_through_date (drawn solid in UI).",
    "extraction_date": "2026-05-14",
    "source_system": "financial-ops portal (Staging)",
    "gaps": [
      "Bank CSV import status not independently verified",
      "Briefing screenshot showed -852,920 SEK; current API returns -814,399 — scheduled payments adjusted since briefing"
    ]
  }
}
```

**Item kind values**: `assumption` | `quarterly` | `annual` | `one_off` | `delayed` (a payment rolled forward from a prior month). The renderer color-codes amount: negative = red (`#D9534F`), positive = green (`#2A7A3A`), assumption = teal-dark (`#163E40`).

**Filtering rule for top_forecast_items**: ALWAYS exclude items where the recurring-payment kind is `monthly_recurring` (salaries, monthly SaaS subscriptions, monthly office rent, monthly DBT capital amortization). The board reads this list for *deviations from run-rate* — adding recurring items defeats the purpose.

**Caveats to surface**: if there's a discrepancy between a briefing screenshot Henrik shared and the live API output, document both in `_metadata.gaps` AND mention briefly in the slide footnote or accept that the slide will show the current Finops state (which is what the board should be discussing anyway).
