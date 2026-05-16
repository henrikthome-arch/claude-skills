---
name: kvartalsredogörelse
description: Create or update Sonetel AB's Kvartalsredogörelse (Q1/Q3 lighter quarterly statement to Nasdaq First North). Use when working on a Kvartalsredogörelse — drives a JSON → HTML/CSS → WeasyPrint → PDF pipeline. Distinct from /sonetel-bokslut which covers Bokslutskommuniké / Halvårsrapport / Kvartalsrapport on Word.
argument-hint: "[period e.g. jan-mar 2026]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel financial reports. If the current working directory does NOT contain `Sonetel/Financial`, STOP immediately and tell the user: "This skill is for Sonetel financial reports only. Current directory: [cwd]". Do NOT proceed.

You are helping Henrik Thomé, CEO of **Sonetel AB (publ)**, prepare a Swedish **Kvartalsredogörelse** for Q1 or Q3 of the fiscal year. The company is listed on Nasdaq First North Growth Market. The working directory is the relevant **Year** folder under `~/Dropbox/Sonetel/Financial/`.

## What this skill replaces

The old workflow lived in `Documentation/Att skapa kvartalsredogörelse/Att skapa kvartalsredogörelse ver 1.0.pdf` — a 10-step manual that involved pasting BDO numbers into Word tables. The manual explicitly warned (step 10): *"Det är lätt att siffror dubbleras eller missas om antalet rader i Excel-fil och Word-mall inte överensstämmer."* This skill retires that failure mode by making `data.json` the single source of truth.

The old skill (`/sonetel-bokslut`) is **not** replaced — it still drives Bokslutskommuniké, Halvårsrapport, and Kvartalsrapport (the heavier reports). Use the right tool for the report type.

## Pipeline

```
data.json  ──►  pydantic validate  ──►  11 reconciliation guards (pre-render)
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
4. Update KPI block from operational data (sales_analysis, finops) — see `/sonetel-bokslut` for ARR scaling methodology if needed; for Kvartalsredogörelse a simpler MSEK pull suffices.
5. **Run the deviation analyzer** (see "KPI deviation analysis" section below) — it surfaces income-statement rows and KPIs with material YoY changes. For each flagged item, gather the underlying driver from the user **before** drafting VD-ordet. For cost-side flags, the typical pattern is to spawn a read-only research agent into `Workspace/financial-ops/` to identify root causes (vendor-level breakdowns, one-time vs recurring split). This is a cross-repo read-only operation — do not edit financial-ops files.
5b. **MANDATORY in Q1 cycle (and recommended in every cycle): verify `share_capital.bemyndigande_text` and `sammanstallning[Outnyttjat bemyndigande].antal` against the most recent bolagsstämma kommuniké.** Q1 Kvartalsredogörelse is typically published in May, AFTER that year's ordinarie bolagsstämma (held in April), so a fresh bemyndigande exists by Q1 publication date. Default canonical-source location: `~/Dropbox/Sonetel/Corporate documents/Bolagsstämmor/<YYYY MM DD> Ordinarie bolagsstämma/kommuniké/Kommuniké årsstämma Sonetel <YYYY-MM-DD> v*.pdf`. Read the kommuniké, extract: (a) date of stämma, (b) percentage cap (typically 10% or 20%), (c) full bemyndigande text (omfattning: aktier only vs aktier+teckningsoptioner+konvertibler). Update `bemyndigande_text` verbatim. Compute `Outnyttjat bemyndigande antal` = round(antal_aktier × percentage / 100). Validated Q1 2026: stämma 2026-04-23, mandate 10%, outnyttjat 757 138 (= 10% × 7 571 381). FY24-25 had 20% mandate; never assume — always re-read the kommuniké each cycle.
6. Update `kalendarium` from sonetel.com/sv/investerare/ (see "Kalendarium rule" section).
7. **Port chart-source CSVs from prior period** (see "Chart source data" section). Copy `Grafkälldata/*.csv` from the previous period's folder, then append rows for the new quarter — using BDO numbers where available and `XX` placeholder rows where finops fetch is pending.
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

**Renderer status**: `build_placeholder_charts()` in render.py currently produces 2-bar comparisons (current vs prior) from the KPI block, NOT from these CSVs. Upgrading to multi-quarter line charts that consume the Grafkälldata CSVs is a TODO — the CSVs are kept up to date in anticipation.

## Source consistency for operational KPIs

**Principle (Henrik 2026-05-13)**: each KPI must come from ONE canonical source, used consistently across periods. ARR can be calculated multiple ways and the same name on different sources can produce non-comparable numbers. Document the chosen source in `data.json kpis.<key>.source` so any future report can reconcile.

**Canonical sources (validated Q1 2026 — exhaustive list)**:

| KPI / data | Canonical source | Endpoint / file / location | Note |
|---|---|---|---|
| **ARR (MUSD/MSEK)** | financial-ops API (mirrors upstream Sonetel billing-system daily email) — this is the **förbättrade ARR-modell** Sonetel rolled out ~1 year ago and reports daily | `GET /api/v1/metrics/trend?metric=arr_total` — value extracted verbatim from "Call report-daily" email's `ARR(Annual recurring revenue)` table, row `Total`. Stored USD-only in `email_metrics`. Confirmed by Henrik 2026-05-13 as **the most accurate ARR source** — replaces older sales_analysis "Annualized payments" methodology which should NOT be used going forward. | Formula owner = upstream billing-system (NOC/billing engineering); financial-ops only mirrors. Audit-trail: `Workspace/financial-ops/config/analytics/email_metric_definitions.yaml:252-265` and `metric_documentation.yaml:24` document `arr_total = arr_phone_numbers + arr_premium_plan + arr_business_plan + arr_business_package`. Cross-validated 2026-05-13: Dec 25 EOQ from FinOps = $2,813M × 9.21 SEK/USD = 25.9 MSEK matches FY24-25 Bokslutskommuniké v21 published figure ✅. SaaS40 uses ARR USD-basis growth (FX-neutral); ARR display in MSEK uses period-end Riksbanken dagskurs |
| **Antal aktiva betalande kunder** | `sales_analysis_<YYYY-MM-DD>.xlsx` — sheet `'Data'`, **row 731** "In accounts with positive balance" (under section 'Customers with subscriptions') | Henrik's hint 2026-05-13: financial-ops also has it via DuckDB-ingested Subscriptions CSV table filtered `WHERE status = 'A'`, count at EOQ. Both should produce same value (validated Mar 2026 = 33 857 via finops `monthly_process_metrics.subscriptions_positive_balance`). xlsx row 731 is canonical because it preserves continuity with FY24-25 Bokslutskommuniké v21 (Dec 2025 row 731 = 33 636 ≈ v21 published 33 600 ✅) and gives YoY history back to 2022+ | DO NOT use email_tables_raw "Active past month" (29 430) — that's activity-filtered, not the canonical positive-balance count. Henrik specifically flagged this as wrong source. |
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
| **VD-ordet drafts** | GPT-5 via OpenAI API + 2 critic personas | see `vd-ordet-pipeline/PIPELINE.md` | Henrik provides transcript + WHY answers as input |
| **Bemyndigande (share_capital.bemyndigande_text + Outnyttjat-antal)** | most recent ordinarie bolagsstämma kommuniké | `~/Dropbox/Sonetel/Corporate documents/Bolagsstämmor/<YYYY MM DD> Ordinarie bolagsstämma/kommuniké/Kommuniké årsstämma Sonetel <YYYY-MM-DD> v*.pdf` | **Re-read each cycle (especially Q1 since publication is post-stämma).** Validated 2026-04-23: 10% mandate (replaced 18-dec-2024 20% mandate). Outnyttjat = round(antal_aktier × pct/100). Never copy from prior period — always read fresh kommuniké |

**Operational rule**: when an existing KPI's source changes between periods, set a `source` field in `data.json` describing the change AND flag in the VD-ordet brief that the YoY comparison may not be strictly like-for-like. The very first period on a new source is "transitional" — the next period and onward are clean.

**Cost-side commentary**: when deviation analyzer flags cost-line moves, spawn the read-only finops research agent (see "KPI deviation analysis" section above). The agent reconciles BDO accounts to vendor-level drivers — codified as a standard step.

## Reconciliation guards (built into render.py)

The script runs 11 fail-loud guards before emitting the PDF:

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
| 12 | `kpi_tiles[i].value` matches the corresponding `kpis.*` field (per built-in mapping) | KPI tiles are hand-curated and can drift from KPI block; this guard re-derives expected and fails on mismatch |

## Moderbolag tables — NOT included in Kvartalsredogörelse

The Kvartalsredogörelse (lighter Q1/Q3 format) presents **koncern tables only**: resultaträkning, balansräkning, and kassaflöde for the consolidated group. It does **not** include separate moderbolag tables — those appear in the heavier Halvårsrapport and Bokslutskommuniké formats only. The v1.0 jul-sep 2025 reference confirms this scoping.

The CR initially listed `tables.resultatrakning_moderbolag` / `tables.balansrakning_moderbolag` in the schema; the implementation deliberately omits them. If a future Halvårsrapport adopts this pipeline, those tables get added then.

## Charts — current limitation

`build_placeholder_charts()` in render.py produces simple **2-bar** comparisons (prior vs current period) for the Nyckeltal page. The published v1.0 uses **multi-quarter line charts** (typically 6–8 quarters). The visual quality of the Nyckeltal page is therefore the largest single gap vs v1.0. To upgrade, extend `build_placeholder_charts()` to read a `Grafkälldata/*.csv` directory like `/sonetel-bokslut` does, and use `line_chart()` for monthly/quarterly series. The function name `build_placeholder_charts` is deliberate — rename to `build_charts` once real series data is wired.

## Kalendarium rule

**List ALL future events from publication date forward.** Typical Q1 publication has 6 events ahead (next Verksamhetsredogörelse, Halvårsrapport, the other Verksamhetsredogörelse, Bokslutskommuniké, Årsredovisning, Bolagsstämma). Q3 publication has 4–5 ahead. Don't truncate to a fixed count — show whatever's actually scheduled.

**Canonical terminology** (aligned with `/sonetel-bokslut`):
- **"Verksamhetsredogörelse Q1"** / **"Verksamhetsredogörelse Q3"** (NOT "Kvartalsredogörelse")
- **"Bolagsstämma"** (NOT "Årsstämma")
- "Halvårsrapport", "Bokslutskommuniké", "Årsredovisning" unchanged

The v1.0 jul-sep 2025 used the older terms ("Kvartalsredogörelse" / "Årsstämma") — that was reconciled away from the Q1 jan-mar 2026 cycle onward. The website at sonetel.com/sv/investerare/ is the source of truth for the actual scheduled dates; manually copy from there each cycle (auto-fetch is a TODO).

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

For file-size reduction (rarely needed — typical output is ~700 KB):
- Open in **Preview → File → Export → Quartz Filter: Reduce File Size**

## Layout & visual conventions

These rules emerged from iteration cycles with Henrik. **Treat them as defaults, not negotiable** — undoing one usually triggers the same feedback again.

### WeasyPrint paged-media patterns

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

### Tables

- **Pale-blue tint (`tint_current=True` default in `render.py`) on the current-period column on ALL three financial tables**, not just balansräkning. Resultaträkning, balansräkning split parts, and kassaflöde all get the tint.
- **Tint must be continuous top-to-bottom — section-headers render as `label + empty value cells`, NOT `colspan`.** Colspan breaks the tint band because `:nth-child(2)` no longer matches.

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

If regeneration is needed: write a CORRECTIVE prompt that explicitly forbids the observed defect (e.g. "no third hand on the fabric stack, exactly two arms"). The first regen often resolves it. Validated Q1 2026: Marrakech leather artisan needed leg-twist fix; Lisbon cover needed cat-not-cropped fix; Jaipur woman needed three-arm fix on first iteration.

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

- **WeasyPrint can't find libgobject / libpango**: `DYLD_LIBRARY_PATH` must be set before Python starts. `render.py` calls `os.environ.setdefault(...)` early, but the macOS dyld behaviour around `DYLD_*` is finicky — if it still fails, run with the env var explicit: `DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 render.py …`.
- **Gotham SSm renders as Helvetica fallback**: verify `~/Library/Fonts/GothamSSm-{Book,Medium,Bold}.otf` exist. The CSS uses absolute `file://` URLs — relative paths won't resolve.
- **A guard fires but the data looks correct**: read the error message — it includes the JSON path. Don't bypass with `--allow-date-mismatch` unless you actually intend a mismatch (publication ≠ signing).
- **Chart looks like 2 bars when it should be a line series**: that's the current placeholder limitation (see "Charts" section above). Upgrade `build_placeholder_charts()` to use real time-series data.
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

- **Layoutad PDF**: `<Q-folder>/Kvartalsredogörelse/Layoutad/Sonetel kvartalsredogörelse <period> v<N>.pdf`
- **data.json**: lives at `<Q-folder>/Kvartalsredogörelse/data.json` (next to the BDO underlag folder)
- **Versions**: `v0.1, v0.2, ...` for drafts; `v1.0` when released to Cision
- **Charts directory**: auto-managed; safe to delete and re-generate

## When to use this skill vs /sonetel-bokslut

| Report type | Skill | Pipeline |
|---|---|---|
| **Kvartalsredogörelse** (Q1/Q3) | `/kvartalsredogörelse` | JSON → HTML → WeasyPrint → PDF |
| **Kvartalsrapport** (Q2/Q4 detailed) | `/sonetel-bokslut` | Word template, manual |
| **Halvårsrapport** | `/sonetel-bokslut` | Word template, manual |
| **Bokslutskommuniké** | `/sonetel-bokslut` | Word template, manual |
| **Årsredovisning** | `/arsredovisning` | Separate workflow (BDO bakvagn + CEO framvagn) |

A future CR may migrate the heavier reports to the same JSON pipeline once Kvartalsredogörelse is proven.

## VD-ordet writing pipeline

The text of the VD-ordet section is **not** drafted by Claude (insufficient Swedish quality per Henrik's empirical experience). It is drafted by GPT-5 via OpenAI, with iterative critic-agent review until both an Avanza retail-investor and a sell-side analyst persona score ≥8/10, then surfaced to Henrik for corrections, then ship.

**Source of truth for the persona/voice rules**: `vd-ordet-style-guide.md` (this skill, root). The §10 system prompt is verbatim what GPT-5 sees.

**Pipeline orchestration**: `vd-ordet-pipeline/PIPELINE.md` documents the 10 steps (init folder → extract prompt → compose brief → draft → critic round → score eval → revise loop → Henrik review → promote final → MAR-decision). Scripts in `vd-ordet-pipeline/scripts/draft_vd_ordet.py`. Critic persona templates in `vd-ordet-pipeline/critic-personas/{retail,sellside}.md`.

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
