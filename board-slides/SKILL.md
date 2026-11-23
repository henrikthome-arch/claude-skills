---
name: board-slides
description: Render Sonetel AB board meeting decks as 16:9 landscape PDFs from JSON via Jinja2 + WeasyPrint. Use when producing slide decks for any meeting in `Sonetel/Board/Board meetings/<year>/<meeting folder>/slides/`.
---

**DIRECTORY GUARD**: This skill is for Sonetel board meeting decks only. If the current working directory does NOT contain `Sonetel/Board/Board meetings/`, STOP and tell the user: "This skill is for Sonetel board meeting decks only. Current directory: [cwd]". Do NOT proceed.

The skill is a deliberate replacement for PowerPoint. Decks are produced as a single PDF rendered from a Jinja2 HTML template via WeasyPrint, sized 16:9 landscape (297 mm × 167 mm). The data lives in `data.json` next to the renderer; the slide structure derives partly from `agenda/agenda.json` and partly from per-item content slides in `data.json`.

This is iteration #1 of the skill — extracted from meeting #7 (May 21, 2026). Expect ongoing iteration as new patterns surface.

---

## ⚠ Writing rules — apply to EVERY bullet, EVERY slide, BY DEFAULT

The board reads each slide in 10–15 seconds. Cramming, jargon, and engineer-prose erode that signal. Henrik has rejected the same anti-patterns across 8+ versions in this thread alone. **These are not "edit-tight after rejection" rules — they are how the first draft of every bullet must read.**

**0. THE RELEVANCE LENS — apply to EVERY element (number, label, note, driver, caveat, subtitle), not just bullets.** Before anything ships, ask the one question that governs all the rules below: **"does a board member actually need or want to know this?"** If it would make them think *"why is this here / why does this matter?"*, CUT it. Show only the figure that matters (the **net**, the **change**, the **so-what**) — never the gross-and-its-breakdown, the internal routing, or the how-it-was-derived. **Explaining the mechanics of a number is clutter, not credibility**; it adds confusion, not trust. (Hard-learned 2026-07-07: a cash-driver note read *"net reimbursement to the CEO −35K — most of the 100 KSEK reimbursed telecom (Voxbone) the CEO had paid personally."* Henrik: *"this is rubbish. In what way is the 100 KSEK of ANY interest to the board beyond the 35 KSEK… Adding clutter adds confusion 'why is this important???'. Skill should know better."* The whole note was the answer to a question no board member was asking — the line should have been just **"Net reimbursement to the CEO −35K"**, or nothing.) When in doubt whether an item clears the lens, it doesn't — leave it off or ask Henrik.

**1. One bullet, one fact.** What changed + what it means for cash. That's the cap. Multiple distinct facts → split into multiple bullets. **Em-dashes, parentheticals, and semicolons inside a bullet are a smell** — each typically means a second idea is being chained on. If your draft has more than one em-dash or semicolon, you are cramming. Cut.

**2. Strip accounting / engineering detail.** Account numbers, factor coverage, range gating, sub-system names (MOSS, COGS factor, 4xxx, 6571/6572, recurring_payment IDs, PLAN-A/B/C names) — **none of that goes on a board slide**. The board cares: what changed, what's the cash impact, is it good/bad/neutral. Detail belongs in `content/<topic>-input.md` (speaker notes), not on the slide.

**3. Translate agent prose — don't relay.** Sub-agents (Finops, churn-analysis, etc.) write technical prose for themselves. When their bullet recommendations contain em-dash chains, parentheticals, account numbers — **read for the headline only and discard the technical scaffolding**. Rewrite tight from scratch; don't paste.

**4. Neutral word choice.** Use plain factual verbs: *missing*, *fixed*, *re-timed*, *deferred*, *added*, *increased*, *reduced*. **Avoid editorialising hedge-words**: *over-optimism*, *aggressive*, *conservative*, *adverse*, *favourable*. Those read as opinion, not fact, and invite pushback.

**5. No strategic verbs relayed from upstream.** Verbs that imply a direction Sonetel should move (*exit*, *expand*, *kill*, *pivot*, *restructure*) are claims, not data. If they appear in agent prose, flag them to the user before they land on the slide.

**6. Verify every concrete number against source before shipping.** When a source updates, EVERY data point on the affected slide is suspect — not just the row data. Caveats, subtitles, denominators, comparisons all go stale together. See §26 for the audit pattern.

**7. Minimal text, no footnotes (Henrik 2026-11-20, staff-meeting thread: "You add too much text, making the page overwhelming. We often have the same issue in the board slide generation" · "No one will read such text").** Default every slide to: title, the figures, at most one short takeaway line. No footnotes, no grey sub-lines, no definitions on the slide — those go in speaker notes. Chart comments are callouts (small label · big figure · short grey note), not sentences. Count the words before rendering and cut every one that doesn't change what the viewer understands.

**7. Drop imprecise numbers — describe the item, not the figure.** If a magnitude is uncertain, approximate, or derived from a still-shifting model, omit it. *"India costs higher"* beats *"India costs increased ~165 KSEK/month"* when the 165 itself is a moving estimate. A "~" or "approximately" on the slide is a tell that the number shouldn't be there — the board will anchor on it as if it were precise and quote it back. Only ship a number when it's audit-grade and stable.

**8. Be exact about what was aligned with what.** *"Aligned with the budget"* is not the same as *"aligned with the underlying data the budget was built from"*. If the comparison source is a working spreadsheet, an Excel sheet, or a prior forecast — name that, not the downstream artifact. Sloppy source attribution invites pushback ("you said budget, but the budget already has that figure"). When in doubt, ask Henrik what the actual source-of-truth being reconciled to is, before drafting the bullet.

**9. No methodology on the slide — default to NO footnote/subtitle, and no redundant titles.** Titles, subtitles, and footnotes are not where source/method goes. **Never** write provenance/method on a slide — "Finops / SIE-booked / group_pl_budget / India intra-group markups eliminated / EBITDA = Rörelse + avskrivningar / published BDO statutory basis / same basis" — the board can't parse it at a glance and reads it as clutter (Henrik, 2026-06-08: *"these cryptic texts … no one can make sense of from a glance. Better remove them"*). Titles carry no redundant gloss: **"SaaS40", not "SaaS40 (Rule of 40)"**. A subtitle/footnote earns its place ONLY if it adds non-obvious, board-relevant info in plain words — if the chart legend or a table column already shows it, **drop it**. Methodology lives in the deterministic generator + audit trail + speaker notes, never on the slide. *"If there is something you really want to say, say it briefly with simple words."* See §10 (reversed).

**Gut-check before shipping any bullet**: read aloud as if to a non-technical board member. If you'd verbally say "that means…" to explain a parenthetical, or "and another thing…" to introduce a second fact, the bullet is over-stuffed. Split or strip.

**This section is the TL;DR of §23 / §25 / §27. Read it every session. Apply it before the first draft, not after the user rejects.**

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
   - `scripts/build_financials.py` (deterministic consolidated-koncern P&L generator — see §32/§36)
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
| `two_column` | Two parallel lists side-by-side | `left: list[str]`, `right: list[str]`, optional `left_title` / `right_title` (uppercase rules above each column — use for then-vs-now comparisons) |
| `data_table` | Generic free-text table — price tables, competitor comparisons, sensitivity ladders, option/verdict grids | `columns: list[str \| {label, align}]`, `rows: list[list[str] \| {cells, emphasis}]`, optional `notes`. See §47. |
| `numbered_two_col` | Numbered list 1–10 in two columns (e.g. growth ideas) | `entries: list[{text, badge?, badge_tone?}]` (also accepts plain strings) |
| `pnl_table` | P&L line items with actual + budget + variance | `pnl_rows: list[PnlRow]`, optional `pnl_columns`. See §11 (merge rule) and §10 (sources in footnote). |
| `kpi_grid` | 3×2 grid of KPI cards (Finops Monthly Pulse styling) | `kpis: list[{label, value, lines[], tone}]`. See §8 for sizing. |
| `breakeven` | Two-box breakeven/cashflow assessment | `breakeven_boxes: list`, `breakeven_note` |
| `cash_position` | Cash trend + drivers panel | `data_ref` → `cash-position.json`, optional `drivers_title`. See §12. |
| `cash_flow_forecast` | Daily cash projection chart + top-5 items panel (Finops UI styling) | `data_ref` → `cash-flow-forecast.json`. See §15. |
| `trends_grid` | 3×2 grid of small charts (Finops Monthly Pulse styling) | `data_ref` + `trends_layout`, OR inline `trends`. See §9 for figsize. |
| `saas40` | SaaS40 (Rule of 40) trend — stacked growth+margin bars + benchmark line + component table | `periods: [{label, growth_pct, margin_pct, saas40_pct}]`, optional `benchmark` (default 40). **Published statutory figures only — see §33.** |
| `quote` | A single quote with attribution | `quote`, optional `attribution` |
| `image_row` | A row of stills (e.g. video ads), each with a caption | `images: [{src, caption}]` (src relative to `slides/`), optional `image_width_mm` (default 36; 6 portrait stills fit at 36). Fixed mm widths on purpose (§16). |
| `stat_row` | 2–4 big figures where the NUMBER is the point (a funnel collapse, a before/after) | `stats: list[{value, label, note?, tone?}]`, optional `connector` (e.g. `"→"`). See §50. |
| `layers` | A stacked diagram — product tiers, an architecture, a build order | `layers: list[{tag, name, detail?, metric?, tone?}]`. See §50. |
| `orbit` | Capabilities as concentric rings around a core asset, radius = distance from it | `rings: [{name, hops, fill, ink?, features:[{name,status}]}]`, `core_line1/2`, `core_radius`, `ring_step`. Statuses: shipped / september / gap / later. Geometry by `prepare_orbit()`. See §55. |
| `growth_waterfall` | Today's position, each lever, where we land — on one growth axis | `steps: [{label, value, color?}]`, `start_lo`/`start_hi`, `start_label`, `end_label`, `y_min`/`y_max`. See §54. |
| `growth_stack` | "Which opportunity is big" — a stacked column where block HEIGHT is the growth each adds | `blocks: list[{name, value, step?, tone?}]`, optional `stack_height_mm`, `cap`, `baseline_label`. Sized by `prepare_growth_stack()`. See §53. |
| `knob_row` | 3–4 levers as amplifier dials, each showing how far it is turned and what a turn is worth | `knobs: list[{name, gain, fill (0..1), step?, tone?, color?}]`, optional `total`. Geometry computed by `prepare_knobs()`. See §53. |
| `flow_hub` | Inputs → a central store → outputs, with a connector to something outside | `inputs[]`, `hub{name,detail?,badge?}`, `outputs[]`, `sink{name,detail?}`, `inputs_title`, `outputs_title`. See §53. |
| `matrix_2x2` | Four segments on two axes | `quadrants: list[{key, name, headline, facts[], tone?}]` — exactly 4, read left-to-right, top row first. See §50. |

**Opening slides** go under `items["0"]` in `data.json`: they render after the cover and before the agenda, with eyebrow "Summary" and no section divider. **Every deck opens with a "Key messages" slide there — see §70.**

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

Supported `kind`: `bar`, `line`, `stacked_bar`, `hbar`.

`hbar` is for **categorical** comparisons — lever sizes, sensitivity ladders, option grids — where
the category names are too long to survive a rotated x-axis. Its points carry `label` instead of
`month`, and categories read top-to-bottom in the order given. Any chart kind also accepts
`reference_lines` and `band`; see §50.
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
- `balance-sheet.json` — for a **balance-sheet change** slide: `GET /api/v1/balance-sheet?scope=group|parent`
  (MCP `get_balance_sheet`, `scope`). **Use the group (consolidated) view on board slides** (Henrik 2026-11-05, when
  Finops shipped it): Sonetel AB + the India subsidiary, BDO's consolidation method. `scope=parent` (Sonetel AB only,
  CR-2026-11-04b) stays available. The default columns are the latest month, the previous fiscal year-end and the
  same month a year earlier; `changes` = first column minus each other column. Only use the numbers if `balances`
  is true. A group column with `estimate: true` uses an estimated markup elimination until BDO's quarterly figures
  arrive (Sep 2026 was one on 2026-11-05): mark it. Across a year-end, compare total equity rather than "Profit for
  the period" (null in the group view). See `financial-ops/docs/api/balance-sheet.md`.
  **Build it with** `build_financials.py --balance-sheet --period <YYYY-MM|YYYY-QN> --write slides/data.json`
  (2026-11-04, Henrik: "Balance sheet page after the quarterly P&L page with comparisons"). The scope is group by
  default; `--bs-scope parent` gives the parent company. The script inserts a `data_table` (dense) right after the
  P&L slide, or replaces the one already there. The title says "group" or "parent company". Columns: the reporting
  month-end (the quarter's last month), three months earlier, the last year-end (Dec), twelve months earlier,
  then the changes vs a quarter and vs a year, in KSEK. An estimated column gets a `*` and the subtitle says
  "* Estimate until BDO's quarterly figures." Keep the subtitle on one line, because a second line pushes the note
  off the slide. The year-end column is there because a loan taken and partly repaid between the compared dates
  is otherwise invisible (DBT loan 2, Nov 2025). A hand-written `notes` line on the slide survives re-runs, so
  recheck its figures after a re-run.
  Nine rows: small lines grouped, zero lines dropped, equity = total equity (incl. minority interest). "Other
  liabilities" includes provisions and untaxed reserves; the group has 0.8 MSEK of provisions that the parent
  lacks. The script stops if Finops says the columns don't balance, if the API returns another scope, or if
  the rows don't add up to Finops' totals (a line missing from `BS_ROWS`). Include the slide in every quarter-close
  deck, next to the quarter P&L (§69).

- `subscriber-flow.json` — the **"Paying customers with subscriptions"** chart (Henrik 2026-11-09, his long-running
  Excel churn chart, now built from Finops only; never from the sales_analysis Excel). **Build it with**
  `build_financials.py --subscriber-flow 2025-05 2026-10 --out financials-data/subscriber-flow.json` (18 months,
  ending on the report month). New/day = `customers_new_paying_monthly_total` (`/metrics/trend`) ÷ days, rounded to
  1 dp; net/day = month-end change in `subscriptions_positive_balance` (`/monthly-metrics`, the month before the
  window is fetched too) ÷ days; lost/day = new − net. The script stops if June 2026 isn't 32,133 (36,623 = the
  SNTLRND-9836 double count) or if the spot months don't match Finops' verified values (`SUB_FLOW_KNOWN`).
  Slide: a one-chart `trends_grid` with `kind: "flow"`, `keys: [net_per_day, new_per_day, lost_per_day]`, which
  draws green net columns with whole-number labels and blue (new) and red (lost) lines on one axis. It sits in
  Financials after the 13-month trends. Include it in every board update.

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

### 8b. Bullet slides — `dense` variant for 7+ items (v0.41)

Default `.slide-bullets` is 16pt with 5mm gaps — generous, but **7–8 bullets (especially with a 2–3-line wrapping item) overflow onto a second page**, which reads as a layout bug (the continuation page shows a stray mid-list bullet with no title). The template auto-applies a `dense` class when `bullets|length > 6` → 14pt / 1.4 line-height / 3mm gaps, keeping the slide one page. **Six bullets can already overflow** if one wraps to two lines (Oct 2026 marketing slide: 0.7 mm over). Set `"dense": true` on the slide to force the variant; the template honours `s.dense`. If a `dense` slide still overflows (≥9 long bullets), split the content or trim — don't shrink further.

**Bold lead-in labels for readability (v0.42).** On "Key focus"-style action lists, each bullet reads better as a **bold topic label + detail** (`**Mobile apps.** Roll out.`). A `bullets` item is either a plain string *or* a `{"label": "...", "text": "..."}` object — the model coerces strings to `{"text": ...}` and the template renders `<strong>{{label}}.</strong> {{text}}` (the period is added by the template; `label` has none). Give every bullet on such a slide a label so the column of bold lead-ins is consistent — invent concise category labels where the source bullet has none (e.g. a bare "New sign-up and landing pages" → label **Sign-up**), and surface the invented labels to Henrik to tweak. Don't label narrative slides (Comments, Conclusions) — there the bullets are full sentences, not topic+detail.

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

### 10. Source/methodology notes go OFF the slide — default to no footnote (REVERSED 2026-06-08)

**This rule used to say the opposite** ("sources belong in the footnote; name the datasets explicitly"). Henrik reversed it on 2026-06-08, reviewing the June board-update deck: the source footnotes ("*Consolidated koncern (Finops, April 2026 SIE-booked; India intra-group markups eliminated). Budget: Finops FY2026 koncern (group_pl_budget)*") and method subtitles were called cryptic clutter — *"no one can make sense of from a glance. Better remove them."*

**New rule: financial slides carry NO source/methodology footnote by default.** Where the figures come from and how they're derived (actuals source, budget source, consolidation eliminations, statutory-vs-Finops basis, SIE-booked status, mapping caveats) belongs in the **audit trail** — the `scripts/build_financials.py` docstring + its `--reconcile` check, the coordination log, and this SKILL.md — NOT on the slide. The board trusts the numbers; it does not want the plumbing.

If a figure genuinely needs provenance for the board (rare), say it in **one plain phrase** (e.g. "Estimate" / "preliminary"), never a datasets-and-mapping sentence. Detailed methodology that a presenter might be asked about goes in the `content/<topic>-input.md` speaker notes, not the slide. See top writing-rule #9.

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

**Driver classification rule**: A driver is included on the slide only if it is *outside the recurring monthly cost base* — i.e. a one-off cost, a quarterly recurring (Q1/Q4/Q7/Q10 typical for VAT, Certified Advisor fees), or an annual recurring (audit fees, AGM ads).

**For the cash-position drivers, reconcile against the ACTUAL BANK CSVs — NOT the forecast model, NOT a P&L-based decomposition (Henrik, 2026-07-07; cost a long detour).** Explaining June's −105K EOM decline took THREE wrong model-based attempts before the bank data resolved it in one pass: (1) "−183K less revenue than May" — rejected (at ~2.4 MSEK the company is above the operating cash-flow-positive target, so operations were roughly neutral; a revenue-vs-prior-month delta cannot be an absolute cash drain); (2) "loan principal + interest are the structural driver" — also rejected (the +0.2M operating surplus roughly *covers* the ~0.2M monthly loan service, and recurring loan payments are base run-rate you don't highlight); (3) an agent-built "operations +90K / loan −195K" bridge — a plug, not real. **The truth only came from the downloaded bank statements:** a **−100K reimbursement to the CEO cleared 23 June** (the forecast had wrongly *deferred* it to Aug–Oct) — BUT ~65K of that 100K was telecom (**Voxbone/Bandwidth**) the CEO had paid on his own card, i.e. economically the company paying its Voxbone bill (a normal operating cost), so the **genuine net repayment to the CEO was only ~35K**; the rest of June was normal operations. **Two lessons: (1) open the bank CSVs first — the Finops forecast's recurring/scheduled *timing* is unreliable; (2) even the "one notable item" needs Henrik's read — a large CEO reimbursement can be mostly operating pass-through, so ASK what a reimbursement actually covers before labelling it a repayment.**

Bank CSVs: freshest in `~/Downloads`, filed under `~/Dropbox/Sonetel/Financial/<year>/Month/<YYYY MM>/`. **5 accounts** = PlusGiro **91 55 78-9** with 3 currency pockets (SEK/EUR/USD) + **214 72 32-9** (EUR) + **214 72 33-7** (USD). The two 214 accounts are almost all `DEPOSIT VALUTA`/`FÖRFALL DEPOSIT VALUTA` FX-term-deposit pairs that net to ~0 — ignore them; **the SEK pocket carries the operating story.** Format: semicolon-delimited, Swedish decimals (`-16847,00`), cols `Datum;Belopp;…;Namn;Ytterligare detaljer;Meddelande;Egna anteckningar;Saldo;Valuta`. Bulk payments export as **"Corporate Access"** / **"Importerade kontohändelser"** with NO payee — the payee shows only in the bank UI's transaction-detail popup, so **ask Henrik to identify large unlabelled batches** (he did: SEB Kort = card settlement, Skatteverket = tax, Mangold = Certified Adviser fee, Importerade = net salaries). Then: the only board-worthy driver is what's genuinely non-recurring (here the CEO reimbursement, per §38); say "normal operating month" for the rest rather than manufacturing drivers.

**ALWAYS list deferred payments on this slide — standing rule (Henrik, 2026-08-04).** If the
month's cash moved because payments *slipped into the next month* rather than because operations
changed, the slide must say so. The August 2026 email update showed July EOM improving +129K —
but 261K of payments had simply moved into August (DBT Lån 1 135,098 → 5 Aug; BDO audit invoice
125,904 → 15 Aug). Presenting +129K without that context reads as a turnaround it wasn't. Title
the panel for what actually happened ("Why July cash improved"), list each deferral with its new
date, and show deferrals as **positive** amounts (they genuinely helped that month's cash) with
real outflows negative. Find them in `POST /api/v1/cash-flow/forecast` → `days[].outflow_details`,
where slipped items carry `type: "scheduled"` and a description saying so ("Delayed July Lån 1
payment paid early Aug", "CEO-deferred end-June -> July -> mid-August").

**The drivers list does NOT have to reconcile to the full MoM change** — it is the named
non-run-rate items, not a complete bridge. In the August deck the three drivers summed to +201K
against a +129K actual move; the residual is ordinary operating variance and needs no line.

**`render.py` reads the drivers from the legacy key `april_drivers`** (render.py:301) no matter
which month the deck covers. Naming it `july_drivers`/`june_drivers` produces a silently EMPTY
panel and spills the slide onto a blank second page. Same for `april_change_msek`. Also note the
slide's own `drivers_title` in `data.json` **overrides** the one in the data file.

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

**Sub-rule (post v0.130): one bullet, one idea — strip accounting / engineering noise. RELENTLESSLY.** This is THE recurring failure mode on board slides — repeated across multiple meetings, multiple sessions, multiple sub-agents. A bullet that *technically* fits on one line can still be cognitively dense: em-dash chains, parenthetical technical detail, semicolon-joined sub-explanations, account numbers, factor coverage, range gating, methodology fragments. Each of those is noise to the board.

**Anti-pattern examples** (all from this thread, all rejected by Henrik):
- "*PSP fees (PayPal 45K/mo + Adyen 14K/mo) now modelled as explicit outflows — previously missing entirely (COGS factor covers only 4xxx accounts; PSP lives on 6571/6572); adds ~59K SEK/month of outflow, correcting prior over-optimism*" — five distinct ideas, two parenthetical technical asides, account numbers, an editorial qualifier. Board read: opaque.
- "*VAT now treated symmetrically — Swedish suppliers shown incl. VAT, monthly EU-VAT inflow added; net cash effect ~0 over the quarterly cycle*" — three clauses + a methodology footnote. Also factually fuzzy (claimed "~0" when reality was "+~0.1K marginal").

**The fixed versions Henrik signed off on**:
- "*PSP fees ~60K/month added to the forecast — previously missing in error*"
- "*VAT model refined — marginal net cash improvement*"

**Rules**:
1. **One bullet states one fact.** What changed (1 phrase) + impact (1 phrase). That's the cap. If you have two distinct facts, split into two bullets — don't chain them.
2. **Strip accounting / engineering detail entirely**. Account numbers, factor coverage, range gating, methodology fragments — none of that goes on a board slide. The board cares: what changed, what does it mean for cash. Anything more belongs in speaker notes (`content/<topic>-input.md`), not the slide.
3. **Translate agent prose, don't relay**. Sub-agents (especially Finops cash-flow agents) write technical prose for themselves. When they hand you bullet recommendations, **read for the headline only and discard the technical scaffolding**. If their bullet contains em-dash chains, parentheticals, account numbers — extract the one core fact and write a fresh, tight version.
4. **Word choice matters**. Hedge-words like "over-optimism" carry an editorial framing the board may not accept. "Was an error" is honest; "over-optimism" sounds like spin. Use neutral plain-English: *missing*, *fixed*, *re-timed*, *deferred*, *added*. Avoid: *optimism*, *pessimism*, *adverse*, *favourable*, *aggressive*, *conservative* — these read as opinion, not fact.

**Quick gut-check before shipping any bullet**: read it aloud as if to a non-technical board member. If at any point you'd verbally explain a parenthetical or an acronym ("that means..."), or if you'd say "and another thing..." to introduce a second fact, the bullet is over-stuffed — split or strip.

**Hard-learned** (2026-05-21, meeting #7 v0.129 → v0.131): slide 2.8 "Cash-flow forecast — changes since the April board update" shipped with two over-stuffed bullets. Henrik: *"this is a recurring problem you have. Can you update the skill to avoid this moving forward? ... USE BOARD LEVEL LANGUAGE."* The PSP bullet contained five facts in one sentence; the VAT bullet was factually fuzzy AND over-stuffed. Pattern has appeared in v0.79 (Churn slides too verbose), v0.95 (Churn cohort table notes), v0.110 (cash slide deviation bullets), v0.122 (Communications slide), v0.124 (cash slide actions). Each time the fix is the same: split into one-idea bullets, strip accounting/engineering noise. **The skill exists to prevent this default behaviour — write tight from the start, not edit-tight after the user rejects.**

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

**Sub-rule (post v0.101 cash-research): upstream agents over-dramatize observations into "newly discovered failure modes" or "fundamental insights". Sanity-check before relaying.** A research agent operating in a sibling project (financial-ops cash-flow log) framed standard insufficient-funds bank behavior ("Hejdad" = Nordea won't clear a SEK payment when the SEK account has no funds) as a "newly discovered silent-blocking algorithm" — implying a hidden bank mechanism the company hadn't accounted for. Henrik: *"Nonsense. The only blocking/hejdad happens when there is not sufficient funds in the Nordea account of the payment currency to make the payment. No secret mechanism, just a matter of funds not being there."*

The pattern: log entries written *in-the-moment* by the agent encountering a phenomenon for the first time can dress routine operational reality in "discovery" language. By the time those entries are summarised for a board slide, the dressing reads as substantive insight. **When an agent's report includes phrases like "fundamental insight", "newly discovered", "new failure mode", "silent X" — pause and ask: is this routine operational reality the operator already knows about, or is it actually new?** When in doubt, flag to the user before putting on the board slide. The board doesn't want to read about the agent rediscovering how banks work.

**Sub-rule (post v0.112 SEB Kort pushback): accounting reshuffles dressed as cash deviations.** When an agent's report cites a line-item increase like "+40K/mo" and attributes it to "baseline correction" or "underestimated budget", verify against actual cash flow: is the line truly higher, or did something get moved INTO it from another (now-disabled) line? Net cash impact = `new_combined_total − old_combined_total` across ALL affected lines, not just the one that visibly changed. **If the net is ~0, it's not a deviation — it's bookkeeping.** Board slides should report cash deviations only; bookkeeping changes belong in the internal-changelog, not on a slide.

**Hard-learned** (2026-05-16, meeting #7 v0.110 → v0.112): the cash slide carried "SEB Kort baseline too low (actuals 129–190K vs 120K budget) — net +40K/mo after fix". Henrik: *"is this really true? Isn't the increase just a result of that META was moved into here?"* Agent verification confirmed META was always physically on SEB Kort; the original "id 28 META & Bing" budget line was a phantom that never reflected a separate cash channel. Disabling the phantom + raising SEB Kort budget to match actuals netted out — no new cash leaked. Bullet dropped from the slide.

### 30. Cash-flow chart refresh from Finops: API ≠ UI, validate against the live page the user looks at

When the user says "the model has been updated, refresh the cash slides", **the chart visible on the rendered slide must match the live Finops UI the user is looking at — not just the API endpoint a sub-agent happened to hit**. Failure modes that have actually bitten:

1. **Agent extracts at time T1, user reads UI at T2 > T1** — model can change in between; agent's JSON is already stale.
2. **API endpoint ≠ UI endpoint** — `/api/v1/cash-flow/forecast` may serve a different aggregation than the portal's `/analytics/cash_flow.html` page. Same model state, different views.
3. **Chart PNG cache in `slides/assets/charts/`** can serve a stale chart even after the JSON is refreshed — the cache key is hashed on input shape, not regenerated unconditionally.

**Procedure**:
1. **Before** a cash-slide refresh, ask the user (or screenshot-grab) the current Finops UI min projected balance + date. That's the validation anchor.
2. Refresh the JSON via Finops API.
3. **Delete `slides/assets/charts/`** before re-rendering, so the chart PNG is regenerated.
4. After render, compare the chart's trough to the user's anchor number. If they differ by more than rounding, **escalate to the user before shipping** — the API and UI are out of sync and the slide cannot be trusted.

**Hard-learned** (2026-05-20 → 2026-05-21, meeting #7 v0.124 → v0.127): refreshed cash data via Finops agent; agent saved `-862,731 SEK on 2026-05-28` to `cash-flow-forecast.json`; chart rendered from JSON; shipped v0.124. Henrik: *"you have totally ignored my request to have the graph updated with data from finops (API)"* — and shared a screenshot of the Finops UI showing `-900,549 SEK on 2026-05-28`. The API I hit four times (with and without cache-bust params) returned `-862,731` consistently, but the UI showed `-900,549`. The API and UI endpoints were serving different states because of asymmetric cache-handling: the UI route (`/analytics/cash-flow/forecast`, session-auth) ran `_run_rate_cache['expires'] = 0` before generating, while the API route (`/api/v1/cash-flow/forecast`, Bearer-auth) had no equivalent cache invalidation. The Bearer-token API could not reach the analytics route (302 → login), so no agent / script could reproduce the UI's fresh state on its own.

**Resolution** (CR-2026-05-21-cashflow-api-ui-parity, deployed 2026-05-21): Henrik patched the finance-ops backend so both routes delegate to two shared methods (`set_revenue_override`, `generate_forecast_with_overrides`) and a cache-aware `_get_run_rate` that **self-heals on `business_parameters` override changes**. The `/api/v1/cash-flow/forecast` route now accepts a `revenue_override_msek` parameter (>0 sets, 0/null clears, omitted leaves unchanged). UI and API now return numbers within ±1 SEK of each other, and a DB-side override flip is immediately reflected on the next API call (no 10-min cache wait). 5 regression tests in `test_cashflow_route_parity.py` lock this in. After the deploy, the API returned `-862,731 SEK on 2026-05-28` and the UI returned the same — confirming the UI's earlier `-900,549` figure was a *stale UI snapshot from before the model state had converged*.

**Operating rule going forward**: when the user's UI screenshot disagrees with the API by more than rounding noise, the **first** action is to surface the discrepancy to the user explicitly and ask whether (a) the model has been further edited since the UI was rendered, (b) the UI needs a "Generate" / hard refresh to pick up the latest state, or (c) there is an underlying engineering issue (cache, endpoint divergence). Do NOT silently pick one side and ship — the cost of asking is one message; the cost of shipping the wrong number to the board is much larger.

### 31. Cash-flow top-items panel: only deviations from monthly run-rate; sign discipline mandatory

The `top_forecast_items` panel on the cash-flow-forecast slide exists to explain **deviations from the monthly burn run-rate**. Quarterly items, annual items, one-offs, retiming events. It **must not** contain:

- Monthly salaries (whether to Sweden, India, or anywhere)
- Monthly recurring SaaS / cloud
- Monthly India operations tranches (T1 vendor, T2 statutory, T3 salaries, Padma SWIFTs — all monthly operational)
- Monthly marketing spend
- Anything that is part of the steady-state burn

If an agent (or you) pre-populates this panel with monthly recurring items, **remove them**. Document the convention inline in the data file (`_metadata.notes`) so future agent refreshes don't reintroduce them.

**Sign discipline**: all outflow `amount_sek` values must be **negative**. The render template colour-codes red-negative / green-positive, so a wrong sign produces a visually misleading slide (a payment OUT shown as green inflow). Always verify direction.

**Note format**: each item's `note` must be ≤1 line (~≤120 chars). The slide template renders notes inline; multi-line notes overflow into the next row, producing the "text overlapping" failure mode. Keep notes brief; details go in the speaker-input doc.

**Hard-learned** (2026-05-20, meeting #7 v0.125 → v0.126): the cash-flow agent populated `top_forecast_items` with **"India SWIFTs to Padma — May/Jun bundle" at +1,590,867 SEK** (i.e. positive — rendered as a green inflow). Henrik: *"this is nonsense to add as a positive cashflow thing"* and *"these are just two months' regular payments! That goes against the whole idea here. The list should include deviations from the regular monthly flows!"* Both errors at once: regular monthly item AND wrong sign. Also the agent's notes ran 246–538 chars, overflowing into the next panel row. Dropped India SWIFTs, dropped Forvis slutfaktura (already past in actuals window), trimmed remaining notes to ≤105 chars each, and added a `_metadata.notes` sentence documenting the convention.

### 28. Financial source data — where to find Q1 P&L, prior-year, and budget figures

**Quarterly P&L actuals + prior-year comparison** (Sonetel AB, koncernen):
- Canonical machine-readable: `~/Library/CloudStorage/Dropbox/Sonetel/Financial/<calendar-year>/Quarter/<Q>/Kvartalsredogörelse/data.json`
- Path for Q1 2026: `Sonetel/Financial/2026/Quarter/Q1/Kvartalsredogörelse/data.json`
- The P&L lives in `tables.resultatrakning_koncern.rows[]` with `values[0]=Q1 current, values[1]=Q1 prior year, values[2]=trailing-period (usually rolling 12mo or full prior fiscal)`. Column labels: `tables.resultatrakning_koncern.columns`.
- KPIs (ARR, revenue, EBITDA, churn, etc.) with prior-year are at `kpis.<metric>.{current, prior, ...}`.

**Excel-original from BDO** (backup source for cross-check):
- `Sonetel/Financial/<year>/Quarter/<Q>/Kvartalsredogörelse/Underlag från BDO/<date> Underlag BDO/SonetelKvartal*.zip`
- Cross-check the data.json values against the Excel when introducing a new row to the slide or when the analyst flags a discrepancy.

**Budget figures**: Finops API (`group_pl_budget` table for the relevant FY). Used as the `budget` field on the slide; the variance vs budget is on the slide. Out-of-scope: marketing-channel splits, plan-tier splits.

**Prior-year fiscal-year footgun**: Sonetel changed fiscal year from Jul–Jun to Jan–Dec at the 2025-05-22 EGM. **Q1 2025 (calendar)** = the **old "Q3 jan-mar 2025"** in `Financial/2024 2025/Quarter/Q3 jan-mar 2025/` if you ever need to go beyond what the KR data.json carries. But the KR data.json `values[1]` is already mapped to the calendar-Q1 prior-year (per `columns` field), so you should never need to spelunk the old fiscal folders for the standard Q1 P&L slide.

**Apply**: any time a slide needs prior-year or budget P&L data, read from `Kvartalsredogörelse/data.json` first; only descend into the BDO Excel if a number doesn't match or you need a row the KR doesn't surface (e.g. account-level detail).

### 29. "Solvable" Yes/No is honest — don't dilute to "Within scope" or "Effort tier" just to be diplomatic

When a board reviewer asks why something is marked "✗ No" / "unfixable" on an analysis slide, the reflex is to soften: rename to "Within scope", split into effort tiers, etc. Resist. Clear binary status is more honest than diplomatically vague language, especially on a board slide.

The case for keeping the binary: "✗ No" on the churn analysis means *the underlying gap is external (regulator, third-party platform, upstream provider, Quarter+ feature build with no commitment) or wouldn't actually retain customers*. By definition this is outside what Sonetel can fix at reasonable cost. Calling it "high effort" or "out of scope" makes it sound like a budget question — which it isn't, the gap is structural.

**Rule**: if a binary status field truthfully captures the operating reality, keep it binary. Don't add a third tier just to look thoughtful. The footnote can spell out what "No" means (regulator / third-party / etc.) without diluting the column itself.

**Hard-learned** (2026-05-16, meeting #7 v0.101): Sebastian (board) flagged: *"hur kan något inte vara 'solvable' eller un-fixable? I princip bör väl allt gå att lösa men till olika kostnader och level of effort?"* Initial instinct was to rename `Solvable` → `Within scope` or split into effort tiers. Henrik corrected: *"On #3 I think this is splitting hair. If we have to change regulations in country X to resolve it, it is by default impossible. It is better with clear language, than deceivingly vague language."* Kept the column as-is.

### 32. Finops `group-pl` is PRE-consolidation — apply the koncern eliminations (use `scripts/build_financials.py`)

The `GET /api/v1/group-pl/{fy}` endpoint returns **pre-consolidation** category lines (parent + India aggregated) — its `calculated.ebit`/`profit_loss` are NOT the koncern result. To get the consolidated koncern P&L you must apply the `consolidation_adjustments` per line:
- `india_support_markup` (20%) → add to **Personal-/övriga rörelsekostnader** (opex)
- `india_rd_markup` (10.9%) → add to **Av/nedskrivningar** (depreciation)
- `india_dividend` → add to **Finansiella poster** (dividend income eliminated in consolidation; fires only some months, e.g. January — **missing it silently breaks any quarter that includes one**)

Always **reconcile the computed PBT against `consolidated_profit[i]`** — if they don't match, an adjustment is mis-keyed or missing. **Do NOT hand-derive this each cycle** — run `scripts/build_financials.py --period YYYY-MM|YYYY-QN --reconcile` (month or quarter), which applies all three eliminations, derives the koncern budget, and emits/patches the `pnl_table` rows. (Hard-learned 2026-06-08, June board update: hand-derivation silently dropped the R&D-depreciation markup due to a wrong adjustment key; the reconcile check caught it.)

### 33. SaaS40 uses the PUBLISHED statutory EBITDA — NEVER Finops EBITDA

SaaS40 (Rule of 40) = **Nettoomsättning YoY growth % + EBITDA-marginal %** (canonical def in the `kvartalsredogörelse` skill; NOT ARR-based). The EBITDA component is the **published BDO statutory basis = Rörelseresultat + Avskrivningar**. **Do not compute it from Finops** — the Finops-vs-statutory EBITDA gap is **non-constant and sign-changing** (Q1'26 +382K, H1'25 −389K), so no fixed offset works; Finops would print ~45% vs the published 40% for Q1 2026. Source per-period figures from `Financial/<year>/.../Saas40/Saas40 <period> v1.{md,xlsx}`. Published trend (declining): H1'25 70% · Jul–Sep'25 60% · Q1'26 40%. Rendered via the **`saas40` slide type** (stacked growth+margin bars + 40 benchmark line + component table; see `render_saas40_chart` + template branch). (Hard-learned 2026-06-08.)

**Closed periods stay published; the OPEN current quarter gets an INDICATIVE QTD point (deterministic, Henrik 2026-07-07).** The rule above ("never Finops") governs *closed, published* quarters — never overwrite H1'25/Q1'26/etc. with Finops values. But the *current* quarter has no published figure yet, and the board wants an early read. So `build_financials.py --saas40 --period YYYY-QN --write` computes a **quarter-to-date** point from the **booked** months only (Finops consolidated basis = Rörelse + avskrivningar), labels it **"Qn YYYY (QTD)"**, upserts it onto the slide (replacing any prior same-quarter row), and sets a slide `notes` caveat *"…is quarter-to-date (Apr–May 2026), indicative — Finops consolidated basis, pre-audit."* Growth% is basis-independent and solid; **margin% typically overstates the eventual published figure** (Finops monthly margins ran 33–44% vs Q1's published 28%), so the QTD SaaS40 is a directional early read, not a forecast. When the quarter closes and BDO publishes, **replace the "(QTD)" row with the published figure** (drop the caveat). This is additive — it never regresses a published number, so it's consistent with the determinism-tradeoff rule below.

### 34. `group-pl` budget is only 6 lines — financial + PBT budget is an API gap

The endpoint returns a `budget` array on only: `cogs`, `depreciation`, `india_support`, `marketing`, `ebitda`, `gross_profit` (same with `?view=budget`). Derive the rest: `net_sales_budget = gross_profit_b − cogs_b`; `opex_budget = ebitda_b − gross_profit_b`; `ebit_budget = ebitda_b + depreciation_b`. **There is NO budget on the financial lines or `profit_loss`** in the API — even though the **Finops UI displays them**. So the financial-items and Resultat-före-skatt budget must be supplied manually (ask Henrik) until the API is fixed (draft CR `financial-ops/docs/plans/CR-2026-06-08-group-pl-full-budget.md`). The FY budget is **koncern-level** (confirmed Henrik 2026-06-08), so it compares directly to consolidated actuals.

### 35. Board-update mode — lighter financials-only deck

The 1-hour **board update calls** (not numbered board meetings, no minutes) use a lighter deck = the **financials block** (P&L → SaaS40 → KPI snapshot → breakeven → 13-month trends → cash position → cash-flow forecast) → the **Web traffic & conversion slide (§46)** → the **board action-log slide (§44)**, cover title "Board update", closing "Questions?". Agenda: "Financials", "Web traffic & conversion", and "Action log" items. Roll forward each cycle: **live slides on the latest complete month; P&L on the latest SIE-booked month (≈ current month −2)**; **and refresh the open action-log items from Sebastian's Excel + Henrik's status (§44)**. Folder: `Board meetings/<year>/<YYYY MM DD> Board update/`. First on the pipeline: 2026 06 09.

**Omitting non-financial section dividers.** The agenda can list items others present from their own decks (Roadmap/Prashant, Mobile app + Marketing/Tomas) — they belong on the Agenda slide but have NO content slides here, and Henrik doesn't want their divider slides cluttering the financials-only deck. Set `"section_header": false` on those `agenda_items` in `agenda.json` (AgendaItem flag, default true). `build_slide_sequence` then skips that item's divider while keeping it on the Agenda list; keep `section_header` true (default) on **Financials** so its "04 · Financials" divider stays. Result: cover → agenda → Financials divider → financial slides → closing.

### 36. Prefer deterministic generators over agents for Finops-sourced slides (Henrik directive 2026-06-08)

*"Doing it just on skills is too brittle."* For anything mechanically derivable from Finops (the P&L especially), use a **deterministic, reconciled script** (`scripts/build_financials.py`) rather than re-deriving by hand or via a read-only agent each cycle. The script is version-controlled, self-checks (PBT vs `consolidated_profit`), and is copied into the meeting `slides/` folder alongside `render.py`. Extend the same pattern to KPIs/trends/cash over time. The Finops agent (§ "Financial data") remains the fallback for data not yet scripted.

### 37. Breakeven & profitability slide = the Finops monthly-pulse formula, NOT ad-hoc EBITDA/EBIT math

> **SUPERSEDED 2026-11-04 by financial-ops CR-2026-11-03b — read this first.** The slide now comes from Finops `GET /api/v1/pulse/breakeven` via `build_financials.py --breakeven --period <any> --write` (`breakeven_from_api`), the same figures as the Pulse page. **Box 1 "Breakeven"**: target from the **last 12 booked months** (FX-adjusted by Finops), compared with the latest completed month's **actual** revenue (that part of the rule below still holds). **Box 2 "Cash-flow positive"** (updated 2026-11-04 after Finops added `cash_forward.sales_needed_sek`): same Target / Actual / Gap shape as box 1. Target = monthly sales needed to cover every payment in the next 12 months (average, incl. planned cost increases, loan repayments and interest; late bills excluded), actual = the same actual revenue as box 1. Scope line says so. Note line = where cash dips (lowest balance + date, and the warning line if crossed). Don't show the Pulse's raw mix (average monthly change, "6 of 12 months below zero", lowest balance) in the box: three measures in one box was unreadable (Henrik 2026-11-04: *"impossible for anyone to understand"*); an interim three-balance version (v0.23) was replaced by this. Keep one measure per box; Finops status green/amber/red → box ok/warn/critical. `--fx-factor` no longer applies. Why: one month's costs decided the old threshold (the India bonus month, one-offs), and "cash flow positive" ignored loan repayments — Nov 2026 showed "+24% above cash flow positive" while the 12-month forecast had 6 negative months. Boxes carry preformatted `rows` + `scope`; amounts to 2 decimals (2.51 vs 2.56 at a 2% margin). The rest of this section describes the old one-month method and is kept for history.

The breakeven slide MUST match the Finops monthly-pulse "Breakeven & profitability" panel — Henrik checks it against the pulse. The pulse formula (`GroupPLService.calculate_breakeven_runrate` + `DailyPulseService.get_breakeven_assessment`, wired in `portal/blueprints/analytics.py`):
- **Latest *booked* month**, consolidated/adjusted P&L.
- `fixed_costs = gross_profit − adjusted_profit`, where adjusted_profit = `runrate_profit` (= consolidated + currency/management adjustments).
- **breakeven revenue = fixed_costs / gross-margin%**
- **cashflow-neutral = breakeven − |depreciation| × (1 − GM%)** (depreciation is the PRE-consolidation `categories.depreciation` line).
- Targets **FX-adjusted** for the move between the cost month and the actual-revenue month (factor ≈ 1 + 0.6 × (rate_now/rate_pl − 1)).
- **The "actual" on the BOARD slide = the latest completed month's ACTUAL net revenue** — `SUM(net_revenue_usd)` from `customer_monthly_revenue` (= Finops `get_month_actual_revenue`), served at `GET /api/v1/analytics/revenue/trends`, converted USD→SEK. **NOT booked MRR, and NOT the pulse's run-rate.** This is the one deliberate deviation from the pulse: the pulse compares a forward *run-rate* to the target, but Henrik wants the board to compare the breakeven point against **real revenue** (2026-06-08: *"Is this run rate??? it is supposed to be May Actual revenue"*). `achieved = actual ≥ target`. **State both months in the subtitle**: "Breakeven from <cost-month> costs · actual = <revenue-month> revenue".

Use `build_financials.py --breakeven --fx-factor <f> [--usd-sek <r>] [--write <data.json>]` — it computes the targets from group-pl AND **auto-pulls the latest completed month's actual revenue** from `/analytics/revenue/trends` (override with `--actual-msek`). Targets reconcile to the pulse's raw targets; only the small FX factor (~1.005) and USD→SEK rate are inputs.

**"Cash flow positive" is an OPERATING measure — caveat it when cash is falling (Henrik, 2026-07-07).** The cashflow-neutral target = breakeven − |D&A|×(1−GM%) is pure P&L/EBITDA (group_pl_service.py:941-946): it adds back the whole "Av- och nedskrivningar" line (tangible depreciation **and** intangible amortization) but **excludes loan amortization (~98K SEK/mo principal repayment), interest, VAT/tax timing, working capital, and CEO-loan repayments** — those live only in `cash_flow_forecast_service.py`, never in the breakeven path. So a month can read **"cash flow positive: achieved" while the bank balance still falls** (which is exactly what the cash-position slide shows). So the board doesn't misread the green box, the breakeven slide carries a one-line `breakeven_note` caveat. **`build_financials.py --breakeven --write` now emits this caveat by DEFAULT** (via `setdefault`, so a deck can override it with a period-specific wording — e.g. this deck's July note names the quarterly VAT): *"'Cash flow positive' covers operating costs only — it excludes loan repayments, interest and timing items, so cash can still fall in a month shown as achieved."* Every future generated breakeven slide therefore has the line automatically. If you hand-author a breakeven slide, add the note yourself. Confirm the exact inclusions/exclusions against the code if you reword it (they're EBITDA-operating only).

**CORRECTION (2026-11-03) — interest IS in both targets.** `fixed_costs = gross_profit − runrate_profit`, and `runrate_profit` is profit AFTER financial items (consolidated PBT + FX adjustments only). So "Breakeven" means profit after interest ≥ 0, and "Cash flow positive" = that minus the depreciation add-back: **it includes interest and excludes only loan repayments (and VAT/timing)**. The earlier caveat "excludes loan repayments, interest…" was wrong. Henrik asked to make the exclusion clearer: each box now carries a `scope` line from the generator ("Profit after interest" / "Includes interest. Excludes loan repayments."), and the default `breakeven_note` no longer mentions interest.

**The target is also a single-month cost snapshot — so it's volatile** (confirmed 2026-07-07, group_pl_service.py:908-946): both targets are built from ONE booked month's costs (± FX/consolidation overlays), with no averaging/annualizing. A seasonal *operating* cost (audit, AGM, annual license) raises the target only in the month it books; a month carrying it shows an artificially higher (harder) target, a light month a lower one. This is a verbal/speaker-note point, NOT slide clutter — keep it off the slide (§10). YTD columns (§ P&L `--ytd`) are the antidote to this single-month lumpiness on the P&L slide.

**Hard-learned (2026-06-08, June board update):** (1) an earlier read-only agent invented its own two-basis "Breakeven (EBITDA) 1.54 / Cash-flow (EBIT) 2.66" math — wrong; reproduce the pulse formula, never compute ad-hoc. (2) The first faithful reproduction used the pulse's **run-rate** as the actual (2.46) — Henrik rejected it; the board wants **actual revenue**. Final June figures: April-cost breakeven **2.15** / cashflow-neutral **2.00** MSEK vs **May actual revenue 2.54** (both achieved). (3) The breakeven slide must also **state which month the cost side is from** (Henrik) — the generator's subtitle does this. The pulse assessment + run-rate aren't served as JSON, but the actual monthly revenue IS (`/analytics/revenue/trends`).

### 38. Finops data sources for the cash & revenue slides — and their gaps

Where each figure on the financial slides actually comes from (hard-won 2026-06-08):
- **Actual monthly net revenue** = `GET /api/v1/analytics/revenue/trends` (= `SUM(net_revenue_usd)` from `customer_monthly_revenue`, the same source as Finops `get_month_actual_revenue`). This is the **only complete monthly net-revenue series**. Use it (× USD/SEK):
  - as the breakeven **"actual"** (§37);
  - to **fill the Net Revenue (SEK) 13-month-trend** when statutory `net_sales` isn't SIE-booked yet. The Finops trend file leaves recent months `null` → the SEK bars go missing on the slide (Henrik flagged this). Backfill the unbooked tail from `revenue/trends`. (Booked months reconcile: April statutory `net_sales` = `net_revenue_usd` × month FX.)
- **Bank actuals** — `GET /api/v1/bank-transactions/<YYYY-MM>` is frequently **empty (0 transactions)**; the bank-CSV import lags badly. **Do NOT rely on it** for actual payments, and don't conclude "no data" from it. Cash-position **drivers are model-based** from `/cash-flow/recurring` (non-monthly items firing in the target month: `annual_month==M` or `quarter_months` containing M, magnitude ≥ 5K). Sign convention in that table: **positive = outflow, negative = inflow**.
- **Slipped / deferred / catch-up payments** and **CEO loan + utlägg repayments to Henrik** ARE in JSON — `POST /api/v1/cash-flow/forecast` with a `start_date` covering the period returns **`days[].outflow_details`** (per-payment `amount_sek` + `description` + `category` recurring|scheduled). Deferrals are flagged in the description text: grep for `delayed from <month>` / `Försenad` / `delayed from March`. The Henrik payback items have `recipient: "Henrik Thome"`. (E.g. June update: the DBT loan repayment 134K + interest 16K = **150K was "delayed from April 28 — credit line saturated"**; plus Adyen + Rainbow April invoices ~54K paid in May.) Beware false positives (a long note may contain "delay" incidentally — verify it's actually a deferral). They carry mid-revision plan notes ("PLAN-*", "CR-PLAN-M", "SUPERSEDED <date>") — exclude superseded rows.

  **Two DIFFERENT panels — don't conflate them** (cost a flip-flop on 2026-06-08):
  - **Cash position "items outside monthly run-rate"** (backward, what happened this month): show genuine deviations from the normal monthly flow. A payment that **slipped/deferred** between months IS such a deviation and belongs here — e.g. the **DBT loan repayment that slipped April→May** (−150K, "delayed from April 28, credit line saturated") was *correct* to show (Henrik confirmed). It's the *timing anomaly* that's the deviation, not the recurring nature.
  - **Cash-flow forecast "top items impacting forecast"** (forward): show deviations from the run-rate ONLY. **Exclude regularly-scheduled recurring payments** (India ops, salaries, SaaS, telecom, the regular DBT) — they're the base run-rate, not a highlight (Henrik 2026-06-08: *"Recurring monthly payments should not be highlighted"*). **Always include the CEO-loan + utlägg repayment to Henrik** (`recipient: "Henrik Thome"`) — financing, non-recurring — *"I am missing repayments to me"*; show it **aggregated and carried each deck until settled**.
  - Henrik's "recurring shouldn't be highlighted / missing repayments" critique was about the **forecast** panel, not the cash-position one. When he flags a panel, confirm WHICH slide before editing — I edited the wrong one and had to restore it.
- **Transient empty responses:** several Finops GETs (revenue/trends, bank-transactions) occasionally return an empty body on first hit — **retry 2–3× before trusting a "0"/empty result** (a false "0" led to a wrong "no data" conclusion this session).

### 39. Verifying renders without image access, + the variance-colour CSS gotcha

**Verifying the PDF when you can't view it as an image.** In long sessions the image-read budget runs out (PNG/PDF reads get rejected). Verify renders deterministically with `pdftotext` instead:
- **Overflow / fit check** (e.g. a wide pnl table): `pdftotext -bbox -f N -l N deck.pdf /tmp/p.html` then compare the max `xMax` of any `<word>` against the `<page width>` — if `xMax < width`, it fits; also check column x-positions don't overlap. This is how the 7-column (+YTD) P&L was confirmed to fit.
- **Content check**: `pdftotext -f N -l N deck.pdf -` → grep for the values/labels you expect (breakeven numbers, driver lines, subtitle text). `grep -c '<page ' /tmp/p.html` gives the page count.
- To actually see a page, rasterize small: `pdftoppm -png -r 96 -f N -l N deck.pdf /tmp/p` (keeps it under the 2000px image limit) — though even those reads can be rejected once the budget is gone; lean on the text/bbox checks.

**Variance colours need extra specificity.** `pnl_table` variance cells are `class="col-num variance-negative|positive"`. The rule `.pnl-table td.col-num` (specificity 0,2,1) **outranks** `.pnl-table .variance-negative` (0,2,0), so the black `col-num` colour wins and red/green never shows (Henrik: *"can 'bad' % numbers be red?"*). Qualify the variance rules as `.pnl-table td.col-num.variance-negative { … }` (0,3,1) so they win. The sign convention already encodes favourability (cost lines are negative numbers, so a less-negative actual → positive % → green = good), so a single sign-based red/green rule is correct for all lines.

### 40. Cash-flow forecast = the Finops UI's Daily Cash Balance Projection, pulled VERBATIM

The "Cash flow forecast — Daily projection" slide must reproduce the Finops UI chart (`portal/templates/analytics/cash_flow.html`) 1:1. Generate it deterministically: `python build_financials.py --cashflow --cashflow-out financials-data/cash-flow-forecast.json` (function `fetch_cashflow_forecast`, pulls `GET /api/v1/cash-flow/forecast`).

- **Plot `days[].running_balance` VERBATIM — never re-derive it.** It's the *absolute* daily cash balance (starts at the EOM-prior balance, e.g. −733,638 on 06-01). The old deck re-based the series to 0 and recomputed daily flows with *net-of-COGS* revenue (70,896/day), which sank the line to a false −1.14M min instead of the true **−859,749 on 2026-07-30**. Henrik: *"Cash flow forecast is wrong. See Finops UI version which is much better. Make the process deterministic."*
- **Reference lines are SIGNED plot values**, stored ready-to-plot: `0` (green), warning **−650,000** (orange), credit **−credit_line_sek** = −1,000,000 (red, a floor *below* the balance). The old data stored these as *positive* (+1,000,000, +200,000) so the renderer drew the credit line *above* the balance — nonsense. The **−650,000 warning is hardcoded in the Finops frontend** (`cash_flow.html` ~line 1416), NOT derived from `buffer_sek` (which is 200,000) — don't try to compute it.
- **Assumed-revenue DISPLAY = gross `run_rate_daily`** (84,000 SEK/day = 2.52 MSEK/month), matching the UI label — even though the balance internally uses the net-of-COGS inflow. Drop the old "Revenue assumption rationale: … net of COGS" banner (clutter).
- **`actuals_through_date` = `actual_revenue_summary.last_date`** → the grey actual/forecast boundary marker ("Revenue actuals through 06-07").
- **`top_forecast_items` is a CURATED board view** (recurring removed, repayment-to-Henrik added per §38) — the writer **preserves** it; NEVER overwrite from the API's amount-ranked `top_cost_items` (that re-introduces the recurring India bundle Henrik told us to drop).
- **General lesson**: when a deck chart looks wrong vs a Finops screen, the *frontend template* in financial-ops is the deterministic source of truth for the exact series, line values, and formulas — read it (read-only) and reproduce, rather than hand-deriving.

### 41. Henrik-authored narrative slides — write verbatim, don't synthesise

The narrative slides (Comments on the P&L, the breakeven caveat note, "My key focus", cash-flow commentary) are **Henrik's words**, not AI-generated (see the no-AI-synthesised-content feedback). When he hands you copy:
- **Write it verbatim.** Fix only unambiguous mechanical typos (`A/Btesting`→`A/B testing`, missing spaces). For word-level changes that alter meaning — `product lead growth`→`product-led growth` (the PLG term) — make the change but **flag it explicitly** in your reply so he can revert. Don't silently reword.
- **Trim only when he asks.** He'll say e.g. *"remove 'Roll out ' … these are implicit"* — then cut exactly that. Don't pre-trim.
- **Remove placeholders once he's done.** Leaving `[Henrik — add further points]` after he says *"I have no more to add"* is clutter — delete it.
- **Slides are repurposable**: title + bullets are data-driven, so "Cash-flow forecast — changes" → "My key focus" is just a title+bullets swap on the same `bullets` slide. No template change.
- **Caveat pattern**: the `breakeven` slide has a `breakeven_note` field (`<p class="slide-notes">` below the boxes) for a forward caveat — e.g. flagging that the system's profitability figures are *too optimistic* because of a known upcoming cost (the May Voxbone double-charge, ~14 KUSD over April run-rate). Use it when the deterministic number needs a human "but…".

### 42. Determinism roadmap — what's generated, what's blocked, and why

Henrik's standing goal is to make the deck deterministic (pull from Finops, not hand-derive). Status as of the June 2026 update:
- **Web traffic & conversion** (`build_neon_metrics.py` → `financials-data/neon-metrics.json`): new-visitor traffic + lead→payment conversion from the sonetel.com Neon DB. Deterministic; see §46.
- **Generated deterministically** (`build_financials.py`): P&L (`--period`; **YTD + Δ YTD columns are ON BY DEFAULT** — board standard, per Henrik 2026-07-07; pass `--no-ytd` only for the rare deck that shouldn't have them), breakeven (`--breakeven`; also emits the "cash flow positive" caveat by default — see §37), cash-flow forecast (`--cashflow`), **KPI grid (`--kpis --period YYYY-MM`)**. These reproduce byte-for-byte and should never be hand-edited.
- **Still hand-entered — and the honest blockers**:
  - **SaaS40 margin** — needs **BDO statutory EBITDA** (Rörelse + avskrivningar), which is **NOT in Finops** and whose gap vs Finops EBITDA is non-constant (see `saas40-statutory-ebitda` memory). The growth% half is Finops-derivable (nettoomsättning YoY), but margin% is not → can't fully automate. Low value anyway: these are *published, stable* historical quarters that don't change.
  - **13-month trends** `net_revenue_sek` — the monthly SEK values **mix sources** (some months statutory BDO, some operational USD×FX), and need per-month FX. Forcing a single deterministic formula would *regress* the hand-verified statutory figures. Don't auto-generate without first agreeing one consistent SEK basis with Henrik.
  - ~~**KPI grid**~~ — **DONE 2026-06-09.** `--kpis --period YYYY-MM` pulls the **Monthly Business Pulse VERBATIM** from `GET /api/v1/pulse/monthly?month=YYYY-MM` and maps each card 1:1 with the Finops UI (`portal/templates/analytics/pulse_monthly.html`). See §43 — this was NOT cleanly derivable from piecemeal endpoints; reconstructing it produced multiple wrong values, which is exactly what the pulse endpoint avoids.
  - **Cash-position trend** (EOM balances Dec→May) — Finops-derivable; the *drivers panel* stays curated (like `top_forecast_items`). Medium value.
- **Rule**: don't "make it deterministic" if the deterministic source is *less* accurate than the current hand-verified value (trends SEK, SaaS40 margin). Determinism serves correctness, not the reverse — surface the trade-off to Henrik rather than silently regressing a number.

### 43. KPI grid = the Finops Monthly Business Pulse, pulled VERBATIM (don't reconstruct)

`--kpis --period YYYY-MM` pulls `GET /api/v1/pulse/monthly?month=YYYY-MM` and maps each card 1:1 with the Finops UI (`portal/templates/analytics/pulse_monthly.html`). **Never reconstruct the KPI snapshot from piecemeal endpoints.** The first attempt did, and got *multiple* values wrong because the pulse's real logic is non-obvious:
- **Revenue = net revenue** (`customer_monthly_revenue`, e.g. 272 KUSD / −17% YoY), NOT subscription MRR (215 KUSD / −1%). Using MRR was wrong.
- **EBITDA = latest SIE-booked month with fallback** (April, −22%, 1.1 MSEK) — not whatever month you assume (March +53% was wrong).
- **SEK uses per-MONTH FX rates** (`_get_monthly_sek_rate`), so SEK MoM/YoY ≠ USD MoM/YoY (ARR YoY: +1% USD but −2% SEK). A single flat USD/SEK is wrong.
- **Budget lines** (ARR 30.0 MSEK −17.8% behind, Revenue 2.8 MSEK −9.8% behind) come from the pulse's budget comparison — not exposed elsewhere.
- Subscribers = `subscription_monthly` active enterprise_ids (not churn `end_of_month_customers`); acquisition MoM is on the daily-avg basis (−17%, not −13%).

**The endpoint had to be built.** The pulse was computed by `DailyPulseService.get_monthly_pulse_data(month)` but only served to the session-auth web page `/pulse/monthly` — no `/api/v1` route. So we drafted `CR-2026-06-08-monthly-pulse-api`, reviewed it to 9/9, and implemented it (additive read-only route, OBSERVER scope, returns the service dict unwrapped). **General pattern**: when a Finops UI screen shows data the deck needs and there's no `/api/v1` route for it, draft+ship a CR exposing the existing service method — never hand-reconstruct the computation from lower-level endpoints. The generator maps `kpis.{arr,revenue,customer_acquisition,churn,subscribers,ebitda}` → cells; budget line only when `budget_sek` present; tone = sign of YoY (churn neutral); EBITDA label carries `(actual_month)` when it lags the snapshot month. Parity-check the rendered values against the live UI screen after each pull.

### 44. Board action log slide — open follow-ups from prior meetings

**Every board update AND every quarterly board meeting carries a slide reviewing the OPEN board action-log items.** The board raises follow-up actions at each meeting; this slide keeps them visible and shows current status so nothing is silently dropped.

**Source of truth is Sebastian's Excel, NOT this pipeline.** File:
`~/Library/CloudStorage/Dropbox/Sonetel/Board/Board action log/Board Action Log <YEAR>.xlsx`
Sebastian maintains it. **This skill READS it — never writes back.** Henrik relays any status changes to Sebastian separately; do not edit the workbook.

Structure (sheet **"Action Log"**, three labelled sections down column B; data columns: **C = TASK, D = OWNER, E = Comment/status**):
- **A. CLOSED ACTIONS** — done since last meeting; excluded from the slide (or moved to the "Processed" sheet).
- **B. OPEN ACTIONS** — the live list. **This is what the slide shows.**
- **C. NEW ACTIONS** — actions just raised at the most recent meeting; fold into the open list.

Read it deterministically (openpyxl, `data_only=True`) — the section headers are the anchors, not fixed row numbers (rows shift as items are added/closed):
```python
import openpyxl
wb = openpyxl.load_workbook(PATH, data_only=True)
ws = wb["Action Log"]
rows, section = [], None
for r in ws.iter_rows(min_col=2, max_col=5, values_only=True):
    label, task, owner, comment = r
    if label and isinstance(label, str) and label.strip().upper().endswith("ACTIONS"):
        section = label.strip().upper()          # A./B./C.
        continue
    if section == "B. OPEN ACTIONS" and (task or comment):
        rows.append({"task": task, "owner": owner, "comment": comment})
```

**Process (do this every prep cycle — it's a required step, not optional):**
1. **Pull** the current OPEN (+ NEW) items from the Excel.
2. **Present them to Henrik** as a numbered list with each item's existing comment, and **ask him for the current status of each** — which are done (drop), which changed, what the one-line status is now. Do NOT guess status or roll forward last cycle's wording.
3. **Populate the slide** with only what the Excel + Henrik give you. The **no-synthesis rule (§1) applies fully**: task wording comes verbatim (trimmed to board-length) from the Excel; status comes from Henrik. Don't invent progress narrative.

**Slide rendering** — reuse `numbered_two_col`: one entry per open item, `text` = the action (trimmed to one board-length line), `badge` = the status, `badge_tone` mapped:

| Status in Excel comment | badge | badge_tone |
|---|---|---|
| DONE / CLOSED (just closed, worth showing once) | Done | `positive` |
| WIP / in progress / tracking löpande | WIP | `info` |
| PAUSED / on hold | Paused | `warn` |
| Not started / OPEN | Open | `neutral` |

Keep it to the genuinely open items (≈6–10); if there are more, the longest-stalled or highest-priority ones lead — don't shrink the font to fit everything. Follow the wrapping-is-a-trim-signal rule (§ writing rules): each entry one line. Henrik's fuller verbal commentary happens live in the meeting; the slide is the at-a-glance status, so a per-item free-text comment column is **not** on the slide by default. If Henrik later wants the comment text visible per row, add a dedicated `action_log` slide type (task + status pill + one-line comment) — that's a renderer change and triggers the standard QC cycle; flag it, don't sneak it in.

**Where it goes in the deck:**
- **Board update** (§35): append after the financials block, before the closing slide — either as its own agenda item "Action log" or under a short "Follow-ups" divider.
- **Quarterly board meeting**: its own agenda item near the opening/formalities (alongside the previous-minutes status, §2a) or at the close, per that meeting's agenda.

### 45. Line-chart series must tolerate null — a leading/embedded `null` crashes matplotlib

**Symptom** (2026-07-05, July board-update trends): render died with `TypeError: ufunc 'isfinite' not supported … could not be safely coerced` when a `trends_grid` line series (ARR) had a leading `null` (the revenue/trends API only returns from month +1, so the first window month was null).

**Why**: in `render.py`'s `render_chart()`, the **bar** and **stacked_bar** paths coerce `null→0` (`p.get("value") or 0`), but the **line** path passed raw values straight into `ax.plot`/`ax.fill_between`, which reject Python `None`. So a partially-populated or dead series (e.g. `arr_total` returning empty, or `revenue/trends` missing the oldest month) crashes only on line charts, not bars.

**Fix** (applied, ported to the skill's `render.py`): line path coerces `null→float('nan')` (NOT 0 — nan breaks the line into a gap; 0 would draw a false dip to zero), and `_format_y` filters nan via `[v for v in vals if v == v]`:
```python
vals = [(p.get("value") if p.get("value") is not None else float("nan"))
        for p in series.points]
...
_format_y(ax, series.y_format, [v for v in vals if v == v])  # v==v drops nan
```
**Apply to**: any `trends_grid` line series. Also a data-hygiene reminder: a leading `null` on a **bar** series renders as a misleading **0 bar** (looks like "zero that month") — when a series can't cover the oldest window month, prefer trimming the window (e.g. 13→12 months) over shipping a null/zero leading point. See §44's data pull.

**Hard-learned**: the `arr_total` ARR-trend series went empty the same week as the `customer_monthly_revenue` wipe (§ two separate rebuild casualties) — a dead upstream series manifests as this crash, not an empty chart. If a line chart crashes, suspect a dead/lagging source series first.

### 46. Web traffic & conversion slide — deterministic from the sonetel.com Neon DB (Henrik 2026-07-07)

Board action item: track **website traffic** + **lead→payment conversion**. Generated deterministically by `scripts/build_neon_metrics.py` (copied into the meeting `slides/`), which runs **read-only** SELECTs against the sonetel.com first-party-analytics **Neon** Postgres DB (project `sonetel-ab-testing`) and writes `financials-data/neon-metrics.json` (a `trends_grid` `data_ref`). Rendered as a 2-chart `trends_grid` (new visitors bar + conversion line, `y_format: percent`) — its own agenda item "Web traffic & conversion", placed after Financials, before Action log.

- **Connection**: reads `$AB_DATABASE_URL`, else `AB_DATABASE_URL=` from `~/Library/CloudStorage/Dropbox/Workspace/sonetel.com/.env.local`. Needs `psycopg2`. READ-ONLY session — never write to that DB.
- **Two series — REDEFINED 2026-09-10, see §56 before touching them**: `distinct_visitors` = plain per-month distinct visitor cookies in `ab_page_views`, excluding sign-in paths. `signup_to_paid_pct` = of visitors whose first `/sign-up/` page view fell in month M, the % who ever `purchase`d. The earlier `new_visitors` / `lead_to_payment_cvr_pct` definitions below are retired — both misled.
- **`drop_partial()`** removes the current (incomplete) month and a ramp-up first month (value <60% of the next) so only complete months show.
- **Caveats to keep in mind (don't necessarily slide them)**: history is SHORT (from ~2026-05) and `ab_page_views` **self-purges at 95 days** — so without a persistent monthly rollup on the sonetel.com side, this never shows more than ~3 months. CVR is `visitor_id`-cookie-attributed (~62%), so **understated**; "lead start" = a signup-page *view*, not a click; recent-month CVR ticks up as late conversions land; no bot filter. For multi-year history the board would need GA4/Search Console, or a rollup table in sonetel.com (a draft-CR into that repo, its side implements — not yet done).
- **Other Neon metrics available** (future slide candidates, in `ab_conversions`): full signup **funnel drop-off**, **geography** of leads, **activation** (trial→purchase), **UTM/channel** attribution, signup **failure** rates, plan-tier mix.

**Lead-source snapshot** (2nd chart on the web section): `build_lead_sources()` reads `portal_user_attributes` (per-account first-touch UTM) → a `lead_sources` bar series rendered full-width. **Only PAID/tagged traffic carries UTM** — organic SEO is untagged and lands in the "Direct" bucket (label it **"Direct/SEO"**, and google is 100% cpc so label it **"Google Ads"** — Henrik: don't imply SEO is in "Google"). Keep the untagged/direct bucket IN the total so it sums to 100% (Henrik: "non-UTM traffic part of the total picture"). Caveat: `portal_user_attributes` only started ~2026-07-02 → a few-days snapshot, not a trend. Result: Google Ads ~48% · Direct/SEO ~38% · ChatGPT ~6% (the AI-search surprise) · IG ~5% · FB ~2.5%.

**Adaptive `trends_grid` columns**: the grid sets `cols-1` (full-width, single chart e.g. lead-sources), `cols-2` (2-up / 2×2 for 2 or 4 charts), else `cols-3` (template `{% set n … %}`, CSS `.trends-grid.cols-{1,2,3}`). Fixed a latent bug where a 4-chart trends slide rendered 3+1 uneven.

**Chart-image width MUST be a fixed `mm`, NOT `width:100%` (WeasyPrint, 2026-07-07 — cost 3 rounds).** In the trends grid, `.trend-card img { width: 100% }` renders TINY (falls back to the intrinsic/default size) — WeasyPrint doesn't resolve the percentage against the grid cell reliably. Fixed `mm` works: **cols-3 → 71mm, cols-2 → 118mm, cols-1 → 246mm**. The tell: "graph is super small" in a full-width card. **Root cause: it's a `display:grid` quirk — `width:100%` on a chart img resolves FINE inside a `display:flex` container** (that's why `.cash-chart-card img { width:100% }` and the `chart_comment` slide work), just not inside the trends `grid`. So for grid use fixed mm; for flex, `width:100%` is fine.

**`chart_comment` slide type** = a chart (left, reuses `.cash-chart-card`/`.cash-grid` flex) + a board **commentary** panel (right, `comment: [str,…]`). Use it when a graph needs board narrative beside it (Henrik: "now it is just a graph — comment page needed suitable for board"). It reuses the trends chart-building (render.py handles `chart_comment` like `trends_grid`), so give it a `data_ref` + `trends_layout` with ONE chart (a squarish `figsize:[6.5,4.2]` fits the ~58% left column). The `ratio` y_format renders "13.1×"/"1.3×". If you add a new column count, give its `.trend-card img` a fixed mm width. A count/percent chart also needs `y_format:"thousands"`/`"percent"` and can set `show_values:true` + a wide `figsize:[11,3.2]` per layout entry.

**Action-log slide fits ONE page (never overflow to a header-less page 2).** 10 rows overflowed with the default `.slide-content` padding (20/22mm) + 34pt title. Fix: `.slide-actionlog` uses tighter padding (`15mm 24mm 12mm`), a smaller `--fs-headline-xl` title, compact table rows (`padding:1.5mm`, `line-height:1.22`), and short status text. Verify with pypdf that the title + last item are on the same page. A board slide spilling to a second page is a layout bug — compact or split, never ship the overflow.

**`trends_grid` supports a `notes` footnote (added 2026-08-04).** It was the only slide type
missing the `{% if s.notes %}<p class="slide-notes">…` block that `bullets`/`pnl_table`/`saas40`
already had, so a web/trends slide had nowhere to carry a one-line board comment. Added after
Henrik asked for a conversion-trend remark under the web charts. Keep it to one line (§25).

**[SUPERSEDED by §56 — kept for history.]** As of 2026-09-10 `ab_page_views` holds everything
since 2026-05-02 (the 95-day purge is gone) and the series no longer uses first-touch, so the
artefact below no longer occurs.

**Neon web metrics: the oldest month is ALWAYS wrong — say so, don't chart it naively.**
`ab_page_views` self-purges at 95 days, so the table's earliest date is exactly `today − 95d`.
New visitors are computed as first-touch (`MIN(timestamp)` per `visitor_id`), so anyone whose
real first visit predates the window is **re-counted as new in the oldest surviving month** —
that month is systematically **overstated**. In the August 2026 deck this made May look flat vs
June when the underlying trend was rising. `drop_partial()` does not catch this (it only trims a
ramp-up month <60% of the next). Until sonetel.com has a persistent monthly rollup, compare only
the two most recent complete months and treat the oldest bar as unreliable.

**Validating a traffic jump before it goes on a board slide** (Henrik asked "is this real?",
2026-08-04). Four cheap read-only checks against Neon, in order of diagnostic value:
1. **Daily series, not monthly** — a real lift moves the *median day*; a bot moves a few days.
   (Jun→Jul: median/day 5,548 → 7,096, and July's worst day beat May's median. Real.)
2. **Pages per visitor** — bots read hundreds of pages each. A May scraper showed up as
   **238 RU "visitors" generating 609,254 views (2,560 each)**; it inflated *page views* only,
   leaving the visitor count clean. Check `COUNT(*) / COUNT(DISTINCT visitor_id)` per country.
3. **Country mix month over month** — a new dominant country is the tell. Stable mix = real.
4. **`user_agent ~* 'bot|crawl|spider|headless|python|curl'`** — worth running but expect ~0%;
   scrapers that matter don't self-identify. Do not conclude "no bots" from this alone.
Note the correlated-subquery form of the first-touch query dies on ~7M rows; a plain CTE
(`WITH ft AS (SELECT visitor_id, MIN(timestamp) …)`) runs fine, and the read-only session
forbids temp tables.

**COUNT series must set `y_format: "thousands"` — NOT the default.** The `auto` y-format prepends `$` for any value ≥1000 (it assumes currency), so a people-count like `new_visitors` rendered as **"$175K"** (Henrik: "Why USD?"). For any non-currency count series, explicitly set `"y_format": "thousands"` ("175K", no `$`). Only actual USD series should use `usd_k`/`auto`.

### 49. Agenda slide spills to page 2 past ~11 rows — auto `dense` variant

**Symptom** (2026-08-29, meeting #8): an 8-item agenda with 4 sub-items rendered a 25-page deck
where 24 was expected. The extra page was the **agenda slide's own overflow** — the last item and
the Total row alone on a header-less page 2. Nothing is clipped and nothing warns; the deck just
grows a page.

**Why**: `.slide-agenda` is a fixed-height flex column with generous chrome — 16/18mm vertical
padding, a `headline-xl` title, `6pt` row padding and `body-lg` titles. That budget runs out at
roughly **11 rows** (items + sub-items + the Total row). Meeting #7's agenda had 11 and fit;
#8 had 13 and did not.

**Fix**: the template now counts the rows in Jinja and adds a `dense` class past 11, mirroring the
`bullets` dense pattern (§8b). No `render.py` change.

```jinja
{% set agenda_rows = s.agenda_items|length
                   + s.agenda_items|map(attribute="subitems")|map("length")|sum
                   + (1 if s.total_minutes else 0) %}
<section class="slide slide-agenda{% if agenda_rows > 11 %} dense{% endif %}">
```
```css
.slide-agenda.dense { padding: 12mm 28mm; }
.slide-agenda.dense .slide-title { font-size: var(--fs-headline-lg); margin-bottom: 4mm; }
.slide-agenda.dense .agenda-table td { padding: 3.5pt 10pt; }
.slide-agenda.dense .agenda-table .col-title { font-size: var(--fs-body-md); }
.slide-agenda.dense .agenda-table .sub-row td { padding: 2pt 10pt; }
```
Dense fits ~15 rows. Past that, cut agenda items rather than shrinking further — and note §"Keep
agendas brief" says 5–8 items anyway, so a dense agenda is already at the edge of Henrik's
preference.

**`check_fit.py` is necessary but NOT sufficient.** It sums a section's direct children against
its content box, so a slide whose body is a flex ROW (chart + panel, diagram + key) reports the
height of the taller child and misses the overflow. The rings slide passed the fit check and still
spilled a footnote onto a second page. **Always check the page count as well** — the two together
catch what neither catches alone.

**Verify**: count pages. Expected = 1 cover + 1 agenda + (one section divider per item, minus any
with `section_header: false`) + content slides + 1 closing. A page more than that is an overflow,
not a feature — find it with `pypdf` page-by-page `extract_text()`.

**Apply to**: the auto-generated `agenda` slide only.

**Hard-learned** (2026-08-29, meeting #8 v0.1 → v0.2): the board asked for eight agenda items
(Sebastian's four topics plus Annika's two plus formalities and the action log), which is one more
than the pipeline had ever rendered. Caught by a page count, not by looking at the PDF.

### 47. `data_table` — the generic table type, and the "one question per table" rule

`pnl_table` number-formats every cell (thousands separators, variance colouring) and only knows
actual/budget/variance columns, so it is useless for **price tables, competitor comparisons,
sensitivity ladders, and option/verdict grids**. `data_table` is the free-text equivalent:

```json
{
  "type": "data_table",
  "title": "Every avenue we looked at",
  "columns": [
    {"label": "Avenue", "align": "left"},
    {"label": "Would raise per year", "align": "right"},
    {"label": "Verdict", "align": "left"}
  ],
  "rows": [
    {"cells": ["Monthly plan prices", "0.35 – 0.70 MSEK", "Proceed."], "emphasis": true},
    ["Phone number prices, +$0.50", "2.19 MSEK", "No. We tried this in 2018–19."]
  ],
  "notes": "One line, ≤150 chars — see §20."
}
```

- `columns` accepts plain strings (first column defaults left-aligned, the rest right) or
  `{label, align}` dicts. **A prose column MUST be `align: "left"`** — `dt-right` carries
  `white-space: nowrap`, so a right-aligned sentence overflows the slide.
- `rows` accepts a plain list of cells or `{cells, emphasis}`. `emphasis: true` bolds the row —
  use it for the row the board should read first (the recommendation, the proposed price).
- Cells are rendered verbatim. Format the number yourself, including its unit.

**Two hard content rules, both learned the same session:**

1. **One question per table.** A table answers exactly one question. If a column exists to answer
   a *second* question, cut it. (Henrik, 2026-08-20, on a 3-column sensitivity table: *"Too
   confusing"* — the slide asked "how much does it raise?", "what share of revenue is that?" and
   "at what churn does it break even?" at once. Cut to two columns and it read instantly.)
2. **Never put an unexplained unit in a row label.** Analyst prose says "+1 point", "+3.2 points"
   of churn; a board member reads "point" and stops. Show the **resulting level** instead —
   `14.9% → 15.9% → 16.9%`, with the baseline in the column header ("If monthly churn goes from
   14.9% to"). Likewise "share of revenue" as a bare column header means nothing without the
   denominator. (Henrik, 2026-08-20: *"What points is is not clear. Nor is share of revenue clear
   what it means."*) **Generalise: any column header that needs a footnote to be understood is
   the wrong column header.**

**Unit consistency across a comparison column.** When a source doc quotes some options in
$/month and others in MSEK/year, convert them all to one unit before they share a column —
otherwise the board does the arithmetic mid-meeting. Convert deterministically from the source's
own stated FX rate and flag the conversion to Henrik.

**`two_column` gained `left_title` / `right_title`** in the same pass — uppercase rules above each
column, for then-vs-now comparisons ("2018–19" vs "What we propose"). Without them the heading has
to be faked as a first list item, which renders as a bullet.

**Hard-learned** (2026-08-20, price-changes deck): built for a standalone analysis deck summarising
`Financial/2026/Analysis/2026 08 20 Price increase analysis.md`. Reference `data.json` is at
`examples/price-changes-data.json` — it exercises `data_table` in five shapes (price change,
sensitivity ladder, option/verdict grid, competitor comparison, historical price path).

### 48. Analysis decks live outside `Board meetings/` — and framing is Henrik's call, not the source doc's

Not every board-facing deck is a meeting deck. A deck summarising an analysis for the board (or a
single board member) belongs **next to the analysis it summarises** — here
`Financial/2026/Analysis/<date> <topic> deck/` with the full pipeline (`slides/render.py`,
`template/`, `data.json`, `agenda/agenda.json`, `output/`). The directory guard at the top of this
skill is about not using the pipeline for non-Sonetel-board work; an analysis deck for the board
qualifies. Set `meeting.title` to the topic, `meeting_number: 0`, `location: null`, and
`section_header: false` on every agenda item — a single-topic deck does not want six divider
slides between twelve content slides.

**The source document's framing is a starting point, not the deck's framing.** The price analysis
was written as *"What we recommend"*. Henrik reframed it as *"the least bad approach, if we want
to raise prices — and the true impact from churn is unknown"*. That is a materially different
deck: agenda item 1 becomes "The least bad option", the cover subtitle becomes "If we want to
raise prices", and the uncertainty moves from a risks slide at the back to the subtitle of slide
one. **Ask how he wants it framed before drafting, or expect to rebuild.**

**Show the rejected options and why, not just the recommendation.** Henrik: *"Presentation needs
to show the thought process on the other avenues and the rationale for not pursuing. It should
also be clear on open questions."* A board deck that presents only the chosen option looks like
advocacy; one that lays out every avenue with its size and its verdict looks like analysis. The
working shape: **one overview table of all avenues (size + verdict)**, then a slide per rejected
avenue with the actual evidence, then a dedicated **"What we don't know"** and **"What we need to
find out"** pair at the back.

### 50. Visual slide types — charts and diagrams instead of a bulleted memo

**Symptom** (2026-08-29, meeting #8): the strategy and growth sections shipped as thirteen slides
of bullets and tables. Henrik: *"The presentation is quite boring. Can we add graphics to make it
easier to understand? It is just like an emailed bulleted list split across slides."*

**The rule this establishes.** A section that argues something — a gap, a ranking, a
sensitivity, a segmentation, a product stack — should carry **at most one or two prose slides**.
Everything else is a chart or a diagram. Reach for a bullet list only when the content genuinely
is a list of statements (decisions being asked for, caveats being disclosed).

**What was added to the pipeline**

*Chart features* (`render.py`, all kinds):

| Field | What it does |
|---|---|
| `reference_lines: [{value, label?, color?, style?, label_va?}]` | Named thresholds. Horizontal on vertical charts, vertical on `hbar`. |
| `band: {from, to, label?, color?, label_color?, label_va?}` | A shaded region — use it when the answer is a **range**, not a point. |
| `tone` on a point | `primary` (dark teal) / `warn` (red) / `muted` (grey) — one bar carries the emphasis. |
| `value_label_fmt` | e.g. `"+{v:.2f}%"`, `"{v:.0f}/day"`. |
| `kind: "hbar"` | Horizontal bars keyed on `label`. |

*New slide types*: `stat_row`, `layers`, `matrix_2x2` (see the slide-type table).

**Four things that bit, in order**

1. **Chart PNG filenames collided and one chart silently overwrote another.** The name was
   `trend-{agenda_number}-{chart_idx}-{title_slug}`. Two single-chart slides under the same
   agenda item, both with an empty series title, both resolved to `trend-3-0-.png` — the deck
   rendered the same chart twice with no error. Filenames now carry the slide's index in the
   deck. **If two charts look identical, check the filenames before checking the data.**

2. **Reference-line labels have to be given their own space.** Anchored at the axes edge they
   sit over the data; two thresholds a few units apart (104 and 113) overlap each other. The fix
   is to widen the x-axis by ~40% into empty margin and drop the labels there. **And a multi-line
   band label must anchor to the band's edge (`label_va`), never its centre** — centred on a
   band a few units tall it spills across its own boundary lines.

3. **When two thresholds are close, shade the band between them instead of labelling both.**
   This was the better slide anyway: the requirement genuinely is a range that turns on one
   untested number, and a shaded band says that in one glance where two colliding labels did not.

4. **CSS Grid + `writing-mode: vertical-rl` is unusable in WeasyPrint** (compounding lesson §3).
   The first `matrix_2x2` used a 2-column grid with rotated axis labels: rows came out uneven,
   cell content overflowed its own background, and the rotated label rendered **mirrored and
   overlapping** the cells. Rebuilt on nested flex (`.matrix-rows` > `.matrix-row` > cells) — even
   rows, no overflow. **And the axis labels turned out to be redundant**: the quadrant names
   ("Domestic, business" / "Cross-border, consumer") already carry both axes.

**Stop guessing at heights — measure. `scripts/check_fit.py` is the tool.**

`.slide` is `height: 167mm; overflow: hidden`, so an over-full slide is **silently clipped**
(§21) — and depending on how far it overruns, WeasyPrint may instead emit a header-less second
page (§49). **Page count proves nothing either way.** Four rounds were burned tightening padding
by guesswork before the box tree was actually read; twice the change made it *worse*.

```
python3 slides/check_fit.py
```

It renders `.last_render.html` through WeasyPrint, walks the box tree, and prints per slide the
content height against **that slide's own content box** (which differs — `.slide-cash`,
`.slide-trends` and `.slide-agenda.dense` all override the default 20/22mm padding). It exits
non-zero if anything is clipped. **Run it after every render that touches layout.**

Typical measured heights, for budgeting: default content box **125mm**; slim-header types
(`padding: 13–15mm 28mm 12–14mm`) **138–142mm**; a one-line `slide-title` at `headline-2xl`
**~27mm** and **~35mm on two lines**; `headline-xl` saves ~9mm; a two-line `slide-subtitle`
**~23mm**; a `slide-notes` footnote **~14mm**.

**The cheapest 10mm is almost always the title and the subtitle, not the content.** On the
`matrix_2x2` slide the subtitle restated what the quadrant names already said — deleting it
saved 14.5mm and made the slide better (§25 sub-rule 4). Diagram-carrying types get
`font-size: var(--fs-headline-xl)` on the title by default for the same reason.

**Hard-learned** (2026-08-29, meeting #8 v0.2 → v0.15): thirteen renders. Two were spent on a
chart that was silently a duplicate, four on layout guessed rather than measured, and three on
threshold labels that collided until the band replaced them.

### 51. Rehearse the deck with a virtual board panel — it finds what the writer cannot

**Symptom** (2026-08-29, meeting #8): after a full visual rebuild, Henrik still said the slides
were not easy enough to understand and asked for a review by a virtual board audience. Four
role-played reviewers found **two arithmetic contradictions a director would catch live**, both
of which had survived the author's own review, the fit check, and a source-fidelity audit.

**The pattern.** Rasterize the section (`pdftoppm -png -r 100 -f A -l B deck.pdf out/slide`) and
spawn reviewers in parallel, one per seat, each reading the PNGs with the Read tool. Requires the
user to have asked for it.

**Seats that earned their place** — tune to the real board's stated interests, but role-play the
archetype rather than putting words in a named director's mouth:

| Seat | What it uniquely caught |
|---|---|
| Chair (commercial) | that none of the chair's own agenda asks were answered, and no slide carried a cost |
| Marketing / digital | two slides proposing *different decisions*; legal exposure in the positioning; the repeat-it test |
| Investor (numerate) | every missing denominator; that a 9-unit band on a 200-unit axis cannot be read |
| **Cold read** | the highest-value seat — sequence failures and every undefined term |

**The prompt rules that made it work**, all load-bearing:
- *"You have NOT read the source document. Judge ONLY what is on the slide."* Without this they
  reconstruct the argument from the source and report that the deck is clear.
- *"Spend 10–15 seconds per slide"* — the real dwell time. Ask what they took away in that time,
  what they re-read, what they'd say out loud, and **what they might MISREAD at a glance**. The
  misread question is where the arithmetic contradictions surfaced.
- *"Quote the exact words or numbers that caused the problem."* Otherwise you get "slide 7 is
  unclear".
- *"Be blunt. Do not be encouraging."* And "rank hardest to easiest" — the ranking is more useful
  than the per-slide notes.
- Give them the exact page→slide map; they cannot see the agenda.

**What the panel reliably finds that self-review does not:** a figure stated two ways on one slide;
a chart whose title asserts what the chart cannot show; jargon invisible to the author (*"Goa"*,
*"the Skype wave"*, *"the rest is procurement"*); an approval slide with no cost; and terms used
several slides before they are defined.

**Two content rules generalised from the findings**

1. **Every share needs its denominator ON the card, not in the footnote.** "62% of revenue" with
   "~49% of company revenue" in the footnote is one slide asserting two values for one quantity.
   Put the base in the subtitle where it governs every card.
2. **Arrows between figures assert arithmetic.** A `stat_row` with `connector: "→"` says each
   number derives from the last. If one figure has a different denominator, the chain is false —
   a numerate reader does the division, gets a different answer, and stops trusting the deck.
   Either make it a true chain or drop the odd figure to the footnote with its own base named.

**Hard-learned**: both defects had been read past repeatedly by the author. The panel found each
one four times out of four, within minutes.

### 52. `value_labels_inside`, and the passthrough whitelist that swallows new chart flags

Bar value labels default to sitting **above** the bar. When a `band` or `reference_lines` sits
near the bar tops, they land on it and both become unreadable. Set `value_labels_inside: true` to
draw them just inside the bar top instead.

**The gotcha that cost a render**: `expand_data_refs()` copies presentation keys from the
`trends_layout` spec to the series through an explicit **whitelist**. A new flag that is not added
to that list is silently dropped — the render succeeds and the feature simply does not appear.
When a chart option has no effect, check the whitelist before debugging the drawing code.

### 53. Speak in the unit the board already holds, and give each lever a symbol

**Symptom** (2026-08-31, meeting #8): after two rebuilds Henrik still rejected the growth and
vision sections — *"we show far too much detail… boil this down to something super brief, few
words, graphics to support the message… People don't always relate to percentage points. We need
to make it child-level easy."*

**The unit rule.** Pick the one unit the section has already taught the board and price everything
in it. Here the deck opens with "we need 104 new paying customers a day", so every lever is worth
*N customers a day* — not percentage points. The conversion is arithmetic from the model's own
coefficients (+10/day = +2.37%, so 1% ≈ 4.2/day) and it turns four incommensurable units
(+1pp of base share, −0.5pp of monthly churn, +1pp of signup share) into one countable thing.
State the step in plain words too: *"one more in every hundred upgrades"*, not *"+1pp"*.

**`knob_row`** draws each lever as an amplifier dial — Henrik's own metaphor, used before. A
270° track from 7 o'clock, a coloured arc for how far this lever is turned up, a needle.
`fill` is 0..1 and `prepare_knobs()` computes the SVG arc paths, so the template stays
declarative. **Inline SVG renders reliably in WeasyPrint** — unlike CSS grid (§3) and
`writing-mode` (§51) — so it is the right tool for a small diagram.

**`flow_hub`** draws inputs → a central store → outputs, plus a connector to something outside
it. Built on flex with `→` and `↓` glyphs rather than drawn connectors; WeasyPrint places these
predictably where SVG arrows between HTML boxes would not.

**Two content rules that came with it**
- **A "candidates we have not priced" column is not a weaker version of the priced one** — say so
  on the slide (*"The right-hand column is not smaller than the left. It is unmeasured."*), or the
  board reads absence of a number as absence of value.
- **Every lever needs its "what we would do to turn it" next to it.** A sized lever with no named
  action reads as analysis, not a plan.

**And then the knobs failed too, for a sharper reason.** Henrik, on the rendered dials:
*"this is useless. There is no way for the reader to understand what matters — growth here."*
Two defects, both worth remembering:

1. **The dial angles encoded nothing.** The `fill` values were authored by hand to look plausible.
   A reader comparing two dials learns nothing, because the geometry is not the data. **If a
   graphic's shape is not computed from the value it represents, it is decoration.** The fix is
   `growth_stack`, where block height *is* the growth and the comparison is unavoidable.
2. **The unit collapsed into the lever.** Pricing "ten more customers a day" at "10/day of growth"
   is circular — the input and the output are the same quantity, so the biggest-looking knob was
   the most meaningless one. **Check that the common unit is an OUTPUT measure, distinct from
   every lever's own unit.** Percent of revenue growth works; customers/day does not, once one of
   the levers is customers/day.

**A layout trap that came with it:** the first `growth_stack` put labels in a column parallel to
the blocks, each label sized to match its block. The label column has its own minimum content
height, so it — not the data — drove the slide height, and shrinking the stack made the slide
*taller*. **Put the labels inside the blocks.**

**Hard-learned**: three rebuilds. The first added charts but kept the analyst's units; the second
added a metaphor whose geometry carried no data. What finally worked was the plainest possible
encoding — size equals magnitude — with the plain-words step beside each label.

### 54. Make the reference value the ORIGIN, not an annotation

**Symptom** (2026-08-31, meeting #8): a growth section was rebuilt twice and still failed. An
information-design review measured the rendered pixels and found all three charts had the same
defect — **the number the slide compares against was drawn as an annotation instead of as zero.**

- The gap chart ran a 0–185 axis to fit a wave that had ended; the decisive 9-unit requirement
  band was **8.5 px**, and the difference between "level" and "nine short" was **2–5 px**. Under a
  millimetre projected.
- The scenario chart's four bars spanned 512–585 px — a **14% length difference** carrying what
  the slide called the difference between comfortable and badly short. Zero-based, honest, and
  unreadable.

**The rule.** When a slide asks *"are we above or below the line"*, plot the **difference**, with
the line at zero. Differences of a common quantity have a true zero, so this costs nothing in
honesty and buys an order of magnitude in resolution. It also hands the section one convention —
**zero = what we need, teal above, red below** — which resolves most cross-chart colour
inconsistency as a side effect.

Applied here: monthly acquisition became **+7, +12, +3, −10, −4, −2** against 104/day instead of
111…102 on a 185 axis. The scenario chart became **0, +5, +11, +15** extra customers needed
instead of 104/109/115/119.

**A minimum bar size is a lie about the data.** The stacked-block version floored the smallest
block so its label would fit, drawing +0.46% about **50% taller than its value** — 1:3.5 against
the top block instead of the true 1:5.2. The floor is unfaithful precisely where the reader cannot
check it. If the smallest value is illegible at true size, **the axis is wrong**, not the value —
change the form (`growth_waterfall` gives every increment room on a −4…+8 axis) rather than
inflating the geometry.

**Colour must encode one thing, monotonically, or be uniform.** Four teal shades whose lightness
order did not match their value order is decoration fighting the height encoding. In the rebuild
colour splits on **timing** (dark = ships in September, light = Q4) — one meaning, one key, stated
in the footnote.

**And check the graphic is not arguing against you.** The stack's tallest block was the lever the
*next slide* de-prioritised, and the slide after that dated it Q4. A board member reading only the
chart leaves with the opposite conclusion. **Order by execution or conviction, not by size**, and
let the number column carry magnitude.

**`growth_waterfall`** is the form that fixed it: today's position drawn as the **range it actually
is** (−2.4% to +0.8% — wider than three of the four levers, and previously a footnote), each lever
as a floating increment in execution order, and the result as a range. `render_growth_waterfall()`
in `render.py`.

**A waterfall builds from ONE baseline, and the total is the sum of what is drawn.** Two related
errors, one after the other, both caught by Henrik:

*First*, the result was drawn as a floating range bar (+3.6 to +6.8) sitting on top of the
accumulation. Its top aligned exactly with the last increment's top, so the destination read as one
more step rather than as where you land — *"shouldn't the far right one be higher up?"*

*Second, and worse*: today's growth was a **range** (−2.4% to +0.8%), the increments were stacked
from the optimistic end (+0.8) and the total was drawn from the pessimistic end (+3.6). So a reader
traced the steps up to 6.8 and then saw the total stop at 3.6 — *"visually it seems as if the last
item doesn't deliver growth on top of the others."* It didn't, on the page. **Never let the
increment path and the total start from different points.**

The fix for both: **build from the flat line**. The chart becomes "points added", every increment
sits on the previous one, and the total column runs 0 → sum, so it is necessarily the tallest thing
on the chart. Today's range moves to the subtitle, where it is context rather than a baseline the
arithmetic has to carry. **When a starting position is a range, do not make it the origin of a
waterfall** — state it, and build from zero.

**Hard-learned** (2026-08-31, v0.29 → v0.33): three rebuilds of one section. Charts were added,
then a metaphor whose geometry carried no data, then a stack that inflated its smallest value.
What worked was moving the reference to zero. **When a section keeps failing, suspect the axis
before the chart type.**

### 55. `orbit` — concentric rings only work when radius means something

Henrik has asked twice for "the circles around the phone number, with closeness in feature to the
number". The trap is drawing rings because they look like a strategy diagram; the ring is only
worth drawing if **radius encodes a real quantity**.

Here it does, and the metric was already in the strategy: *"Nothing more than one hop from the
number. A call is zero hops. An online meeting is one. A conversation across a table is one. A
note-taking app is none."* Ring distance = distance from the asset the company owns, so ring 4 is
literally the edge of what the company will do, and "a note-taking app — never" sits outside it.
**Look for the distance metric in the source before inventing one** — same discipline as §54's
"the reference value is the origin".

**Form**: inline SVG rings on the left (WeasyPrint renders SVG reliably — §53), a colour-keyed list
on the right, one block per ring, features as status-tinted chips. Do not try to place feature
labels on the rings themselves; the arc maths is fiddly and the result is unreadable at slide size.

**The status column is the honest part and the risky part.** Populating shipped/missing/planned
from strategy memos is inference — a memo that says a competitor records calls does not tell you
whether *we* do. Populate it, then **put the whole column to the product owner for correction
before it is shown**. Saying "I inferred these, please correct" is cheap; a board slide asserting
a feature exists when it does not is not.

**What made this slide land**: ring 2 came out entirely red, which is the argument — three of its
four capabilities were specified in 2019 and never built, and call queues were the second
most-requested feature in 2020. The diagram did not have to say that; the colour did.

### 56. Website metrics: count visits, and divide by the page-view record — never by a client event

**Symptom**: the web slide showed "Lead → first payment" climbing 2.7 → 3.1 → 3.5 → 3.8% over
four months, and the Aug 4 deck told the board it was "hopefully the result of the persistent
work we are doing". It was mostly arithmetic.

**Why**: the denominator was visitors who fired the `signup_started` client event. That event
captured 50.2% → 48.0% → 44.0% of the people who actually loaded the signup page (Jun/Jul/Aug,
re-derived 2026-09-10) and is still falling (42.4% Sep-to-date). A shrinking denominator makes
the ratio rise with no change in conversion. Divided by signup-page *page views* instead, the
same months are **1.83 → 1.96 → 1.95% — flat Jul→Aug.** The second series had its own flaw:
`new_visitors` used first-touch (`MIN(timestamp)`), which re-counts every long-standing visitor
as "new" in the oldest month the table holds.

**Fix** (`scripts/build_neon_metrics.py`): `distinct_visitors` = plain `COUNT(DISTINCT visitor_id)`
per month, no first-touch; `signup_to_paid_pct` = of visitors whose first `^/([a-z-]+/)?sign-up/$`
page view fell in month M, the % who ever purchased. Label them **"Website visits / month"** and
**"Signup page visits → paid"** — cross-month cookie persistence is ~3.8% (Safari caps the cookie
at 7 days), so this counts visits, not people. 98%+ of payments land within 30 days of arrival,
so the latest complete month is materially final.

**Apply to**: any ratio on a board slide. Before charting one, ask what the denominator is
measured by. If a client-side event, check its capture rate against a server/page-view record
over the same months — a moving capture rate manufactures a trend.

**Board discontinuity**: the Sep 2026 deck re-plots the same months ~half as high as the Aug deck.
Say so once, in the slide's notes line; do not leave the board to notice.

**Hard-learned** (2026-09-10, meeting #8): the analysis already existed in a draft CR
(`Board/docs/plans/CR-2026-08-28-board-slides-consume-frozen-monthly-series.md`, §5) a fortnight
before the deck — nobody had read it into the skill. Upstream CR (sonetel.com, frozen monthly
series) is still unbuilt; when it lands, read `final:true` rows from it per that CR.

**§56 CORRECTION (2026-09-10, same day — read this before trusting the section above).**
Henrik asked "signup started = unique visitors?" and tracing it through sonetel.com reversed the
premise. The page-view "denominator" is NOT the ground truth this section assumes:
- signup-page rows in `ab_page_views` are written by **middleware on every request**
  (`src/middleware.ts` → `record-page-view.ts`), which skips only self-declared bots. RSC
  **prefetches** pass through middleware (comment at `middleware.ts:791`) and there is no prefetch
  skip, so prefetched sign-up links very probably count as visits. Uncaught crawlers are in it too:
  Aug 2026 had ~13.5K "visitors" on a Linux-Chrome UA with no country (9.6K of 11.4K Swedish signup
  "visitors"; Swedish capture 3.7% vs English 46%).
- `signup_started` `trigger:page_load` fires client-side in `useEffect` (`signup-page-instrumentation.tsx`)
  with **no consent gate** (Neon `internal` destination, `requiresConsent: null`). It is the closer
  count of real people who opened the page. Beware: `trigger:form_submit` rows share the event name —
  filter on `properties->>'trigger'`.
So "capture fell" may be junk growing in the log, not events being lost, and last month's rising line
may be partly real. **Neither ratio is clean. Prefer charting the count of new paying customers from
the site (no denominator) until sonetel.com filters prefetches and crawlers from `ab_page_views`.**
**§56 FINAL (2026-09-10, after the sonetel.com agent's report — this supersedes both paragraphs above).**
`build_neon_metrics.py` now implements `sonetel.com/docs/reports/2026-09-10-signup-conversion-clean-denominator.md`
and reproduces its table exactly (Jun 3.08 · Jul 3.48 · Aug 3.82%):
- **Rate** `opened_to_paid_pct` = per month, PEOPLE whose signup page really rendered
  (`signup_started` `trigger='page_load'`, exact match) → first `purchase` at/after that month's first
  opening. People = union-find over cookies via session_id, phone (form_submit) and account_id
  (signup_completed); months counted independently. Chart from June (May partial).
- **Visitors** `distinct_visitors` = robots excluded: robot signature (bot UA, empty UA, Chromium 79,
  Linux-Chrome with no country, ≥50 pages or ≥300 views) AND no site event other than the server-side
  `recommended_country_resolved`. Beacons are NOT proof of a person — the Aug-2026 robots run JS.
- **Paying customers** = distinct payers per month; shown next to the rate (Henrik's choice).
- **Website visitors are NOT comparable across 2026-06-10.** The browser beacon (`<AbPageViewBeacon>`,
  CR-2026-06-06) switched on 9–10 Jun and made cached pages visible for the first time: browser-only
  visitors went 0 → 37K (Jun) → 90K (Jul) → 99K (Aug) while server-logged visitors went 172K → 145K →
  138K → 141K. The Aug-4 deck's "traffic up" and the Sep-17 v0.75/0.76 visitor chart were this
  artefact (Henrik: "Where is a big jump in web traffic reflected in new paying customers?").
  Server-logged alone is also biased (CloudFront caching hides visits). **Don't chart a visitor
  trend spanning June 2026.** The slide shows the funnel instead: people who opened the signup page ×
  opened→paid ≈ payers — the three charts must multiply out; if they don't, a series is wrong.
- Henrik's decisions for the ATTEMPT-based rate (not on the slide; Jul–Aug only): fraud = email-path
  deny-list blocks only (Google-path blocks pay at ~10%); "already has an account" = duplicate.
- Terminal risk: `purchase` is the legacy app.sonetel.com webhook; when retired the numerator is zero.

Also: `trigger` in `ab_conversions` holds SQL-/command-injection probes from a scanner (bxss.me) hitting
`/api/track-signup` — filter to known values, and flag to sonetel.com.

### 57. Every deck is checked against the standing-slide manifest — gaps are chased, not dropped

**Symptom**: the meeting #8 deck was rendered with its financial slides and Henrik had to notice
that the web-traffic slide and SaaS40 were simply not there (2026-09-10). Neither was broken:
one lives on a different source (Neon, not Finops) and was never pulled; the other needed the
newly published Q2 report. Six more standing slides were also absent and nobody had said so.
Henrik: *"Skill needs to keep track of all this and chase me until data is available to render
slide."*

**Why**: nothing listed what a deck is *supposed* to contain. A slide with no data looked
identical to a slide nobody wanted.

**Fix**:
- `standing-slides.json` — the slides every deck carries: how to detect each in `data.json`,
  its expected period, its source, the build command, and who owns it when blocked.
- `scripts/coverage.py` — run from the meeting folder. Probes Finops, Neon, the published
  quarterly reports and the action-log workbook (it detects a Dropbox online-only placeholder
  instead of hanging on it); checks every standing slide and every agenda item that renders a
  divider; writes `slides/COVERAGE.md` with a chase list grouped by person; exits 1 while
  anything is outstanding. Statuses: OK · STALE · INCOMPLETE · BUILD · WAIT · WRITE · ASK.

**Rules**:
1. **Step 0 of every build, and the first thing in every session in a meeting folder**: run
   `coverage.py`. Open the reply to Henrik with what changed in the chase list since last time.
2. **Never call a deck done while it exits 1.** Report the chase list instead.
3. **BUILD items are Claude's**: do them in the same session, don't list them back to Henrik.
4. **WAIT/WRITE items are chased**: name the person, the one thing needed, and the item. Repeat
   every session until the status changes — that is the chase. Don't soften it after the
   third time.
5. A slide that recurs in two decks goes into `standing-slides.json` the same day.
6. `local_file` in the manifest means data already pulled into the folder: a source being down
   no longer blocks that slide, only its human parts do.

**Control**: the Aug 4 update deck (full standing set) comes back all ✅, exit 0.

**Hard-learned** (2026-09-10, meeting #8): two slides missed, both caught by Henrik rather than
the pipeline. A render that succeeds says nothing about whether the deck is complete.

### 58. Look at every chart PNG after a render — two defects no fit-check can see

**Symptom** (2026-09-10, meeting #8): after adding SaaS40 and the web slides, the deck rendered,
fit, and was wrong twice. (a) SaaS40 Q2 2026 (−16.2 growth, +33.8 margin) drew as a plain 18%
bar in the *margin* colour — reads "margin 18%, growth 0". The Aug 4 deck shipped the same
defect. (b) The conversion chart labelled its 0.25-step ticks with one decimal: 1.75 → "1.8%",
0.25 → "0.2%", so May (1.74%) appeared to sit on 1.8%.

**Why**: (a) `render_saas40_chart` stacked margin on `bottom=growth`; a negative growth bar went
below zero and `set_ylim(0, …)` cut it off. (b) `_format_y` percent used `{v:.1f}`.

**Fix** (`render.py`): negative growth is drawn below the axis in red ("Revenue decline YoY"),
the margin bar rises from 0, and the SaaS40 total is a black tick across the bar labelled
"= 18%", with the two components labelled at their ends. Percent ticks use `{round(v,3):g}`.

**Apply to**: any stacked bar whose components can go negative — never stack on a negative
`bottom`. After every render, `Read` each new PNG in `slides/assets/charts/` before telling
Henrik the deck is ready.

### 59. Deferred payments: prove them from dates, never from the absence of a keyword

**Symptom** (2026-09-10, meeting #8): I told Henrik "nothing was deferred out of August" after
grepping the forecast's `outflow_details` for `delay|försen|deferr|slipp|moved|postpon|skjut`.
Henrik: *"Not true. DBT eom aug slipped to sept."* The Finops row said *"Augustis amortering på
Lån 1 **uteblev** (kassabrist) och betalades manuellt 2026-09-07"* — a word the grep lacked.

**Why**: the notes are free text in two languages written by whoever edited the plan. No keyword
list is complete; a zero-hit search proves nothing.

**Fix — the check is structural**: for the month M on the slide, list every recurring and
scheduled outflow the plan dated in M (loans, interest, audit, VAT, salaries, CEO repayments)
and find each one in `GET /bank-transactions/M` by amount (±1%) and counterparty. Anything
planned in M with no bank match is a deferral candidate: look for the same amount in M+1 in
the forecast or bank, and **ask Henrik** about each one before calling it deferred or not.
Report "no deferrals" only if every planned row is matched. Also search `uteblev`, `betalades
manuellt`, `kassabrist`, `flyttad`.

**Batches hide payments**: a `(1) Corporate Access` row in the feed can be a batch that bundles several payments — 14 Aug 2026's −134,447 was BDO 125,904 + Skatteverket 8,543, so an amount search for 125,904 found nothing and BDO looked unpaid. When a planned payment has no match, check the batch rows whose amount is ≥ it, and ask Henrik to open that batch in Nordea.

**Read each plan row's own date and note before calling it "planned in M"** (2026-10-04, Oct update): I listed "DBT Lån 1 September 98,000, planned 28 Sep — deferred?" as an open question. The plan had no September amortisation at all — the pause (Sep 2026–Jan 2027, rows 25/61 closed `valid_to 2026-08-31`, restart rows 80/81 `valid_from 2027-02-01`) was already in Finops and in the Sep 17 deck's forecast note. The 98,000 I saw was the **2026-09-07 catch-up row for AUGUST**, which I merged with the 31,500 interest row on 28 Sep. A recurring row is live only between `valid_from` and `valid_to`; `enabled: true` alone means nothing.

**Also**: `/bank-transactions/M` holds outflows only (inflows are absent — net sums are
meaningless), and `Ny DEPOSIT VALUTA` rows are FX term deposits, not spending (§12).

**Hard-learned** (2026-09-10, meeting #8): the cash slide's standing rule is to list deferrals
(memory `cash-slide-deferred-payments`); a false "none" is the exact failure that rule exists to
prevent.

### 60. A slide can SPILL instead of clip — and check_fit could not see it

**Symptom** (2026-09-10, meeting #8): the 13-month trends 2×2 put its bottom row (churn,
subscribers) on a separate header-less page. **The 2026-08-04 board update shipped with exactly
this spill** (its p10 → p11) and nobody noticed. `check_fit.py` said "All slides fit".

**Why**: `.slide` clips overflow — but a `display:grid` body is *paginated* by WeasyPrint, so the
same `<section>` continues on the next page. check_fit measured each page's first section on its
own, so the continuation looked like a short slide with slack.

**A second, opposite defect — check_fit false positive**: the cash slide read **937mm** tall
while it painted fine. A box dump showed the `.cash-grid` flex row at 884.9mm with children of
80mm and 45mm. I first blamed the multi-`tbody` table; an A/B test (render the one section four
ways, measure the grid) disproved it: merging tbodies changed nothing, a **fixed-mm image width**
brought the grid to 79.9mm. Same family as §46: `img { width:100% }` is unreliable in WeasyPrint
containers — here it inflates the flex row's measured height.

**Fix**:
- `check_fit.py` now flags a page whose first section is the **same element** as the previous
  page's: `SPILLED pN->pN+1`, exit 1.
- `render.py` `expand_data_refs`: a 4-chart `trends_grid` defaults every chart to
  `figsize [6.6, 1.85]` (2.25 still clipped by 12.6mm; a 118mm image may be ≤ ~34mm tall).
- `style.css`: `.cash-chart-card img { width: 127mm }` (shared by cash, saas40, chart_comment);
  `.cash-drivers-card` is `display:block`.
- Keep cash-driver labels to one line (~35 chars, e.g. "DBT loan, Aug — deferred to 7 Sep").

**Method worth keeping**: when a measurement looks absurd, dump the box tree for that one page,
then A/B the suspected causes on that section alone before editing shared CSS.

**Apply to**: any grid/flex-wrap slide body; any table inside a flex column (use block).

**Chart SHAPE in a 2×2 (2026-09-10)**: the row height is capped ~33mm, so don't also use the full
card width — 3.5:1 flattens every trend (Henrik). Use **88mm wide** (figsize [5.2, 1.95]) and narrow
the COLUMNS to match: `.trends-grid.cols-2.rows-2 { grid-template-columns: 94mm 94mm;
justify-content: center; }`. Two dead ends: 44mm-tall charts clipped both 4-chart slides, and neither
`margin:auto` nor flex `align-items:center` moves a fixed-width image inside `.trend-card` — measure
the box tree before trusting either.
Rasterise suspect pages (`pdftoppm -r 60 -f N -l N`) and `Read` them — that is how both
defects were seen.


### 61. Date axes must adapt to the horizon — daily ticks at 600 days are a smear

**Symptom** (2026-09-10, meeting #8): Henrik set the cash-flow forecast horizon to 600 days
("We can change to 600"). The chart kept its weekly `%m-%d` ticks — ~85 overlapping labels, an
unreadable black band under the plot. check_fit cannot see this; only the rasterised page shows it.

**Fix** (`render_cashflow_forecast_chart`): past 120 days use `MonthLocator` with `%b %y`,
thinned to at most ~12 labels (`interval = round(span_days / 30.4 / 12)`); weekly ticks otherwise.

**Apply to**: any date-axis chart whose window is data-driven. When a user changes a horizon,
re-check the axis, not just the data.


### 62. Chart only windows with a consistent measurement method (Henrik directive 2026-09-10)

*"We should only show graphs were the data methodolgy is consistent and the trends aren't impacted
by changes in how we log or measure."* A logging change inside a chart's window is a reason to CUT
the window (`from_month`) or drop the chart — not to footnote it.

**Checklist before any trend goes on a slide:**
1. List every change to the series' writers in the window: `git log --since` on the tracking code
   (sonetel.com: signup instrumentation, `/api/track-*`, `record-page-view.ts`, beacon, `track-event.ts`),
   CR titles, data cutovers (e.g. AB-011 promotion 2026-07-02), retention changes, basis changes
   (statutory vs USD×FX in `net_revenue_sek`).
2. For each change, test capture with an independent signal before vs after (e.g. page_load share
   of render-traced visitors across the 2026-07-06 transport change).
3. Put the cut-off in `from_month` and the reason in the data file's `_metadata`.

**Known cut-offs (sonetel.com Neon):** page_load from 2026-05-13 (May partial → rates from June);
browser beacon 2026-06-10 (visitors from July). Finops series: see §42 on `net_revenue_sek`.

**Hard-learned:** the Aug 4 update told the board "traffic up" on the beacon launch.


### 63. Never hardcode a rate, a price or any market input — pull it for the period

**Symptom** (2026-09-14, meeting #8): the breakeven slide put August 2026 revenue at 2.31 MSEK.
The right figure was 2.36. `build_financials.py` defaulted `--usd-sek` to a **hardcoded 9.336**
while August's actual rate was **9.50895** — ~42,600 SEK understated, and the slide's headroom over
breakeven read 4.2% instead of 6.2%. The deck had already been sent to the board. It surfaced only
because a finops agent reconciled two revenue figures that differed between slides.

**Why it bit**: ~95% of Sonetel's revenue is non-SEK, so the FX rate is not a rounding detail; and
a default that silently works is never questioned — the KPI card (pulse, correct rate) and the
breakeven slide (hardcoded rate) drifted apart with no error anywhere.

**Fix**: `--usd-sek` now defaults to `None` → `fetch_actual_revenue()` pulls that month's
`fx_info.actual_rate` from `/pulse/monthly` and prints which rate it used. Pass the flag only to
override deliberately.

**Apply to**: any market input — FX, share price, interest, index. Fetch it **for the period the
figure belongs to**, print it, and store it in the data file's `_metadata`. If two slides show the
same quantity from different sources, reconcile them before the deck goes out (§26).

### 64. Generator fixes from the Oct 2026 update QC (2026-10-04)

- **Breakeven gap % from the unrounded actual.** `breakeven_from_pl` rounded the actual to 0.01 MSEK before computing gaps, overstating the gap % (7.6 vs 7.4). Fixed; `fetch_actual_revenue` no longer rounds either.
- **P&L title is patched with the period**, not just the subtitle — an August P&L had shipped titled "July 2026 — condensed P&L".
- **Financial-items and PBT budget now exist** in `group-pl/{id}.group_budget` (`financial_items`, `profit_before_tax`, per month) — §34's gap is closed in the API. Until the generator reads them, pass `--fin-items-budget` / `--pbt-budget` from that field.
- **KPI EBITDA tile: use the koncern P&L figure** (label "… (koncern)"), as the Sep 17 deck did. The pulse EBITDA is pre-consolidation (no India support markup), so it differs from the P&L by ~48K and the board sees two EBITDAs. Pulse `ebitda.mom_pct` is also wrong when `actual_month` lags the snapshot month (compares the month with itself → 0.0); compute MoM against the prior koncern month.
- **Cash-flow-neutral target keeps the pre-consolidation depreciation** (§37, matches the pulse) even though a reviewer flagged it as a basis mismatch — the pulse is what Henrik checks against. Raise it with Henrik, don't silently change it.

### 65. P&L header: group the columns by period, label them in plain words

**Symptom** (2026-10-04, Oct board update): Henrik on the 7-column P&L (ACTUAL · PRIOR YEAR · Δ YOY · BUDGET · Δ VS BUDGET · YTD · Δ YTD): *"It is a bit hard to understand what each column shows."* "Actual" doesn't say which month; "Δ YTD" doesn't say against what.

**Fix**: `build_financials.py` emits `pnl_column_groups` (`[{label, span}]`) and `pnl_column_labels` (key → display label) via `pnl_header()`, and sets the subtitle to "Koncernen, SEK" since the groups now carry the periods. The template renders a two-row header — **August | August budget | January–August** over **2026 · 2025 · Change | Budget · Actual vs budget | 2026 · vs 2025** — with a 6mm gap and a separate rule under each group (`<span>` border, not the `th` border, which runs continuously). `pnl_columns` keys are unchanged, so cell logic is untouched; decks without the new fields render as before. Quarter periods get "Q2 | Q2 budget | January–June".

**Apply to**: every `pnl_table`. Generally: a column header must name the period it covers; never a bare "Actual" or "Δ".

### 66. Rolling a board update forward — what went wrong on the Oct 2026 update

**Hard-learned** (2026-10-04, board update 12 Oct, September data). Each item cost a question from Henrik or a review finding:

1. **Check what Finops has actually booked before you assume "meeting month −2".** `GET /group-pl/fiscal-years` → newest FY → `/group-pl/{id}.periods`. August was not loaded yet, so the P&L generator failed and coverage called it STALE (owner Claude) when it was really WAIT (owner Henrik/BDO). `coverage.py` now probes the latest booked month and flags the lag.
2. **Every text carried over from the previous deck goes stale together.** Footnotes, `notes`, subtitles and action-log wording copied from meeting #8 still said "Q3 2026 is July only", "today" (meaning 17 Sep) and "end September". On rollover, list every `notes`/`subtitle`/free-text field in the copied slides and re-check each one against the new period. A generator re-run fixes only the fields it writes. **This includes `meta.cover_date_label`** — the Nov 2026 rollover rendered a cover dated "12 October 2026" until caught on page 1. Also drop last deck's one-off slides (e.g. "September without the production issues").
3. **Compare the forecast low point with the previous deck's, and explain the move before Henrik asks.** The low at 28 Dec went from −0.79 MSEK (Sep 17) to −1.15 MSEK. The board will put the two slides side by side. Ask a financial-ops agent (read-only) for a bridge from that repo's cash-flow log: model changes since the last pull, the change of starting month, and **actual vs plan for the month just closed**, which was the biggest item here (about −300K).
4. **Finops writes go through a financial-ops agent, and a permission denial ends the attempt.** If the agent's SSH/dbshell write is denied, it stops and reports the SQL. The board session must not run that write itself (a denial is not to be routed around). Give Henrik the ready SQL and ask him. Note that restart rows usually have **new ids** (here 80/81), and the originals (25/61) were closed with `valid_to`.
5. **Check a dip in the weekly payers-by-source chart against the daily purchase count before shipping.** The week of 7 Sep showed about half the usual payers. Neon `ab_conversions` purchases per day were 23–66 on 4–13 Sep against about 100 normally, while page views were normal. Say so on the slide or ask Henrik whether sales were really lost or recording failed. Don't leave the board to read it as demand.
6. **The Neon build (`build_neon_metrics.py`) takes 5+ minutes.** Run it in the background at the start and do the Finops work meanwhile.
7. **Run `coverage.py` from the skill path, not a copy.** It resolves `standing-slides.json` relative to its own location, so a copy in `slides/` crashes.
8. **Time zone.** Stockholm is on CEST until the last Sunday of October. Henrik said "CEET" for a 12 Oct call; the agenda says CEST.
9. **zsh:** a word that starts with `=` (e.g. `echo ====`) is expanded as a command path and fails the whole line. Use `echo "--"`.
10. **Coverage marks the action log OK as soon as the slide exists.** It does not check that the statuses are current. The Excel was still the 3 Jul version, and the slide carried the Sep 17 statuses. Always ask Henrik for current statuses (§44), whatever coverage says.

### 67. No % change when the figure crosses zero

**Symptom** (2026-10-12, Oct update, seen during the call): P&L "Resultat före skatt" −4,785 vs budget +171,796 showed **−102.8%**. Henrik: *"that is impossible?"* The arithmetic is right (a shortfall of 176,581 on a base of 171,796) but a percentage across a sign change reads as an error.
**Fix**: `build_financials.py` `pct()` returns `None` (rendered "—") when actual and base have opposite signs. Losses compared with losses (both negative) keep their % — same convention as cost lines.
**Apply to**: every variance %, on any slide. Check result lines (EBIT, PBT) near zero before shipping.

### 68. Analysis deck for management + board: ask first, one threshold story, review with two agents (2026-10-30)

**Symptom**: the in-app sales deck (Strategy/2026 10 App store commission/deck) scored 5/10 from a virtual board panel on v0.3 — no explicit ask, no total cost, and three different-looking break-even figures (18% on a chart, ~12% implied by a value table, 30–42% in the decision rule).
**Fix / rules**:
- **The ask is slide 1 and the closing slide.** Title "Proposal: approve …", bullets What / Budget / Downside / Test / Condition; `closing_message` repeats the decision with the full exposure (budget + fees), not "Questions?".
- **Every threshold says what it includes.** Break-even *with* build and running cost on the chart; value table explicitly "before build and running cost"; decision bands explain the margin above break-even. Otherwise numerate readers find a contradiction.
- **A downside figure and a full-year scenario figure must be labelled so they can't be confused** (pilot loss ≈ USD 4k vs "no lift" year −USD 36k).
- **Decision rules read best as a 3-card `stat_row`** (Stop / Adjust / Roll out) rather than a table.
- **Fill `presenter` on agenda items** or the agenda shows an empty PRESENTER column (reviewers called it sloppy).
- **`layers` with 4 bands: check_fit reports ~0.8 mm "CLIPPED" while the page renders fine** (bands stretch). Verify by rasterising; don't trim content to chase it.
- **Negative values on `hbar`** collide with their labels — use a `data_table` for signed outcomes.
- Directory guard: analysis decks may live next to the analysis (§48), here a Strategy project folder.
**Process that worked**: two parallel agents — a source-verification agent against the business case and a role-played board panel on PNGs (chair, investor, product/tech, cold read) — three cycles: panel 5→7→8→9, numbers 7→8→9.

### 69. P&L period: the quarter at quarter close, the month otherwise (Henrik 2026-11-03)

**Rule**: when the latest booked month ends a quarter (Mar, Jun, Sep, Dec), the P&L shows the **quarter instead of the month** — `--period YYYY-QN`, groups **Q3 | Q3 budget | January–September**, title "Q3 2026 — condensed P&L". In any other month, keep month + YTD. Never show month and quarter together (10 number columns is too much to read in 10–15 seconds). No mid-quarter "quarter forecast": Finops has no P&L forecast, and booked months + budget for the rest is just the budget again.
**Why**: September 2026 alone was −126K PBT while Q3 was +269K. The month alone undersold the quarter.
**How**: `--fin-items-budget` / `--pbt-budget` take the **sum of the quarter's months** from `group-pl/{id}.group_budget` (Q3 2026: −153,056 / 358,277). The generator now patches the title for quarter periods too.

### 70. Every deck opens with "Key messages" — the period in 4–5 bullets (Henrik 2026-11-04)

**Rule**: every board update and quarterly deck has a `bullets` slide titled **"Key messages"** under `items["0"]` (after the cover, before the agenda). It is a standing slide (`standing-slides.json` → `key_messages`), so `coverage.py` chases it.

**Build it LAST**, once every other slide is final — it quotes them, so it goes stale with them.

**Content — the shape used in Nov 2026 (Henrik signed it off):** 4–5 bullets, each a bold label + one short sentence, in this order:
1. **ARR** — month-on-month change first (Henrik: *"MoM growth in key KPIs is important. Especially ARR"*), plus revenue MoM. Say the currency (USD).
2. **Customers** — the clearest customer KPI move (churn, new customers/day, subscribers).
3. **Profit** — the P&L headline for the period on the P&L slide (the quarter at quarter close, §69).
4. **Cash** — what moved cash and where the forecast stands vs the credit line.
5. **Henrik's strategic message** — e.g. releases that unlock growth. His words, lightly edited; ask for it if he hasn't given one.

Nov 2026 example: *ARR. Up 1% from September (USD). Revenue up 4%.* · *Customers. Churn down to 7.6%, from 8.2% in September.* · *Q3 profit. Profit before tax 269 KSEK, up from 106 KSEK a year ago.* · *Cash. A 600 KSEK owner loan covered the India bonus and EU VAT. Forecast stays above the credit line.* · *Releases. Mobile and web app releases unlock growth potential and free up resources for other growth work.*

**Rules for the figures:**
- Every number must appear on, and match, the slide it comes from (KPI grid, P&L, cash). Re-check after any data refresh (§26).
- Don't claim a trend two sources disagree on. Nov 2026: subscribers were "+0% MoM" on the KPI slide but "+90" in churn data, so "subscribers growing again" was dropped.
- Lead with the good MoM news if that is the period's story, but tell Henrik in your reply when the YoY figure on the KPI slide points the other way (ARR +1% MoM, −13% YoY) — the board will ask.
- The no-synthesis rule (§1) is relaxed here by Henrik's request: draft bullets 1–4 from the deck's own figures, show them to Henrik, and say which ones you wrote.

### 71. Contributor decks: merge without header pages (Nov 2026)

`merge_deck.py` splices contributor PDFs into the rendered deck → `… vN + complete.pdf`, the file the board
gets. Configure in `agenda.json` per item: `"external_decks": [{"file": "contributions/<name>/<pdf>", "pages": "4-6"}]`.
- **Drop header pages** (Henrik 2026-11-08: "excluding unnecessary header slides"): use `pages` to leave out each
  contributor's cover, own agenda, section dividers and "Thank you" page. Look at every page first: image-only
  pages (no text) can still be content (Prashant's roadmap timelines).
- **Anchors:** a contribution goes before the start of the next agenda item that has its own pages: its divider
  ("05 …") or, now that dividers are off, its first slide's kicker ("5 · FINANCIALS"). Without the kicker fallback
  every contribution landed before the closing slide.
- A contributor topic missing from our agenda (Prashant's "Appraisal cycle", Nov 2026) is put under the nearest
  item; ask Henrik whether to add it to the agenda.
- After merging, look at a contact sheet of the merged pages, then `open` the `+ complete` PDF.
- Once the deck is sent, log "DISTRIBUTED" in the CHANGELOG; later changes are logged as post-distribution.

### 72. Subscriber data double count (SNTLRND-9836) — and a chart that guards itself (2026-11-09)

Finops' `subscriptions_positive_balance` double-counted Jun–Oct 2026 until 9 Nov 2026 (June 36,623 instead of
32,133). The Excel-style churn chart (`--subscriber-flow`, see Data files) has hard checks against Finops' verified
values and stopped the first build, before the fix had been deployed. Pattern: when Finops gives check values with
a data request, put them in the builder as `*_KNOWN` constants that stop the build, not just a one-off check. Any
other chart built from subscriber counts in the same window must be rechecked after such a fix.

### 73. Cash-flow forecast always shows a no-growth line (board request 2026-11-09)

Annika asked on the 9 Nov 2026 call what the 0.5%/month growth rests on, and asked for a scenario without it. Henrik
said "always in the presentations moving forward". The answer for the board: the 0.5% is Henrik's own management
assumption, set in the Finops portal on 2026-08-25, not derived from analysis.
- `fetch_cashflow_forecast` calls `/cash-flow/forecast` twice: stored growth, then `?revenue_growth_pct_monthly=0`
  (Finops CR-2026-11-09b; the override is per request and saves nothing). The result goes into
  `cash-flow-forecast.json` → `flat_scenario` (daily balance, min, min date, end balance). The chart draws it as a
  grey dashed "No growth" line under the blue growth line, with a legend.
- The script stops if the API ignores the override (an older build returns the stored rate): never draw growth data
  as the flat line.
- **NEVER POST `revenue_growth_pct_monthly: 0`**: it deletes the stored rate for every Finops user, with no log.
- How to read it: the low point is close in time (Dec 2026: −789K with growth vs −800K without), so growth barely
  moves it. Growth mainly changes the end of the horizon (≈ +2.4 MSEK vs +0.4 MSEK at 600 days). Say this when the
  board asks.

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
- `standing-slides.json` — the slides every deck is expected to carry (§57), incl. the Key messages opener (§70).
- `scripts/coverage.py` — checks a meeting folder against it; writes `slides/COVERAGE.md` (§57).
- `scripts/build_neon_metrics.py` — web traffic + conversion + lead sources from Neon (§46, §56).
- `scripts/build_financials.py` — P&L, KPIs, breakeven, cash-flow forecast, SaaS40 QTD from Finops.

This skill is versioned in spirit, not git — iterate on the files here as the pipeline evolves. The pattern: when a meeting's `slides/render.py` proves a new feature, port the improvement back here so the next meeting starts from it.
