---
name: kvartalsredogörelse
description: Create or update Sonetel AB's Kvartalsredogörelse (Q1/Q3) or Halvårsrapport (H1) for Nasdaq First North. Drives a JSON → HTML/CSS → WeasyPrint → PDF pipeline, with deterministic extraction of the financial tables from BDO's workbook. Distinct from /sonetel-bokslut, which still covers Bokslutskommuniké and Kvartalsrapport on Word.
argument-hint: "[period e.g. jan-jun 2026]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel financial reports. If the current working directory does NOT contain `Sonetel/Financial`, STOP immediately and tell the user: "This skill is for Sonetel financial reports only. Current directory: [cwd]". Do NOT proceed.

You are helping Henrik Thomé, CEO of **Sonetel AB (publ)**, prepare a Swedish **Kvartalsredogörelse** for Q1 or Q3 of the fiscal year. The company is listed on Nasdaq First North Growth Market. The working directory is the relevant **Year** folder under `~/Dropbox/Sonetel/Financial/`.

## What this skill replaces

The old workflow lived in `Documentation/Att skapa kvartalsredogörelse/Att skapa kvartalsredogörelse ver 1.0.pdf` — a 10-step manual that involved pasting BDO numbers into Word tables. The manual explicitly warned (step 10): *"Det är lätt att siffror dubbleras eller missas om antalet rader i Excel-fil och Word-mall inte överensstämmer."* This skill retires that failure mode by making `data.json` the single source of truth.

The old skill (`/sonetel-bokslut`) is **not** replaced — it still drives Bokslutskommuniké, Halvårsrapport, and Kvartalsrapport (the heavier reports). Use the right tool for the report type.

## Pipeline

```
data.json  ──►  pydantic validate  ──►  reconciliation guards (pre-render; see table)
        ──►  matplotlib charts  ──►  Jinja2 → HTML  ──►  placeholder scan (post-render)
        ──►  WeasyPrint  ──►  PDF
```

Single command produces the PDF:

```bash
python3 ~/.claude/skills/kvartalsredogörelse/render.py \
  <period-folder>/data.json \
  <period-folder>/Layoutad/Sonetel\ kvartalsredogörelse\ <period>\ v<N>.pdf \
  --debug    # also writes debug_output.html
```

If any guard fails, the script exits with code 2 and a specific error pointing at the offending JSON path. **Fix the data, don't bypass the guard.** Skipping `--allow-date-mismatch` is the only legitimate override.

## Folder convention per period

```
<Year>/Quarter/<Q-folder>/Kvartalsredogörelse/
├── Underlag från BDO/YYYY MM DD Underlag BDO/    ← BDO source files
│   ├── SonetelKvartal<N><YYMMDD>.zip               (current period)
│   └── SonetelKvartal<N-1><YYMMDD>.zip             (prior-year comparable)
├── data.json                                       ← THE source of truth
├── charts/                                         ← auto-generated PNGs
├── debug_output.html                               ← --debug intermediate
└── Layoutad/
    └── Sonetel kvartalsredogörelse <period> v<N>.pdf
```

Versions: always save as a new `v0.N` (draft) or `v1.N` (released). Never overwrite a delivered version.

## BDO field mapping (xlsx → data.json)

BDO delivers a zip per period — current and prior — both named `SonetelKvartal<N><YYMMDD>.zip`. Inside, the key files are:

| BDO file (per zip) | Purpose | Maps to data.json |
|---|---|---|
| `Kvartalsredogörelse <YYMMDD> inkl kc.xls` (older format) or `Huvudbok kc ... .pdf` | Resultaträkning + Balansräkning + Kassaflöde, koncern | `tables.resultatrakning_koncern`, `tables.balansrakning_koncern`, `tables.kassaflode_koncern` |
| `Saldolista bokslut <YYMMDD> Sonetel AB.pdf` | Per-account balances for moderbolag | (cross-check only — Kvartalsredogörelse uses koncern tables) |
| `Koncernmatris Sonetel AB (publ) ... .pdf` | Konsolideringsmatris | (cross-check) |
| `Kassaflödesanalys kcn ... .pdf` | Kassaflödesanalys koncern | `tables.kassaflode_koncern` (verify against summary table) |
| `Specifikationer kc ... .pdf` | Specifications per account | (drill-down reference) |
| `Verifikationslista kc ... .pdf` | All entries | (audit reference) |
| `1010-101N Balanserade utgifter ... .xlsx` | Capitalized R&D detail | (reference for the Balanserade utgifter row in balansräkning) |
| `Omräkning EK för IB och utdelning <YYMMDD>.xlsx` | Equity adjustments | (cross-check Annat eget kapital movement) |
| `Sonetel Indien/Saldolista bokslut <YYMMDD> Sonetel Indien.pdf` | Subsidiary balances | (cross-check minority interest = "Innehav utan bestämmande inflytande") |

**Workflow for a new period:**

1. Open the **current period's** `Kvartalsredogörelse <YYMMDD> inkl kc.xls` (or equivalent PDF) and the **prior comparable's** equivalent.
2. Copy the columns into `data.json → tables.*` as raw SEK integers. Each row is `{ "label": ..., "values": [current, prior, ytd_current, ytd_prior] }` (4-column tables) or 3 columns for balansräkning.
3. Update `meta.period_label`, `period_short`, `period_short_compare`, `publication_date`, `governance.vd_signing_date`.
4. **Fetch the operational KPIs with `fetch_kpis.py`** (CR-2026-11-18) — never by hand:
   ```
   ~/.weasy/bin/python ~/.claude/skills/kvartalsredogörelse/fetch_kpis.py <period-dir> \
       --period-end 2026-09-30 --sales-analysis "<period-dir>/Underlag - dataserier/sales_analysis_<date>.xlsx"
   ```
   It derives the quarter from `--period-end`, reads `sales_analysis` (telefonnummer, Premium,
   Business, nya kunder, CAC — the workbook **must be opened and saved in Excel** first; any empty
   cell stops the run), finops (ARR, kunder — needs VPN and `FINOPS_API_URL`/`FINOPS_API_TOKEN` in
   the environment; no token file is read) and Riksbanken (USD/SEK). It writes the quarter's row in
   seven `Grafkälldata` CSVs and `.current`/`.source` for `arr`, `aktiva_betalande_kunder`,
   `cac_kr`. It never writes `.prior` or `yoy_pct` — comparatives are the published figures.
   ARR in SEK: every quarter at its own quarter-end day rate, checked against `PUBLICERAT` amounts
   (±0,05 MSEK). `--partial` writes `PENDING` for what it cannot fetch (drafts only, render with
   `--utkast-grafer`); `--dry-run`, `--overwrite`, `--allow-jump` as named.
   **Token, per run (Henrik 2026-11-18):** the finops token is not stored anywhere. Before each run,
   create an empty `finops-token.txt` (mode 600) in the session scratchpad — outside Dropbox — open
   it for Henrik, and ask him to paste the token (named *Claude-henrik-financial-reports*). Pass it
   as `FINOPS_API_TOKEN="$(tr -d '[:space:]' < file)"` with `FINOPS_API_URL=http://44.194.218.109:8000`,
   never echo it, and delete the file right after the run. VPN must be up (a 401 from port 8000
   means reachable, unauthenticated). Validate first: a `--dry-run` on the previous quarter must
   reproduce its published kunder and ARR (jun 2026: 32 133 and 2,5951 MUSD).
5. **Run the deviation analyzer** (see "KPI deviation analysis" section below) — it surfaces income-statement rows and KPIs with material YoY changes. For each flagged item, gather the underlying driver from the user **before** drafting VD-ordet. For cost-side flags, the typical pattern is to spawn a read-only research agent into `Workspace/financial-ops/` to identify root causes (vendor-level breakdowns, one-time vs recurring split). This is a cross-repo read-only operation — do not edit financial-ops files.
5b. **MANDATORY in Q1 cycle (and recommended in every cycle): verify `share_capital.bemyndigande_text` and `sammanstallning[Outnyttjat bemyndigande].antal` against the most recent bolagsstämma kommuniké.** Q1 Kvartalsredogörelse is typically published in May, AFTER that year's ordinarie bolagsstämma (held in April), so a fresh bemyndigande exists by Q1 publication date. Default canonical-source location: `~/Dropbox/Sonetel/Corporate documents/Bolagsstämmor/<YYYY MM DD> Ordinarie bolagsstämma/kommuniké/Kommuniké årsstämma Sonetel <YYYY-MM-DD> v*.pdf`. Read the kommuniké, extract: (a) date of stämma, (b) percentage cap (typically 10% or 20%), (c) full bemyndigande text (omfattning: aktier only vs aktier+teckningsoptioner+konvertibler). Update `bemyndigande_text` verbatim. Compute `Outnyttjat bemyndigande antal` = round(antal_aktier × percentage / 100). Validated Q1 2026: stämma 2026-04-23, mandate 10%, outnyttjat 757 138 (= 10% × 7 571 381). FY24-25 had 20% mandate; never assume — always re-read the kommuniké each cycle.
6. Take `kalendarium` from the **previous published report** and drop events dated on or before this report's publication date (see "Kalendarium rule" section).
7. **Port chart-source CSVs from prior period** (see "Chart source data" section). Copy `Grafkälldata/*.csv` from the previous period's folder, append the nettoomsättning row from BDO, and let `fetch_kpis.py` (step 4) write the operational rows. **Never type `XX` rows by hand** — guard 25 stops a release on them, and that is how three charts ended on Q2 in the jul–sep 2026 draft.
8. Update VD-kommentar paragraphs in `narrative.vd_kommentar` (a list of strings, one per paragraph) — incorporate the WHY answers gathered in step 5.
9. Run `render.py`. If any of the 11 guards fail, fix the data.
10. Visual review the PDF. Iterate v0.1 → v0.N → v1.0 with Henrik.

## KPI deviation analysis

After loading BDO numbers into `data.json`, run the deviation analyzer to identify which KPIs and income-statement rows moved materially YoY and therefore require explicit commentary in VD-ordet:

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/analyze_kpi_deviations.py \
  <period-folder>
```

Writes `<period-folder>/vd-ordet/briefs/kpi-deviations.md` with one bullet per flagged item plus a `**WHY?**` prompt. The analyzer flags:
- **Sign flips** (positive ↔ negative) — always flagged
- **Pct changes** ≥ 15% on absolute KPIs, ≥ 5pp on percent KPIs (margin, ratio)
- **Absolute swings** ≥ 0.30 MSEK on income-statement rows

**Mandatory step**: surface the report to the user, ask for the WHY behind each flagged item, and incorporate the answers into the VD-ordet brief. Without this, VD-ordet risks omitting commentary on material moves that the audience (investors, retail shareholders, sell-side) will notice from the tables alone.

For **cost-side flags** specifically — e.g. "Övriga externa kostnader +67% YoY" — the codified pattern (validated Q1 2026) is to spawn a read-only research agent into `Workspace/financial-ops/` (project root: `/Users/henrik/Library/CloudStorage/Dropbox/Workspace/financial-ops/`) with explicit "no edits, pure investigation" mandate.

**Agent prompt template**:
```
READ-ONLY root-cause investigation. You must NOT edit/write/shell-mutate any file in financial-ops/.

Context: Sonetel AB (publ) is preparing Q<N> <YYYY> Kvartalsredogörelse. BDO numbers show:
[paste the relevant flagged cost lines from kpi-deviations.md, with current vs prior MSEK]

Project root: /Users/henrik/Library/CloudStorage/Dropbox/Workspace/financial-ops/
Read its CLAUDE.md and START-HERE.md first. Staging VPN must be up for cost data.

Investigate:
1. Vendor / supplier breakdowns — which vendors paid more YoY? Top 10 by cost increase.
2. <cost-line-1> breakdown — what categories drove the change?
3. <cost-line-2> breakdown — what categories drove the change?
4. One-time vs recurring split — any lump-sum invoices in current period not in prior?
5. Cost actions in flight — documented initiatives that haven't yet impacted numbers?

Output: ≤500 words markdown report with: drivers per cost line (account number + name + delta), one-time vs recurring split, data gaps, suggested narrative angles for VD-ordet.

NO edits. Pure read.
```

Save the agent's response to `<period-folder>/vd-ordet/briefs/kpi-deviations-WHY-from-finops.md` and treat it as the answer set for the WHY? prompts in `kpi-deviations.md`.

**Validated 2026-05-13 (Q1 jan–mar 2026)**: agent successfully reconciled parent deltas to koncern deltas, identified vendor-level drivers (AI-tjänster, AWS molntjänster, Meta-Google channel mix-shift, etc.), flagged data gaps honestly (no AP-ledger in financial-ops API, only quarterly BDO bundle for 2026, India INR breakdown unavailable). The cross-repo read-only pattern is the recommended approach for cost-commentary research; do not bypass via direct edits.

## Chart source data (Grafkälldata)

Multi-quarter and multi-month chart series live as CSV files under `<period-folder>/Grafkälldata/`. Current set:

**Quarterly (5-bar pattern: last 4 quarters + same quarter prior year)** — fed into Nyckeltal page charts via `_per_kvartal_källdata.csv`:

- `nettoomsattning_per_kvartal_källdata.csv` — quarterly nettoomsättning (MSEK), source = BDO Resultaträkning per period
- `arr_per_kvartal_källdata.csv` — quarterly ARR EOQ (MUSD + MSEK), source = financial-ops API `arr_total`. **DO NOT use the historical `arr_källdata.csv` monthly values** — those came from sales_analysis "Annualized payments" which is a DIFFERENT metric than what FY24-25 Bokslutskommuniké v21 published. Validated: Dec 25 EOQ from FinOps = $2,813M × 9.21 ≈ 25.9 MSEK matches v21 published figure.
- `kunder_per_kvartal_källdata.csv` — quarterly betalande kunder EOQ, source = sales_analysis xlsx Data-fliken row 731 "In accounts with positive balance"
- `telefonnummer_per_kvartal_källdata.csv` — quarterly subscribed phone numbers EOQ, source = sales_analysis xlsx Data-fliken sum of rows 838+839+840 (Monthly + 1-year + 3-year subscriptions, excluding accounts with insufficient funds). Cross-validated Dec 25 sum = 57 962 = FY24-25 v21 published exactly ✅
- `premium_per_kvartal_källdata.csv` — quarterly Premium subscriptions EOQ, source = sales_analysis xlsx Data-fliken sum of rows 755+756 (Premium Monthly + 1-year)
- `cac_per_kvartal_källdata.csv` — quarterly CAC SEK 3-month average EOQ, source = sales_analysis xlsx Data-fliken row 704 "CAC SEK average past 3 months" at EOQ months. Q1 2026 = 47 kr vs Q1 2025 = 162 kr (-71% YoY)

**Monthly (legacy / supplementary)**:

- `arr_källdata.csv` — monthly ARR (MUSD + MSEK). **WARNING**: legacy file from prior period, used wrong source (sales_analysis "Annualized payments"). Either replace with FinOps monthly snapshots OR remove.
- `cac_källdata.csv` — monthly CAC (SEK)

**5-bar chart convention (Henrik 2026-05-13)**: `Nyckeltal`-page charts ideally show 5 bars = last 4 quarters + same quarter prior year (e.g. for Q1 2026: Q1 25, Q2 25, Q3 25, Q4 25, Q1 26 — the Q1 25 anchors the YoY comparison while Q2/Q3/Q4 25 show the trailing trend). The `build_placeholder_charts` function in render.py reads the last 5 rows from `*_per_kvartal_källdata.csv` and builds a 5-bar `bar_chart`. If <5 rows or CSV missing, falls back to 2-bar prior-vs-current from KPI block.

**Workflow per new period**: copy the prior period's `Grafkälldata/*.csv` into the new period's folder, then append rows for the new quarter. Use canonical sources per "Source consistency for operational KPIs" section. If a value is not yet fetched, append `XX` placeholder rows with a "PENDING — <source> via <channel>" note in the source column. This makes it visually obvious in the CSV which rows still need real data.

**USD→SEK currency convention** (validated Q1 2026, follows prior Bokslutskommuniké pattern): apply **ONE single period-end dagskurs to the entire historical series** within a given period's chart. For Q1 2026 this is 9.5173 SEK/USD (dagskurs 2026-03-31). Document the rate in the CSV's footer rows. Re-translating history at each period removes intra-series FX noise and produces a clean SEK chart.

For YoY KPI display in the body, use **period-end dagskurs for both current and comparable** (i.e. Mar 2026 rate for Mar 2026 ARR, Mar 2025 rate for Mar 2025 ARR). This produces the SEK growth shareholders actually experienced. Note: the resulting SEK growth differs from the FX-neutral USD-basis growth (Q1 2026: SEK +15%, USD +22%); SaaS-industry convention prefers USD-basis (constant currency) for SaaS40 because it isolates the operating signal from FX. We pick **USD-basis for SaaS40 specifically** and **SEK-basis for koncern-level ARR YoY display** — see `kpis.arr.source` field for the per-period decision and audit trail.

**Renderer status (corrected 2026-08-19)**: `build_placeholder_charts()` **does** read these CSVs and builds a 5-bar quarterly chart when ≥5 rows exist, falling back to a 2-bar KPI comparison otherwise. Earlier text in this file claiming it only produces 2-bar output was stale and misled two independent reviewers. Chart paths are emitted absolute — a relative path yields `file://Layoutad/...`, which WeasyPrint cannot load, and the page renders with empty chart boxes and no error.

## Source consistency for operational KPIs

**Principle (Henrik 2026-05-13)**: each KPI must come from ONE canonical source, used consistently across periods. ARR can be calculated multiple ways and the same name on different sources can produce non-comparable numbers. Document the chosen source in `data.json kpis.<key>.source` so any future report can reconcile.

**Canonical sources (validated Q1 2026 — exhaustive list)**:

| KPI / data | Canonical source | Endpoint / file / location | Note |
|---|---|---|---|
| **ARR (MUSD/MSEK)** | financial-ops API (mirrors upstream Sonetel billing-system daily email) — this is the **förbättrade ARR-modell** Sonetel rolled out ~1 year ago and reports daily | `GET /api/v1/metrics/trend?metric=arr_total` — value extracted verbatim from "Call report-daily" email's `ARR(Annual recurring revenue)` table, row `Total`. Stored USD-only in `email_metrics`. Confirmed by Henrik 2026-05-13 as **the most accurate ARR source** — replaces older sales_analysis "Annualized payments" methodology which should NOT be used going forward. | Formula owner = upstream billing-system (NOC/billing engineering); financial-ops only mirrors. Audit-trail: `Workspace/financial-ops/config/analytics/email_metric_definitions.yaml:252-265` and `metric_documentation.yaml:24` document `arr_total = arr_phone_numbers + arr_premium_plan + arr_business_plan + arr_business_package`. Cross-validated 2026-05-13: Dec 25 EOQ from FinOps = $2,813M × 9.21 SEK/USD = 25.9 MSEK matches FY24-25 Bokslutskommuniké v21 published figure ✅. SaaS40 uses ARR USD-basis growth (FX-neutral); ARR display in MSEK uses period-end Riksbanken dagskurs |
| **Antal aktiva betalande kunder** | finops `subscriptions` parquet, `COUNT(DISTINCT ENTERPRISEID) WHERE ACCOUNT_STATUS='A'` — **not** the `subscriptions_positive_balance` metric, see warning below. Definition unchanged from `sales_analysis` **row 731** "In accounts with positive balance" (under section 'Customers with subscriptions') | Henrik's hint 2026-05-13: financial-ops also has it via DuckDB-ingested Subscriptions CSV table filtered `WHERE status = 'A'`, count at EOQ. Both should produce same value (validated Mar 2026 = 33 857 via finops `monthly_process_metrics.subscriptions_positive_balance`). xlsx row 731 is canonical because it preserves continuity with FY24-25 Bokslutskommuniké v21 (Dec 2025 row 731 = 33 636 ≈ v21 published 33 600 ✅) and gives YoY history back to 2022+ | DO NOT use email_tables_raw "Active past month" (29 430) — that's activity-filtered, not the canonical positive-balance count. Henrik specifically flagged this as wrong source. |
| **CAC (SEK)** | `sales_analysis_<YYYY-MM-DD>.xlsx` Data-fliken | **row 704 "CAC SEK average past 3 months"** at EOQ (this is the rolling 3-month avg = Q1 average for the 3 months Jan/Feb/Mar at Mar EOQ); also row 703 "CAC SEK" for single-month values used in monthly chart series. **Critical**: the xlsx must be opened+saved in Excel/Numbers to populate cached formula values (formulas like `=FK699*FK4` return None via openpyxl until re-saved). Henrik validated 2026-05-13 by saving `CAC q1 2026.xlsx` which extracts identical row-16 values | Validated Q1 2026: CAC = 47 kr (Q1 26 avg) vs 162 kr (Q1 25 avg), YoY -71%. Cross-check with `Underlag från ledning/CAC q1 2026.xlsx` row 16 matches |
| **SaaS40 (Rule of 40)** | derived per Sonetel canonical formula | **NETTOOMSÄTTNING YoY tillväxt + EBITDA-marginal**. Save calculation breakdown as `<period>/Kvartalsredogörelse/Saas40/Saas40 <period-label> v1.md` (or .xlsx) per period — must show both inputs (nettooms current, prior, growth %; EBITDA absolut, marginal %) and the sum. NOT ARR-based — confirmed Q1 2026 by Henrik | Q1 2026 = 12% (nettooms YoY) + 28% (EBITDA) = **40%**. Earlier (incorrect) draft used ARR USD-basis growth + EBITDA = 50% — that's a common SaaS-industry variant but NOT what Sonetel publishes |
| **Telefonnummer-abonnemang (EOQ count)** | `sales_analysis_<YYYY-MM-DD>.xlsx` Data-fliken | sum of rows **838 (Monthly) + 839 (1-year) + 840 (3-year)** under section r837 'Subscribed phone numbers (excluding accounts with insufficient funds)'. Cross-validated Q1 2026: Dec 25 sum = 42463+13295+2204 = 57 962 ✅ matches FY24-25 v21 published "57 962" | Per kvartal CSV: `<period>/Kvartalsredogörelse/Grafkälldata/telefonnummer_per_kvartal_källdata.csv` |
| **Premium-abonnemang (EOQ count)** | `sales_analysis_<YYYY-MM-DD>.xlsx` Data-fliken | sum of rows **755 (Monthly) + 756 (1 year)** under section r754 'Premium User subscriptions (from daily report)'. Q1 2026: Dec 25 sum = 3655+2001 = 5 656 (FY24-25 v21 reported "5 226" — slight definitional drift; verify if material delta in future cycles) | Per kvartal CSV: `<period>/Kvartalsredogörelse/Grafkälldata/premium_per_kvartal_källdata.csv` |
| **Snitt anställda** | manuell fetch per period: India HR (Padma Karanam) + Sverige headcount (Henrik) | Padma email/Slack each period: "Average for <period> is <N>". Sverige typiskt 2 (Henrik + ev. konsult-räknad-som-anställd). Koncern total = India + Sverige | Validated Q1 2026: India 37 (Padma) + Sverige 2 = **39**; Q1 2025: India 36 + Sverige 2 = **38**. Not in financial-ops API |
| **Resultaträkning, Balansräkning, Kassaflöde** (alla rader) | BDO Kvartalsredogörelse zip | `<period>/Kvartalsredogörelse/Underlag från BDO/<YYYY MM DD> Underlag BDO/SonetelKvartal<N><YYMMDD>.zip` — `Kvartalsredogörelse <YYMMDD> inkl kc.xls` (or PDF equivalent) | Both current period AND prior comparable in same delivery |
| **Bruttomarginal, EBITDA-marginal, Soliditet** | derived from BDO Resultaträkning + Balansräkning | computed in data.json by Henrik/Claude during BDO mapping | — |
| **Cost root-causes (vendor-level breakdowns)** | financial-ops read-only research agent | spawn agent into `Workspace/financial-ops/`, read BDO saldolista + monthly Resultatrapporter | See "KPI deviation analysis" section above for prompt template |
| **Chart-source historical series** (5-bar quarterly + monthly time-series) | each period's `Grafkälldata/*.csv` (built per period from canonical sources above) | `<period>/Kvartalsredogörelse/Grafkälldata/{nettoomsattning,arr,kunder,telefonnummer,premium}_per_kvartal_källdata.csv` (5-bar quarterly) + `{arr,cac}_källdata.csv` (monthly time-series). Each CSV documents source + validation in footer rows | New row(s) per period; source documented in CSV footer per "Chart source data" section |
| **USD/SEK exchange rate** | Riksbanken dagskurs via financial-ops `/api/v1/currency/rate` | Period-end dagskurs applied to entire historical series within a period's chart for consistency | Mar 2026 = 9.5173, Mar 2025 = 10.0314 |
| **Cover & affärsmodell images** | `image-gen/scripts/generate-image.mjs` (Flux model via this skill) | output to `<period>/cover.webp` + `<period>/affarsmodell.webp` | See "Cover & affärsmodell images" section above for prompt rules + audit |
| **VD-ordet drafts** | Henrik i ChatGPT med Claudes brief (API-pipelinen är reserv) | see `vd-ordet-pipeline/PIPELINE.md` | Henrik provides transcript + WHY answers as input |
| **Bemyndigande (share_capital.bemyndigande_text + Outnyttjat-antal)** | most recent ordinarie bolagsstämma kommuniké | `~/Dropbox/Sonetel/Corporate documents/Bolagsstämmor/<YYYY MM DD> Ordinarie bolagsstämma/kommuniké/Kommuniké årsstämma Sonetel <YYYY-MM-DD> v*.pdf` | **Re-read each cycle (especially Q1 since publication is post-stämma).** Validated 2026-04-23: 10% mandate (replaced 18-dec-2024 20% mandate). Outnyttjat = round(antal_aktier × pct/100). Never copy from prior period — always read fresh kommuniké |


### Read the operational KPIs from the finops API, not from the spreadsheet

> **Superseded in part by CR-2026-11-18 (`fetch_kpis.py`).** Telefonnummer, Premium and Business are
> now read from `sales_analysis` (r838–840, r755–756, r777–778) — the workbook is needed for CAC and
> nya kunder anyway, and it needs no VPN. Equivalence with the API was verified below and holds.
> The precondition stays: the workbook must be opened and saved in Excel; the script stops on any
> empty cell. ARR and kunder still come from finops, as below.

Validated 2026-08-19 (CR-2026-08-19). The definitions below are unchanged — only the access path.
`sales_analysis.xlsx` is a *rendering* of finops data, and reading it requires opening and
re-saving the file in Excel, because openpyxl returns `None` for every cached-formula row
(704, 731, 754–756, 838–840). That manual step has no place in a pipeline claiming determinism.

| KPI | Use | Verdict |
|---|---|---|
| Telefonnummer | `phone_numbers_by_term` | **Equivalent** — the insufficient-funds exclusion (`ACCT_STATUS='A'`) is applied identically. Dec-25 = 42 463 + 13 295 + 2 204 = 57 962, matching the published figure |
| Premium | `subscriptions_premium_monthly` + `_annual` | **Equivalent** — matches the spreadsheet rows exactly |
| Aktiva betalande kunder | recompute from the `subscriptions` parquet | **The metric is unsafe** — see below |
| CAC | still requires `sales_analysis.xlsx` | **No API equivalent.** Marketing cost, DIDWW test-number cost, support-org cost and the manual "share of support cases from new customers" assumption are all absent from the API |

⚠ **Do not use `phone_subscriptions_total`.** Despite appearing in the metrics catalogue it is
mis-extracted and returns undifferentiated rows including a currency amount.

⚠ **`subscriptions_positive_balance` was wrong for 2026-06 and 2026-07** — 36 623 against a true
32 133, an 11% phantom spike. Cause: two corrupt rows in `Subscriptions.csv.gz` (an unescaped
quote shifting the columns) make `ENTERPRISEID` mixed `int`/`str`; with pandas' default
`low_memory=True`, `nunique()` counts `5048380` and `'5048380'` separately. Draft
CR-2026-08-19c in financial-ops proposes the fix. **Always sanity-check this metric against the
trend and against `new_paying_accounts` before publishing it** — an 11% monthly jump that
reverses the following month is not a business event.

**Verify equivalence once per metric, record it in the provenance file, and do not re-derive it
every period.**


### Reading `sales_analysis_<date>.xlsx` when you must (CAC only)

CAC is the one KPI with no API path, so the spreadsheet is still required for it. Two traps:

**1. The column is not findable by date.** The `Data` sheet's header row is **row 8**, and its
date headers stop at **2025-05 (column 169)**. Later columns continue monthly with **no header**,
so date matching silently finds nothing and every lookup returns `None`. Count instead:

```
column = 169 + months_since_2025_05      # 2026-06 → column 182
```

Verify the column before trusting it — r731 (kunder), r838 (telefonnummer) and r755 (Premium)
should match the finops API values for that month.

**2. A partial read looks like a successful read.** Rows 703 and 704 (CAC) are formulas with no
cached values and return `None` in *every* column until the file is opened and re-saved in Excel.
Rows 731/838/755 *do* carry cached values, so a script that checks "did I get data?" gets a yes
and a silently missing CAC. Assert specifically that r704 is non-null.

**3. The spreadsheet inherits the `subscriptions_positive_balance` defect.** For 2026-06 its r731
reads 36 623 — the same wrong figure as the API metric, not an independent source. Do not treat
the workbook as a cross-check for that KPI.

**Operational rule**: when an existing KPI's source changes between periods, set a `source` field in `data.json` describing the change AND flag in the VD-ordet brief that the YoY comparison may not be strictly like-for-like. The very first period on a new source is "transitional" — the next period and onward are clean.

**Cost-side commentary**: when deviation analyzer flags cost-line moves, spawn the read-only finops research agent (see "KPI deviation analysis" section above). The agent reconciles BDO accounts to vendor-level drivers — codified as a standard step.




### Subhead spacing — and a CSS specificity trap

Space above a `.subhead-red` in flowing body text: **20pt** in the sammandrag columns, 20pt on the
Övrigt page, 16pt base. Raised from 6pt on 2026-08-20 — *"Det behövs mer spacing ovanför rubriker
i löptext"*. Measured effect: the gap above the period heading went 28,4pt → 44,4pt.

⚠ **Raising the base `.subhead-red { margin }` alone does nothing.** More specific selectors —
`.sammandrag .kpi-paragraphs h3.subhead-red` and `.ovrigt h2.subhead-red` — set their own top
margin and win. I raised the base from 6pt to 16pt, then to 24pt, then to 32pt, and measured the
identical 24,4pt gap every time, because the specific rule was setting `margin-top: 0`. **Change
the specific rule, then verify by measurement.**

**Verifying spacing without opening the PDF** (image display may be unavailable in a long
session): extract text positions with a pypdf `visitor_text` and measure the baseline delta
between a heading and the line above it. Note WeasyPrint's output has **y increasing downward**
in the text matrix, so the preceding line has the *smaller* y — sorting the wrong way measures the
gap below the heading instead and looks like the change had no effect.


### Kommentarer kring verksamheten (Halvårsrapport only)

Between Affärsmodell and Nyckeltal the Halvårsrapport carries the narrative section the
Kvartalsredogörelse does not. Structure, per the jan–jun 2025 precedent (its pages 6–10):

**VERKSAMHETEN UNDER PERIODEN** — eleven sub-headed blocks: Intäkter · Virtuella telefonnummer ·
Premium och Business · Årligt återkommande intäkter (ARR) · Bruttomarginal · Kostnader ·
Investeringar · Resultat · Kassaflöde · Kundanskaffning · Kundbetyg.
**AKTIVA KUNDER** table — five month-end columns, placed with Kundanskaffning.
**VERKSAMHETEN EFTER PERIODEN** — free sub-blocks.
**FRAMTIDSINFORMATION** — 4.4.6(h).

Data shape: `narrative.verksamhet_under_perioden` is a list of `{rubrik, text[], tabell?}`;
`verksamhet_efter_perioden` the same with `rubrik` optional; `framtidsinformation` a list of
paragraphs. The section renders only when `verksamhet_under_perioden` exists, so a
Kvartalsredogörelse is unaffected.

**The section has ONE column container unless something wide has to sit between the halves.**
`verksamhet_under_perioden` and the `VERKSAMHETEN EFTER PERIODEN` / `FRAMTIDSINFORMATION` tail are
emitted from the same Jinja macro, and the template only closes and reopens `.body-2col` when a
block declares `graf_bred`, `tabell` or `bild_bred` (`has_wide`). The reason: two stacked
two-column bands put the first band's column 2 **above** the second band's column 1, so a
paragraph that happens to straddle the boundary reads as if a red section heading had been
dropped into the middle of it. On 2026-08-21 a paragraph under *Produktutveckling* broke that way
the moment a head banner shifted the flow. If you add wide content, the split returns — and that
is fine, because the wide element is itself the visual divider that makes the two bands legible.

**Tables must sit OUTSIDE the `.body-2col` container.** WeasyPrint ignores `column-span: all`,
and a six-column table does not fit inside one ~77mm column — the month headers wrap and the
figures split across lines. The template closes the column div, renders the tables full width,
then reopens it for the remaining blocks.

**Jinja gotcha:** `{{ r.values }}` resolves to the dict's `.values()` *method*, not the `values`
key, and fails with "builtin_function_or_method is not iterable". Use `r['values']`.

**Write this section as a reply to the previous report.** The jan–jun 2025 "Verksamheten efter
perioden" is a list of commitments — senior AI orchestrators in India, a 5× efficiency target,
new mobile apps, technical debt — and page 8 already named the app quality problem as the reason
customer ratings fell. Reporting back against those makes 4.4.6(h) substantive rather than a
formality, and it is what a reader who kept the last report will look for.


**Text templates: [narrative-templates.md](narrative-templates.md).** Sentence patterns per block
with slots, derived from **two** published reports — halvårsrapporten jan–jun 2025 (pp. 6–10) and
Bokslutskommuniké FY24-25 v21 (pp. 7–9). What recurs in both is a pattern; what appears in only
one is a one-off and must not be copied forward. The file also carries the house style rules
(comparative in parentheses, signed percentages, "under perioden" vs "vid periodens slut", and the
rule that **a figure without a stated cause is not finished text**), plus a table of triggers for
when the skill should write analysis of its own beyond the template.

**Write the base text, then flag what cannot be sourced.** For jan–jun 2026 the eleven blocks were
drafted from verified figures, with explicit `XX` and a stated requirement wherever a number had no
documented source — CAC (needs the workbook re-saved), the jan–jun 2025 new-customer comparative
(`monthly_process_metrics` starts 2025-07), and the Trustpilot rating. Never fill a slot with a
plausible number.

**The Skype framing is already published.** Bokslutskommuniké v21 states that Microsoft's Skype
shutdown drove the 2025 inflow and that it *"normaliserades successivt under hösten 2025"*. A later
report continues that explanation rather than introducing one, which is a far stronger position
than explaining a decline for the first time.

### Sammandrag: two blocks in a Halvårsrapport, one in a Kvartalsredogörelse

From the halvårsrapport jan–jun 2026 the summary page carries **two** blocks — the quarter first,
then the reporting period:

```
KONCERNEN ANDRA KVARTALET 2026 (APRIL – JUNI)
KONCERNEN JANUARI – JUNI 2026
```

**Why.** The precedent report showed only the half-year, because BDO did not deliver quarterly
columns until 2026. Now it does, and the half-year alone hides the newest information. For
jan–jun 2026 the divergence was large in both directions: revenue fell 4% over the half-year but
**16% in the quarter**, while the quarter was *more* profitable than the half-year (operating
result 0,41 MSEK for Q2 against 0,40 for all of H1, because Q1 ran a small loss).

The deciding argument is not presentation but exposure: **the financial tables already carry the
quarterly columns**, so any reader can compute the quarterly decline themselves. A company that
does not mention a figure its own tables disclose looks evasive. Publish both and you own the
decline while also claiming the improvement.

First North 4.4.5: quarterly figures are a voluntary addition and may never *replace* the
half-year figures. Here they supplement.

**Only flow measures belong in the quarter block.** Likvida medel, soliditet, antal kunder,
antal aktier and the like are measured at period end and are identical whether the period is
called a quarter or a half-year — repeating them is noise. `derive_kpis()` enforces this via
`FLOW_ONLY`.

**It is automatic.** The block renders when `resultatrakning_koncern` has ≥4 columns and
`meta.quarter_label` is set. A Kvartalsredogörelse has neither and is unaffected.

**Both blocks must sit in ONE `.kpi-paragraphs` container.** That element is `column-count: 2`,
so two containers produce two independent column sets and the text visibly restarts at the block
boundary — Henrik flagged it immediately as unnatural. With a single container the quarter block
fills the top of the left column, the period heading falls mid-column, and the rest runs on into
the right column unbroken. The headings carry `break-after: avoid` so one is never stranded alone
at a column foot.

**Verifying column layout without opening the PDF:** `pdftotext -layout` reproduces the visual
arrangement; plain `extract_text()` gives content order and will look correct even when the
columns are wrong.

## Derived figures are computed, never typed

`derive_kpis()` runs after validation and before the guards. It computes every KPI that follows
arithmetically from the tables — nettoomsättning, rörelseresultat, resultat före skatt, likvida
medel, kassaflöde, bruttomarginal, EBITDA-marginal, soliditet, SaaS40, and `yoy_pct` for any KPI
with both sides — and fills them where `data.json` leaves them null.

**A supplied value is not overwritten; it is checked.** A disagreement beyond tolerance is
guard 23 and a hard error. The rule: if a figure can be derived from a table, do not type it in.
Typing it creates a second place to be wrong, which is the failure class this pipeline exists to
remove.

The same applies to `kpi_tiles`. A tile left on `XX` is filled from the KPI it maps to; guard 12
then still catches any hand-edited tile that drifts.

**Externally sourced KPIs must still be supplied:** ARR, aktiva betalande kunder, telefonnummer,
Premium, CAC, snitt antal anställda, resultat per aktie.

## Sign-aware language

`fmt_change(yoy)` renders the change sentence. The template previously hardcoded
`ökade med +{{ pct }}%`, which turns a decline into "ökade med -2%". Use `fmt_change` for any
sentence describing a change; never concatenate a sign in the template.

**Convention (Henrik 2026-08-19): decreases carry the minus sign, increases do not.**

| Case | Output |
|---|---|
| +10 | `ökade med 10%` |
| −2 | `minskade med -2%` |
| 0 | `var oförändrad` |
| null | `förändrades med XX%` |

The minus is deliberate — it makes the direction visible in the figure itself and matches the
signed KPI tiles. It is strictly a double negative, and Henrik has been told; he prefers it. Do
not "fix" it in a later period.

## Seeding a period from the previous one

Copying the prior period's `data.json` is the fastest start and the most reliable way to publish
a stale field. These carry over silently and are **not** caught by the numeric guards:

| Field | Symptom if missed |
|---|---|
| `governance.vd_signing_date` | The signature page carries the previous report's date |
| `transaktioner_narstaende` | "under perioden januari – mars" in a half-year report |
| `boilerplate.version_stamp` | Wrong month stamp in the footer |
| `assets.*` | Previous period's cover and affärsmodell images |
| `kalendarium` | Events that have already passed |

Guard 8 (`publication_date == vd_signing_date`) catches the signing date — **but only if you are
not passing `--allow-date-mismatch`.** That flag is for a deliberate mismatch, not for getting a
draft to render. Using it during skeleton work is how a stale signing date survives to v0.5.

After seeding, grep the file for the previous period's month names and year-month stamps.

## Reconciliation guards (built into render.py)

The script runs these fail-loud guards before emitting the PDF:

| # | Guard | Why |
|---|---|---|
| 1 | `kpis.nettoomsattning.current` ↔ `tables.resultatrakning_koncern` revenue rows (within ±0.05 MSEK) | KPI text and table must agree |
| 2 | Rörelseresultat structural: intäkter + kostnader = rörelseresultat-raden | Catches sign errors and missing rows |
| 3 | Summa tillgångar = Summa skulder och eget kapital (every column) | Balance sheet must balance |
| 4a | IB + Periodens kassaflöde = UB (every column) | Cash flow self-consistency |
| 4b | Kassaflöde UB = Balansräkning Likvida medel | Cross-table consistency |
| 4c | Likvida medel ≈ KPI likvida_medel_eom (within 0.1 MSEK) | KPI text matches detail |
| 5 | Declared yoy_pct ≈ computed (current − prior)/prior × 100 | Narrative-vs-data drift |
| 6 | meta.period_short and period_short_compare non-empty | Required headers |
| 7 | meta.footer_label non-empty + present in rendered HTML | Footer label dual-write site |
| 8 | publication_date == vd_signing_date (unless --allow-date-mismatch) | Date-on-two-places dual-write |
| 9 | No placeholder tokens in rendered HTML (XXXX, TODO, FIXME, ???, leaked `{{`) | Highest-leverage guard against First North correction triggers |
| 10 | Board ≥ 4 members, has Styrelseordförande and VD roles | Signing block sanity |
| 11 | Kalendarium non-empty, no placeholder dates | Forward calendar required |
| 12 | `kpi_tiles[i].value` matches the corresponding `kpis.*` field (per built-in mapping) | Tiles restate figures that exist elsewhere; a tile left on `XX` is auto-filled, and a hand-edited one that drifts fails here |
| 13 | Moderbolagets balansräkning balances per column, ±1 kr | Real residuals are +0,49 and −0,33 — exact equality fails on correct data |
| 16 | Förändring EK closing balance = balansräkningens egna kapital | Ties the equity table to the balance sheet. Note both sides include minority interest |
| 17 | No value originated from a stale sheet, column or row | Sheet-level checks are insufficient — see the three levels of staleness above |
| 18 | Kassaflödets UB = balansräkningens likvida medel, moderbolag too | Generalisation of guard 4b |
| 19 | Resultat per aktie recomputed, both rows on moderföretagets aktieägare | BDO's file uses a different numerator on the efter-utspädning row; with no dilutive instruments the two must be identical |
| 20 | The derived 12-month column carries its label | The one figure that comes from arithmetic rather than the ledger must be marked as such |
| 21 | Koncern and moderbolag tables are not identical | Their Nettoomsättning is identical in every column, so an extractor reading one sheet twice would be invisible |
| 22 | `len(row.values) == len(table.columns)` | A short row renders silently with a blank tail — the most likely failure of a column-count change |
| 23 | A supplied KPI agrees with the value derived from its table | See "Derived figures are computed, never typed" |
| 24 | Every chart spec that names a source CSV could read it | Shipped placeholder charts in the published jan-jun 2026 report; the fallback was silent by design. Raises `ChartSourceError` |
| 25 | Every quarterly chart **ends at the report's quarter** (derived from `balansrakning_koncern.columns[0]`, e.g. 2026-09-30 → `Q3 26`) and has a value there | The window used to be "last N numeric rows in the file". A period row holding `XX` was silently skipped, so in the jul–sep 2026 draft ARR and kunder ended on Q2 26 with no error (Henrik 2026-11-18: *"Är det inte en deterministisk process styrd av ingångsvärden kring perioden?"* — it was not). Now the axis is anchored on the period, rows after it are cut off, and a missing or `XX` value fails the render. `--utkast-grafer` (draft only) draws the slot empty and labelled `XX` instead |


## Halvårsrapport — extract_bdo.py

Since CR-2026-08-19 this skill also drives the **Halvårsrapport**, which differs from the
Kvartalsredogörelse in three ways: eight tables instead of three (koncern *and* moderbolag,
plus förändring i eget kapital for each), five period columns instead of four, and figures
extracted from BDO's workbook by script instead of by hand.

```bash
python3 ~/.claude/skills/kvartalsredogörelse/extract_bdo.py \
  "<period>/Underlag från BDO/.../Kvartalsredogörelse <YYMMDD> inkl kc.xls" \
  --period-end 2026-06-30 --derived-fy-token 202501-202512 \
  --out <period>/tables.json --provenance <period>/bdo-provenance.json
```

Merge `tables.json` into `data.json` under `tables`, adding `currency_unit: "SEK"` per table.

### BDO's workbook is a decade-old template — three kinds of stale data

This is the single most important thing to know about the source file. **Eight of its twenty
sheets carry old figures**, and staleness exists at three levels:

| Level | Example | Why the obvious defence fails |
|---|---|---|
| **Whole sheets** | `Resultaträkning`, `Balansräkning`, `Kassaflöde`, `Finansiella utv i sammandrag` hold 2015/16 data | They bear the most inviting names in the workbook |
| **Prefix twins** | `RR`, `BR`, `KF` hold 2013–2016 data and are exact prefixes of the current `RR 260630`, `BR 260630`, `KF 260630` | Any `startswith`, fuzzy or prefix match lands on the stale twin |
| **Rows inside a current sheet** | `KKF 260630` and `KF 260630` carry 2015/16 rows at r42–r58, **in the current columns** | Column-level checks cannot see them — only a row terminator can |
| **Columns inside a current sheet** | `BR 260630` carries 2015–2016 columns at c14–c17 and c23 | Sheet-level checks cannot see them |

Evidence you are reading the stale sheet: `Resultaträkning` reports Personalkostnader of
−3 600 kr for a period, against −888 331 kr in the current `RR 260630`.

### Three extraction modes, because the workbook has three shapes

| Mode | Sheets | Mechanism |
|---|---|---|
| **A** — token search | `KRR`, `RR`, `KKF`, `KF <YYMMDD>` | Search the header row for the expected period token (`202601-202606`). Never assert a column index |
| **B** — date search + data-column resolution | `KBR`, `BR <YYMMDD>` | Headers are date-typed cells or serials. `BR` has headers at c4/c6/c8 but **data at c4/c7/c9** — resolve the column where data actually sits |
| **C** — row-block anchor | `Koncern Förändring i eget kap`, `Förändring i eget kapital` | Sheet names carry **no** period token. Anchor on ISO dates in the IB/UB row labels. Columns are equity *components*, not periods |

**Column layouts are not uniform.** `KRR`/`RR` use 1,3,7,8,10; `KKF`/`KF` use 1,3,5,7,9;
`KBR` uses 5,7,9. `KF` has no Q1 column at all. Do not derive one layout for all sheets —
rev 1 of the CR tried and the data refuted it.

**Mode C pitfalls, both of which produced silent wrong answers during the build:**
- The same opening-balance date opens two blocks (the full year and the half-year). Pair each
  closing balance with the **nearest preceding** matching opening balance.
- The component header row must be the one above the *current* blocks. The first `Aktiekapital`
  in the sheet belongs to the stale 2015 block and has different columns.
- The `Summa` column sits at c5 for koncern and c6 for moderbolag. Both sheets happen to hold
  `62 957 874` in a non-total column, so a wrong column pick returns the *same* plausible number
  for both companies — which is what exposed the bug.

### Column order leads with the half-year

`260101–260630`, `250101–250630`, `260401–260630`, `250401–250630`, `250101–251231 (härledd)`.
This matches the precedent report and is **required** by the guards, which read `values[0]`
against the half-year KPI block. Leading with the quarter fires guard 1 on the first run.

### Two rows that need care

- **Resultat per aktie** is genuinely fractional. Rounding it to an integer prints −0,02 kr as
  `0`. `_num()` keeps two decimals for non-integral values for exactly this reason.
- BDO wraps long labels over two spreadsheet rows with the figures on the second. Merge a row
  whose label starts lower-case into its predecessor, or the first half renders as a line of `XX`.

## Moderbolag tables — NOT included in Kvartalsredogörelse

(Applies to the Kvartalsredogörelse only — the Halvårsrapport includes them, see above.)

The Kvartalsredogörelse (lighter Q1/Q3 format) presents **koncern tables only**: resultaträkning, balansräkning, and kassaflöde for the consolidated group. It does **not** include separate moderbolag tables — those appear in the heavier Halvårsrapport and Bokslutskommuniké formats only. The v1.0 jul-sep 2025 reference confirms this scoping.

The CR initially listed `tables.resultatrakning_moderbolag` / `tables.balansrakning_moderbolag` in the schema; the implementation deliberately omits them. If a future Halvårsrapport adopts this pipeline, those tables get added then.

## Charts

`build_placeholder_charts()` reads `Grafkälldata/*_per_kvartal_källdata.csv` and renders a 5-bar
quarterly chart per KPI, falling back to a 2-bar current-vs-prior comparison when a CSV is missing
or has fewer than 5 rows. Keep the CSVs current and the charts follow.

**Ordering matters and is not enforced.** The renderer takes the *last 5 rows* in file order. A
quarter appended below a blank line, or out of sequence, silently produces a chart with the
quarters in the wrong order. Sort the rows chronologically when appending.

## Kalendarium rule

**Source: the previous published report — always, when one exists (Henrik 2026-11-17).** Copy its
`kalendarium` (its `data.json`, verified against the published PDF), drop every event dated on or
before this report's `publication_date`, and keep the rest unchanged. Do not invent dates and do not
ask Henrik for a calendar the previous report already answers. Add an event only when Henrik
supplies it or the previous report lacks one that a later published source (e.g. a stämma
kommuniké) has fixed — and say which source it came from. Validated jul–sep 2026: seeded from the
halvårsrapport jan–jun 2026, the Q3 event (2026-11-24) dropped, three events remain.

**List ALL future events from publication date forward.** Typical Q1 publication has 6 events ahead (next Verksamhetsredogörelse, Halvårsrapport, the other Verksamhetsredogörelse, Bokslutskommuniké, Årsredovisning, Bolagsstämma). Q3 publication has 4–5 ahead. Don't truncate to a fixed count — show whatever's actually scheduled.

**Canonical terminology** (aligned with `/sonetel-bokslut`):
- **"Verksamhetsredogörelse Q1"** / **"Verksamhetsredogörelse Q3"** (NOT "Kvartalsredogörelse")
- **"Bolagsstämma"** (NOT "Årsstämma")
- "Halvårsrapport", "Bokslutskommuniké", "Årsredovisning" unchanged

The v1.0 jul-sep 2025 used the older terms ("Kvartalsredogörelse" / "Årsstämma") — that was reconciled away from the Q1 jan-mar 2026 cycle onward. The previous report is the primary source (see top of this section); sonetel.com/sv/investerare/ is a cross-check only.

## Schema (pydantic models in render.py)

Top-level keys of `data.json`:

- `meta` — period labels, report type, footer label, publication date
- `kpis` — the 14 KPI pairs (current, prior, yoy_pct)
- `kpi_tiles` — the six big red SVG tiles on the sammandrag page
- `narrative` — VD-kommentar (list of paragraphs), affärsmodell, kommentar till grafer
- `tables` — resultatrakning_koncern, balansrakning_koncern, kassaflode_koncern (raw SEK)
- `share_capital` — ISIN, LEI, Kortnamn, antal aktier, bemyndigande, sammanställning
- `governance` — board[] with namn+roll, vd_signing_location, vd_signing_date
- `disclosures` — om_bolaget, certified_adviser, redovisningsprinciper, väsentliga_risker, kontakt, granskning_status
- `transaktioner_narstaende` — string or null (null → "Inga transaktioner...")
- `kalendarium` — 4 events typically
- `definitioner` — list of {term, definition}
- `boilerplate` — version stamp + source link
- `units` — tables in raw SEK, KPIs in MSEK, formatting policy

See `examples/jul-sep-2025/data.json` for a fully-populated regression fixture.

## Charts

Rendered by matplotlib into `<period>/charts/*.png`. Brand color `#B80404`, Gotham SSm fonts, y-axis from 0, space-thousand-separator. Currently uses simple bar charts derived from the KPI block (current vs prior). To upgrade to multi-quarter line charts: extend `build_placeholder_charts()` in `render.py` to read a `Grafkälldata/*.csv` directory like `/sonetel-bokslut` does.

The "Kommentar till grafer" text box is a CSS `<div>` with red left border — no PIL image generation needed (unlike `/sonetel-bokslut` Bokslutskommuniké which embeds PIL-rendered boxes into a Word doc).

**Do NOT port** the PIL exact-pixel resizer from `/sonetel-bokslut` — it exists for docx image injection at fixed pixel dimensions. WeasyPrint sizes images via CSS `mm`, so the resizer is irrelevant here.

## PDF export

WeasyPrint produces the final PDF directly — no Word, no Print → Save as PDF, no `docx2pdf`. The script sets `DYLD_LIBRARY_PATH=/opt/homebrew/lib` automatically so the Homebrew-installed Pango/Cairo/glib resolve.

### Photographs MUST be JPEG, not WebP (Henrik 2026-08-21)

**WeasyPrint decodes WebP and re-embeds it losslessly (Flate).** For a photograph that is
catastrophic: five WebP files totalling 2.1 MB on disk produced a **14.8 MB** PDF. Converting the
same five to JPEG took the PDF to **2.3 MB** — a 6.4× reduction — with no visible loss at 150dpi.
JPEG is passed through as DCTDecode and never re-encoded.

Cision's upload limit is about **5 MB** (see below), so a WebP-illustrated report simply cannot be
published without a manual compression pass. Do the conversion at source instead:

```python
im = Image.open(src).convert("RGB")
if im.width > 1700:                     # 210mm at ~200dpi — plenty for a distributed PDF
    im = im.resize((1700, round(im.height * 1700 / im.width)), Image.LANCZOS)
im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
```

`generate-image.mjs` writes `.webp`, so **every generated image needs this pass** before it goes
into `data.json`. Keep the WebP original alongside as the master. Screenshots and charts with flat
colour and hard edges are the exception — PNG stays right for those, and they are small anyway.

For further reduction (rarely needed once the images are JPEG):
- Open in **Preview → File → Export → Quartz Filter: Reduce File Size**

## Layout & visual conventions

These rules emerged from iteration cycles with Henrik. **Treat them as defaults, not negotiable** — undoing one usually triggers the same feedback again.

### WeasyPrint paged-media patterns

- **`body` MUST be `margin: 0`.** WeasyPrint applies the UA default of 8px (~2.1mm), and nothing
  in this stylesheet reset it until 2026-08-21. The effect: every full-bleed element — cover,
  back cover, KPI bands, affärsmodell photo, section banners — stopped **2mm short of the paper
  edge** and printed a thin white strip down both sides. It is easy to miss on screen and
  obvious in a spread. Henrik caught it on the cover and the affärsmodell photo.
  The fix has two halves and both are needed:
  - `body { margin: 0 }` **and** `@page { margin: 18mm 20mm }` — sideways 20mm so the text block
    lands exactly where it did before (18mm page + 2mm body), vertically 18mm because the body
    margin never applied per page. Setting all four to 20mm costs 4mm of column height per page
    and grew the report by a page.
  - Bleed offsets follow the same split: **-20mm left/right, -18mm top/bottom.**
  To verify, render a page to PNG at 100dpi and check that the outermost pixel column is not
  white — do not trust the eye.
- **Never put `border-radius` on a full-bleed photograph.** Rounded corners at the paper edge
  read as exactly the white-edge defect above.

- **WeasyPrint's CSS Grid cannot span a cell across columns.** `grid-column: 1 / -1` on the
  *Kommentar till grafer* card collapsed the six chart cards into narrow slivers. If an element
  needs the full width of a grid page, take it **out** of the grid and make it a sibling below.
  As a grid cell the note also ran to eight lines in one column, no longer fitted under the third
  chart row, and the whole row — the note alone — was moved to a page of its own. Full width
  halves the line count and it fits.
- **Bottom-anchored elements (KPI bands, image strips) MUST use `position: absolute`, not flexbox.** WeasyPrint's flex support in print mode is unreliable: `display: flex; flex-direction: column` with `margin-top: auto` did NOT bottom-align in repeated tests, nor did `justify-content: space-between` with explicit height. The proven pattern:
  ```css
  .sammandrag {
    position: relative;
    height: 261mm;  /* A4 297mm minus 18mm top + 18mm bottom margins */
    page-break-after: always;
    page: no-pagenum;
  }
  .sammandrag .kpi-bands {
    position: absolute;
    bottom: -18mm;  /* full-bleed past page bottom margin */
    left: -18mm;
    right: -18mm;
  }
  ```
- **Suppress page numbers on pages with bottom-anchored full-bleed elements** (sammandrag, affärsmodell). Pattern:
  ```css
  @page no-pagenum {
    @bottom-right { content: none; }
    @bottom-left { content: none; }
  }
  ```
  Then assign `page: no-pagenum;` on the section. Without this, the red page-number lands on top of the KPI band / image.

### Typography

- **Body text: Light (300) + text-shadow double-strike for faux-~340 weight.**
  ```css
  body { font-weight: 300; text-shadow: 0.05em 0 0 currentColor, -0.05em 0 0 currentColor; }
  ```
  Reasoning: Henrik finds Light (300) too thin and Book (400) too bold. Available font weights are 250/300/400/500/700 — no native 325/350 file. Per CSS Fonts spec, `font-weight: 325` rounds down to 300, so it's not a workaround. The double-strike thickens visual stroke without changing the font, landing between Light and Book. Adjustable: `0.03em` ≈ 310, `0.04em` ≈ 325, `0.05em` ≈ 340 (current).
- **Inline bold (`<strong>`, `<b>`): Medium (500), NOT Bold (700).** With body at faux-340, the contrast to Bold (700) is too jarring. Medium gives a controlled 1.5-step bump that reads as emphasis without shouting. Display elements (KPI tile values, banner labels, red small-caps subheads) keep their original Bold (700) — those are headings, not inline body emphasis.
- **Lead-in (first paragraph of VD-ordet): Medium (500), same step as inline bold.** Earlier iterations tried Bold (700) but the contrast was wrong against the lighter body.
- **All "page title" patterns share `margin-bottom: 24pt` for symmetric divider spacing.** This includes `.page-title`, `.sammandrag .tagline`, `.vd-content .vd-title`. The `.page-divider` itself has `margin-bottom: 24pt`, so total spacing is 24pt above and 24pt below the blue stroke. (Doubled from 12pt per Henrik 2026-05-13 — the doubled spacing breathes better in the layout.)
- **Footnote markers**: a single footnote in a table uses `*`. Multiple footnotes use `*` / `**` / `***`. Don't use `**` for a lone footnote.

### Customer flow chart (Nyckeltal page, from jul–sep 2026)

`chart_kundflode.png` replaces "Nya betalande kunder per kvartal" on the Nyckeltal page (Henrik
2026-11-18; the board valued the same chart in the 2026-11-09 update). Per day: new paying (navy
line), lost (red line), net (bars). Source `Grafkälldata/kundflode_per_manad_källdata.csv`, built
from the finops series the board deck uses (`customers_new_paying_monthly_total`,
`subscriptions_positive_balance`). **Lost = new − net** — derived, not measured; say so in
*Definitioner*. Months after the report period sit behind a dashed "Efter perioden" divider; the
series must contain the period's last month or guard 25 stops the render.

### KPI band: what the signed tiles compare with (standard from jul–sep 2026)

The tiles mix signed changes (ARR, nettoomsättning, abonnemangskunder) and levels (bruttomarginal,
EBITDA, SaaS40). **A signed tile gets one small caption under its value — `mot jul–sep 2025` — and a
level tile gets none** (an empty line keeps the figures aligned). No band-wide note: a note over all
six tiles also labels the levels as changes, which is wrong (Henrik 2026-11-18: *"Vissa tal är väl
inte jämförelsetal?"* … *"Minimum clutter. Keep it clean"*). Do not add comparatives to the level
tiles either; they are in the sammandrag text above.
**Standard, no input:** `render.py` derives the caption from `resultatrakning_koncern.columns[1]`
(`kpi_band_comparison()`; English "vs Jul–Sep 2025"); a tile counts as a change when its value
starts with `+`, `-` or `−`. `meta.kpi_band_jamforelse` overrides the caption text.

### Tables

- **Pale-blue tint (`tint_current=True` default in `render.py`) on the current-period column on ALL three financial tables**, not just balansräkning. Resultaträkning, balansräkning split parts, and kassaflöde all get the tint.
- **Tint must be continuous top-to-bottom — section-headers render as `label + empty value cells`, NOT `colspan`.** Colspan breaks the tint band because `:nth-child(2)` no longer matches.
- **Summing rows are BOLD with a rule above** — the convention in every pre-2025 report, lost in
  the move to this pipeline and restored 2026-08-21. `mark_summa_rows()` in `render.py` sets
  `summa`/`bold` at load time from `SUMMA_EXACT` / `SUMMA_PREFIX`, keyed on **table name**, not on
  the label alone: *Periodens resultat* is a total in the income statement and an equity component
  in the parent balance sheet. A row that sets `summa` in `data.json` is left alone. Do not give
  `tr.summa-bold td` a `padding-top` — 43 total rows at 3pt each push the group income statement
  onto a second page.
- **Value cells are `white-space: nowrap`.** *29 457 171* was wrapping after the thousands group
  in the equity tables' Summa column and printing as two lines that read like two numbers. Header
  cells are deliberately left wrappable.
- **Rows that are zero in EVERY reported column are omitted** (`drop_zero_rows()` in
  `render.py`, on by default). ÅRL 3:4 §5 permits it — a post with no amount may be left out when
  the comparative has none either — and here the row is empty in every column shown. Sebastian
  Ahlskog (styrelsen) asked for it 2026-08-21; there were **42** such rows across the eight
  statements, worst in förändring i eget kapital where three of seven movement rows in each parent
  block were empty. The filter runs at render time, *after* the guards and `derive_kpis()`, so
  nothing that reads the data model is affected. Every omission is printed at build time —
  the deviation from BDO's own layout must stay auditable, and it is worth telling BDO about.
  Watch one case: a line that is zero in the parent but not in the group (H1 2026: the parent's
  tax line) disappears from one statement and stays in the other.
- **Date ranges in column headers go through `bind_range_dash()`** — a non-breaking space before
  the en dash, so *2026-04-01 – 2026-06-30* has exactly one legal break point, after the dash.
  Without it a narrow column prints three lines with the dash alone in the middle. It costs
  width: the narrowest a period column can now be is `2026-01-01 –`, which is why header cell
  padding is 3pt rather than 4pt.



## Sourcing rules learned the hard way (2026-08, halvårsrapport jan–jun 2026)

### A comparative is what was published, not what you recompute

Twice in one cycle the recomputed figure differed slightly from the published one:

| Figure | Recomputed | Published in the prior report | Used |
|---|---|---|---|
| CAC, jan–jun 2025 | 139,0 kr | **137 kr** | 137 |
| Snitt antal anställda, jan–jun 2025 | — | **39** | 39 |

**Always use the published figure as the comparative.** A two-krona drift is rounding or a
marginal definitional difference; silently correcting it in a later report changes history and
makes the series non-comparable. If the difference is material, say so explicitly rather than
quietly restating.

### The missing comparative is usually in the previous report

`monthly_process_metrics` starts 2025-07, so the jan–jun 2025 new-customer figure looked
unobtainable. It was in the precedent report's own text: *"23 750 nya betalande kunder inkom under
perioden."* **Read the previous report before concluding a figure does not exist.** The same
applies to headcount, Trustpilot, and any operational KPI Sonetel has published before.

### Read the previous report's forward-looking statements before writing this one

4.4.6(h) requires framtidsinformation compared with the previous report, and that is only
substantive if you know what was said. The Q1 2026 VD-ord contained **five checkable commitments**
— a 28% headcount reduction from 1 July with a 1,2–1,5 MSEK annual saving, new apps "färdigställda",
SMS already shipped, the portal rolling out in autumn, and an explicit warning that *"Q2 blir
fortsatt svagt i YoY-jämförelse"*.

Two consequences, both easy to get wrong:
- **Do not present as news what was already announced.** SMS and the portal were both public in May.
- **A prediction that came true is worth more than any explanation after the fact.** Q2 came in at
  −16% exactly as flagged. Say so.

### Verify a claim before writing it, against more than one source

The CEO reported that lead inflow was rising and conversion improving. Three independent sources
said otherwise: signups flat at 33–40k/month, signup→paying conversion flat at ~8%, and organic
search clicks down from 13 594 (mar) to ~10 000 after the April site launch. What *had* improved
was CTR.

**A figure that cannot be traced to a system of record does not go in the report.** When a claim
survives scrutiny only at one funnel step, name that step — an unqualified "leads are increasing"
that the company's own published customer numbers contradict is worse than silence.

### Do not publish an estimate

Headcount after the reduction was given as *"It's 30 I guess, I'm on leave… will share exact number
once I'm back"*. That is not a figure. Wait for it, or describe the direction without a number.

### Derived measures need someone who owns them

Sonetel has a formal CFO for Nasdaq purposes but no operational finance function — Henrik does the
work. So "CFO sign-off" is not a real control. Constructed measures with no owner — a
constant-currency growth rate derived from the billing platform and never reconciled to the
audited accounts — should not be published at all. See [[project_ar_roles]].

### Verifying the PDF when image display is unavailable

A long session can exhaust image display. Everything visual is still checkable:

| Question | Tool |
|---|---|
| Does the column layout flow correctly? | `pdftotext -layout` (plain `extract_text()` gives content order and looks fine even when columns are wrong) |
| Did spacing actually change? | pypdf `visitor_text`, compare baseline deltas. **y increases downward** in WeasyPrint output |
| Did a section render at all? | page count plus first lines per page |
| Are formulas present but unevaluated in a workbook? | load twice, `data_only=True` and `data_only=False` — formulas without cached results prove the file was generated, not saved by Excel |

## READ THE SKILL'S OWN GUIDES BEFORE WRITING ANYTHING YOURSELF

**Hard-learned 2026-08-19, and the most expensive mistake of that cycle.**

This skill ships `image-gen/COVER_STYLE.md` and `image-gen/prompts/cover-default.md`. They are
authoritative, they are detailed, and they exist because earlier cycles already made the mistakes
they warn about. In the halvårsrapport cycle I never opened either file. I wrote cover and
affärsmodell prompts from scratch, reasoning from first principles, and produced exactly the
image the style guide forbids in bold on its first page:

> Wide environmental shots — the setting is the protagonist; the human is part of the
> composition, not the subject of a portrait. Person occupies ~5–20% of the frame height.
> ❌ Close-up portrait — the ad-image skill's default. **Wrong for a financial report cover.**

My subject filled ~60% of the frame. Henrik's verdict: *"Omslagsbilden är konstig.
Illustrationerna på väggen ser fejk ut. Hon ser fejk ut. Har du försökt styra för hårt? Inte
låtit standardskillen göra sitt jobb?"* — and he was right on every count.

Four further violations, each of which the guide states plainly:

| Guide says | I did |
|---|---|
| 28mm at f/4–5.6, deep depth of field, environment in focus | Asked for shallow depth of field |
| "The phone may not even be visible at this distance, and that's fine" | Made the call the hero — an explicit anti-trope |
| Atmosphere over detail; the cover is seen small before it is opened | Loaded the frame with fine detail, which is exactly why it read as fake |
| Anatomy constraints are for **regeneration**, as a tighter pose instruction | Front-loaded a wall of "exactly TWO arms…" boilerplate into the first prompt, which flattened the result |

**The rule, and it generalises far beyond images:**

> When this skill ships a guide, a template or a default prompt for a task, read it and use it
> before writing your own. Improvising over documented know-how does not produce a fresh
> perspective — it reproduces mistakes the guide was written to prevent, and it wastes the
> deadline you were trying to save.

Concretely, before generating any image: read `image-gen/COVER_STYLE.md` **and**
`image-gen/prompts/cover-default.md`, then start from the template there. Vary the setting per
the rotation rules. Add constraints only when a generated image actually fails the audit — never
pre-emptively.

**A second lesson from the same cycle:** the audit checklist below covers anatomy, text and
framing, but it does not ask whether the depicted *action is physically possible*. One
affärsmodell attempt showed a man pouring beans into a bag whose top was visibly sealed. Add that
check: does the scene make sense as an event, not just as a picture?

### Cover & affärsmodell images

- **Generated via `image-gen/scripts/generate-image.mjs`** (Flux model, 9:16 aspect for cover, 16:9 for affärsmodell).
- **Gender balance**: when the report contains 2 person-images (typical: cover + affärsmodell), **at least one MUST depict a woman**. Validated Q1 2026 by regenerating affärsmodell from Marrakech leather artisan (man) → Jaipur textile boutique owner (woman) once Henrik flagged this. Failing to balance is a Henrik-flagged regression in repeated cycles.
- **Mix Western and non-Western settings per quarter** — at least one Western-recognisable scene per cover/affärsmodell pair, since the audience is Swedish investors. Cover Western, affärsmodell non-Western (or vice versa) is the default rotation.
- **Avoid shabby/derelict cues.** Sonetel's customers are SMBs and the audience is investors — settings should read as cared-for, well-maintained, prosperous-but-charming. Explicitly forbid: peeling paint, weathered surfaces, derelict shopfronts. Allow: aged-but-cared-for, lived-in patina.
- **Anatomy QC in prompt**: AI image models often produce twisted/crossed legs when subjects lean against doorframes or sit on furniture, OR a third arm/hand near a counter or surface. Prompt explicitly: *"both feet planted naturally and visibly, weight evenly distributed, anatomically correct posture, legs straight and natural — not twisted or crossed; exactly TWO arms and TWO hands, no extra limbs anywhere in the frame, no third hand on the counter or surface, no duplicated body parts."*
- **Secondary subjects (cats, etc.) must be fully in frame, not cropped at the bottom edge.** Prompt explicitly: *"complete body visible from paws to ears within the frame; ensure the cat sits within the frame margin and is not clipped."*

### MANDATORY post-generation image audit

After every `generate-image.mjs` call, **Read the generated .webp file with the Read tool** (Claude is vision-capable) and run this checklist before declaring the image done. If any item fails, regenerate with corrective prompt language:

1. **Limb count**: count visible arms and hands. Standard human anatomy. Look especially near surfaces (counters, tables, fabric stacks) where AI models often hallucinate a third hand.
2. **Hand structure**: each visible hand has 5 fingers, no merging, no duplication.
3. **Face structure**: one mouth, two eyes, two ears (if visible), proportional features.
4. **Pose plausibility**: legs/arms in natural positions, no twisting, weight grounded.
5. **Frame margin**: secondary subjects (cats, props) fully in frame, not clipped at edges.
6. **Setting cues**: cared-for and well-maintained — no peeling paint, derelict surfaces, or shabby cues.
7. **Gender balance**: across the report's 2 person-images, ≥1 must be a woman.
8. **No readable text**: no signage, logos, or readable letters anywhere (AI text rendering is unreliable).
9. **Is the action physically possible?** Not just "are the limbs right" but "could this happen".
   Pouring into a sealed bag, lifting an object no hand is touching, a tool held backwards. Ask
   what the person is *doing* and whether the scene supports it.
10. **Framing against COVER_STYLE.md**: is the person 5–20% of frame height, or has it drifted
   into portrait? This is the single most likely way a cover goes wrong.

If regeneration is needed: write a CORRECTIVE prompt that explicitly forbids the observed defect (e.g. "no third hand on the fabric stack, exactly two arms"). The first regen often resolves it. Validated Q1 2026: Marrakech leather artisan needed leg-twist fix; Lisbon cover needed cat-not-cropped fix; Jaipur woman needed three-arm fix on first iteration.

### Photographs always run FULL PAGE WIDTH (Henrik 2026-08-21)

**This is the house rule and it is not negotiable.** Every photograph in the report bleeds from
paper edge to paper edge — the cover, the affärsmodell picture, the VD banner, and any picture
placed inside a narrative section. Never at text width. Never at column width. A photograph set
inside one ~77mm column reads as a thumbnail and Henrik will reject it.

- **A large photograph is ALWAYS anchored to the top or the bottom of a page** (Henrik
  2026-08-21). Never floating in the middle of a page with text above *and* below it. This is
  the second half of the same house rule as full-page width, and it is what makes the pictures
  read as design rather than as illustrations dropped into the flow. Look at the report: the
  cover fills the page, the affärsmodell photo and the KPI bands sit hard against the bottom
  edge, the VD banner against the top. A picture that starts a third of the way down a page is
  wrong even if it bleeds correctly sideways.

  **The one thing to understand first: WeasyPrint will not let a flowed box paint below the
  text area.** A negative *top* margin bleeds upwards fine — that is how the section-head banner
  and the VD banner work. A negative *bottom* margin does nothing: the picture stops 18mm above
  the paper edge no matter how tall you make it, and once it is taller than the space left it
  jumps to the next page. This was measured on 2026-08-21 by sweeping the height in 1mm steps —
  at every height that still fitted, the gap to the paper edge stayed at exactly the page's
  bottom margin. Only an **absolutely positioned** box escapes downwards, which is precisely why
  the affärsmodell photograph and the KPI bands have always worked.

  **How to anchor one**, in order of preference:
  1. **Section head** — `.section-banner` above the page title. Top-anchored for free, because
     the section already starts a new page. Negative top margin is enough here.
  2. **Foot of a page, inside a flowed section** — a wrapper in the flow that claims exactly the
     space left on that page, with the image absolutely positioned inside it and bleeding past:
     ```css
     .wide-photo { position: relative; height: 146mm; margin: 10mm 0 0 0;
                   break-inside: avoid; break-after: page; }
     .wide-photo img { position: absolute; top: 0; bottom: -18mm;
                       left: -20mm; right: -20mm; object-fit: cover; }
     ```
     `break-after: page` makes the picture the last thing on its page; the text that no longer
     fits continues overleaf. The wrapper `height` is per-report and must be **measured**:
     render, read how far the picture's bottom sits from the paper edge, add that to the height,
     repeat. Two or three passes. Declare the picture on a block partway through the section,
     not at the end — it can only appear where it sits in the flow.
  3. **A full page** — `break-before: page`, `height: 297mm`, margins `-18mm -20mm`, fed an image
     already cropped to A4 proportion (0.707). Anchored top and bottom by definition. Use when
     the picture deserves a page of its own; costs a page.

  **Position a DIV, never the `img`.** WeasyPrint ignores `object-fit` on an absolutely
  positioned replaced element: it sizes the picture from its intrinsic dimensions instead, and
  the page rendered as a wild zoom into one corner of the photograph — close-up flowerpots where
  a café scene should have been. Put the offsets on a wrapper `div.photo-bleed` with
  `overflow: hidden`, then let the image fill it with `width/height: 100%; object-fit: cover`.

  **A caption goes INSIDE the picture**, absolutely positioned bottom-left and aligned with the
  text margin. A full-bleed photograph has no room beneath it for a caption line — adding one in
  the flow pushes the picture back off the paper edge, and it cost a page the first time. Leave
  clear space in the composed image for it (drop the subject to ~77% of the band height) rather
  than laying type over the subject. Light backgrounds take `--muted`; a dark photograph needs
  `.banner-caption-light`, white with a shadow.

  **Composite product shots from ONE render, on the render's own background colour.** Mixing a
  separately-cropped screenshot with a self-rendered one gave two phones with different edges —
  one with square-cut black corners where the crop had sliced through the bezel, the other with
  a grey halo left by flood-filling the background away. Both were visible in print. Render every
  screen the same way, read the background colour out of the render, and make the band that exact
  colour: the antialiasing then blends perfectly and no alpha work is needed at all.

  **Verify by measuring, not by looking.** Render the page to PNG at 100dpi and check the
  outermost pixel rows and columns — and allow for antialiasing, the edge pixel reads around
  243–247 rather than a clean value.

- **A photograph with space around it may claim a half page or a whole page.** Do not try to
  squeeze it into a band. At 210mm wide, a **1.6:1** crop is roughly half a page (131mm); **1.35:1**
  (155mm) fills what is left under a short column of text. Choose the crop to decide how much
  page the picture takes, and let the height follow the file's aspect ratio.
- **Charts are the opposite.** A chart is data: it goes at text width or column width, inside a
  bordered card. Never bleed a chart.
- **Spread the pictures out.** Two full-bleed images on consecutive pages read as one clump when
  the reader scrolls — this is how the customer photograph and the affärsmodell tuk-tuk collided
  on 2026-08-21. Keep at least a page of text between photographs, and check by scrolling the
  PDF, not by looking at single pages.
- **Do not bundle two subjects into one composite** to dodge a layout problem. A customer scene
  and a product screenshot are two pictures; merging them into one band was rejected immediately.

**The three placement slots**, all full-bleed:

| Slot | Key in `data.json` | CSS | Where it lands |
|---|---|---|---|
| Section head | `assets.verksamhet_banner_image` | `.section-banner` | Above the page title, fixed 62mm, `object-fit: cover` |
| Mid-section | `bild_bred` on a block under perioden | `.wide-photo` | Between the two column halves |
| Section foot | `assets.verksamhet_slutbild` | `.section-banner-foot` | After the last text block, height from the file |

`.section-banner-foot` must NOT set a height. The base `.section-banner img` rule crops with
`object-fit: cover`, so a fixed height silently cuts the picture instead of growing the box —
that is why the app screenshot printed with its keypad sliced in half on the first attempt.

**The section-foot slot is fragile.** The narrative text usually ends just over a page break, so
a picture placed there lands alone at the top of an otherwise empty page. It happened twice on
2026-08-21. Either give it a crop tall enough that the page reads as a deliberate picture page,
or use the mid-section slot instead.

**The mid-section slot earns its keep twice.** See *Kommentarer kring verksamheten* below: a
picture there also supplies the `has_wide` split between the two column containers.

### VD-banner

- **Banner-label position: bottom-right.** Bottom-left lands on Henrik's face; top-right lands on a bright section of the office image (hard to read). Bottom-right is the only corner that has worked.

### Placeholder for missing numbers

- **`XX`** is the canonical draft-mode token for unknown numbers in body text and KPI tiles. Two characters, all-caps, visually distinct, **does NOT trigger** the `XXXX` (4-char) post-render guard.
- All `fmt_*` helpers in `render.py` return `_TBD_PLACEHOLDER = "XX"` when input is `None`. Guard 12's `TBD_TOKENS` includes `XX` so KPI tiles can show `XX` when underlying KPI is null.
- Before final v1.0 release, every `XX` should be replaced with a real value. The 4-char `XXXX` guard remains as the final-release safety net (would fail on `XXXX` but not `XX` — intentional).

### Back cover

- Brand aqua: `--teal-light: #7BC4C4` (saturated brand colour, not the muted `#8FC1C6` grey-teal).
- Monogram watermark: `filter: invert(1) brightness(1.4)` + `opacity: 0.30` on the icon SVG → light watermark feel, not dark mark on light background.

## Troubleshooting

- **WeasyPrint can't find libgobject / libpango**: the cause is System Integrity Protection, and the usual advice does not work. **`/usr/bin/python3` is SIP-protected, so macOS strips every `DYLD_*` variable out of its environment** — measured 2026-08-25: `DYLD_LIBRARY_PATH=/opt/homebrew/lib /usr/bin/python3 -c "import os; print(os.environ.get('DYLD_LIBRARY_PATH'))"` prints `None`, while the same command against `/opt/homebrew/bin/python3.12` prints the path. `os.environ.setdefault()` inside `render.py` cannot help either: dyld reads the variable at process start, before Python runs.
  In an interactive login shell it often works anyway (the loader inherits a different environment). **In a non-interactive session — which is where an agent runs — it does not.** Fix: use a non-SIP interpreter.
  ```
  /opt/homebrew/bin/python3.12 -m venv ~/.weasy && \
  ~/.weasy/bin/pip install weasyprint pydantic jinja2 matplotlib pypdf eval_type_backport && \
  DYLD_LIBRARY_PATH=/opt/homebrew/lib ~/.weasy/bin/python render.py …
  ```
  **Version matters for pagination:** the published jan–jun 2026 report was made with WeasyPrint 66.0 and is 24 pages; the same `data.json` under 69.0 is 26. Compare two renders under the *same* version, never a fresh render against a published PDF from another one.
- **A `{placeholder}` printed into the PDF**: `PLACEHOLDER_PATTERNS` matches `{{`/`}}` only, so a single-brace token passes every guard. `{translation_date}` reached a rendered PDF this way on 2026-08-25. `i18n.scan_placeholders()` now aborts the render on any surviving `{name}` — do not widen `PLACEHOLDER_PATTERNS` instead, `XX` and `{HH:MM}` have their own rules.
- **Gotham SSm renders as Helvetica fallback**: verify `~/Library/Fonts/GothamSSm-{Book,Medium,Bold}.otf` exist. The CSS uses absolute `file://` URLs — relative paths won't resolve.
- **A guard fires but the data looks correct**: read the error message — it includes the JSON path. Don't bypass with `--allow-date-mismatch` unless you actually intend a mismatch (publication ≠ signing).
- **Chart shows 2 bars instead of 5**: the period's `Grafkälldata/*_per_kvartal_källdata.csv` is missing or has fewer than 5 data rows. Port the prior period's CSVs and append this quarter.
- **Guard 25 fails / a chart ends a quarter early**: the CSV lacks a row for the report quarter, or that row is `XX`. Fill the value. While a value is genuinely pending, render drafts with `--utkast-grafer` — never a release.
- **Chart boxes render empty with no error**: chart paths must be absolute. Fixed in `build_placeholder_charts`; if it recurs, check that `str(p.resolve())` survived.
- **Numbers don't tie**: read the guard error. The most common cause is BDO row ordering — verify the row you're mapping in `data.json` corresponds to the **same** row in the BDO xlsx. The instruction PDF's step 10 warning still applies: misaligned rows produce silently wrong totals. The guards catch the structural cases; row-level errors within a sum can slip through.
- **KPI bands / bottom image not bottom-aligned**: do NOT switch to flexbox; see "WeasyPrint paged-media patterns" above. The position-absolute pattern is the only one that has reliably worked.
- **Page number lands on top of a bottom-anchored band/image**: assign `page: no-pagenum;` to that section, see same section above.

## Dependencies

Install once:

```bash
brew install pango cairo libffi
pip3 install --user weasyprint pydantic jinja2 matplotlib eval_type_backport python-docx pypdf
```

## File and version conventions

- **Layoutad PDF (drafts)**: `<Q-folder>/Kvartalsredogörelse/Layoutad/Sonetel kvartalsredogörelse <period> v<N>.pdf` (v0.1, v0.2, ...)
- **Release PDF (after final approval)**: `<Q-folder>/Kvartalsredogörelse/Layoutad/Sonetel kvartalsredogörelse <period>.pdf` (no version number — the file Henrik sends to Cision)
- **Archived drafts**: `<Q-folder>/Kvartalsredogörelse/Layoutad/Archive/` (created at final-approval cleanup; preserves draft history for audit trail)
- **data.json**: lives at `<Q-folder>/Kvartalsredogörelse/data.json` (next to the BDO underlag folder)
- **Charts directory**: auto-managed; safe to delete and re-generate

## Cision rubrik convention (per Henrik 2026-05-26)

The Cision press-release **headline** (rubrik) must be short to work in all media + Sonetel hemsida. Format:

**`Sonetel kvartalsredogörelse <period-short-no-year>`**

Example: *"Sonetel kvartalsredogörelse jan-mar"* / *"Sonetel kvartalsredogörelse jul-sep"*. Year is omitted (Cision distribution-date supplies the year context).

Do **NOT** use the report's internal `meta.tagline` (e.g. *"+54% kundtillväxt och SaaS40 vid 40%"*) as the Cision rubrik. The internal tagline is for the PDF cover; the Cision rubrik is the press-distribution headline — a different thing.

### Release timing

Typical: **08:30 CET** (morning, before market open). Occasional exceptions handled per Henrik direction — Q1 2026 publicerades kl. 10:30 CET efter ett möte Henrik hade på morgonen (validerat 2026-05-26).

### T0-ändringsprotokoll (när tiden ändras EFTER paket är genererat)

**Validerad lärdom 2026-05-26:** När T0 ändras mitt under launch-dagen (t.ex. "10:30 istället för 08:30 efter ett möte"), är **ingress-stämpeln i pressmeddelandet** det lättaste att missa eftersom den ligger inbäddad i texten — inte i en header. Henrik fick ett mail från Cision där headern visade "10.30 CEST" (faktisk distributionstid) men brödtextens ingress fortfarande sa "Stockholm, 2026-05-26, kl. 08:30 CET" — den gamla stämpeln överlevde till publicering eftersom HTML-utkastet hade klistrats in i Cision innan T0-ändringen.

**När T0 ändras, gå igenom DENNA EXAKTA CHECKLISTA — varje plats måste uppdateras:**

```
T0 = HH:MM CET (nytt värde)
T0 − 30 min = HH:MM CET (för internal Teams)

Filer att uppdatera (script-baserad sökning är säkrast):

  □ 99-cision-paste.html
    □ MAR Art. 17-statement i slutet (ENDA platsen i body där HH:MM finns):
      ...för offentliggörande den DD månad YYYY kl. HH:MM CET.
    □ HTML-kommentar med Cision-fältkonfiguration

  □ 10-press-release-sv.md (samma — endast MAR-statement)

  □ 00-story.md
    □ Launch-fältet längst upp
    □ Distribution-kanalmatris (T0 (HH:MM CET) rad)

  □ 01-checklist.md
    □ "Launch date / time"-raden
    □ Timing pivot-paragraph
    □ Artifacts-tabellen (Cision-rad + Teams-rad)
    □ Cross-domain timing rules
    □ Pre-launch-checklista (T0 − 30 min + T0 + T0 + 0–60 min sektioner)

  □ 02-mar-decision.md
    □ Lansering-fältet
    □ Distribution-grind
    □ Internkommunikation-grind (T0 = HH:MM, intern bekräftelse HH:MM−30)
    □ Post-publish-verifiering

  □ 50-internal-msg-en.md
    □ Publish-time i header
    □ "Today at HH:MM CET" i body
    □ "live at HH:MM" påminnelse i slutet
    □ Meta-row (om finns)

  □ _preview-all.html
    □ Release-header meta-fält (T0 + 30 min ovan)
    □ Cision-sektionens publication stamp (mirror)
    □ Cision-sektionens MAR-statement (mirror)
    □ Teams-sektionens header desc + meta-row + body
    □ Pre-launch-checklist sektion längst ner
```

**Säkert sätt — script-baserad sweep:**

```bash
cd <launch-folder>
# 1. Verify alla gamla tider är borta:
grep -n "OLD_TIME\|OLD_TIME_minus_30" *.html *.md
# 2. Räkna förekomster av nya tiden (rimlighet-check — typiskt 20-30 träffar):
grep -c "NEW_TIME" *.html *.md
# 3. Sista verifiering — öppna preview och scanna med ögat:
open _preview-all.html
```

**Om Cision-paste redan har klistrats in i Cision-portalen INNAN T0-ändringen:** Cision draft måste **omklistras** med uppdaterad HTML innan publicering — texten i drafter är frusen vid paste-tillfället och uppdateras inte automatiskt från lokala filer. Detta är det vanligaste sättet att en stale T0 överlever till publicering. Gå in i Cision draft-vy, ersätt body-HTML med ny version från `99-cision-paste.html`, spara, schemalägg om.

**Tumregel:** Vid T0-ändring är `grep -n "08:30" *.html *.md` (med den gamla tiden) ditt vapen — det skall returnera 0 träffar innan du säger "klart".

### Cision PDF upload — file size

Cision portal (portal.ne.cision.com) returned generic "Ett okänt fel har inträffat" on 2026-05-26 when uploading a 5.3 MB PDF. Empirical limit appears to be **~5 MB** for the primary PDF-bilaga. **Compress the release PDF once** via **macOS Preview → File → Export → Quartz Filter: Reduce File Size** before upload — use that single compressed PDF for both Cision and sonetel.com (no need to maintain two versions). Filename can keep "ö" / non-ASCII chars — that was NOT the cause of the error (v0.1 with same filename uploaded fine; size was the trigger).

## Fynd ur granskningen av den publicerade jan–jun 2026 — åtgärda före nästa rapport

Rapporten granskades efter publicering av två agenter med skilda mandat: en visuell som rastrerade
samtliga 24 sidor och tittade på dem, en numerisk som kontrollerade cirka 430 poster. **De åtta
uppställningarna är rena** — varje delsumma, varje kolumnbalans och varje koppling mellan
kassaflöde, balansräkning och eget kapital stämmer, och Q1 reproduceras exakt av H1 − Q2 i alla
fjorton nyckeltal Q1-rapporten publicerade.

Defekterna nedan är formatering, konsistens och definitioner. **Ingen är ett felaktigt tal.** Henrik
beslutade 2026-08-25 att inte publicera en tredje version — men allt här ska vara åtgärdat innan
nästa rapport går ut.

### 1. En metod för ARR i SEK — text och graf måste räkna lika

**Detta är det allvarligaste fyndet.** Samma datum, 2025-06-30, står med två olika tal i samma
rapport:

| Var | Tal | Metod |
|---|---|---|
| Sammandrag och löptext | 25,8 MSEK | 2,7124 MUSD × dagskursen 9,51067 |
| ARR-grafen | 26,4 MSEK | 2,7124 MUSD × 9,73626, samma kurs på alla kvartal |

Texten säger −2 %, grafen implicerar −4,2 %. Båda metoderna är försvarbara — grafen räknar om alla
kvartal till en kurs så att kurvan visar volym och inte valuta — men **rapporten säger ingenstans att
den gör det**, och ARR-definitionen nämner ingen valutaomräkning.

**Regel:** ARR i SEK räknas med **en** metod i hela rapporten. Väljs fast kurs för graferna ska
samma kurs användas i text och nyckeltal, eller så ska omräkningsmetoden stå i definitionen. Kontroll
före publicering: **jämför nyckeltalets ARR-värden mot ARR-grafens datapunkter för samma datum.**

`Grafkälldata/arr_per_kvartal_källdata.csv` bar dessutom två motstridiga noteringar om vilken kurs som
använts — en angav mars 2026, en juni 2026. Värdena följde juni. Källfilernas metadata ska stämma med
deras värden.

### 2. Grafernas källserier ska vara samma som de publicerade talen

Rapporterat av granskaren, **ej verifierat**: Premium-grafen visar 5 656 abonnemang för Q4 2025 medan
bokslutskommunikén FY24-25 publicerade 5 226 för samma datum. H1-serien bygger på `sales_analysis`
r755+756, bokslutskommunikén på finops `ACCOUNT_STATUS='A'`.

**Regel:** en graf som sträcker sig bakåt över tidigare publicerade perioder ska använda den serie
som producerade de publicerade talen. Byts källa ska bytet noteras i källfilen och avvikelsen
kontrolleras mot vad som redan står i tryck. Kontrollera detta för **varje** serie som går längre
tillbaka än innevarande period.

### 3. Kontinuitet mot tidigare publicerade rapporter

Rapporterat av granskaren, **ej verifierat**: ARR per 2025-06-30 publicerades som 26,1 MSEK i
periodrapporten jan–jun 2025, och bokslutskommunikén publicerade 25,9 per 2025-12-31 där H1-grafen
visar 27,4.

**Regel:** varje tal som avser ett datum en tidigare rapport redan publicerat ska stämmas av mot den
rapporten. Skiljer det sig ska skillnaden antingen förklaras i texten eller inte tryckas.

### 4. SEK-tabeller är hela kronor

Åtgärdat i koden 2026-08-25 — `fmt_decimal` saknade tusentalsavgränsare och `fmt_table_value`
skickade varje decimaltal dit, så tio celler i moderbolagets uppställningar visade `52145444,51` i
stället för `52 145 445`. Samma orsak gjorde att moderbolagets balansräkning inte summerade i två
kolumner, med 0,49 respektive −0,33 kronors differens.

`fmt_table_value` avrundar nu SEK-belopp över 1 000 till hela kronor; resultat per aktie behåller sina
decimaler.

### 5. Poster med nollvärde får inte renderas som rubriker

Tre rader är felklassade som `section_header: true` i `tables.json` och renderas som tomma fetstilta
rubriker: **Fordringar hos koncernföretag**, **Inbetald ej reg nyemission** och **Aktieägartillskott**.
Den sista ser ut som en rubrik över Amortering, Upptagna lån och Checkräkningskredit.

De är riktiga poster utan belopp, inte rubriker. Rättade blir de poster som `drop_zero_rows` tar bort
— rätt utfall enligt ÅRL 3:4 §5. **Kräver Henriks instruktion**, eftersom det är en ändring i
redovisningsdata.

Extraktorn markerar varje rad utan värden som rubrik. Kontrollera utfallet varje period.

### 6. Layoutdefekter i mallen

- **Sidnummer saknas** på sammandragssidan och affärsmodellsidan; ligger **inklippt i hörnet** på
  omslag och baksida, där de inte ska finnas alls; och har **för låg kontrast** mot mörkt fotografi
  på två sidor.
- **Sammandragets högerspalt saknar avsnittsrubrik.** Punkterna där är en fortsättning på
  januari–juni-listan, men den som skannar sidan uppifrån kan läsa dem som kvartalstal.
- **Summaraden heter `Kortfristiga skulder`**, inte `Summa kortfristiga skulder`, inkonsekvent mot
  `Summa avsättningar` och `Summa långfristiga skulder` på samma sida. Gäller båda balansräkningarna.
- **Linjediagrammet "Betalande kunder"** har x-axel som slutar före seriens slut och en översta
  gridlinje under kurvans topp.
- **Grafen i Kundanskaffning visar den totala kundbasen** medan avsnittets text handlar om inflödet.
  Talen i texten återfinns inte i grafen. En graf intill en text ska svara mot den texten.

### 7. Definitioner som inte stämmer med rapportens innehåll

- **"Resultat efter skatt"** definieras med *"schablonskattesats om 20,6 %"*. Den tillämpas ingenstans
  — koncernens faktiska skattesats är en annan och moderbolagets skatt är noll i samtliga fem
  kolumner. Ärvd boilerplate; stryk eller skriv om.
- **"ROI"** definieras som antalet månader innan intäkterna betalat av kundanskaffningskostnaden. Det
  är återbetalningstid, inte avkastning. Löptexten använder korrekt "Återbetalningstiden".
- **Aktiva kunder** definieras som "bibehållit ett positivt saldo", men periodens tal kommer ur
  `ACCOUNT_STATUS='A'`. Definitionen beskriver en annan metod än den som producerat talet.

### 8. Nyckeltal utan jämförelsetal

**SaaS 40 publicerades utan parentesvärde** — ensamt bland tjugoen punkter. `derive_kpis` saknar
nettoomsättning för jämförelseperiodens föregående år och kan därför inte härleda talet. Effekten är
att den största försämringen i nyckeltalsblocket är den enda utan referens.

Antingen förs det saknade underlaget in, eller så skrivs frånvaron ut.

### 9. Sekventiell rörelse som motsäger årsjämförelsen

Kundbasen föll från 33 857 (publicerat i Q1, per 2026-03-31) till 32 133 per 2026-06-30 — −5,1 % på
ett kvartal — medan sammandraget och VD-ordet framhåller +11 % mot föregående år. Båda är korrekta.
Men nedgången syns i två diagram och kommenteras ingenstans.

**Regel:** rör sig ett nyckeltal åt annat håll sekventiellt än det gör mot föregående år, ska den
sekventiella rörelsen nämnas i texten.

## Graferna — källdata, guard 24, och vad som gick fel 2026-08-25

**Grafernas källdata ligger i `<period>/Grafkälldata/*.csv` och lokaliseras relativt `data.json`,
aldrig relativt utdata-PDF:en.**

### Vad som hände

Halvårsrapporten jan–jun 2026 **publicerades med platshållare i stället för grafer**. Text och
siffror var korrekta; graferna var det inte.

`build_placeholder_charts()` härledde källkatalogen ur utdatasökvägen:

```python
grafkalldata_dir = out_dir.parent.parent / "Grafkälldata"   # FEL — borttaget
```

`out_dir` är `<pdf-katalog>/charts`. Renderas PDF:en till `Layoutad/` pekar det på
`Grafkälldata/` och allt fungerar. Renderas den till `Layoutad/Archive/` pekar det på
`Layoutad/Grafkälldata/`, som inte finns — och **varje graf degraderade tyst**. Funktionens
dokumenterade kontrakt var att falla tillbaka i två steg: CSV om den finns, annars två staplar ur
KPI-blocket, annars en platshållarruta.

v0.86 renderades till `Layoutad/` och hade riktiga grafer. v0.87 och v0.88 renderades till
`Archive/` för att hålla katalogen ren. v0.88 publicerades.

### Varför ingenting fångade det

- **Guards täcker tal och text, inte bilder.** `scan_rendered_html()` läser HTML-text och kan inte
  se in i en PNG.
- **Sidantalet var oförändrat** — en platshållare fyller samma yta som en graf.
- **sha256 stämde** mot arkivkopian; den mäter att filen är den avsedda, inte att den är riktig.
- **Tvåagentsverifieringen granskade Cision-texten**, inte PDF:en.
- **Ingen öppnade den renderade rapporten.** Det är den egentliga orsaken. Se nedan.

### Vad som är rättat

**Källkatalogen härleds ur `data_path`.** `build_placeholder_charts(data, out_dir, data_path=...)`
tar nu emot datafilens sökväg och löser `Grafkälldata/` relativt den. Var PDF:en skrivs saknar
betydelse. Saknas `data_path` kastas `ChartSourceError` i stället för att gissa.

**Guard 24 — fail loud.** En grafspecifikation som namnger en CSV och inte kan läsa den är ett
**fel**, inte en fallback. Renderingen avbryts med samtliga drabbade grafer uppräknade och orsaken
per graf (katalog saknas / fil saknas / för få rader). Endast specifikationer med `csv_name=None` får
falla tillbaka på tvåstapelsvarianten ur KPI-blocket.

Verifierat 2026-08-25: rendering till `Archive/` ger nu riktiga grafer, och en pekning mot en
obefintlig källkatalog flaggar alla nio graferna och avbryter.

### Regeln som gäller framöver

**Öppna alltid den renderade PDF:en innan en version godkänns.** Inte sidantalet, inte guards, inte
sha256 — bilden. Rastrera med `pdftoppm -png -r 130` och **titta på varje sida**. `pdftotext` finns
inte på maskinen.

Granskningen 2026-08-25 gjordes så och fann fjorton defekter som samtliga textbaserade kontroller
hade passerat: platshållare i grafer, tio celler med råa decimaltal, tomma fetstilta rubriker,
saknade sidnummer. Ingen av dem syns i data, i HTML eller i ett sidantal.

**Kontrollistan före publicering, utöver guards:**

- [ ] Varje sida rastrerad och sedd. Antal sidor sedda = antal sidor i rapporten.
- [ ] Varje graf innehåller staplar eller en linje med data, rubrik och axeletiketter — ingen
      platshållarruta, ingen tom bildyta.
- [ ] **Nyckeltalens värden stämmer mot grafernas datapunkter för samma datum.** Se fynd 1 nedan.
- [ ] Varje tal som avser ett datum en tidigare rapport publicerat stämmer mot den rapporten.
- [ ] Inga celler med decimaler i SEK-tabellerna.
- [ ] Inga tomma fetstilta rubriker i uppställningarna.
- [ ] Sidnummer finns på alla sidor som ska ha dem och är läsbara mot underlaget.

Det stod redan i granskningsavsnittet att granskare ska se den renderade artefakten, med
revisionerna 2026-08-23 som exempel — där ingen såg rapporten och ett fynd därför inte höll. Samma
misstag upprepades 2026-08-25, med den skarpare varianten att inte heller den som renderade tittade.

**En guard kan bara fånga det den kan mäta.** Guard 24 fångar den här felmoden. Nästa felmod i en
bild fångas av att någon tittar.

## Final approval — cleanup workflow

After Henrik says "approved" (or equivalent — "final godkänd", "ok ship it", etc.) on a specific v0.N, run this cleanup before handing off to Cision-distribution:

```bash
cd "<period>/Kvartalsredogörelse/Layoutad" && \
mkdir -p Archive && \
mv "Sonetel kvartalsredogörelse <period> v"*.pdf Archive/ && \
cp "Archive/Sonetel kvartalsredogörelse <period> v<N>.pdf" "Sonetel kvartalsredogörelse <period>.pdf" && \
shasum -a 256 "Sonetel kvartalsredogörelse <period>.pdf" "Archive/Sonetel kvartalsredogörelse <period> v<N>.pdf"
```

What this does:
1. Creates `Layoutad/Archive/` subfolder
2. Moves ALL `Sonetel kvartalsredogörelse <period> v*.pdf` (every draft v0.1...v0.N) into Archive/
3. Copies the approved v0.N to release path `Sonetel kvartalsredogörelse <period>.pdf` (no version suffix — Cision-ready)
4. Verifies sha256 match between release copy and source v0.N — they MUST be identical

After cleanup the Layoutad/ folder contains exactly: the release PDF, the Archive/ subfolder, the auto-generated charts/ folder, and debug_output.html. The release PDF is what gets sent to Cision; the archive preserves the draft history.

Do NOT delete Archive/. It is the auditable draft trail showing how the report evolved (board/CA feedback iterations). Validated 2026-05-26 (Q1 jan-mar 2026): v0.57 approved → 57 drafts moved to Archive/ → release copy verified bit-identical via sha256.

## Cision publish flow (when PDF is godkänd)

Once `v0.N` has graduated to `v1.0` (Henrik approval) — or in practice, on the day before the planned publication, when the final draft (often `v0.5N+`) is approved — the next step is **Cision publication via the IR external-communications repo**. This is a separate, codified workflow that lives at `~/Library/CloudStorage/Dropbox/Workspace/Sonetel external communications/`. Validated end-to-end in Q1 jan-mar 2026 cycle (2026-05-25 session).

**Sonetels Cision-konvention för periodiska rapporter (FINAL, validerad 2026-05-26):** Pressmeddelandet är en KORT narrativ version av rapportens kärna + standard Cision-element (länk till PDF + boilerplate + kontakt + MAR). Den fullständiga rapporten — alla regulatoriska detaljer, tabeller, signaturer och definitioner — lever **endast i den layoutade PDF:n** som bifogas Cision-utskicket. Det är ett medvetet val: pressmeddelandets body ska vara läsbar och fokuserad, inte en återgivning av hela rapporten.

**Cision-paste-bodyn innehåller (i denna ordning):**

1. **Kort h1-rubrik:** `Sonetel kvartalsredogörelse <q-period>` enligt "Cision rubrik convention"-sektionen ovan (jan-mar / apr-jun / jul-sep / okt-dec — INGET år).
2. **Underrubrik (h2):** kvartalets tagline från `data.json meta.tagline` (t.ex. "+54% kundtillväxt och SaaS40 vid 40%"). Tagline är endast underrubrik, INTE huvudrubriken (huvudrubriken är den korta Cision-formen i punkt 1).
3. **Intro-mening (p):** `Sonetel AB (publ) publicerar härmed sin kvartalsredogörelse för perioden <månad> – <månad> YYYY.` — **INGEN tidsangivelse i ingressen.** Tidsstämpeln för publiceringen lever endast i MAR Art. 17-statement i slutet (för MAR-klassificerade releaser). För eventuella non-MAR releaser räcker Cisions distribution-header som tidskälla — ingen tid i body alls. Validerat 2026-05-26: tidigare draft hade `<strong>Stockholm, YYYY-MM-DD, kl. HH:MM CET.</strong>` som prefix, vilket skapade dual-write-risk när T0 ändrades sent — Henrik fick ett Cision-mail där ingress visade stale "08:30" trots att header visade korrekt 10:30. **Single source of truth = MAR statement.**
4. **Sammandrag** (h3 "Koncernen <månad> – <månad> YYYY" + 14 KPI-bullets från `data.json kpis`).
5. **VDs kommentarer** (h2 + h3 subtitle + N paragrafer från `narrative.vd_kommentar` + signatur Henrik Thomé / VD och grundare).
6. **Affärsmodell** (h2 + paragrafer från `narrative.affärsmodell` + 2 prisplaner-bullets + `affärsmodell_avslutning`).
7. **Audit caveat (em) — kommer FÖRE länken:** `Denna kvartalsredogörelse har inte granskats av bolagets revisorer.`
8. **Download link (p) — kommer EFTER caveaten:** `Kvartalsredogörelsen är tillgänglig för nedladdning på https://sonetel.com/sv/investerare/#rapporter`
9. **Om Sonetel (h2 + boilerplate verbatim från `_boilerplate/om-sonetel-sv.md`):** 4-mening Om Sonetel + "Mer information om bolaget finns på www.sonetel.com/sv/investerare/"
10. **Kontakt (h2 + block från `_boilerplate/kontakt.md`):** Henrik Thomé / VD / 08-525 060 11 / henrik@sonetel.com
11. **MAR Art. 17 statement (em, efter `<hr>`):** standard-mall från `_boilerplate/mar-statement-sv.md` med substituerad datum + tid.

**Vad som INTE ingår i pressmeddelandets body** (allt detta lever ENDAST i PDF-bilagan):

- ❌ Övrigt-blocket: redovisningsprinciper, väsentliga risker, aktier+bemyndigande, sammanställning, transaktioner med närstående, kalendarium
- ❌ Avlämnande + styrelse-signaturer (alla 6 ledamöter)
- ❌ Resultaträkning, Balansräkning, Kassaflöde — alla 3 koncerntabeller
- ❌ Definitioner (alla termer)
- ❌ Nyckeltal-sidans grafer + "Kommentar till grafer"-textbox (grafer exkluderas; kommentar-textens Skype-kontext duplicerar VD-kommentaren §2)
- ❌ KPI-tile-bandet (de färgade rutorna på sammandrag-sidan) — samma siffror redan i bullets
- ❌ Bilder (cover, VD-banner, affärsmodell-bild) — Cision card preview använder cover.webp separat

**Iterations-historik (för att slippa upprepa misstagen — alla från Q1 2026-cykeln):**
- *Första draft 2026-05-25:* tolkade "framvagn verbatim" som hela PDF:n inkl. alla tabeller. Henrik flaggade: *"Du har även tagit med bakvagnen"* → bakvagnen togs bort.
- *Andra draft samma dag:* fortfarande "Kommentar till grafer"-rubrik utan grafer + Övrigt-blocket inklusive signaturer. Henrik flaggade båda: *"Kommentar till grafer blir lite udda"* + *"Allt efter Övrigt ska inte med"*.
- *FINAL 2026-05-26 (denna sektion):* strukturen ovan med 11 punkter. Allt regulatoriskt + tabeller + signaturer lever endast i PDF-bilagan. Pressmeddelandet är ~3 sidor istället för ~10.

### Launch-folder convention

Skapa en lanseringsmapp per CLAUDE.md §6 (Launch Coordination) vid IR-repots `04_content/press_releases/YYYY-MM-DD-slug/`. Slug-formatet för periodiska rapporter: `YYYY-MM-DD-kvartalsredogorelse-q{1|3}-YYYY` (notera: ASCII-slug, ej "ö"). Mappen ska innehålla:

```
YYYY-MM-DD-kvartalsredogorelse-q{1|3}-YYYY/
├── 00-story.md                  ← master story (length, audience, MAR + channel scope)
├── 01-checklist.md              ← audience × channel matrix + pre-publish-stegen
├── 02-mar-decision.md           ← MAR Art. 17 classification (periodiska rapporter = alltid MAR)
├── 10-press-release-sv.md       ← markdown master av framvagnens text
├── 99-cision-paste.html         ← HTML-render av framvagnen för Cision-paste
├── 11-insights-post-sv.md       ← djup-dyk-story (svenska) → publiceras till sonetel.com/sv/investerare/insikter (se "Investor insights post" nedan)
├── 11-insights-post-en.md       ← djup-dyk-story (engelska) → bilingual, publiceras parallellt
├── 12-linkedin-ceo-sv.md        ← CEO LinkedIn post (svenska)
├── 12-linkedin-ceo-en.md        ← CEO LinkedIn post (engelska — för internationella följare)
├── 13-linkedin-co-sv.md         ← Bolags-LinkedIn (svenska)
├── 13-linkedin-co-en.md         ← Bolags-LinkedIn (engelska)
├── 14-x-sv.md                   ← X / Twitter (svenska)
├── 14-x-en.md                   ← X / Twitter (engelska)
├── 50-internal-msg-en.md        ← intern staff-kommunikation via Teams, ENGELSKA (T0 − 30 min)
└── _preview-all.html            ← STANDARD: konsoliderad preview för Henriks review (alla artefakter inlineade)
```

**`_preview-all.html` är obligatorisk** för varje launch — en självkontainerad HTML-fil med sticky vänster-nav och alla artefakter inlineade i samma flöde, så Henrik kan verifiera hela paketet i ett dokument istället för att öppna 13 separata filer. Underscore-prefixet håller den högst i fil-listning + markerar att det är en preview, inte en publicerings-artefakt. Krav: sticky nav med ankarlänkar till varje sektion, platform-frames för LinkedIn (blå border) / X (svart) / Slack (lila) / hub (röd) så Henrik visuellt känner igen kanalen, SV+EN side-by-side i `.duo` grid för LinkedIn/X, MAR-resonemang och pre-launch-checklist i komprimerad form längst ner. Validerad mall: Q1 jan-mar 2026 launch-folder. Header-badges: MAR Art. 17 / Two-agent review status / SV+EN scope. Footer-note måste tydligt säga "INTE för publicering — Cision-publiceringen sker från `99-cision-paste.html`" så Henrik inte råkar klistra preview-filen i Cision.

**Copy-paste-fidelity — KRITISKT (Henrik 2026-05-26):** Social-post-blocken (Teams, X, LinkedIn) inuti `_preview-all.html` MÅSTE använda korrekt HTML-paragrafstruktur så att copy-paste till Teams/X/LinkedIn behåller radbrytningar. **Använd INTE `<p>` med inbäddade `\n` + `white-space: pre-wrap`** — det renderar visuellt rätt men browsers copy-mechanism extraherar DOM-textinnehåll utan radbrytningar (allt blir ett stycke i mottagar-editorn).

**Korrekt mönster för platform-frame-innehåll:**

```html
<div class="platform-frame teams">
  <div class="meta-row">...</div>
  <p>Första stycket.</p>
  <p>Andra stycket med en<br>radbrytning inom samma stycke.</p>
  <p>• Bullet ett<br>• Bullet två<br>• Bullet tre</p>
  <p>Sista stycket.</p>
</div>
```

**Regel:**
- Tomrad i källan = nytt `<p>...</p>` element
- Single newline (t.ex. mellan bullets) = `<br>` inom samma `<p>`
- Browser-copy konverterar då `<p>` till "\n\n" och `<br>` till "\n" → texten klistras in med fullt bevarade radbrytningar i Teams/X/LinkedIn

**CSS-konsekvens:** `.platform-frame p` ska INTE ha `white-space: pre-wrap` (eftersom paragrafstrukturen redan ger korrekt visuell rendering). Lämna bara `margin` + `font-family`.

**Generations-script:** när preview byggs från markdown-källor måste markdown-paragrafer (separerade av tomrad) konverteras till separata `<p>`-element; bullet/list-rader inom samma stycke konverteras till `<br>`. En enkel Python-transform efter generering räcker:

```python
def md_para_to_html(text):
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return '\n'.join(
        '<p>' + para.strip().replace('\n', '<br>\n') + '</p>'
        for para in paragraphs if para.strip()
    )
```

**Validerat 2026-05-26:** första preview-iteration hade alla social-post-bodies som single `<p>` med `\n` + `white-space: pre-wrap`. Henrik fick copy-paste-merge till ett enda stycke när han klistrade in i Teams. Korrigerat genom att restrukturera till `<p>`-per-stycke + `<br>`-för-linjebrytning. Skill-uppdatering: detta är default-genereringsmönstret framöver.

**Auto-open preview för Henrik (STANDARD-STEG):** Så snart `_preview-all.html` är skriven (eller uppdaterad efter agent-review-fixar), kör `open "<full-path-to-_preview-all.html>"` via Bash så filen öppnas i Henriks standard-webbläsare. Han behöver inte be om det — det är förväntat efter varje generering/uppdatering av preview-filen. Validerat 2026-05-25: Henrik flaggade detta som ett återkommande mönster — om preview-filen finns ska den öppnas. Gäller även efter regenereringar (t.ex. om agent-review hittade fixar och preview-filen uppdaterats). Inga undantag.

**INTE relevant** för periodiska rapporter (skip these artifacts):
- `20-customer-email.md` (ingen kundkommunikation)
- `21-in-app-banner.md` (ingen produktnyhet)
- `30-blog-brief.md` / `31-help-brief.md` (ingen SEO/CS-uppdatering)
- `40-press-kit/` (ingen journalist-pitch)
- `60-app-store-copy.md` (ingen App Store-uppdatering)

### Verbatim PDF→HTML rendering rules

These rules reflect den slutgiltiga Cision-konventionen från Q1 jan-mar 2026-cykeln (validerad 2026-05-26 efter Henriks korrigeringar). **Apply them when rendering the press release body into `99-cision-paste.html`:**

1. **Rubriken är kort form:** `Sonetel kvartalsredogörelse <q-period>` (jan-mar / apr-jun / jul-sep / okt-dec). Tagline går som h2-underrubrik, INTE som huvudrubrik. Se "Cision rubrik convention"-sektionen ovan.
2. **Intro-mening överst (utan tidsstämpel):** `<p>Sonetel AB (publ) publicerar härmed sin kvartalsredogörelse för perioden <månad> – <månad> YYYY.</p>` — INGEN bold Stockholm/datum/kl-prefix. Tiden lever ENDAST i MAR Art. 17-statement i slutet, så det finns bara EN plats där HH:MM CET förekommer i pressmeddelandets body. Detta är Henrik 2026-05-26-konventionen efter att en stale ingress-tidsstämpel överlevde till publicering.
3. **Sammandrag:** h3 "Koncernen <månad> – <månad> YYYY" + flat ul med 14 bullets från `data.json kpis`. Linjärisera PDF:ns två kolumner (vänster sedan höger). KPI-tile-bandet (de färgade rutorna) skippas — samma siffror finns i bullets.
4. **VDs kommentarer:** h2 "VDs kommentarer" + h3 (samma som tagline) + paragrafer från `narrative.vd_kommentar`. Första paragrafen `<strong>` (lead-in / ingress). Signatur som `<p><strong>Henrik Thomé</strong><br><em>VD och grundare</em></p>`.
5. **Affärsmodell:** h2 "Affärsmodell" + paragrafer från `narrative.affärsmodell` + 2-bullet `<ul>` för prisplaner + paragrafer från `narrative.affärsmodell_avslutning`. Notera semikolon-meningen "Sonetel erbjuder tre prisplaner;".
6. **Övrigt-blocket, signaturer, Nyckeltal-sidan, alla 3 tabeller, Definitioner SKIPPAS HELT.** De lever endast i PDF-bilagan. Tidigare iterationer inkluderade dessa felaktigt; Henrik flaggade 2026-05-26 att pressmeddelandet ska vara den kortare narrativa kärnan + standard Cision-element (länk + boilerplate + MAR).
7. **Audit caveat först efter affärsmodell:** `<p><em>Denna kvartalsredogörelse har inte granskats av bolagets revisorer.</em></p>`
8. **Download link efter caveaten:** `<p>Kvartalsredogörelsen är tillgänglig för nedladdning på <a href="https://sonetel.com/sv/investerare/#rapporter">https://sonetel.com/sv/investerare/#rapporter</a>.</p>` (Henrik 2026-05-26: revisor-caveaten ska stå före länken så läsaren ser disclaimern innan call-to-download)
9. **Om Sonetel-boilerplate:** h2 "Om Sonetel" + verbatim text från `_boilerplate/om-sonetel-sv.md` (4-mening + "Mer information om bolaget finns på www.sonetel.com/sv/investerare/"). Använd `_boilerplate/om-sonetel-sv.md` som källa — INTE PDF:ns signing-page-version (de har olika scope; vi använder boilerplate för kort-form-pressmeddelandet).
10. **Kontakt-block:** h2 "Kontakt" + verbatim text från `_boilerplate/kontakt.md` (Henrik Thomé, VD / Telefon: 08-525 060 11 / henrik@sonetel.com).
11. **MAR Art. 17-statement i slutet** efter `<hr>`, från `_boilerplate/mar-statement-sv.md` med substituerad datum + tid. Periodiska rapporter är ALLTID MAR-klassificerade.
12. **Number formatting (i sammandrag-bullets och VD-prosa):** space-thousand-separator (`33 857`, ej `33,857`); comma decimal (`-0,05`, ej `-0.05`); minus-prefix för negativ (`-0,2`, ej `(0,2)`).
13. **Streck-typer:** en-dash (–) i numeriska intervall och datum-spans (t.ex. "januari – mars 2026"), em-dash (—) i narrativa avbrott i prosa. Källan är `data.json`; render.py renderar verbatim till PDF. När du kopierar text till HTML, behåll vad data.json har.

### Two-agent verbatim review pattern (MANDATORY before Cision publish)

Sonetel-prio is "no First North-correction triggers" — felaktig siffra eller felstavad rubrik i en MAR-klassificerad regulatorisk disclosure triggar både en pinsam korrigeringsmeddelande och potentiell First North-tillsynsförfrågan. To prevent: spawn **two independent reviewer agents in parallel** on the rendered `99-cision-paste.html`, each with PDF v0.{N|N+1} as the source-of-truth file.

**Why two agents:** They are independently prompted and reach independent confidence scores. If both reach ≥9/10 without coordination, that's a strong signal. If they disagree, that surfaces the actual edge cases.

**Agent specialization** (validated 2026-05-26 — uppdaterad efter kort-form-konventionen fastställdes):
- **Agent A — structural focus:** rubriken (kort form `Sonetel kvartalsredogörelse <q-period>`), underrubrik = tagline, publication stamp, sammandrag h3-rubrik + 14 bullets struktur, VDs kommentarer paragraf-räkning + signatur, affärsmodell-paragrafer + 2 prisplaner-bullets, download-link, audit caveat, Om Sonetel + Kontakt + MAR-statement i rätt ordning. Verifierar att INGET av Övrigt/signaturer/tabeller/Definitioner-blocken finns i body.
- **Agent B — numerical focus:** sammandrag-bullets-siffrorna (alla 14 KPI-bullets verbatim mot PDF sida 2), siffrorna i VD-kommentaren (CAC, kundbas, MSEK-värden, datum, procent verbatim mot PDF sida 3), prisplan-värden i affärsmodell (17 kr, 99 kr, 85%, 80% bruttomarginal verbatim mot PDF sida 4). PDF:ns bakvagnstabeller (Resultaträkning/Balansräkning/Kassaflöde) ingår INTE i pressmeddelandet och ska INTE verifieras i kroppen — agenten ska istället bekräfta att dessa tabeller är frånvarande.

Both agents must explicitly list **expected legitimate differences** så de inte false-positiv:ar:
- Bilder, grafer, KPI-tile-bandet skippas
- Övrigt-blocket (redovisningsprinciper, väsentliga risker, aktier+bemyndigande, transaktioner, kalendarium) skippas helt — finns endast i PDF-bilagan
- Avlämnande + styrelse-signaturer skippas — finns endast i PDF-bilagan
- Alla 3 koncerntabeller (RR/BR/KF) skippas — finns endast i PDF-bilagan
- Definitioner skippas — finns endast i PDF-bilagan
- Publication stamp tillagd överst (Cision-konvention, ej i PDF)
- MAR Art. 17-statement tillagd i slutet (Cision-konvention för MAR-releaser)
- Download link + audit caveat tillagda mellan affärsmodell och Om Sonetel
- Om Sonetel + Kontakt-block från `_boilerplate/`-filerna (har "Mer information om bolaget finns på..." som inte finns i PDF:ns Om-block — det är OK eftersom källan är boilerplate, inte PDF)

**Pass criterion:** both agents return GO (≥9/10) on the final HTML. If either returns REVISE (<9/10), apply the listed fixes and re-spawn one final verifier agent to confirm fixes are in. This three-step pattern (A+B in parallel → apply fixes → one verifier) was the Q1 2026 cycle and worked: A 5/10, B 6/10 → 4 fixes applied → verifier 9/10 GO.

**Agent-prompt template:** see `~/Library/CloudStorage/Dropbox/Workspace/Sonetel external communications/04_content/press_releases/2026-05-26-kvartalsredogorelse-q1-2026/` for the prompts that produced 9/10 confidence on the Q1 2026 cycle. Steal liberally.

### MAR classification (always Art. 17 for periodic reports)

Periodiska rapporter (Kvartalsredogörelse, Halvårsrapport, Kvartalsrapport, Bokslutskommuniké) är **alltid** MAR-klassificerade per Informationspolicy §§6.1, 7.1 — Art. 7 four-prong-testet är alltid uppfyllt eftersom periodiska rapporter per definition är prisrörande inside information. Decisions-loggen i `02-mar-decision.md` ska reflektera detta:

- **Klassning:** `MAR (inside information per Art. 7)`
- **Reasoning:** standard fyrprongs-test — alla fyra prong är uppfyllda
- **MAR Art. 17-statement bifogas** i pressmeddelandet
- **CA pre-publish-notifiering** 24h pre-T0 (G&W Fondkommission)
- **Closed window §7.6** löper de 30 kalenderdagarna **FÖRE** T0 (per MAR Art. 19(11) + Informationspolicy §7.6). **Fönstret upphör vid T0 publiceringsstund** — så snart pressmeddelandet är publikt är PDMR-handel fri igen. Tidigare formulering "T0+1 handelsdag" var MAR-fel (Henrik 2026-05-26).

Validerat 2026-05-25: format-rules.md i IR-repo dokumenterar att alla 7 periodiska rapporter i 57-release Cision-corpus är `IsRegulatory: true` med MAR-statement bifogad. Konsistens-record.

### Timing & distribution

- **T0:** typiskt **08:30 CET** för periodiska rapporter (pre-market). Validerat mot Sonetels Cision-corpus och cost-reduction-release 2026-05-19 (13:00 CET) som var icke-MAR och därför kunde ligga senare; periodiska rapporter ligger i morgonfönstret. Undantag: Q1 2026 publicerades 10:00 CET (Henrik direction).
- **Cision går först.** Inga audience-derivat (hub, LinkedIn, X, internal Teams) får publiceras innan Cision-tidsstämpel.
- **Internal Teams T0 − 30 min:** staff ska inte upptäcka rapporten via externa kanaler.
- **LinkedIn (CEO), X:** T0 + 0–60 min efter Cision live.
- **LinkedIn (company):** T0 + 1–4 h (efter CEO-post).
- **Investor insights post:** frikopplad från T0 — egen tidslinje (se "Investor insights post — publishing process"). Inte en launch-dags-derivation.

### EN co-publication policy

**Ingen EN-version av själva pressmeddelandet** för periodiska rapporter. Detta är Sonetels mångåriga praxis (samma som Bokslutskommuniké 2026-02-25 och Halvårsrapport 2025-09-25) per Informationspolicy §2. **Bilingual derivat för X och LinkedIn är OK** — de når internationella institutionella investerare och ger amplification utan att skapa en EN-version av MAR-disclosure-dokumentet (vilket skulle utlösa krav på samtidighet och översättningsbörda).

**Investor insights post: bilingual SV + EN** (Henrik 2026-05-28 — tidigare "svenska enbart" är överskrivet). Båda språk publiceras. Se egen sektion "Investor insights post — publishing process" nedan.

**LinkedIn / X bilingual posting** (Henrik 2026-05-25 frågade om båda ska postas):
- **SV är default** för båda kanaler — SONE-ticker handlas på Nasdaq First North Stockholm; retail-investerare läser primärt på svenska.
- **EN är supplemental** — för internationella institutioner och Henriks internationella personal-LinkedIn-nätverk.
- **När båda postas:** spaced 1–2h apart på samma handle (så följare inte ser samma Henrik/Sonetel-post två gånger back-to-back i feeden). På X kan man posta dem back-to-back inom några minuter — X-feed är snabbare och kortare innehåll.
- **Per launch är det Henriks val** om båda eller bara default-språket. Skillen genererar alltid båda; Henrik väljer vid posting.

### Sociala inlägg — tre regler (validerade 2026-08-25, halvårsrapport jan–jun 2026)

**1. Varje inlägg öppnar med en rad som namnger rapporttyp och period.** *"Sonetel halvårsrapport
jan–jun 2026 publicerad."* Utan den raden vet läsaren inte vad posten handlar om — den läser som en
lös kommentar om bolagets siffror. Henrik 2026-08-25: *"It doesn't say what we are talking about,
i.e. a half year report?"* Gäller även sifferuppställningsvarianten: `$SONE halvårsrapport jan–jun
2026:` — inte bara `$SONE H1 2026:`.

**2. Verifiera varje siffra och varje sakpåstående mot pressmeddelandet, inte bara mot rapporten.**
Amplification rule säger att inget nytt får introduceras i sociala kanaler. Vid produktionen
2026-08-25 introducerade prosamodellen **tre** påståenden som inte fanns i pressmeddelandet, varav
två dessutom var falska:

- *"Under vågen var det omkring 100 kunder per dag"* — rapporten anger 50 före vågen och 100 idag,
  ingenting om vågen. Under toppveckorna fyrdubblades inflödet.
- *"Juli var högsta månadsnivån sedan mars"* — april låg högre (3 257 mot julis 3 188).
- Länk till `sonetel.com/en/investors/` — sidan finns inte.

Alla tre lät rimliga. Det är felmoden: modellen fyller i det som borde stämma. **Claude äger fakta,
modellen äger språket** — den arbetsdelningen fungerar bara om faktakontrollen faktiskt görs, post
för post.

**3. Engelska inlägg länkar till den svenska investerarsidan**, med markeringen "(Swedish)". Det
finns ingen engelsk motsvarighet. Samma konvention som Q1 2026.

**Om paketet tas fram EFTER publicering** — vilket hände 2026-08-25 — saknar `01-checklist.md`,
`02-mar-decision.md` och `_preview-all.html` mening och ska utelämnas, inte skrivas retroaktivt. Lägg
en `00-README.md` i lanseringsmappen som säger varför de saknas.

### Internkommunikation: Teams + engelska + EFTER Cision (compliance-kritiskt)

**Henrik 2026-05-25 korrigerade** kanal+språk-konventionen: Sonetels staff är i Indien och använder Teams (inte Slack), på engelska (inte svenska). **Henrik 2026-05-26 korrigerade dessutom timingen**: tidigare draft satte Teams-meddelandet till T0 − 30 min — det är en **compliance-fail**.

**ABSOLUT REGEL — periodiska rapporter (och alla MAR-releaser):** Personal får INTE motta kursdrivande icke-offentlig information (MNPI) innan marknaden. Det betyder att fulla recap-meddelanden med siffror, KPI-värden, kommentarer, etc. går ut **EFTER** Cision-publiceringen, aldrig före. Att skicka KPI-fyllt meddelande till staff 30 min innan Cision är selective disclosure och bryter mot Informationspolicy + MAR.

**Korrekt timing:**

- **T0 + 0–5 min:** Fullt Teams-meddelande med siffror, recap, "thank you for the work behind these numbers". Past-tense: *"Our Q1 2026 Kvartalsredogörelse just went out on Cision"* — inte *"goes out at 10:30"*.
- **T0 − 30 min (ENDAST om logistiskt behov):** Kort heads-up UTAN siffror, UTAN innehållsdetaljer, UTAN headlines. Bara: *"Team — our Q1 financial update goes live on Cision at 10:30 CET (in ~30 min). I'll share the full recap and what it means for us right after publication. Until then, please hold any internal speculation or social activity."* Denna mening innehåller ingen MNPI och är OK. **Default-rekommendationen: skippa heads-up helt** om inte logistiskt nödvändigt — risken att någon i misstag delar något externt finns och bidrar inget värde.

- **Filnamn:** `50-internal-msg-en.md` (NOT `50-internal-slack.md`)
- **Kanal:** Microsoft Teams
- **Språk:** engelska
- **Ton:** CEO-personlig, "three things I'm proud of from this quarter". **INGEN closed-window-påminnelse** efter publicering — så snart pressmeddelandet är publikt finns inga handelsbegränsningar kvar (closed window löper de 30 dagarna PRE T0, slutar vid T0). Staff KAN dela offentlig information efter publicering — det är fri amplification och behöver inte påminnas om compliance.

**Språk-konvention för staff-facing text — audience är junior, non-financial Indien-team:**

Sonetels staff är primärt i Indien — junior engineering/CS/support, **inte finansorienterade**. Teams-meddelandet måste skrivas för dem som mottagare, inte för IR-läsare. Två separata fel detta innebär (Henrik 2026-05-26):

1. **INGEN IR-jargong eller svensk finansterminologi.** Henrik flaggade `"broken fiscal year"` (direktöversättning av "brutet räkenskapsår") som ett tydligt exempel — för en junior icke-finansorienterad indier låter "broken" som att något är trasigt/fel. Andra termer att UNDVIKA i staff-text: Cision, MAR, First North, Nasdaq, PDMR, Art. 17, ARR (de vet inte), SaaS40 / Rule of 40 (jargong), CAC (jargong), FX-neutral, USD-basis, Kvartalsredogörelse (svenskt ord), "fiscal year", "quarterly statement", "structural cost actions".
2. **Skriv inte i siffer-format som IR-people förstår** — översätt till "what does this mean intuitively". Exempel:
   - ❌ "+54% growth, +12% revenue, ARR +15%, SaaS40 at 40, CAC down 71%"
   - ✅ "We're now serving almost 34,000 paying customers — about 12,000 more than a year ago." + "It's costing us much less to win each new customer than it did last year." + "The company is growing AND profitable at the same time."

**Tone-rule:** "what's the story behind the numbers for someone who doesn't read financial reports". Tre punkter, vardera självförklarande, med en mening som ramar varför det är bra. Plus 2–3 punkter "what's coming next" som är konkret produkt-utveckling staff känner igen från sitt eget arbete.

**Avslutning ska vara FRAMÅTBLICKANDE, inte backward-looking-tack** (Henrik 2026-05-26): istället för "thanks for the work behind these numbers — it's your quarter as much as it is mine" (vilket Henrik flaggade som "I wouldn't say it like that"), använd en framåtblickande mening om vad som kommer. Henriks egen verbatim-formulering: *"With all the exciting things we're planning to roll out over the coming quarters, we've got a great ride ahead of us."* Det fångar samma motiverande ton utan att låta som ett tack-tal i pluralis-vi-skola-stil.

**Validerings-check vid generering:** läs igenom utkast och fråga: "skulle en 22-årig CS-agent i Bangalore eller en junior backend-utvecklare i Mumbai förstå varje mening utan att slå upp ord?" Om nej → skriv om.

**Test-audience-review-mönster (MANDATORY, validerat 2026-05-26):** Efter att Teams-utkastet är skrivet (eller iterat), spawna **två oberoende test-audience-agents** parallellt som simulerar mottagarsidan. De ska representera Sonetels typiska Indien-staff: 25–35 år, junior till mid-level, tech-orienterad (engineering/CS/support), icke-finansorienterad. Liknande pattern som two-agent verbatim review på Cision-paste, men med audience-simulation som fokus.

**Persona-template för agent A (junior engineer):**

> Du är Arjun Mehta, 27 år, backend-utvecklare på Sonetels Indien-kontor i Bangalore. Du har 4 års erfarenhet, jobbar med Node.js och Postgres på Sonetels billing-tjänst. Du läser TechCrunch och The Verge men följer inte börsmarknaden alls — du vet inte vad ARR, EBITDA, eller "Rule of 40" betyder, och du har aldrig hört talas om Cision eller First North. Engelska är ditt andra språk men du läser flytande. Det är 10:35 CET, du har precis sett ett Teams-meddelande från Henrik (VD) i #general. Läs det noggrant och svara: (1) förstod du varje mening utan att slå upp ord? (2) känner du dig motiverad och stolt över bolaget efter att ha läst det? (3) är det något som låter konstigt eller fel-översatt? (4) är det något som låter som corporate-speak eller AI-genererad text? Sätt fyra delpoäng (understandability / motivation / naturalness / lack-of-jargon) på skala 1–10 och en sammanvägd snittpoäng.

**Persona-template för agent B (CS/support):**

> Du är Priya Reddy, 31 år, customer support team lead på Sonetels Indien-kontor i Mumbai. Du har jobbat på Sonetel i 5 år, leder ett team om 8 support-agents som svarar på kundärenden via chat och email. Du har en BA i English Literature, inte teknik, och du läser inte finansiella rapporter. Du är bra på engelska men föredrar enkelt språk. Det är 10:35 CET, du har precis sett ett Teams-meddelande från Henrik (VD) i #general. Läs det noggrant och svara: (1) förstod du allt direkt utan att behöva läsa om någon mening? (2) finns det något som låter förmera eller distansherligt? (3) känner du att du och ditt team uppskattas i meddelandet? (4) är det något som skulle vara konstigt att förklara för en ny junior i ditt team? Sätt fyra delpoäng (understandability / warmth / clarity / relatability) på skala 1–10 och en sammanvägd snittpoäng.

**Pass criterion:** båda agenter ska returnera **≥8/10 snittpoäng**. Om en eller båda <8 → iterera utkastet baserat på deras specifika kritik (citerade meningar, ord-byten, ton-fix), re-spawn en eller båda agenter en gång till. Maximalt 2 iterationer; om fortfarande <8 efter andra iterationen → fråga Henrik direkt om vad som hänger.

**KRITISKT — vad agent-feedback betyder och vad den INTE betyder (Henrik 2026-05-26):**

Test-audience-agents ger ärlig läsning av om språket landar. Det betyder INTE att deras föreslagna fixar är rätt. Specifikt: om båda agenter säger *"jag förstår inte ARR / SaaS40 / CAC"*, **dra INTE slutsatsen "ta bort dessa metrics"**. Det är **fel slutsats**. Den rätta slutsatsen är att de behöver **förklaras inline med plain-language**, inte tas bort.

Q1 2026-cykeln gjorde detta misstag: iteration v3→v4 droppade ARR, SaaS40, CAC YoY-delta, samt "+54% YoY"-tillväxt eftersom agenterna inte förstod orden. Resultatet var en intetsägande mjukspråklig version som Henrik flaggade som *"You have removed all the metrics. 34000 customers is known by team since months. You oversimplified it and watered it down to something that contains nothing."*

**Rätt mönster för audience-anpassning:** behåll metric + förklara den. Exempel:
- ❌ Drop: "almost 34,000 paying customers" (statisk total — staff vet redan, "old news")
- ✅ Restore + frame: "Paying customers up +54% year-over-year. Almost 34,000 at the end of Q1, vs about 22,000 a year ago." (förändringen är nyheten + tydlig referenspunkt)
- ❌ Drop: "ARR +15%" (jargong — agenten vet inte vad ARR är)
- ✅ Restore + inline-glossa MED förkortning + full term: "ARR — Annual Recurring Revenue, the yearly value of all active subscriptions — up +22% in USD (and +15% in SEK)"
- ❌ Drop: "CAC dropped" eller utlös bara "Cost to acquire a new customer" (saknar termen så staff inte lär sig den)
- ✅ Restore + inline-glossa MED förkortning + full term: "CAC — Customer Acquisition Cost, what we pay on average to win each new paying customer — dropped from 162 kr to 47 kr"
- ❌ Drop: "SaaS40 at 40" (jargong)
- ✅ Restore + inline-glossa: "SaaS40 = 40. That's a SaaS industry benchmark for balanced growth + profitability (revenue growth % + EBITDA margin %). Hitting 40 means we're growing AND profitable at the same time."

**Konsekvent inline-glossa-mönster:** `**TERM — full uttydning, kort plain-language definition — siffra/förändring.**` Förkortningen kommer först (så staff kan koppla till termen när de ser den i framtida dashboards/möten), sedan utskriven form, sedan en kort plain-language definition, sedan själva siffran. Validerat 2026-05-26: Henrik flaggade att ARR hade fått inline-glossa men CAC inte hade det (jag hade bara skrivit "Cost to acquire a new paying customer" utan att introducera termen "CAC"). Båda termer ska följa samma mall.

**Regel framåt:** när agent-feedback identifierar ett ord/koncept som "okänt för audiencen", **defaulten är inline-förklaring, inte borttagning**. Endast om Henrik explicit säger "drop X" tas substansen bort. Annars är staff-meddelandet en utbildningstillfälle — staff ska EFTER att ha läst förstå (a) vad metricen är, (b) vad förändringen betyder, (c) varför det är bra för bolaget.

**Audience-divergens är legitim men inte alla divergenser ska "fixas":** Q1 2026-cykeln visade att CS (Priya) ville ha AI-reassurance ("supporting your work, not replacing it") medan engineering (Arjun) läste samma mening som "denial IS the signal". Detta är en strukturell skillnad och kan inte optimeras bort utan att tappa andra sidan. Henriks slutgiltiga call är vilken sida som väger tyngre i en given launch.

**Konsistens-check med samtidiga corporate-actions (Henrik 2026-05-26, post-publish):** Varje claim i staff-meddelandet måste vara (a) faktiskt sant just nu OCH (b) internt konsistent med pågående corporate-actions som staff redan känner till. Q1 2026-cykeln gjorde detta fel: utkastet sa *"Growing AND profitable also means we have the runway to keep investing in product and team without raising more money"* — Henrik tog bort raden vid posting med två motiveringar: *"it isn't true lately AND it would raise questions why we then had to let go of their co-workers."*

**Mönster:** När bolaget samtidigt går igenom en omstrukturering / personalreduktion / kostnadsåtgärd som staff känner till (t.ex. 19 maj-reorgen som påverkar 28% av Indien-personalen), undvik claims som motsäger den narrativa logiken bakom åtgärden. Specifikt:
- ❌ Claims om "runway", "no need to raise money", "we can keep investing freely" parallellt med en aktiv personalminskning — staff kommer omedelbart fråga "varför då layoffs?"
- ❌ Claims om "the team is growing" när annan kommunikation samtidigt säger att teamet minskar
- ❌ Claims om "we don't need to cut costs" parallellt med kommunikerade cost actions
- ✅ Tystnad om finansiell hälsa-runway om det INTE matchar restructuring-narrativet; staff behöver inte den extra meningen
- ✅ Tystnad är bättre än motsägelse — staff är smarta nog att märka

**Validerings-check pre-publish:** läs varje claim i utkastet och fråga: "Om den här meningen och vår senaste reorg-/cost-action-kommunikation läggs sida vid sida, ser staff motsägelse?" Om ja → drop claim eller omformulera. Validerat Q1 2026: körde inte den checken pre-publish; Henrik fångade det själv vid posting och tog bort raden.

**Validerat 2026-05-26 (Q1 jan-mar 2026 cykeln):** första två iterationer hade "broken fiscal year" + KPI-jargong + "Cision" — Henrik flaggade detta som off-target för audience tre gånger. Pattern hade fångat det om det funnits från början. Nu kodifierat så framtida cyklar testar utkastet mot personas före human review.

Validerat 2026-05-26: första iteration hade "Q1 2026 Kvartalsredogörelse went out on Cision" + "first quarterly statement in the new calendar fiscal year — following our switch from a broken fiscal year" + KPI-rader med ARR, SaaS40, CAC. Henrik flaggade i två separata varv ("they have no clue what Cision is" + "broken fiscal year — they will wonder if broken means something wrong"). Omskrivet med audience-anpassad ton; lärdomen kodifierad här.

**Validerat 2026-05-26 (Q1 2026 cykeln):** första draft satte Teams till T0 − 30 min med fulla KPI-värden i body. Henrik flaggade som compliance-fail: *"The team message talks about numbers going out in the future. This is wrong. We can never publish numbers to the team before publishing to the market."*

### GPT-5-polish för svenska texter — ALL text, ingen ordgräns (Henrik 2026-05-28)

**ABSOLUT REGEL:** ALL svensk text som publiceras externt eller internt ska gå genom GPT-5-polish innan den sparas/publiceras. **Ingen ordgräns.** Den tidigare "≥150 ord"-tröskeln (från CLAUDE.md §9) är **överskriven** — Henrik flaggade 2026-05-28: *"GPT polish gäller för ALL text. Inte bara 150 ord."*

Skälet: Claudes svenska drar mot "swenglish" — anglicismer och stel syntax — oavsett textlängd. En kort LinkedIn-bullet eller X-mening kan vara lika osvensk som ett långt stycke. Polish-steget fångar det.

**Gäller (alla net-new svenska texter):**
- **Investor insights post SV** — långform deep-dive
- **LinkedIn CEO SV** — oavsett längd
- **LinkedIn company SV** — oavsett längd (tidigare "under tröskeln" är ogiltigt)
- **X SV** — narrativ-versionen polishas; siffer-fokus-versionen (ren KPI-tabell utan meningar) är data, inte prosa — men vid minsta tvekan, polisha
- **Hub/insikter, newsletter, alla derivat med svenska meningar**

**Enda undantaget — redan-polerad källtext:**
- **Press release body (10-press-release-sv.md / 99-cision-paste.html):** VD-kommentaren är källtext och redan GPT-polerad under rapportens framtagande (per `vd-ordet-pipeline/`). Verbatim-utdrag därifrån behöver INTE ny polish. MEN: net-new framings-meningar (publiceringsstämpel, intro-meningar) ska polishas oavsett längd.

**Process per text:**
```bash
python3 ~/.claude/scripts/openai_call.py \
  --system-file ~/.claude/scripts/swedish-polish-prompt.txt \
  --user-file <path-to-draft>.md \
  --model gpt-5 \
  --max-tokens 6000
```
Spara polerad output verbatim till samma fil. Loggens request-ID i changelog. (System-prompten ligger på `~/.claude/scripts/swedish-polish-prompt.txt` — bevarar fakta/siffror/struktur, förbättrar endast idiomatik; validerad Q1 2026.)

**EN-versioner** är deliberata översättningar av högstaks-IR-innehåll (inte auto-translate) men går INTE genom svensk-polish-steget (det är för svenska). Engelsk text skrivs direkt i idiomatisk engelska.

**Polish-regressioner att kontrollera EFTER varje GPT-5-pass (validerat 2026-05-28):** polish-prompten är prosa-orienterad och kan (a) **strippa inline-bold** (`**...**`) från bullet-listor, (b) **drifta terminologi** (t.ex. "AI-orkestrerad" → "AI-styrd"). Efter polish: diffa mot pre-polish och återställ bold-markörer + kanoniska termer som måste matcha publicerad Cision-disclosure (t.ex. "AI-orkestrerad verksamhetsmodell"). Polisha helst bara BODY (inte frontmatter) genom att splitta på `---` före anropet.

### Faktagranskning: attribuera INTE CAC-fall till AI-omställningen (Henrik 2026-05-28)

**Återkommande frestande narrativ som är faktiskt FEL:** att rama lägre CAC som "beviset att AI-omställningen levererar". Det är en kausal-attributionsfel. Den verkliga mekanismen bakom Q1 2026:s CAC-fall (162 → 47 kr):
- **Minskad betald CPC-annonsering** sänkte anskaffningskostnaden på de CPC-baserade konverteringarna
- Eftersom andelen betald trafik minskade **försköts trafikmixen mot organisk** — vilket drar ner det genomsnittliga CAC
- **Organisk trafik ökade INTE i sig** — det är spend-minskningen + mix-effekten som ger det lägre snittet
- Det är ett **medvetet marknadsförings-spend-val, inte en AI-effekt**

Den AI-byggda hemsidan och mobilapparna är en separat capability-story (AI-arbetssätt → snabbare leveranser) som INTE ska kopplas kausalt till CAC-talet. Henrik flaggade 2026-05-28: *"Lower CAC is NOT the result of AI transition."*

**Bonus-lärdom (samma dag):** undvik defensiv "det är INTE X"-framing i rubriker/ingresser när läsaren inte ställt frågan. En rubrik som "CAC halverades — men det är inte en AI-effekt" planterar själv kopplingen och låter som att man argumenterar med sig själv (samma anti-pattern som Arjuns "denial IS the signal" 2026-05-26). Skriv ren faktaframställning: "Anskaffningskostnaden föll 71%" + förklara mekanismen plain. Den publicerade Cision-VD-kommentaren var redan korrekt formulerad ("en effekt av att vi minskat betald CPC-annonsering till förmån för organisk trafik") — felet uppstod i editorialiserade derivat (LinkedIn CEO, insights-post draft).

**Henrik 2026-05-25 + 2026-05-28:** Q1-launchen körde initialt inte polish på alla SV-texter (bara hub-post + LinkedIn CEO SV kördes). Regeln är nu utan undantag: net-new svensk text → GPT-5-polish, oavsett längd.

**TODO — synka CLAUDE.md §9:** projekt-regeln i `Sonetel external communications/CLAUDE.md` §9 säger fortfarande "≥150 ord". Den ska uppdateras till "ALL svensk text" för att matcha denna regel. (Flaggat 2026-05-28; CLAUDE.md-edit kräver Henriks OK eftersom det är checked-in projekt-instruktion.)

### Cision-bilagor

Två bilagor till varje periodisk rapport på Cision:

1. **Layoutad PDF**: senaste godkända versionen (`v0.{N}.pdf` eller `v1.0.pdf`).
2. **Cover image** (`cover.webp`): som Cision card preview image.

### Test-audience-review per channel (Henrik 2026-05-26)

Teams-meddelandet är inte den enda artefakten som ska vetas mot audience-personas. **X och LinkedIn-derivat ska också gå genom test-audience-review** — men med **channel-anpassade personas, INTE samma som Teams**. Audience-profilen är helt olika: internal Teams = junior non-financial India-team; LinkedIn/X = finance-aware investors + customers + tech peers.

**Channel-specifika persona-rekommendationer:**

| Kanal | Persona A | Persona B |
|---|---|---|
| **Teams (internal)** | Junior backend engineer 27 Bangalore (Arjun) | CS team lead 31 Mumbai (Priya) |
| **LinkedIn CEO (personal)** | SaaS-founder peer som följer Henrik | Tech-curious senior dev som följer Henrik från en mässa |
| **LinkedIn company (Sonetel)** | Avanza/Nordnet retail-investerare som äger SONE | SMB tech-decision-maker som funderar på Sonetel som leverantör |
| **X (FinTwit-SE)** | Retail-trader på X som följer SONE-ticker | Mikrocap-bevakare som skriver tråd-analyser |

**Tröskel: ≥8/10 snittpoäng per kanal.** Samma iterations-policy som Teams-mönstret (max 2 iterationer → escalera till Henrik).

**Voice-tone-skillnad: Personal LinkedIn (Henrik) vs Company LinkedIn vs X.**

- **Henriks personliga LinkedIn:** ska låta som Henrik-the-person, INTE Henrik-the-CEO. Anchor: corpus i `07_analytics/ceo_linkedin_corpus/henrik-thome-linkedin-articles.md`. Voice-patterns från corpus:
  - Första-person possessiv: "Mitt bolag Sonetel"
  - Stanza-formad kort prosa, inte tunga block
  - Konkreta detaljer + siffror (vendor-namn, $-belopp)
  - Lite känsla: "euforiskt", "Nu kör vi!", "It's going to be a fun ride"
  - Direkt struktur: "Det handlar inte om X, utan om Y"
  - Inga marknadsförings-fraser ("excited to announce", "leverage", "synergies")
  - En persona ska kunna säga: *"this sounds like Henrik wrote it on his phone, not a comms team."*

- **Company LinkedIn (Sonetel-bolagskonto):** mer formell, brand-voice. Bullets för KPIs OK. Ton: "informerar marknaden om kvartalet". Mindre känsla, mer fakta.

- **X (FinTwit):** kort, direkt, ticker-driven ($SONE). Två versioner per språk — narrativ default, siffer-fokus alternativ. Inga emojis.

**Validerat 2026-05-26 (Q1 2026 cykeln):** första LinkedIn-CEO-draft var "mätta-professionell" — passed för LinkedIn-company-ton men för formell för Henrik-personal-konto. Omskriven v2 i corpus-tonen. Vetting-process: spawn 2 personas per channel, ≥8 snitt.

**Vetting-mängd per launch:** typiskt 3 kanaler × 2 personas = 6 agenter parallellt (på SV-default-versionerna). EN-versionerna är mekaniska speglingar och vetas inte separat (om SV passar, EN antas mekaniskt OK). Sex agenter i bakgrund tar ~2 min totalt.

### House style: NO emojis, NO ikoner (Henrik 2026-05-26)

**Absolut regel för all extern/intern text** (pressmeddelande, investor insights post SV+EN, LinkedIn SV+EN, X SV+EN, Teams-meddelande): **inga emojis, inga icon-tecken.** Henrik flaggade 2026-05-26: *"Skip the emoji/icons. Looks very AI'ish. Applies to all texts."*

**Specifikt INTE använda:**
- Rocket-ikoner (🚀)
- Paperclip / attachment-ikoner (📎)
- Newspaper / press-ikoner (📰)
- Chart / bar-graph-ikoner (📊)
- Link-ikoner (🔗)
- Checkmark-emojis (✅) — använd plain "[x]" eller "☐" om checkbox behövs
- ChatGPT-stilade pilar (→) som bullet-prefix i social-posts (LinkedIn CEO etc.) — använd plain text eller `•` bullet istället
- Andra färgade emojis

**Tillåtet:**
- Typografiska bullets `•` (U+2022) — typografisk markör, inte emoji
- Pilar (→) i logisk text (t.ex. "X → Y" som "leder till") i interna dokument (CR, MAR-decision, story)
- Standard checkboxar `☐` / `☑` i interna checklistor (inte i externt material)

**Validering vid generering:** efter att alla derivat skrivits, kör `grep -P "[🚀📎📰📊🔗✅]" <launch-folder>/*.md` — det ska returnera 0 träffar. Pilar (→) inspekteras manuellt: OK i 99-cision-paste.html om de står i logiska implikationer i Övrigt-blocket (men Övrigt finns inte i body); NOT OK som bullet-prefix i LinkedIn/X/Teams-derivativs.

**Validerat 2026-05-26 (Q1 2026 cykeln):** första draft hade 🚀 i Teams-meddelandets opener, 📎/📰 i avslutningen, 📊 i LinkedIn-bolag-rubriker, → som bullets i LinkedIn CEO, 📎 i X-länk-prefixerna, 🔗 i LinkedIn-bolag-länkar. Alla strippades i samma pass; alla derivat regenererades clean.

## Investor insights post — publishing process (cross-repo, bilingual)

**Bakgrund (Q1 2026-cykeln):** Den ursprungliga `11-hub-post.md` var en reframing av Cision-pressmeddelandet — fel form. En investor insights post är en **deeper story beyond the press release** (operationell deep-dive, strategi-reflektion, kund-narrativ, behind-the-scenes långform). Se rationale-brief: `Sonetel external communications/01_strategy/investor_hub_rationale_2026-05.md`. Implementationen av insights-ytan på sonetel.com drevs av `CR-2026-05-26-public-web-investor-insights-page` (cross-repo, sonetel.com-repot).

**Vad det INTE är:** inte en sammanfattning/reframing av Cision-text. Om posten duplicerar pressmeddelandet är den fel form. Den ska tillföra substans: djupare berättelse, kontext, teknik-narrativ, multimedia.

### Bilingual: SV + EN (Henrik 2026-05-28)

Insights-posts publiceras på **både svenska och engelska**. Filer:
- `content/posts/investor/sv/<slug>.mdx`
- `content/posts/investor/en/<slug>.mdx`

URL: `/sv/investerare/insikter/<slug>/` (svenska) + `/en/investor-relations/insikter/<slug>/` motsvarande. **Bekräftat live 2026-05-28:** router accepterar `INSIGHTS_SLUGS = ["insights", "insikter"]`, men den kanoniska svenska URL:en använder `insikter`.

### Frontmatter-schema (per CR)

```yaml
---
title: "<rubrik på svenska / engelska>"
slug: <kebab-case>                       # samma slug båda språk; blir URL
date: YYYY-MM-DD                         # ISO; sorterar list + tile
author: "Henrik Thomé"
excerpt: "<1–2 meningar>"                 # list-card + tile + meta description
ogImage: /images/insikter/<slug>/og.webp # on-brand bild (se nedan); fallback /og-default.jpg om utelämnad
tags: [operational, ai, growth]          # informational only i v1
relatedRelease: <EncryptedId>            # renderar "Relaterat pressmeddelande"-callout; resolvas från Cision-API (release-rubrik → EncryptedId). Om ej resolvbar: ta bort raden, lämna inte placeholder
---
```

### On-brand bild (Henrik 2026-05-28)

Insights-posts ska ha en **on-brand bild** — wired som `ogImage` (social/OG-delning, båda locales) + hero-bild överst i posten. Bilden genereras med **sonetel.com-repots egna `/generate-image`-skill** (Flux 2 Pro, 16:9) — INTE kvartalsredogörelse-skillens image-gen (det är för rapport-cover/affärsmodell; website har sin egen stil). Asset placeras på `public/images/insikter/<slug>/og.webp` (`.webp` är skillens native-output; `.gitignore` ignorerar `public/images/**/*.webp` så force-add krävs — samma konvention som befintliga genererade heroes).

**Bild-QC (samma brand-regler som rapporten):** ingen läsbar text/logo/skyltning; korrekt anatomi (två armar/händer, fem fingrar, naturlig pose); cared-for/charmig miljö (inga shabby/derelict cues). Skillen har en obligatorisk QC-gate (Gemini-flash) — kör den + egen visuell inspektion, regenerera vid defekt. Q1 2026: sydostasiatisk småföretagare i keramikstudio, QC-pass första försöket.

**VIKTIGT — hero-slot finns redan (sedan 2026-05-28):** den FÖRSTA insights-posten krävde en kodändring (lägga hero-`<img>`-slot i `insight-post.tsx`) — det är gjort. **Framtida insights-posts är därför content-only**: sätt bara `ogImage`-frontmatter + droppa asset, så renderar hero-sloten automatiskt. Ingen ny kodändring → ingen CR krävs för bild på efterföljande posts. (Om hero-layouten behöver ändras strukturellt → det ÄR en kodändring → CR-for-Henrik per gränsen nedan.)

### Ansvarsdelning (Henrik 2026-05-28 — courier-fri modell)

**IR-sessionen (denna skill) gör BÅDA stegen — Henrik är INTE courier:**

1. **Författa (editorial — stannar i IR-sessionen):**
   - Skriv SV-posten: CEO-röst, deep-dive, MAR-compliant, det som INTE får plats i Cision-wire
   - **GPT-5-polish SV-långformen** (≥150 ord — alltid för insights-posts; per CLAUDE.md §9)
   - Skriv/översätt EN-versionen
   - Visa Henrik i preview, få godkännande
2. **Placera (cross-repo, initiator-spawns):**
   - IR-sessionen spawnar en placerings-agent **direkt in i sonetel.com** med de **kompletta färdiga MDX-filerna** (SV + EN), exakta paths, och CR-close-steg i prompten
   - Agenten: droppar båda filerna, kör build för att verifiera render, flippar CR-status + registry + changelog
   - **Henrik couriererar aldrig** mellan sessioner (han har ~50 öppna fönster; courier-rollen tappar saker)

**Varför IR-sessionen spawnar direkt istället för courier:** att skicka den kompletta filen i spawn-prompten är icke-lossy (inget att re-derivera — frontmatter + body är färdiga). Courier-route skulle kräva att Henrik kopierar text mellan sessioner. Initiator-spawns med färdig artefakt undviker både courier-bördan OCH lossy re-derivation.

**KRITISK GRÄNS — content-placering vs kodändringar (Henrik 2026-05-28):**

- **Content-placering** (droppa färdig MDX, kopiera förberedd asset) → spawnad agent får göra DIREKT. Ingen review-cykel krävs för innehåll.
- **Kodändringar** (komponenter, CSS, routes, logik) i sonetel.com → spawnad agent **DRAFTAR en CR och STANNAR**. IR-sessionen granskar/kommer överens om CR:n. **Henrik implementerar via en native sonetel.com-session.** Spawna INTE en agent för att implementera kod direkt.

**Varför kodändringar inte får implementeras av spawnad agent:** en spawnad agent **kan inte själv spawna agenter** (nested Agent-tool-spawning är inte tillgängligt). sonetel.coms process kräver en review-cykel (2 parallella review-agenter till ≥8 confidence) innan en CR implementeras — det kan en spawnad agent fysiskt inte köra, så den faller tillbaka på tunna checks (tsc/eslint/build) och skippar den riktiga reviewen. **En spawnad cross-repo-agent kan därför ALDRIG köra "follow the process".** Validerat 2026-05-28: en IR-spawnad agent implementerade ingress-CSS + hero-bild i `insight-post.tsx` och shippade till staging utan sonetel.coms 2-agent-review (kunde inte spawna reviewers). Henrik behöll arbetet (staging, reversibelt) men satte regeln. Se memory `feedback_cross_repo_spawned_agent_cannot_follow_process`.

**Dropbox-kollisions-skydd:** den spawnade placerings-agenten måste vara ENSAM skribent i sonetel.com-trädet vid det tillfället. Bekräfta att ingen aktiv sonetel.com-session skriver parallellt innan spawn (annars Dropbox-sync-kollision — känd failure mode).

### Timing — frikopplad från Cision-T0

Insights-posten är INTE en launch-dags-derivation (till skillnad från LinkedIn/X/Teams som k015ar mot Cision-T0). Den är en separat deep-dive som kan publiceras på egen tidslinje (CR sample-post hade `date: 2026-06-01`, dagar efter 26 maj-launchen). Amplification rule gäller fortfarande: posten får referera ett Cision-pressmeddelande men inte avslöja MAR-känslig info som inte redan disclosats via Cision först.

### Channel-derivat — content rules

- **Investor insights post (`11-insights-post-{sv,en}.md`):** deep-dive långform, INTE Cision-reframing. CEO-röst (anchor: `07_analytics/ceo_linkedin_corpus/`). Bilingual SV+EN. Publiceras cross-repo till sonetel.com/sv/investerare/insikter via placerings-agent-spawn (se "Investor insights post" ovan). GPT-5-polish obligatorisk på SV-långformen.
- **LinkedIn CEO (SV+EN):** personal voice, 3 punkter, ~150-200 ord. Hashtags `#Sonetel #SaaS #AI #investorrelations #firstnorth`.
- **LinkedIn company (SV+EN):** mer formell, bullets för nyckeltal, ~80-120 ord. Samma hashtags + `$SONE` (ticker).
- **X (SV+EN):** 2 versioner per språk — **narrativ är default** (per Henrik 2026-05-26 — *"For X, narrative version is better"*); siffer-fokus är alternativ för Avanza/Nordnet-stilad publicering. Ticker `$SONE`.
- **Internal Teams (`50-internal-msg-en.md`):** **engelska** (staff i Indien), Henrik-röst, "Three things I'm proud of from this quarter", påminnelse om closed window för LinkedIn-trafik. Publish-time T0 − 30 min via Microsoft Teams.

## English translation (`--lang en`)

Produces an **unofficial English rendering for internal staff use**, clearly marked as a translation.
Never for Cision, sonetel.com or shareholder mailings. Introduced by
`CR-2026-08-25-engelsk-oversattning-halvarsrapport` (Financial repo).

```
DYLD_LIBRARY_PATH=/opt/homebrew/lib <venv>/bin/python render.py \
  <period>/data.json "<period>/Engelsk översättning/<name> (unofficial English translation).pdf" \
  --lang en --charts-dir "<period>/Engelsk översättning/charts"
```

### The rule that matters: never translate `data.json`

`render.py` matches **Swedish string literals** in six places, and five of them fail **silently**:

| What matches Swedish | If you translate the data |
|---|---|
| `_find()` in `derive_kpis()` | No KPI derived *and none back-filled* — every null `yoy_pct` stays null |
| `_table_row()` gates in guards 1, 2, 3, 4a, 4b, 4c | Each gate is a truthiness test with no `else`. **Five reconciliations and one warning vanish without a message** |
| `mark_summa_rows()` | Zero total rows marked — every total loses its bold and rule |
| `render_forandring_ek()` line ~513 | Opening/closing equity lose the `summa` class |
| `tile_to_kpi` in guard 12 | Autofill skipped, tiles publish `"XX"`, and the 4-char `XXXX` pattern does not catch it |
| `governance.board[*].roll` (guard 10b) | Hard error — the only one that fails loudly |

So a translated `data.json` produces **no reconciliation at all, and the output does not show it.**

**Instead:** the Swedish `data.json` stays the single source. Translation is
- a **prose overlay** (`text.en.json`, beside `data.json`) merged **after** `run_guards()` and
  **before** `build_placeholder_charts()` — the guards need Swedish labels, the two-bar chart
  fallback needs the translated `meta.period_short*`; and
- a **glossary** (`i18n/glossary.en.json`) applied at *print time* in `render_fin_table()`,
  `_row_to_html()` **and** `render_forandring_ek()` — in the last one **after** the `summa` test,
  or both equity tables silently lose their emphasis.

Verify with `--lang sv` and `--lang en` on the same data: the guard log must be identical (same
number of summa rows, derived KPIs, dropped zero rows). If it is not, the overlay is merging too early.

### Constraints a translation must respect

- **`affarsmodell_prisplaner` bullets must start with the plan name followed by a full stop.**
  `inline_bold_prefix()` bolds everything up to the first `.` with a regex; a longer opening
  sentence bolds the wrong span, silently.
- **Machine-read fields are never translated** — `narrative[*].graf`, `[*].bild_bred`, any path.
  Translating a chart filename makes the chart disappear with no error. `i18n.apply_overlay()`
  aborts if an overlay value looks like a path or image name.
- **Numbers are not translated, they are re-rendered** from the same `data.json`. Verify by
  extracting every `<td>`/`<th>` and comparing pairwise — 1 149 cells for the jan–jun 2026 report,
  and the difference must be zero. Do not compare flattened page text: adjacent cells run together
  and the result is noise.
- Accounting captions in the glossary are a **first draft until Göran or BDO have read the rendered
  English statements.** The published English launch texts cover P&L and KPI terms only; they say
  nothing about balance-sheet or cash-flow captions, which are most of the 114 entries.

### Keeping the Swedish output byte-identical

Every English branch in `template.html` is `{% if lang == 'en' %}…{% else %}<the original Swedish
markup, moved not rewritten>{% endif %}`, and `t('key', '<swedish literal>')` keeps the Swedish
literal inline. **Jinja block tags add whitespace**: use `{%- if %}` / `{%- endif %}` to strip the
newline and indent the tag introduced, or the Swedish output shifts by blank lines even though the
content is unchanged.

Prove it without rendering, in seconds: stub `weasyprint` in `sys.modules` with a class that captures
the `HTML(string=…)` argument, run `render()` for both the old and new template, and compare the two
HTML strings with sha256. That catches every content and whitespace regression before WeasyPrint is
involved at all.

## When to use this skill vs /sonetel-bokslut

| Report type | Skill | Pipeline |
|---|---|---|
| **Kvartalsredogörelse** (Q1/Q3) | `/kvartalsredogörelse` | JSON → HTML → WeasyPrint → PDF |
| **Kvartalsrapport** (Q2/Q4 detailed) | `/sonetel-bokslut` | Word template, manual |
| **Halvårsrapport** | `/sonetel-bokslut` | Word template, manual |
| **Bokslutskommuniké** | `/sonetel-bokslut` | Word template, manual |
| **Årsredovisning** | `/arsredovisning` | Separate workflow (BDO bakvagn + CEO framvagn) |

A future CR may migrate the heavier reports to the same JSON pipeline once Kvartalsredogörelse is proven.

## Kommentar till grafer och sammanfattningsrubrik — process (Henrik 2026-11-18)

Samma flöde som VD-ordet. Henrik kör texten i ChatGPT och Claude äger fakta, kontroll och layout.

1. **Claude skriver en brief** i `<period>/kommentarer/brief-grafer.md`. Briefen innehåller:
   - en kort skrivarinstruktion: läsaren känner inte bolaget, saklig svenska, bara briefens fakta, inga framtidslöften, högst cirka 90 ord i två stycken;
   - vilka grafer som finns på sidan;
   - verifierade fakta ur `Grafkälldata/`.
2. **Faktakraven kommer från läsartestet av jul–sep 2026:**
   - Förklara även de grafer som går ned, och säg varför.
   - Jämför mot samma baslinje som sammanfattningen, alltså samma kvartal i fjol, eller förklara varför en annan baslinje används.
   - Avrunda inte bort dåliga perioder.
   - Avsluta inte på en enda positiv månad efter perioden.
   - Förklara enheter som "per dag, månadssnitt".

   Annars läses kommentaren som tillrättalagd.
3. **Exportera** skrivarinstruktion och brief i en fil till `~/Downloads/Grafkommentar <period> brief.md`. Ge Henrik filnamnet och samma ChatGPT-steg som i `vd-ordet-pipeline/PIPELINE.md` § STANDARDFLÖDE: ny chatt, Thinking på max, klistra in hela filen.
4. **När Henrik skickar texten** gör Claude följande:
   - kontrollerar varje tal mot `Grafkälldata/`;
   - lägger in texten i `narrative.kommentar_till_grafer`, ett stycke per listelement;
   - renderar och kontrollerar att rutan står på nyckeltalssidan. Hamnar den på en egen sida krymper Claude graferna (`.chart-card img`, i dag 90 %), inte texten. Komprimerade texter blir telegramstil;
   - kör läsartestet med en bild av sidan (`pdftoppm`) och sammanfattningssidans text. Läsarna ska bedöma om kommentaren stämmer med graferna.
5. **Sammanfattningsrubriken** (`meta.tagline`) är som standard VD-ordets rubrik. Så gjordes i Q1 och H1 2026 och i jul–sep 2026. Henrik kan välja en egen.

## VD-ordet writing pipeline

**BINDANDE REGEL (Henrik 2026-11-18): ge skribenten minimalt med instruktioner.** Briefen är material och spärrar: vad perioden handlade om, verifierade fakta, en kort lista på vad som inte får sägas. Inga formler, inga styckeanvisningar, inga ordlistor, inga färdiga meningar — inte heller i revisionsbriefer. Detaljstyrning förstör kvaliteten. Enda innehållsregeln: upprepa inte siffror som redan står i sammanfattningen på sidan före (Henrik 2026-11-18). Systemprompten i stilguidens §10 är medvetet kort; bygg inte ut den.

The text of the VD-ordet section is **not** drafted by Claude (insufficient Swedish quality per Henrik's empirical experience). It is drafted by GPT-5 via OpenAI, with iterative critic-agent review until both an Avanza retail-investor and a sell-side analyst persona score ≥8/10, then surfaced to Henrik for corrections, then ship.

**Source of truth for the persona/voice rules**: `vd-ordet-style-guide.md` (this skill, root). The §10 system prompt is verbatim what GPT-5 sees.

**STANDARD (Henrik 2026-11-18): läsartest med tre virtuella svenska investerare efter varje utkast som visas för Henrik — se `vd-ordet-pipeline/lasartest.md`.**

**STANDARDFLÖDE (Henrik 2026-11-18): Claude skriver briefen, kopierar den till `~/Downloads/VD-ord <period> brief.md`, Henrik kör den i ChatGPT (max thinking) och skickar tillbaka texten; Claude faktagranskar, lägger in i data.json, renderar och kör läsartestet.** Detaljer: `vd-ordet-pipeline/PIPELINE.md` § STANDARDFLÖDE. API-pipelinen nedan är reserv.

**Pipeline orchestration**: `vd-ordet-pipeline/PIPELINE.md` documents the 10 steps (init folder → extract prompt → compose brief → draft → critic round → score eval → revise loop → Henrik review → promote final → MAR-decision). Scripts in `vd-ordet-pipeline/scripts/draft_vd_ordet.py`. Critic persona templates in `vd-ordet-pipeline/critic-personas/{retail,sellside}.md`.

**ABSOLUTE RULE (Henrik 2026-05-25): Every new or changed text in VD-ordet MUST be GPT-5-polished before render.** Claude's Swedish drafting reliably produces "swenglish" — anglicisms and stiff syntax that read as unprofessional. **No exceptions** — applies to rubrik changes, ingress rewrites, any paragraph edit (even small factual rephrasings), CAC/KPI mentions, etc. Process: compose a short brief with the fact + intent (no rule lists, no example sentences) → call `~/.claude/scripts/openai_call.py --system-file <system-prompt.txt> --user-file <brief.md> --model gpt-5 --max-tokens 12000` → apply output verbatim to data.json. If multiple paragraphs change in one cycle, run them ALL through GPT-5 together (one call) for consistent voice. See `vd-ordet-style-guide.md` §7 principle 12 for full rule and validated-regression note.

**Folder layout per period** (working files):

```
<period>/Kvartalsredogörelse/
├── Underlag från BDO/              ← whole-report accounting underlag
├── Underlag från ledning/           ← whole-report management material (cost-actions PPT, framing matrices)
├── data.json                        ← assembled report data (later)
└── vd-ordet/                        ← EVERYTHING VD-ordet-related in one folder
    ├── README.md
    ├── vd-ordet-final.md            ← THE VD-ordet deliverable
    ├── transcript.txt               ← Henrik's recorded brain-dump
    ├── briefs/                      (system-prompt + drafter brief + revision briefs)
    ├── drafts/                      (vd-ordet-draft-vN.md per iteration)
    ├── critics/                     (critic reviews + scores.jsonl)
    └── pipeline/                    (raw API payloads + logs)
```

**Key principle**: everything VD-ordet-related lives under `vd-ordet/`. Whole-report inputs that inform multiple sections (cost-action PPT, framing matrix, BDO numbers) live at the period root in `Underlag från X/` folders — NOT inside `vd-ordet/`.

Quick start for a new period:

```bash
PERIOD='/Users/henrik/.../Kvartalsredogörelse'
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py init-period "$PERIOD"
# Drop transcript.txt → "$PERIOD/vd-ordet/transcript.txt"
# Drop whole-report management material → "$PERIOD/Underlag från ledning/"
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py extract-prompt "$PERIOD"
# Compose "$PERIOD/vd-ordet/briefs/brief-for-drafter.md" from transcript + Underlag (Claude)
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py draft "$PERIOD" --version 1
# Spawn 2 critic agents in parallel using critic-personas/{retail,sellside}.md (Claude)
# Log scores via log-score; if both <8, compose revision brief & call `revise`; loop up to 3
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py promote-final "$PERIOD" <version>
```

See `PIPELINE.md` for the full workflow Claude follows step by step.

## Reference

- CR: `~/Dropbox/Sonetel/Financial/docs/plans/CR-2026-05-12-kvartalsredogörelse-skill.md`
- Old manual: `~/Dropbox/Sonetel/Financial/Documentation/Att skapa kvartalsredogörelse/Att skapa kvartalsredogörelse ver 1.0.pdf`
- Regression fixture: `~/.claude/skills/kvartalsredogörelse/examples/jul-sep-2025/data.json`
- Reference PDF: `~/Dropbox/Sonetel/Financial/2024 2025/Quarter/Q5 jul-sep 2025/Kvartalsrapport/Layoutad/Sonetel kvartalsredogörelse jul-sep 2025  v1.0.pdf`

$ARGUMENTS
