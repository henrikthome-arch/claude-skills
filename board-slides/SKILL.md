---
name: board-slides
description: Render Sonetel AB board meeting decks as 16:9 landscape PDFs from JSON via Jinja2 + WeasyPrint. Use when producing slide decks for any meeting in `Sonetel/Board/Board meetings/<year>/<meeting folder>/slides/`.
---

**DIRECTORY GUARD**: This skill is for Sonetel board meeting decks only. If the current working directory does NOT contain `Sonetel/Board/Board meetings/`, STOP and tell the user: "This skill is for Sonetel board meeting decks only. Current directory: [cwd]". Do NOT proceed.

The skill is a deliberate replacement for PowerPoint. Decks are produced as a single PDF rendered from a Jinja2 HTML template via WeasyPrint, sized 16:9 landscape (297 mm × 167 mm). The data lives in `data.json` next to the renderer; the slide structure derives partly from `agenda/agenda.json` and partly from per-item content slides in `data.json`.

This is iteration #1 of the skill — extracted from meeting #7 (May 21, 2026). Expect ongoing iteration as new patterns surface.

---

## When to invoke

- The user is in a meeting folder under `Sonetel/Board/Board meetings/<year>/<meeting>/`
- They are working with `slides/`, `slides/data.json`, or asking to "render the deck"
- They want to add a new slide type, modify the layout, or apply design-system changes

## When NOT to invoke

- For per capsulam minutes — use the `board-minutes` skill (different pipeline, fpdf2-based)
- For PowerPoint-backed decks — older meetings used `.pptx`; don't convert without explicit user request

---

## File layout

A single meeting's `slides/` folder is the unit of work:

```
<meeting folder>/
├── agenda/
│   ├── agenda.json              # source of truth for items + meeting metadata
│   └── agenda.md                # human-readable mirror
├── content/                     # raw inputs the user wrote (NOT slide content)
├── slides/
│   ├── render.py                # forked from skill into meeting folder
│   ├── template/
│   │   ├── template.html
│   │   └── style.css
│   ├── assets/
│   │   ├── sonetel-wordmark-white.svg
│   │   ├── sonetel-wordmark-black.svg
│   │   ├── fonts/Inter-VAR.ttf  # also installed at ~/Library/Fonts/
│   │   └── charts/              # auto-generated PNG charts (gitignored)
│   ├── data.json                # slide content (per agenda item, keyed by number)
│   └── output/                  # versioned PDFs: "Sonetel board meeting <date> v0.N.pdf"
├── financials-data/             # JSON files from the Finops agent (optional)
└── ...
```

The renderer expects to run **from the meeting folder root**:
```
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 slides/render.py
```
(The DYLD path is needed for WeasyPrint to find Homebrew's libgobject etc.)

PDF auto-versions as `v0.1.pdf`, `v0.2.pdf`, … . Once signed off, drop the `v0.` prefix.

---

## Bootstrapping a new meeting

When the user wants a new deck:

1. **Create the meeting folder** following the board-meeting skill's structure.
2. **Copy the pipeline files** from this skill into the meeting's `slides/` subfolder:
   - `render.py`
   - `template/template.html`
   - `template/style.css`
   - `assets/sonetel-wordmark-*.svg`
3. **Ensure Inter is installed** at `~/Library/Fonts/Inter-VAR.ttf` and `Inter-Italic-VAR.ttf`. If missing, download from `github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf` (and the italic variant) and copy both to `~/Library/Fonts/` AND `<meeting>/slides/assets/fonts/`. The CSS references the user-fonts path.
4. **Author `agenda/agenda.json`** with 5–8 items (keep agendas brief — Henrik's preference).
5. **Create `slides/data.json`** with the meta section + an empty `items: {}` map keyed by agenda item number. Each value is an array of slide dicts.
6. **Render** and iterate.

A clean starter data.json:
```json
{
  "meta": {
    "cover_subtitle": null,
    "cover_date_label": "<DD Month YYYY>",
    "closing_message": "Thank you"
  },
  "items": {"1": [], "2": [], "3": []}
}
```
When `cover_subtitle` is null, the cover automatically uses `agenda.meeting.location` (skips if `location == "TBD"`).

---

## Slide types

All slide types live in `template.html` as `{% elif s.type == "..." %}` branches and have matching CSS in `style.css`. Each accepts these common fields: `title`, `subtitle`. Most also receive `agenda_number` + `agenda_title` automatically (rendered as an uppercase eyebrow).

| Type | Use for | Required fields |
|---|---|---|
| `bullets` | A list of 3–6 procedural or descriptive points | `bullets: list[str]` |
| `two_column` | Two parallel lists side-by-side | `left: list[str]`, `right: list[str]` |
| `numbered_two_col` | Numbered list 1–10 in two columns (e.g. growth ideas) | `entries: list[{text, badge?, badge_tone?}]` (also accepts plain strings) |
| `pnl_table` | P&L line items with actual + budget + variance | `pnl_rows: list[PnlRow]`, optional `pnl_columns`. See §11 (merge rule) and §10 (sources in footnote). |
| `kpi_grid` | 3×2 grid of KPI cards (Finops Monthly Pulse styling) | `kpis: list[{label, value, lines[], tone}]`. See §8 for sizing. |
| `breakeven` | Two-box breakeven/cashflow assessment | `breakeven_boxes: list`, `breakeven_note` |
| `cash_position` | Cash trend + drivers panel | `data_ref` → `cash-position.json`, optional `drivers_title`. See §12. |
| `cash_flow_forecast` | Daily cash projection chart + top-5 items panel (Finops UI styling) | `data_ref` → `cash-flow-forecast.json`. See §15. |
| `trends_grid` | 3×2 grid of small charts (Finops Monthly Pulse styling) | `data_ref` + `trends_layout`, OR inline `trends`. See §9 for figsize. |
| `quote` | A single quote with attribution | `quote`, optional `attribution` |

Section dividers, the cover, the agenda slide, and the closing slide are auto-generated by `build_slide_sequence()` from `agenda.json` + `data.meta`. The user doesn't author them directly.

Badges available on `numbered_two_col` entries:
- `badge_tone: "positive"` — green pill (e.g. "Implemented")
- `badge_tone: "warn"` — amber pill (e.g. "Tax issues")
- `badge_tone: "info"` — blue pill
- `badge_tone: "neutral"` — gray pill

Auto-generated slide types (not authored in `data.json`; emitted by `build_slide_sequence()`):
- `cover` — first slide, taken from `agenda.meeting`
- `agenda` — second slide, rendered from `agenda.items[]`
- `section` — one per agenda item, eyebrow + section number/title + (optional) sub-items
- `closing` — last slide, taken from `deck.meta.closing_message`

Optional `notes: str` field on most slide types renders as a footnote/caption below the main content (`bullets`, `pnl_table`, others). Use it for the source/methodology footnote on financial slides — see §10.

---

## Trends slide: data_ref pattern

For 13-month trend charts, the slide references an external JSON file (typically `financials-data/13-month-trends.json` written by the Finops agent — see below) instead of inlining 91+ datapoints.

```json
{
  "type": "trends_grid",
  "title": "13-month trends",
  "subtitle": "Apr 2025 – Apr 2026",
  "data_ref": "financials-data/13-month-trends.json",
  "trends_layout": [
    {"title": "Net Revenue (USD)", "key": "net_revenue_usd", "kind": "bar"},
    {"title": "New customers / day",
     "keys": ["new_customers_per_day_with_sub", "new_customers_per_day_without_sub"],
     "kind": "stacked_bar"},
    {"title": "Net churn rate", "key": "net_churn_rate_pct", "kind": "line", "y_format": "percent"}
  ]
}
```

`render.py:expand_data_refs()` reads the file and constructs the `trends: list[TrendSeries]` from the layout. Each chart is rendered via matplotlib to a PNG in `slides/assets/charts/` and embedded.

Supported `kind`: `bar`, `line`, `stacked_bar`.
Supported `y_format`: `auto`, `percent`, `thousands`.

The chart styling lives in `render.py:_style_axes()` and uses design-system tokens (charcoal bars, gray gridlines, no chartjunk).

---

## Financial data: spawning the Finops agent

For decks that include P&L, KPI, breakeven, or trend slides, the source data lives in the `financial-ops` project (Postgres-backed, served at `http://44.194.218.109:8000`). **Staging VPN required.** Verify with `curl -s --max-time 5 http://44.194.218.109:8000/health` before spawning the agent — if it fails, ask the user to bring up the VPN.

**Spawn a read-only general-purpose agent** with these guardrails:

1. Working directory = `/Users/henrik/Library/CloudStorage/Dropbox/Workspace/financial-ops`
2. **Read-only in financial-ops** — no Edit, no Write, no git commits, no installing packages. The agent can use Bash for `curl`/`cat`/`grep` only.
3. **Only writes** to `<meeting folder>/financials-data/` (give it the absolute path).
4. Have it read `financial-ops/README.md`, `CLAUDE.md`, `START-HERE.md` and existing scripts to discover API endpoints.

The agent typically produces:
- `q1-budget-vs-actual.json` — Q1 P&L vs budget per line item
- `april-kpis.json` — monthly pulse KPIs
- `april-breakeven.json` — breakeven & cashflow assessment
- `13-month-trends.json` — series data for charts

Schema for each is in `examples/financial-data-shapes.md` (in this skill folder, or see the working example at `Board meetings/2026/2026 05 21 Board meeting (7)/financials-data/`).

**Cross-repo discipline**: Henrik's user-level CLAUDE.md normally prohibits spawning agents into sibling projects, but he has explicitly authorized this for read-only data extraction in board deck work. Stay within those bounds.

---

## Lessons learned (DO READ)

These are hard-earned constraints from working with Henrik. Violating them produces noticeable friction.

### 1. NEVER pre-fill slide content from synthesis

See `~/.claude/projects/-Users-henrik-Library-CloudStorage-Dropbox-Sonetel-Board/memory/feedback_no_ai_synthesised_content.md` for the canonical version. Short form:

- Scaffold the structure (template, pipeline, agenda shape, slide types, empty data slots). Stop there.
- Do **not** write slide bullets by paraphrasing Voice Lake summaries, Q1 Kvartalsredogörelse vd-ordet, prior reports, or memory. Even when those sources look authoritative.
- Numbers from prior reports only land on slides if Henrik explicitly tells you to put them there.
- The board deck speaks in Henrik's voice. It cannot be ghost-written.
- After scaffolding, render an empty deck, show it, and ask what content goes on each slide.

### 2. Keep agendas brief

Henrik's stated preference: 5–8 agenda items max. Avoid procedural padding ("Decisions & resolutions", "Any other business", "Closing") unless he explicitly asks for them. He removed all three of those from the meeting #7 agenda after I added them by default.

The cover, agenda slide, section dividers, and closing slide are auto-generated. The "Closing" agenda item is separate from the auto-generated closing slide — don't conflate them.

### 2a. Minutes are signed digitally via eAvtal — not at meetings

Sonetel uses **eAvtal** (`pro.egreement.com`) for digital signing of board minutes and other documents. Minutes are NOT signed at meetings.

For the Opening & formalities slide, the "previous minutes status" framing should be:
- **Signed** — minutes finalised in eAvtal (e.g. local copies in `<meeting>/Protokoll/Påskrivet/` or `<meeting>/Minutes/Signed/`)
- **Out for signing** — currently pending in eAvtal
- **Drafted** — minutes drafted (`ver 1.md/pdf`) but not yet sent for signing

To check signing status of a given meeting:
- Local: check `<meeting>/Protokoll/Påskrivet/` or `<meeting>/Minutes/Signed/` for a signed PDF
- Authoritative: the eAvtal dashboard at `pro.egreement.com/#/dashboard` (only the user can verify this; ask if status is unclear)

NEVER write "to sign at this meeting" or similar — that's an in-person signing assumption that doesn't apply here.

### 3. CSS Grid is unreliable in WeasyPrint

`grid-template-rows: repeat(N, 1fr)` combined with `grid-auto-flow: column` produced uneven row heights and inconsistent text wrapping. Use flex columns instead. See the `.numbered-cols` / `.numbered-col` pattern in `style.css`.

### 4. Agenda density vs content density

The agenda slide uses a font scale one step below content slides (`headline-xl` 28pt title vs `headline-2xl` 34pt; `body-md` 14pt rows vs `body-lg` 16pt bullets). This is intentional — an information-dense reference slide reasonably sits below content slides in the type scale (typography-system.md generative rule #1).

### 5. Design system alignment

Decks use the Sonetel Design System tokens from `~/Library/CloudStorage/Dropbox/Workspace/Sonetel design system/libraries/tokens/tokens.css`:

- Font: **Inter** (variable) — never Gotham SSm
- Grayscale-dominant palette; primary action / surface = near-black `#0a0a0a`
- Status colors only for semantic meaning (red=critical, green=success, pink=warn)
- No colored backgrounds for *narrative* content slides (exception: cover and closing may use `solid-8`)
- Three text tiers only: primary / secondary / tertiary

Inter variable font is loaded from `~/Library/Fonts/Inter-VAR.ttf` (download if missing — see Bootstrapping above).

### 5a. Finops Monthly Pulse palette (financial slides only)

KPI grid + breakeven slides intentionally adopt the styling of the Finops Monthly Pulse page at `http://44.194.218.109:8000/analytics/pulse` (teal cards, ✓ marks, amber "behind" text). This breaks rule 5's "no colored backgrounds" — but only on the financial slides, and only because the board recognises the Finops look. Don't extend this palette to narrative slides.

The palette tokens live at the top of `style.css`:
```css
:root {
  --finops-teal-dark:  #3D7B81;  /* top KPI row + ✓ box border */
  --finops-teal-light: #7BC4C4;  /* bottom KPI row */
  --finops-amber:      #E1A04E;  /* "behind budget" deltas on dark teal */
  --finops-greenfill:  #DCEAD9;  /* breakeven box fill */
  --finops-greenink:   #1E6A2D;  /* breakeven text + ✓ */
}
```

On `kpi_grid`, the renderer alternates `.kpi-row-dark` / `.kpi-row-light` so row 1 is dark teal and row 2 is light teal. Budget-delta lines that indicate "behind" use `.budget-behind` (amber on dark, deeper amber on light).

### 6. Jinja attribute gotcha

`s.items` in Jinja resolves to `dict.items` method, not the `items` key. Use a different field name in slide dicts. (Why the agenda slide uses `agenda_items` rather than `items`.)

### 7. WeasyPrint env requirement

WeasyPrint can't find Homebrew's libgobject without `DYLD_LIBRARY_PATH=/opt/homebrew/lib`. `render.py` sets it via `os.environ.setdefault`, but on macOS dyld reads the env before Python starts — so the env var must be set in the shell:
```
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 slides/render.py
```

### 8. KPI grid sizing — fixed row height + trimmed header (v0.26)

Three pitfalls hit me in succession on the KPI slide:
1. **`flex: 1` on rows** → cards expand to bottom edge of page, no whitespace.
2. **Fixed row too small (38mm) + 36pt value font + 6mm padding** → card content (label + 28pt value + 3 lines) is ~31mm, overflows 38mm-padding=22mm content area, bottom row visually overlaps the top row.
3. **Default slide header consumes ~32mm** → leaves only ~93mm for KPI block but the block needs ~100mm.

**Working recipe** (meeting #7, v0.26):
```css
.slide-kpi .slide-header { margin-bottom: 4mm; }
.slide-kpi .slide-title { margin-bottom: 2mm; font-size: var(--fs-headline-xl); }
.slide-kpi .slide-subtitle { margin-bottom: 0; }
.kpi-rows {
  display: flex; flex-direction: column;
  gap: 4mm;
  margin-top: 3mm;
  margin-bottom: 10mm;       /* visible breathing room */
}
.kpi-row {
  display: flex;
  gap: 4mm;
  height: 42mm;              /* fixed — not flex */
}
.kpi-card {
  padding: 4mm 6mm;          /* was 6mm 7mm */
  overflow: hidden;          /* clip rather than overlap if content grows */
  /* ... */
}
.kpi-value { font-size: 28pt; /* was 36pt */ }
.kpi-line  { font-size: 9pt;  line-height: 1.25; /* was 9.5pt / 1.3 */ }
```
Total: 30 (slimmed header) + 2*42 (rows) + 4 (gap) + 3 (top margin) + 10 (bottom margin) = 131mm. That exceeds the ~125mm content area by ~6mm — `overflow: hidden` on the cards absorbs the slight bleed without visible clipping. Tighter margins (or fewer KPIs) get you under 125mm exactly if you need it.

**Apply the slim-header pattern (`.slide-kpi`, `.slide-cash`) to any financial slide where header chrome is eating chart real estate.** Default header is fine for slides with bullet lists; financial slides need it tightened.

### 9. Chart sizing — `bbox_inches="tight"` IS the right answer (revised v0.26)

Original take in v0.25 was wrong. `bbox_inches="tight"` is actually what you want — it trims the saved PNG to the chart's *visible* bounding box (axes + tick labels), eliminating matplotlib's whitespace padding. Combined with simple CSS `width: 100%; height: auto`, the chart fills the card naturally.

The earlier "charts look small" symptom was caused by `object-fit: contain` + `flex: 1 1 auto` letterboxing the image inside an oversized flex container — *not* by `bbox_inches`.

**Working recipe** (meeting #7, v0.26):
```python
figsize = series.figsize or (5.0, 3.2)   # ratio shapes label-to-bar proportions, not display size
fig, ax = plt.subplots(figsize=figsize, dpi=200)
fig.tight_layout(pad=0.3)
fig.savefig(out_path, facecolor=FINOPS_CARD_BG, dpi=dpi,
            bbox_inches="tight", pad_inches=0.08)
```
And in CSS (the simpler the better):
```css
.trend-card img {
  width: 100%;
  height: auto;
  display: block;
}
```
**Do NOT** use `object-fit: contain` or `flex: 1 1 auto` on chart images — they letterbox the chart inside oversized containers and Henrik will (correctly) say "graphs are super small."

For the cash position slide use `figsize: [5.5, 3.2]` (set in `expand_data_refs` for `cash_position` type) — slightly wider since the chart sits next to a drivers panel rather than alongside other charts.

### 10. Sources belong in the footnote

When a financial slide presents derived numbers, the footnote must name the source datasets explicitly. Format: `"Sources — Actuals: <source>. Budget: <source>. <Any mapping/caveats>."` This is Henrik's preference — the board reads footnotes precisely to know whether figures are KR-published vs. internal Finops.

For the Q1 P&L slide, the canonical phrasing is:
```
Sources — Actuals: Kvartalsredogörelse Q1 2026, koncernen (resultaträkning).
Budget: Finops group_pl_budget FY 2026 (Jan–Mar). <mapping notes>.
```

### 11. Merge P&L lines where budget mapping is imperfect

The Finops parent-company budget structure (sweden_team, india_support, external_services, marketing, india_rd) does not map cleanly to the consolidated KR labels (Personalkostnader, Övriga externa kostnader). Showing both separate rows with the "best-fit" mapping is correct-but-confusing on a slide.

**The merge pattern** (meeting #7, v0.25): Combine `Personalkostnader` + `Övriga externa kostnader` into a single row labelled **Personal- och övriga rörelsekostnader**. Sum actuals (-2 479 308 + -899 931 = -3 379 239) and budgets (-1 673 638 + -1 335 087 = -3 008 725), recompute variance, document the merge in the footnote. This avoids the "−48% / +33%" pair that looks alarming but is largely a mapping artefact.

Apply this any time a single statutory P&L row corresponds to multiple Finops budget categories — *or* vice versa. Footnote must explain the merge.

### 12. Cash position slide pattern

When cash is negative or trending negative, the cash position slide pairs a 6-month EOM trend chart with a "drivers outside monthly run-rate" panel. This is Henrik's standing structure for the financial section.

Data shape: `financials-data/cash-position.json` (see `examples/cash-position-example.json`). Fields:
- `trend: [{month, value}]` — 6 months EOM SEK
- `april_drivers: [{label, amount_sek, note}]` — quarterly/annual obligations that *fired in the last month* and explain deviation from monthly run-rate
- Optional `april_change_msek` — total monthly delta for context

The Finops agent identifies drivers by querying `recurring_payment` for items with `annual_month` or `quarter_months` matching the target month, then validates against the cash-flow forecast `top_cost_items`. Bank-transaction-level reconciliation is preferred when the CSV import is available; recurring-payment metadata is the fallback.

**Driver classification rule**: A driver is included on the slide only if it is *outside the recurring monthly cost base* — i.e. a one-off cost, a quarterly recurring (Q1/Q4/Q7/Q10 typical for VAT, Certified Advisor fees), or an annual recurring (audit fees, AGM ads). If the last month is negative primarily due to *declining revenue*, list that as the first driver and note it as such.

Slide entry in `data.json`:
```json
{
  "type": "cash_position",
  "title": "Cash position — End of month",
  "subtitle": "Nov 2025 – Apr 2026, SEK",
  "data_ref": "financials-data/cash-position.json",
  "drivers_title": "April outflows outside monthly run-rate"
}
```
The chart uses a baseline at 0 so positive and negative regions shade differently; the renderer auto-formats Y-axis in `thousands_sek` (`-756K` etc.).

**Layout** (the cash slide is two-column: ~58% chart, ~42% drivers panel). Use the slim-header pattern (`.slide-cash`) and constrain the drivers card with `padding: 4mm 5mm`, font-size 10pt for label/amount, 8.5pt for note. Otherwise the panel content (3 drivers × 3 lines each ≈ 65mm) doesn't fit alongside the chart and visually breaks out of the layout. Set `align-items: flex-start` on `.cash-grid` so the panel doesn't stretch to match the chart card height.

### 13. Don't re-render needlessly during sub-second iterations

Render is `~3s` for a full deck — fine, but during a rapid edit loop (e.g. CSS tweaks), batch 3-5 changes before re-rendering and `open`. Henrik reviews each rendered PDF; bouncing the PDF reader 20 times in a minute is annoying.

---

## Quality control discipline (REQUIRED for financial slides)

Established 2026-05-14 after a session where multiple regressions slipped through (chart sizing, KPI overlap, cash slide layout) and the skill itself drifted from the actual code. The board deck has zero room for incorrect numbers — these end up in front of the board and, downstream, in published materials. Same standard as `kvartalsredogörelse` and `sonetel-bokslut`.

### When QC applies

Any of the following triggers a QC cycle:
- Adding a new financial slide (P&L, KPI, breakeven, cash position, cash flow forecast, etc.)
- Updating a number, percentage, label, or footnote on an existing financial slide
- Editing `data.json` slide values that derive from `financials-data/*.json`
- Adding a new slide type to the renderer
- Material edits to `SKILL.md`, `render.py`, or `style.css` (anything beyond a typo/comment)

QC does NOT apply to: narrative bullet content Henrik dictates verbatim, design tweaks that don't touch numbers, agenda text edits.

### The two-agent verification pattern

For each QC trigger, spawn **two independent agents in parallel**. Each must return a confidence score (1–10) and a findings list.

**Pass criteria**: BOTH agents return confidence ≥8/10 with no critical discrepancies.

**Three-cycle limit**: If after 3 review/fix cycles either agent still scores <8, **escalate to Henrik with the open findings**. Do not silently accept lower confidence.

**Spawn pattern** (parallel, single message, two `Agent` tool calls):

1. **Source-verification agent** (general-purpose, read-only)
   - Verify every number on the slide against its underlying data file
   - For P&L actuals: trace to the Kvartalsredogörelse `tables.resultatrakning_koncern.rows[].values[0]` and (where derived) re-compute
   - For Finops-sourced budgets/KPIs/cash: trace to `financials-data/*.json` and the Finops API endpoints documented there
   - Verify variance calculations, signs, units, formatting
   - Cross-slide consistency (e.g. April month on KPI grid == April endpoint on trends chart)

2. **Skill-conformance / quality agent** (general-purpose, read-only)
   - Review the slide(s) against SKILL.md rules (slide types, lessons learned §1–§13, design system)
   - Check code-vs-doc drift: are the code snippets in SKILL.md still accurate?
   - Check that any new lesson learned in this session has been *written back* to SKILL.md (rule §14 below)
   - Flag presentation issues: overlapping cards, charts that letterbox, header chrome eating real estate, footnotes that drift to a second page

Each agent's prompt MUST include: working directory, the exact files to inspect, the source data paths, the output format (confidence score + findings + recommendations), and "read-only — do NOT modify any files."

**Disagreement handling**: If the two agents disagree (one passes, one fails), trust the failing one and fix. Two-of-two is the bar.

### Workflow

```
1. Make the change (code/content edit + render).
2. Spawn both QC agents in parallel.
3. Read findings.
4. If BOTH score ≥8 with no critical issues → ship and move on.
5. Else fix the flagged items, re-render.
6. Goto 2. Max 3 cycles. After cycle 3, escalate to Henrik with the open list.
```

### What to write in the agent prompts

Each prompt must be self-contained (the agent has no conversation context). At minimum:
- One-sentence statement of what you changed and what you want verified.
- Working directory.
- Exact files to read (slide template, data file, source file, financials-data sub-files).
- The verification checklist (numbers, math, cross-references, formatting).
- The output template: `## Confidence score: N/10` then `## Critical findings` then `## Recommended fixes`.
- "Read-only — do not modify files."

Bad prompt: "Audit this slide."  
Good prompt: "Verify the P&L slide actuals in `slides/data.json` items[2][0].pnl_rows against `tables.resultatrakning_koncern.rows[].values[0]` in `<KR-data-path>`, and the budget values against `financials-data/q1-budget-vs-actual.json`. Recompute Bruttoresultat and EBITDA from primaries. Recompute variance_pct. Report any mismatch with file:line refs. Format: ..."

### Why this discipline

- Single-agent (just me) review has known failure modes: I write the slide, *then* I review my own work. The errors I miss are the ones I'm biased toward.
- Two independent agents with explicit confidence floors catches the systemic mistakes (rounding, sign errors, source drift, stale references).
- The 3-cycle limit prevents infinite loops on issues that need human judgement (e.g. "is the budget mapping reasonable?").

### The 3-failure rule for diagnostic problems

QC catches *correctness* failures. The 3-failure rule catches *diagnostic* failures — when I've attempted to solve the same visual/layout/rendering problem three times and the user is still seeing it.

**Trigger**: Three failed attempts at the same defect (chart sizing, layout overlap, content overflow, color drift, etc.) in a single session. "Failed" means the user re-reported the same symptom after a render.

**Action**: STOP trying to fix it directly. Spawn **two independent diagnostic agents in parallel**, each with a different investigative angle. Examples of complementary angles:

- "Inspect the saved chart PNG dimensions and matplotlib pipeline" + "Inspect the rendered HTML and CSS computed dimensions"
- "Trace the data flow through expand_data_refs" + "Trace the data flow through the Jinja template"
- "Check the source file integrity" + "Check the renderer's transformation logic"

Each agent must produce: `## Root cause`, `## Evidence`, `## Proposed fix` (with file:line refs), `## Confidence: N/10`.

**Why**: After three attempts I have a wrong mental model of the problem. Trying the same thing harder produces the same wrong answer. Two independent agents with different starting hypotheses break my framing.

**Hard-learned** (2026-05-14, meeting-7 trends chart): I tried `object-fit: contain`, then `bbox_inches="tight"`, then changing figsize — none of which addressed the actual root cause (which an agent would later identify). Each fix attempt cost a render cycle and a screenshot from Henrik. The rule exists to prevent that pattern.

**After the agents return**: Treat their findings the same as QC findings — apply the fix, then run the standard QC verification cycle.

### 15. Cash flow forecast slide pattern

Companion to the cash-position slide. Where `cash_position` looks *backwards* (6 months EOM, with drivers explaining the last month), `cash_flow_forecast` looks *forward* (~90 days of daily balance projection, with top 5 items that will materially move the line). Both should appear when cash is tight or trending negative.

**Data source**: `financials-data/cash-flow-forecast.json`, produced by the Finops agent via `POST /api/v1/cash-flow/forecast` (the same endpoint that backs the `/analytics/cash-flow` UI). The slide chart is intentionally a near-match to the "Daily Cash Balance Projection" chart in that UI so the board recognises it.

**Top-5 items rule**: items that move the forecast line materially, EXCLUDING normal monthly recurring costs (salaries, monthly SaaS, monthly rent). Include:
1. The revenue assumption itself (with rationale — why this number? typically the manual override stored in `business_parameters.cashflow_revenue_override_msek`).
2. Quarterly obligations firing in the window (EU VAT Q2/Q3, Certified Advisor fees).
3. Annual obligations (audit a-conto, AGM ads).
4. Known one-off planned costs (loan repayments, expense reimbursements, planned investments).
5. Any DELAYED payment that has rolled forward into the window (these are usually the most explanatory of forecast shape).

**Chart specifics**:
- Render via `render_cashflow_forecast_chart()` in `render.py` (not `render_chart()`).
- Blue line `#2563EB`, 2.2pt; open-circle markers (white fill, blue stroke).
- Reference dashed lines: 0 kr (green `#1F9D55`), warning (`warning_line_sek`, amber `#E1A04E`), credit line (`credit_line_sek`, red `#D9534F`).
- Vertical dashed line at `actuals_through_date` (gray) — separates solid actuals from forecast.
- Red dot annotation at `(minimum_projected_date, minimum_projected_balance_sek)`.
- Right-side labels for reference lines (color-matched).
- Date ticks at week intervals, format `%m-%d`.

**Slide entry**:
```json
{
  "type": "cash_flow_forecast",
  "title": "Cash flow forecast — Daily projection",
  "subtitle": "14 May – 12 Aug 2026 (90 days)",
  "data_ref": "financials-data/cash-flow-forecast.json"
}
```

**Summary line** rendered above the chart: `Assumed revenue X.X MSEK/month (Y,YYY SEK/day) · Actuals through YYYY-MM-DD · Min projected −ZZZK SEK on YYYY-MM-DD`.

**Items grid** rendered below: 5 equal-width cards. First card is the revenue assumption (no date, kind=`assumption`); other 4 are dated outflows with sign (`−` red, `+` green) and kind (`quarterly`/`annual`/`one_off`).

**Caveat capture**: the Finops agent reports caveats in `_metadata.gaps` (bank CSV import status, briefing-vs-current min-balance discrepancy if applicable). Surface in the slide footnote when material.

### 16. WeasyPrint flex + `<img width:100%>` does not stretch — use `display: block` or explicit `mm` width

**Symptom**: Images placed inside a `display: flex; flex-direction: column` (or inside flex/grid items) sometimes render at their PNG's intrinsic size, ignoring `width: 100%; height: auto` on the `<img>`. The image appears as a small box in the top-left of an otherwise-empty card.

**Why**: WeasyPrint's flex implementation has incomplete cross-axis stretching for replaced elements (images). The `align-self: stretch` default doesn't reliably apply to `<img>` in column flex containers.

**Two working fixes (in order of preference)**:
1. **Don't put images directly inside flex containers**. Use `display: block` on the card wrapper, then `<img>` with `width: 100%; height: auto` stretches correctly.
2. **If the parent must be flex/grid**, set an explicit physical width on the image in mm: `width: 71mm; height: auto`. Compute the value from `(slide_inner_width − padding − gaps) / columns − card_padding`.

**Hard-learned** (2026-05-14, meeting #7 trends slide): three rounds of CSS tweaks (`object-fit`, `max-width`, `align-self: stretch`) all failed before switching `.trend-card` from `display: flex` to `display: block` + explicit `width: 71mm` on the `<img>`. Three cycles spent before the 3-failure rule triggered the right diagnosis.

**Apply to**: any card-style slide that wraps a single chart image (trends-grid, cash-chart-card, cashflow-chart-card). Don't use `display: flex` on the wrapper unless you have a second child that must align.

### 17. WeasyPrint also breaks: `-webkit-line-clamp` and `table-layout: fixed` with `width: 1%`

Two more WeasyPrint traps from the meeting #7 cash-position drivers panel. Both manifest as content overlapping or overflowing siblings.

**Trap A — `-webkit-line-clamp` on a note element**: silently fails. WeasyPrint paints the clamped element's text but does not reserve the height the wrapped lines occupy. Subsequent siblings (next driver row, next paragraph) paint *on top of* the wrapped text. Visually: bottom of one note overlaps top of next row.

→ **Fix**: never use `-webkit-line-clamp`/`display: -webkit-box` in this pipeline. If clamping a note, trim the source text or use `max-height` + `overflow: hidden` (which clamps cleanly at row boundary even if not at line boundary).

**Trap B — `<table>` with `table-layout: fixed` + `width: 1%` shrink-to-fit on an `nowrap` column**: `fixed` layout computes column widths from the first row's declared widths and then never adjusts. `width: 1%` resolves to ~1% of the table's total width (~3mm at typical card widths). The `white-space: nowrap` cell then *overflows the column horizontally* and the rendered text exits the card border on the right.

→ **Fix**: use `table-layout: auto` (the default) when one column is `nowrap` and shrink-to-fit. `width: 1%` is still a valid hint with auto layout — it tells the renderer to make the column as narrow as possible while fitting content.

**Pattern that does work** for label-left, amount-right rows with a multi-line note below (the meeting #7 cash drivers layout):

```html
<table class="cash-drivers-table">
  <tbody class="cash-driver">
    <tr><td class="label">Skatteverket MOSS/OSS Q1 EU VAT</td>
        <td class="amount negative">−206 000 SEK</td></tr>
    <tr><td class="note" colspan="2">Quarterly EU VAT payment …</td></tr>
  </tbody>
  <!-- repeat tbody per driver -->
</table>
```

```css
.cash-drivers-table { width: 100%; border-collapse: collapse; /* no table-layout */ }
.amount { white-space: nowrap; text-align: right; width: 1%; }
```

Tables (unlike flex) reliably compute row height from cell content in WeasyPrint. Use them for any list-of-rows layout where each row may have wrapping text plus a fixed-format amount.

**Hard-learned** (2026-05-14, meeting #7 cash drivers panel): three rounds of CSS tweaks (padding, alignment, line-clamp) all failed. Spawned two diagnostic agents per §15's 3-failure rule; both converged on the same root causes (clamp not supported, fixed-layout shrink-to-fit broken). The agents' table-based replacement worked on the next render.

### 18. Forecast assumptions must carry a rationale comparing to recent actuals

Any slide that asserts a forecast assumption (revenue/month, growth rate, churn, COGS %) **must** include a visible rationale that compares the assumed number to recent actuals. The board can't evaluate the forecast without seeing whether the assumption is anchored, optimistic, or aggressive.

**Required for every assumption shown on a slide**:
- Most recent month's actual.
- 3- and/or 6-month trailing average.
- An explicit verdict: "matches recent month", "+X% vs run-rate", "below recent avg by Y%", or similar.

**Where it renders**: a `cashflow-rationale` block immediately below the cashflow summary line (subtle grey background, left border, ~8.5pt text). Source: `cash-flow-forecast.json` → `revenue_assumption_rationale` (top-level string). Renderer passes it through `cashflow_summary.revenue_assumption_rationale`; template renders it conditionally.

**Failure mode if missing**: the board sees "Assumed revenue 2.6 MSEK/month" with no anchor. They can't tell if that's conservative, realistic, or wishful. Henrik flagged this explicitly during meeting #7 prep — *"comment on why this is a reasonable assumption — or notify me if it isn't — by looking at recent month sales"*.

**Implementation rule**: when populating `cash-flow-forecast.json` (whether via Finops agent or manually), the rationale field is **mandatory**, not optional. If the assumption differs from the 6-month trailing average by >10%, the rationale must explicitly justify the divergence (one-off effect, deliberate stretch, etc.). When in doubt, recompute the comparison from `financials-data/13-month-trends.json` (`series.net_revenue_sek`) before drafting the rationale.

**Hard-learned** (2026-05-14, meeting #7 cash flow forecast slide): the rationale field existed in the JSON but wasn't surfaced on the slide. The board would have seen the assumption without the comparison. Henrik caught it before distribution.

**Format rules for the rendered rationale** (board-facing, every word counts):
- **One line, ≤140 chars** preferred. Two lines max. Anything longer pushes the chart off-page and dilutes the signal.
- **Numbers and verdict only**: "Apr 2026 actual 2.61 MSEK · 6-mo avg 2.51 MSEK · Matches recent month (+3.5% vs run-rate)." — that's the template.
- **No internal references in board-facing copy**: do NOT cite CR numbers (`CR-2026-04-06`), Jira tickets, commit SHAs, business_parameters keys, model names, or process artefacts. Those belong in the JSON `note` field (which is *not* rendered to the board) or in the meeting CHANGELOG, not on the slide. The board reads "Override CR-2026-04-06" as clutter — they don't have the CR archive, the reference is meaningless to them, and it signals process-talk instead of substance.
- **What to include**: most recent actual, trailing average, magnitude of deviation, qualitative verdict (matches / above / below run-rate). Nothing else.
- **What to exclude**: methodology footnotes (effective COGS %, modelling decisions), provenance (which model output we bypassed), authorship (who approved the override).

**Hard-learned** (2026-05-14, meeting #7 v0.42 → v0.43): first cut of the rationale included "Override CR-2026-04-06." Henrik: *"Don't refer to CRs. That is just clutter for the board."* Rule generalised: board-facing copy contains numbers + verdict, never internal-process references.

### 19. Label every date and dimension precisely — "Actuals" alone is ambiguous

Any date qualifier on a financial slide must name the **dimension** the date governs. A bare "Actuals through 2026-05-12" looks complete but is dangerously ambiguous on a cash flow forecast: the chart mixes revenue (extrapolated by assumption past that date), recurring costs (calendar-driven, no actuals cutoff), and bank balance (which may have its own freshness). The board reads "actuals" → "everything before this date is real" → wrong.

**Rule**: prefix every date qualifier with the dimension it bounds. "Revenue actuals through {date}", "Bank actuals through {date}", "Cost actuals through {date}". Never use bare "Actuals through {date}".

**Apply to**: cash flow forecast summary, cash position summary, any slide that mixes actuals and projections.

**Hard-learned** (2026-05-14, meeting #7 v0.42 → v0.43): the cashflow summary line read "Actuals through 2026-05-12". Henrik: *"that's actual revenue, not costs or actual cashflow."* The label was technically correct (the `actuals_through_date` field tracks revenue) but read on the slide as a sweeping claim. Renamed to "Revenue actuals through".

### 20. Board-facing text is minimum-viable: never duplicate what the chart shows, never include low-signal precision

Every word on a board slide must earn its place. The default is *less*, not *more*. Three failure modes that produce clutter:

1. **Duplicating chart-visible information in text**. If the chart's x-axis shows "04-28 to 08-11" already, do not write "14 May – 12 Aug 2026 (90 days)" in a subtitle. If the chart has a visible dip with a labelled date, do not write "Min projected −814 399 SEK on 2026-05-28" in the summary line. The board reads the chart; the text is for what the chart *cannot* show (the assumption, the rationale, the dimension cutoff).
2. **Redundant unit conversions**. If you state "2.6 MSEK/month", you do not also need "(86 667 SEK/day)". Pick the unit the board thinks in and drop the conversion — it's calculator clutter, not insight.
3. **Process precision the board cannot act on**. "−814 399 SEK" implies the board should react to 1 SEK precision. They won't. The chart's red dot at the trough conveys "we dip below −800K once" — that's the takeaway. Reserve precise figures for the items list (where the magnitude matters per line) and let the chart carry the trajectory.

**Rule for any chart-anchored summary line**:
- Include: the *assumption* (what isn't visible in the chart), the *dimension cutoff* (revenue actuals through {date} — see §19), and any *one-line context* the chart cannot show.
- Exclude: date ranges visible on x-axis, min/max values visible as chart extrema, unit conversions, fiscal-period boilerplate.

**Apply to**: every slide that pairs text with a chart — cashflow forecast summary, cash position summary, trends-grid subtitle, KPI snapshot eyebrows. Before shipping, read each sentence and ask: "if I deleted this, would the board lose something they couldn't get from the chart?" If no, delete it.

**Hard-learned** (2026-05-14, meeting #7 v0.43 → v0.44): the cashflow summary read *"Assumed revenue 2.6 MSEK/month (86 667 SEK/day) · Revenue actuals through 2026-05-12 · Min projected −814 399 SEK on 2026-05-28"* plus a subtitle *"14 May – 12 Aug 2026 (90 days)"*. Henrik flagged all three: SEK/day adds nothing, the date range is in the chart, the min is the chart's visible dip. Cut to *"Assumed revenue 2.6 MSEK/month · Revenue actuals through 2026-05-12"*.

**Sub-rule: footnotes on financial slides must be one line, ≤150 chars.** Board readers do not read four-line footnotes. They read the chart, the headline number, and the eyebrow. If the footnote runs to a paragraph, it is invisible — which is worse than not having it, because you *think* the caveat is communicated.

What belongs in a footnote (in priority order):
1. **Source** — one short clause: "Actuals: KR Q1 2026. Budget: Finops FY26."
2. **One critical caveat that changes how a number reads** — typically the budget-vs-actual mapping mismatch that explains why a delta looks worse than it is.

What does *not* belong in a footnote on a board slide:
- Account numbers (BAS 7960, 49902-2, etc.) — even if Henrik asks "why is this number what it is", the answer goes in the *speaker notes* (`content/<topic>-input.md`), not on the slide.
- Reconciliation paths between data sources — internal.
- Process boilerplate ("based on consolidated figures").
- Items that are "immaterial and omitted" — if they're immaterial, the omission itself is immaterial.
- Multiple caveats — pick the one that matters most; everything else moves to speaker notes.
- Inline FX/methodology explanations — surface those *in the row label itself* (e.g. "Övriga rörelsekostnader (net FX loss)") so the caveat is at the data, not in a paragraph below.

**Rule of thumb**: if you can read the entire footnote aloud in under 6 seconds, it's the right length. Anything longer → cut it, or move it to speaker notes.

**Sub-rule: name actual products / plans / features, not abstractions.** Board copy must reference real, recognisable names — "Business plan" not "current tier", "Recording & summaries" not "Core", "Meeting bot" not "+Bot". When a tier doesn't exist yet, say so explicitly ("new ~$90 tier") so the board knows what they're being asked to greenlight vs what already exists. Generic labels save characters but force the board to translate; that translation cost is paid mid-meeting in confusion, not before.

**Sub-rule: always show units.** Per-user cost numbers must read as "$9.6/user/month" or include "/month" inline somewhere on the line. Never assume the board will infer monthly vs annual vs one-time. A number without a unit on a board slide is a defect.

**Hard-learned** (2026-05-14, meeting #7 v0.56 → v0.57): the Voice Lake cost bullet read *"Core $9.6 · +Bot +$0.7 · +Stories +$17 (~$70 tier) · +Email +$9.5 ($90 tier)"*. Henrik flagged three problems: (a) "Core" was opaque — rename to "Recording & summaries"; (b) no unit — add "/month"; (c) the "~$70 tier" was a fabrication — the company has Business plan + a *proposed* ~$90 tier, no $70 tier. Rewritten to: *"Per-user cost/month (production data): Recording & summaries $9.6 + Bot $0.7 fit Business plan · +Stories $17 + Email $9.5 need new ~$90 tier."* The three sub-rules above were generalised from this.

**Hard-learned** (2026-05-14, meeting #7 v0.46 → v0.47): the Q1 P&L footnote ran 617 characters across 3 wrapped lines — sources + Personal/övriga merge breakdown + capitalised India R&D caveat + Övriga rörelsekostnader FX explanation + "immaterial omitted" line. Henrik: *"Can the footnote be shorter. The board will never read if it has too much text."* Cut to 108 chars: *"Actuals: KR Q1 2026. Budget: Finops FY26 (excludes ~1.8 MSEK capitalised India R&D in Personal- och övriga)."* The FX explanation moved to the row label inline; the immaterial line removed; the account numbers and merge breakdown moved to `content/financials-input.md`.

### 21. WeasyPrint silently clips overflowing `<li>` bullets — no warning, no page-break

`.slide` has `height: 167mm; overflow: hidden` (it has to be exactly 167mm tall — that's the @page size). When a `bullets` slide's content exceeds the inner content area, WeasyPrint does **not** split to a second page, does **not** emit a warning, and does **not** render an ellipsis. It simply drops the overflowing `<li>` from the rendered PDF. The bullet is in `data.json`, the bullet is in the generated HTML, but it doesn't appear in the PDF and `pdf.extract_text()` confirms it isn't there.

**Symptom** the first time it bit: bullets array length 4 in data.json → only 3 bullets visible in the rendered PDF; page count unchanged. Looks identical to a working slide unless you count.

**Why it happens**: `page-break-inside: avoid` on `.slide` + `overflow: hidden` + a fixed-height container = no escape valve. WeasyPrint clips and moves on.

**The math** for `bullets`-type slides (default styling):
- Slide inner content area = 167 − 20 − 22 = **125 mm**.
- Header (eyebrow + margin) ≈ 15 mm; title (headline-2xl + margin) ≈ 20 mm; subtitle (if any) ≈ 8 mm.
- Available for `<ul class="slide-bullets">` = **~84 mm**.
- Per bullet at `font-size: var(--fs-body-lg)` (16pt, line-height 1.5): each line of content ≈ **8.5 mm**, plus `margin-bottom: 5mm`. So a single-line bullet ≈ 13 mm; a 2-line wrapped bullet ≈ 22 mm.
- **Budget**: ~6 one-line bullets, OR ~4 two-line bullets, OR ~3 two-line bullets if one of them is denser. Past that, the last bullet(s) get silently dropped.

**Mitigations (in priority order)**:
1. **Count and budget before rendering**. If you have 4 bullets and any of them is likely to wrap, expect overflow. Merge bullets 1+2 (or rewrite to fit on one line) rather than hoping it'll fit.
2. **Verify after each render**: `pdf.extract_text()` on the slide page and count the bullet count vs `data.json`. If they differ, you're being clipped.
3. **Never trust `len(pdf.pages)`** as proof a slide rendered correctly. Clip happens silently *within* a page.
4. If a slide genuinely needs more density: use the `two_column` slide type, or split into two slides.

**Hard-learned** (2026-05-14, meeting #7 v0.52 → v0.56): added a 4-bullet Voice Lake slide that included a critical cost-ladder bullet. v0.52 rendered to 19 pages — looked fine. The cost bullet was silently dropped. Henrik noticed: *"Not seeing the extra pages with cost data."* `extract_text()` of page 14 confirmed only 3 of 4 bullets in the PDF; data.json had 4. Spent four render cycles (v0.52 → v0.56) before merging bullets 1+2 freed enough vertical space for the cost bullet to render. **Always count bullets in the rendered PDF after a content edit.**

### 22. IR calendar slide — pull from the external comms repo

The board increasingly wants an at-a-glance view of upcoming regulatory disclosures, flagship product launches, quiet periods, and other communications milestones. The canonical source for that calendar lives in a sibling project: **`~/Library/CloudStorage/Dropbox/Workspace/Sonetel external communications`**.

That repo maintains `ir_calendar.json` at the **repo root** (not in a `data/` subfolder — easy to miss) — a structured event list (typed activities: `disclosure`, `content`, `event`, `ops`, `decision`, `blackout`, `subscription-renewal`, etc.; each with `start_date`, `end_date`, `title`, `tags`, `mar_sensitivity`, `audience`, `links`, `status`, `confidence`, and more). It also renders its own A4 portrait one-pager HTML (`01_strategy/publishing_schedule_2026_summary.html` SV and `_summary_en.html` EN, both regenerated from the same JSON). The deck does **not** embed that HTML — it has the wrong orientation/aspect for 16:9 landscape. Instead, the deck **reads the JSON directly** and renders its own 16:9 slide via the `ir_calendar` slide type.

**Critical**: the canonical JSON's schema includes `title` (the internal working name, e.g. *"Voice Lake commercial launch + new priced tier — flagship event"*) **and** `headline_sv` / `headline_en` (the publication-ready press-release headlines, e.g. *"Sonetel lanserar konversationsintelligens över samtal, SMS, e-post och möten"*). The board wants to see the **published headlines**, not the internal working names. Default render: `headline_sv` → `headline_en` → fall back to cleaned `title` (the IR canon is Swedish-primary; English is voluntary co-publication). Configurable via `ir_filter.headline_lang: "en"` if a meeting deck needs the English variant.

**Workflow when a meeting needs an IR calendar slide**:

1. **Spawn a read-only agent** in `Sonetel external communications` (cross-repo read is authorised for the board-slides skill; see "Financial data: spawning the Finops agent" for the analogous pattern). Give the agent the **literal Swedish headline text** of one or two events you expect to see, and have it grep to confirm those strings exist in the JSON it copies — that's how you verify you got the right file. (The first time around for meeting #7, the wrong-source check failed silently because the agent grabbed a freshly-modified JSON that *was* canonical but lacked our published headlines in the field we were reading — same file, wrong field.)
2. Have the agent copy two files into the meeting folder's `financials-data/`:
   - `ir-calendar.json` — the source data the deck renders from. Authoritative.
   - `ir-calendar-reference.html` — a reference copy of how the upstream repo renders it. **Not** used by the deck; only kept so future-me can see the canonical visual language and verify the deck output matches.
3. **Never modify** the source repo. Just read + copy.

**Slide-type contract** (`type: ir_calendar`):

```json
{
  "type": "ir_calendar",
  "title": "2026 communications pulse",
  "subtitle": "Full event cadence — disclosures, content, product launches, ops",
  "data_ref": "financials-data/ir-calendar.json",
  "ir_filter": {
    "from_date": "2026-05-22",
    "to_date": "2026-12-31",
    "exclude_types": ["subscription-renewal"],
    "headline_lang": "sv"
  },
  "notes": "Source: Sonetel external communications · ir_calendar.json. Blue background = financial disclosure. Orange = flagship. Italic grey = internal ops/decisions."
}
```

**Filter semantics**:
- An activity passes the **type filter** if (a) its `start_date` is inside `[from_date, to_date]`; AND (b) its `type` is in `include_types` OR any of its `tags` is in `include_tags` (omit both for "all types"); AND (c) its `type` is NOT in `exclude_types`.
- An activity passes the **status filter** by default unless its `status` is in `["done", "cancelled", "deferred"]` — these are hidden so the slide matches the canonical HTML view ("forward-looking active items"). Override via `exclude_statuses: []` to show everything.
- **Placeholder-confidence items are included by default** (`exclude_placeholders: false`). Many product-launch items live at `confidence: "placeholder"` until ~6 weeks out — the HTML view still shows them. Set `exclude_placeholders: true` only if a meeting deck needs the confirmed-only subset.
- Tune `from_date` to start the day after the board meeting (don't show today's items as "upcoming") and `to_date` to the board's planning horizon (~9 months, or end-of-year for a year-pulse view).

**Type → pill mapping** (rendered visual):
- `disclosure` → blue `REG` pill
- `flagship` tag → orange `FLAGSHIP` pill (added on top of any other pill)
- `blackout` → grey italic `QUIET PERIOD` pill with the row date-range and muted text
- Everything else → no pill

**Layout** (`slide-ircal`): 3-column table — Date column (28mm, tabular nums, nowrap) · Title column (flex) · Tags column (right-aligned, nowrap). 11pt body. Calendar order is enforced by `start_date` sort. Notes footnote at 8pt per §20's footnote rule.

**Two density modes**:
- **Compact mode** (~8 events): single-column 3-cell table. Use when the board wants a "what's coming next" highlight reel — typically 3-month horizon, regulatory + flagship only.
- **Full-pulse mode** (~25–35 events): manually partitioned 3-column flex layout, grouped by month, with cleaned-up titles. Use when the board wants the full publication cadence visible at a glance. Set `ir_filter.columns: 3` and use `exclude_types` to filter out admin items rather than `include_types` to include only headline items.

**Title cleanup** (full-pulse mode): `render.py` strips noisy prefixes (`"CEO LinkedIn post — "`, `"Monthly hub post — "`) and suffixes (`" — hub post"`, `" — flagship product launch"`, etc.) from event titles. Flagship status is conveyed by the `.ircal-flag` styling on the title, not by leaving the word "flagship" in the prose. This keeps each row to ≤2 wrapped lines in a narrow column.

**Manual column partition** (vs CSS `column-count`): WeasyPrint's `column-count` doesn't balance multi-month content cleanly across columns — it tends to overflow to a second page even when content would fit if balanced. `render.py` instead computes weighted month-group widths (header + events) and partitions into N flex columns so each column has ~equal weight without splitting a month. Predictable single-page result every time.

**Capacity** (full-pulse 3-col):
- ~10–12 month-groups, ~30 events → fits comfortably.
- Past 35 events the column heights start to differ and the bottom rows get clipped — apply §21 discipline (extract, count, compare).

**Hard-learned** (2026-05-14, meeting #7 v0.57 → v0.61):
- v0.58 — initial 7-event "highlights" version (single column table). Works for compact mode.
- v0.59 — Henrik asked for the full 2026 pulse (~30 events). Tried CSS `column-count: 2` → WeasyPrint overflowed to a second page.
- v0.60 — `column-count: 3` + title cleanup → still overflowed (title block alone on one page, grid on next).
- v0.61 — switched to manual partition in `render.py` (weighted month-group balancing across 3 flex columns) → single page, 31 events, clean layout. Pattern locked in.

**Hard-learned** (2026-05-14, meeting #7 v0.62 → v0.69) — five compounding mistakes on one slide:

1. **"Wrong JSON" was actually wrong-field-within-right-JSON.** v0.61 shipped with internal `title` strings ("Mobile Release 3 — async communication...") rendered as rows. Henrik flagged: *"You seem to be pulling the wrong json"* — pointing at the rendered HTML showing polished Swedish headlines. First agent reported "JSON is correct" (same path: repo-root `ir_calendar.json`). It WAS — but in May 2026 the schema gained `headline_sv` / `headline_en` holding press-release headlines, and `render.py` was still reading internal `title`. **Verify against the rendered HTML's literal strings, not schema presence. "Wrong JSON" may mean "wrong field within the right JSON."**

2. **Default-on placeholder filter was too aggressive.** First fix in v0.62: prefer headlines, plus filter out done/cancelled/deferred AND `confidence: placeholder`. The placeholder filter dropped ~half the events (many product launches sit at `confidence: placeholder` until ~6 weeks out, but the canonical HTML view still shows them). v0.63 fix: `exclude_placeholders` default false. **Match the canonical HTML's status filter, not your assumption of "what's certain."**

3. **`overflow: hidden` on columns clips mid-line.** v0.65 added `overflow: hidden` to `.ircal-col` as a backstop against text bleeding into adjacent columns. WeasyPrint then laid lines slightly wider than the column (Swedish compound words don't break at hyphens by default), and `overflow: hidden` clipped them — visually showing "Sonetel anv…" with no continuation. **Do not use `overflow: hidden` as a bleed-prevention backstop. Use `overflow-wrap: anywhere; hyphens: auto;` instead — WeasyPrint will then break ANY character to fit, with `‐` hyphenation marks at word breaks, no clipping.**

4. **3-col was too narrow; 2-col was too tall.** v0.66 switched to 2 columns to give each title ~102mm width. Worked for 25 events but overflowed to a second page at 29 events (longer English titles + more May items). v0.69 went back to 3 columns with the proper text-wrapping CSS — fits 29+ events on one page with 2-line wrapping for long titles. **3 cols + `overflow-wrap: anywhere` + `hyphens: auto` + 16mm date col + no `overflow: hidden` is the recipe.**

5. **`from_date` should be earlier than the meeting date.** v0.62 set `from_date: 2026-05-22` (the day after the May 21 meeting). Henrik flagged: *"du skippade de först i Maj?"* — the May items leading up to the meeting (cost-reduction disclosure on May 19, mobile release on May 21) are recent news the board wants to see in context. v0.69 fix: `from_date: 2026-05-01` (start of meeting month). **Default `from_date` to the start of the meeting's month, not the day after the meeting. The slide is a "where are we and where are we going" view, not "upcoming only."**

6. **Language preference defaults to the deck's language.** v0.63 defaulted `headline_lang: 'sv'` (matching the canonical Swedish HTML view I had been shown). Henrik flagged: *"Fanns det inte texter även på engelska?"* — board deck is English, so headlines should be English. **Default to the deck's language (read from `CLAUDE.md` "Language: English") rather than the canonical HTML's language. Override via `ir_filter.headline_lang` if a meeting wants the other variant.**

### 23. Narrative slides — plain English, not engineer English

§20 covered chart-anchored text. This is the parallel rule for `bullets` / `two_column` slides where the slide IS the text. The board reads a slide in 10–15 seconds; engineer prose forces them to translate as they read, and they stop.

**Anti-patterns that mark a slide as engineer-written**:
- **Internal product / version nouns**: "Portal v2", "PoC → production", "Verif", "Voice Lake backend wired into Portal v2". The board doesn't track our internal codenames. Use the *function* ("the new web app", "moving from prototype to live use") and keep the codename only when it's a recognised brand to the board.
- **Engineering verbs**: "wired into", "blind on", "swap in", "hardening", "instrumented". Replace with "connected to", "have no data on", "replace", "make production-ready".
- **Telemetry / metric jargon**: "funnel telemetry", "drop-off telemetry", "instrumentation gaps". Say "data on where customers drop off" or "visibility into sign-up".
- **Unexpanded acronyms**: PoC, KYB, IDV, MVP, OTP — define on first use or replace with the noun ("prototype", "business verification", "identity verification", "first version", "verification code").
- **Process detail the board can't act on**: "Working with Venkat (senior backend)", "owner: TBD", "Q3 grooming". Those belong in speaker notes, not the slide.
- **Math notation when prose works**: "PoC → production" reads as code; "moving from prototype to live use" reads as a sentence. Same length, drastically different cognitive load.
- **Compound technical sentences**: "Backend wired into Portal v2 (transcriptions, summaries, search); architecture audited by Venkat — sound. Decision: replace legacy summaries/transcriptions with Voice Lake." → "Connected to the new web app. Voice Lake will replace our older transcription and summary system." Same information, half the friction.
- **False precision in range estimates**: "~90–95% reimplemented" → "about 80% built". A range like 90–95% is engineer hedging; the board needs one rounded number they can repeat back.

**Rule**: before shipping any narrative slide, read each bullet aloud as if to a non-technical board member. If you'd verbally explain an acronym, a codename, or a phrase as you said it — that's the prose the slide should already have.

**Apply to**: `bullets`, `two_column`, `numbered_two_col`, `quote`, and any `mechanism_table` row label that exceeds ~10 words.

**Hard-learned** (2026-05-15, meeting #7 v0.80 → v0.81): the Web app and Voice Lake slides shipped with phrases like *"regain dev agility + onboarding telemetry"*, *"~90–95% reimplemented"*, *"PoC → production hardening"*, *"backend wired into Portal v2"*. Henrik: *"Can we simplify the language in these slides so that they are easily understood by the board?"* Rewrote each bullet to drop codenames, replace engineer verbs with plain English, round 90–95% to 80%, and remove process boilerplate ("Working with Venkat"). The same factual content went from technical-progress-report tone to board-readable narrative without losing a single substantive point.

### 24. Never change established slide structure (columns, layout, ordering) without an explicit user ask

When a user gives feedback on slide *content* (text, language, numbers, footnote), restrict the change to exactly what they asked for. Do not also change the *structure* — column order, column set, slide type, row count, sort order, headers — even when an internal rationale ("the new data doesn't have this column anymore", "this column is now constant so uninformative") feels obvious. Approved structure stays approved until explicitly changed.

If the underlying data genuinely no longer supports the approved structure, **surface the conflict and ask**. Do not silently re-design.

**Symptoms of this anti-pattern**:
- The user pastes a screenshot from an earlier version and asks "why is this different?"
- You added or removed columns "while you were in there" alongside an unrelated text edit.
- Your rationale chain reads "well, the new analysis dropped X, so I replaced it with Y" — Y was not in the user's request.

**Rule of thumb**: changes to *what's in a cell* (rewording, rounding, new figures from updated data) are in-scope for content feedback. Changes to *which cells exist* (which columns, which sort, which slide-type) are out-of-scope unless the user explicitly asks. The two-second test: "did the user mention this column/structure by name in their request?" If no, don't touch it.

**Hard-learned** (2026-05-15, meeting #7 v0.79 → v0.80 → v0.81): when rebuilding the Churn section to the new 3-bucket cohort structure (a user-asked content change), I also dropped the `Loss rate` and `% of identified` columns and added `Customers` + `ARR/yr` — none of those were requested. Henrik: *"For the 3 slides it seems as if you forgot the feedback I provided earlier and changed format without me asking?"* and then *"These were the columns before. Why did you change that part???"* Reverted to the approved 6-column structure (`# / Mechanism / Loss rate / % of [cohort label] / % of identified / Solvable`) with cohort-specific denominators for the new bucket structure (loss rate = primary-cohort / total per mechanism; % of identified = mechanism customers / cohort-identified-count, e.g. 141 for C1, 197 for C2, 174 for C3). **The columns are part of the design contract; only the data within them flexes when the analysis changes.**

### 25. Executive brevity — every prose block on a board slide is one line, not three

§20 ruled out duplicated/low-signal chart text. §23 ruled out engineer jargon. §25 is the parallel rule for *length*: prose blocks (caveat, takeaway, footnote, subtitle) must be **one line each**, not a paragraph. The board reads a slide in 10–15 seconds. Three-line caveats and four-line takeaways don't get read — they get squeezed against the source footnote and visually clutter the table.

**Symptoms of this anti-pattern**:
- Caveat / takeaway / footnote wraps to 3+ lines on screen.
- Sentences chained with "—", "(", or multiple clauses.
- "For context, …" appendix sentences explaining a relationship the headline already implies.
- Footnote spells out a formula or definition that the column header already conveys.

**Sub-rules**:
1. **Caveat box**: one sentence stating the load-bearing methodology assumption. If the column headers already convey the structure (e.g. "Viable silent share (est.)" already signals "this is an estimate"), drop the caveat entirely — don't restate.
2. **Summary takeaway**: one sentence with the headline number + framing. No "for context, …" tail; no editorial comparisons unless they're the whole point.
3. **Source footnote**: one line — source + one critical disclaimer ("Sensitivity, not a forecast.") at most. Per §20 sub-rule, ≤150 chars.
4. **Subtitle**: drop unless it adds something the title doesn't. The title carries the slide's job; a subtitle that paraphrases is dead text.

**Rule of thumb**: when in doubt, read each block aloud — if you take more than 5 seconds, cut. If you're tempted to write "For context, …", the context probably isn't load-bearing for the board.

**Apply to**: every narrative prose block on every slide — bullets, two_column, mechanism_table caveats/notes, arr_summary takeaway, anywhere a long sentence wraps.

**Hard-learned** (2026-05-16, meeting #7 v0.94 → v0.95): slide 5.5 "Recoverable ARR — summary" shipped with a 3-line caveat box at the top (restating the column headers in prose) plus a 4-line summary takeaway box at the bottom (with a "for context, …" YoY comparison appendix) plus a 4-sentence source footnote (Silent ratio formula + Viable share definition + Sensitivity disclaimer). Henrik: *"You added too much text on this slide. As usual."* Cut the caveat entirely (column headers already self-explain), reduced takeaway to one sentence (`On ~$2.7M current ARR: documented fixes ≈ +1%; upper bound with silent estimate ≈ +3.6% — about half a year of organic growth.`), and trimmed footnote to source + sensitivity disclaimer. **The pattern is recurring — write less from the start.**

**Sub-rule (post v0.98): editorial comparisons depend on a stable baseline — verify, or don't include.** A "≈ half a year of organic growth" tail anchors the headline against the current YoY rate. That comparison is only useful if YoY is *representative* — i.e. not anomalous, not a one-off spike, not a recovery against a depressed prior period. When the comparison baseline is itself unusual (in this case, Sonetel's +6% YoY ARR is compared against a 2025 Skype-wave spike, so it's not "organic growth" the board would recognise as normal), the comparison misleads more than it clarifies. **Default**: skip benchmark comparisons unless the headline number is meaningless without them. If you do include one, you must be able to state the baseline assumption in one breath — and that assumption must be uncontroversial.

**Hard-learned** (2026-05-16, meeting #7 v0.96 → v0.99): added "— about half a year of organic growth" to the 5.5 takeaway. Henrik: *"We have an extremely low ARR growth now as we compare with 2025 Skype spike. It is not a 'normal' ARR growth. So remove it."* The +6% YoY comparison wasn't a stable baseline — it was a recovery slope after a 2025 spike. Cut the tail.

**Sub-rule (post v0.100): a wrapping bullet is a trim signal.** If a `bullets` slide entry wraps to a second line in the rendered PDF, the bullet is too long. Don't accept "it fits on one page" as good enough — the wrap itself is visual noise on a board slide. Cut until it's one line. (The same applies to `numbered_two_col` entries.)

### 26. When source data updates, audit every data point on every affected slide — not just row values

Slides that derive from a source (MEMO, financial data, analytics report) carry data in many more places than the obvious table rows: subtitles, caveat lines, footnote denominators, summary numbers, comparison percentages, headline captions. **All of those go stale together** when the source moves. Refreshing only the rows leaves the rest pointing at the old snapshot and the board sees internally inconsistent slides.

**The fix is a comprehensive audit on every update, not a row-by-row patch:**
1. Read each affected slide fully — every concrete number, percentage, count, and named comparison.
2. For each one, identify the source field in the upstream data and re-verify against the current snapshot.
3. When the audit spans more than 2–3 slides, spawn a read-only agent in the source project. Give it the slide paths, the data paths, and an explicit "verify every data point" instruction. Henrik has authorised this pattern for read-only churn-project / financial-ops verification.

**Symptom**: the slide ships with row values that match the new source but a caveat that still cites the old contact rate / denominator / count. The user notices the inconsistency and (reasonably) loses confidence in the rest.

**Hard-learned** (2026-05-16, meeting #7 v0.91 → v0.92): refreshed slides 5.2 / 5.3 / 5.4 with new MEMO ARR + solvable values, but left the per-cohort caveat lines pointing at the prior snapshot (C1 contact rate "~6%" while the new MEMO §9 had 0.76%; "~31K monthly non-converters" while the new annualised cohort total was 517,364 → ~43K/mo; B "~55%" → 28%). Henrik: *"You never updated the header with up to date info as I asked you to. ... You needed to verify — with an agent in the churn project if need be — all data points."* Spawned a read-only audit agent that found the 3 stale figures plus a curation question; would have shipped a draft with conflicting numbers without it.

### 27. Don't blindly relay substantive framings from an upstream source onto a board slide

When an analyst, memo, or other upstream contributor writes prose that ends up on a board slide, watch for **strategic verbs** (exit, expand, pivot, kill, restructure, deprecate), **attributions** (who's at fault, what to fix, who owns the next move), and **recommendations**. These are *claims*, not data — and they may be wrong in the operating context the board reads them in.

**Pattern to watch for**: a sentence in the upstream source that recommends a *direction* Sonetel should move. Even when the underlying data is correct, the directional framing may be outside the analyst's scope or against operating reality.

**The fix**: when converting upstream prose into board copy, flag every strategic verb and recommendation for confirmation. If you're rewriting an analyst's bullet, read your output and ask *"would the user agree with this exact phrasing if a board member quoted it back?"* If you're not sure, flag the bullet in the response and let the user confirm before it lands in a draft the board will see.

**Hard-learned** (2026-05-16, meeting #7 v0.97 → v0.98): the analyst memo recommended *"exiting countries with intractable doc requirements (Australia, Germany, Norway, Poland, Hungary, Chile, Switzerland) or restructuring DIDWW dependencies."* I copied this onto slide 5.7 verbatim. Henrik: *"Exiting is wrong. We can still offer numbers to locals. What we CAN do is to be more clear on requirements up front, so that ineligible customers don't even start the process. I.e. lesser churn, but no gain in revenue."* The analyst's framing was a strategic claim outside their scope; relaying it put incorrect strategy on the draft. Rewrote to "Clearer pre-purchase doc requirements — ineligible customers don't start the process (reduces churn, no revenue gain)." **Strategic verbs from upstream sources are always pass-through candidates worth flagging.**

---

## §14. The skill must self-reflect and self-update — every session

The skill is a living artifact. Every meeting iteration produces new learnings (gotchas, working recipes, layout rules, data-shape constraints). Those learnings **must** be folded back into this SKILL.md, `render.py`, `template/`, and `examples/` before the session ends. No exceptions. The conversation transcript disappears; the skill is the only persistence layer.

### Trigger: when to self-reflect

Self-reflection is **mandatory** at any of these moments — not deferred to end-of-session:

1. **A user correction lands** — Henrik points out a defect ("graphs too small", "numbers outside card", "comment on assumption"). The fix is incomplete until the rule that prevents recurrence is in SKILL.md.
2. **A diagnostic agent returns a root cause** — per §15's 3-failure rule, the agent's finding becomes a numbered lesson immediately, with file:line references and the working code pattern.
3. **A new WeasyPrint quirk is discovered** — every quirk that bit you will bite a future session if not documented. Examples in §16, §17.
4. **A new content rule is established** — "every assumption needs a rationale" (§18) is a content rule, not a layout rule, and must be captured the same way.
5. **End of each iteration cycle** — before declaring the deck ready, re-read SKILL.md and ask: "is anything in the last 10 turns missing from the skill?"

### What to capture

For every learning, write a numbered lesson with this skeleton:

```
### N. <one-line title — the rule, not the symptom>

**Symptom**: what the user/I observed that triggered the investigation.
**Why**: the underlying mechanism (CSS spec quirk, WeasyPrint implementation gap, content judgement principle).
**Fix**: the concrete code pattern — with file:line refs and a copy-pasteable snippet.
**Apply to**: which slide types or contexts this rule governs.
**Hard-learned** (YYYY-MM-DD, meeting #N context): a one-sentence postmortem so future-me knows this came from real pain, not theory.
```

### What to port alongside

When a learning involves code, the file change ports atomically with the lesson:
1. Edit the lesson into SKILL.md.
2. `cp` the corrected `template.html` / `style.css` / `render.py` from the meeting folder into `~/.claude/skills/board-slides/`.
3. If a data-shape changed, update `examples/financial-data-shapes.md` and the relevant `examples/*.json`.
4. If applicable, cite the lesson by `§N` in the meeting's `CHANGELOG.md` entry, so the rule's provenance is traceable from the deck back to the skill.

### Anti-patterns (do not do these)

- ❌ "I'll update the skill at the end of the session." → end-of-session in long threads gets cut off; the learning is lost.
- ❌ "The fix is obvious from the diff." → no, it isn't. The *fix* is in the diff; the *reasoning* (and the rule that prevents recurrence) lives only in SKILL.md.
- ❌ "I already covered this in a comment in the code." → code comments are seen only by readers of that file. SKILL.md is loaded into every session's context.
- ❌ Writing a long retrospective in the conversation that never makes it to the skill.

### Self-check before declaring "done"

Before ending an iteration, run this checklist:
- [ ] Every Henrik-flagged defect this session: rule captured in SKILL.md? (Y/N)
- [ ] Every diagnostic-agent root cause: lesson written? (Y/N)
- [ ] Pipeline files (`render.py`, `template/`, `style.css`) in the skill match the meeting folder? (Y/N)
- [ ] `examples/` reflects the latest reference data shapes? (Y/N)
- [ ] CHANGELOG entry references the §N of any rule that drove a change? (Y/N)

Any "N" → keep working. The session is not closed until all five are "Y".

---

## Iteration discipline

- Re-render after each meaningful change. `python3 slides/render.py` versions to the next `v0.N.pdf`.
- `open <pdf>` after each render so Henrik can review.
- Don't ask "is the design OK?" until you've shown the rendered PDF.
- Pre-distribution: edits flow freely. Post-distribution: changes require a CR (see meeting CLAUDE.md).

---

## Future work (not yet implemented)

- Adapter pattern: `data_ref` for `pnl_table`, `kpi_grid`, `breakeven` (currently inlined). Mostly a cleanup; current inline approach works.
- Auto-derive `cover_date_label` from `agenda.meeting.date` when null. (Currently requires explicit string in `data.json`.)
- Image slide type with caption (defined, not yet exercised).
- A `decisions` slide type that aggregates decisions from `agenda.json` items.
- Speaker-notes export (PDF "Notes" view for the chair).

---

## Files in this skill

- `render.py` — the renderer (≈600 lines). Copy to each meeting's `slides/` folder.
- `template/template.html` — Jinja2 template with all slide types.
- `template/style.css` — design-system-aligned CSS.
- `assets/sonetel-wordmark-{white,black}.svg` — logos.
- `examples/financial-data-shapes.md` — schemas the Finops agent produces for each financial slide type.
- `examples/meeting-7-data.json` — current reference `data.json` (used to validate the schema; updated each iteration).
- `examples/meeting-7-agenda.json` — current reference `agenda.json`.
- `examples/cash-position-example.json` — sample `cash-position.json` payload.

This skill is versioned in spirit, not git — iterate on the files here as the pipeline evolves. The pattern: when a meeting's `slides/render.py` proves a new feature, port the improvement back here so the next meeting starts from it.
