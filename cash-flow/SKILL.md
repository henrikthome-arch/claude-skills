---
name: cash-flow
description: Analyze actual cash position vs. forecast. Cross-check bank CSV against planned recurring/scheduled payments. Show what's paid, what's pending, and funding capacity.
argument-hint: "[paste bank CSV or 'check status']"
---

**DIRECTORY GUARD**: This skill operates on the financial-ops repo. Working directory must contain `financial-ops`.

You are helping the CEO of **Sonetel AB (publ)** manage cash flow. The company has limited liquidity and a 1 MSEK credit line that is typically heavily drawn. Precision matters — getting a number wrong can mean breaching the credit limit.

---

## First-time-here checklist (read this if it's your first session with this skill)

If you're a future agent reading this skill for the first time, work through this checklist before doing any analysis or making any changes. It's the fastest path to "I understand the model well enough to be useful."

1. **Read this checklist + Step 0** (you're here)
2. **Read [`Model overview`](#model-overview--how-forecast-numbers-are-built-read-this-first)** further down — single source of truth for the data flow, conventions, and known limitations
3. **Read [`Calibration registry`](#calibration-registry--pl-truth-vs-current-model-snapshot-2026-05-08)** — see which P&L lines are well-calibrated vs which have known drift
3a. **Read `~/.claude/skills/cash-flow/todos.md`** — the persistent outstanding-work list (revise CRs, calibration investigations, deferred items, quarterly recalibration cadence). If the user asks about future work, this is where it lives.
3b. **MANDATORY: Generate a fresh session snapshot at session START** at `~/.claude/skills/cash-flow/snapshots/YYYY-MM-DD-cashflow.md` (or `YYYY-MM-DD-HHMM-cashflow.md` if multiple in same day) AND an HTML twin at the same path with `.html` extension. This snapshot is the working artifact for the session AND a permanent record afterward. See `~/.claude/skills/cash-flow/snapshots/2026-05-09-cashflow.md` for the canonical structure. After writing both files, run `open ~/.claude/skills/cash-flow/snapshots/YYYY-MM-DD-cashflow.html` (macOS) so the user sees the rendered tables in their default browser. See [HTML snapshot template](#html-snapshot-template) below for required styling.

   **IMPORTANT: Fetch payment schedule data from the portal JSON endpoint, NOT by hand-aggregating from raw DB queries.** Per CR-2026-05-09 (Payment Schedule v2 — SHIPPED 2026-05-10):
   - **`GET http://44.194.218.109:8000/analytics/payment-schedule.json?month=YYYY-MM`** returns the canonical per-month schedule (totals + payments[]) computed by `PaymentScheduleService` using the same code path as the forecast service. No ±20K hand-aggregation errors.
   - The portal page at `/analytics/payment-schedule` is browsable directly so the user can view anytime without invoking an agent (linked from sidebar under CASH MANAGEMENT).
   - The skill snapshot file then becomes thin: import JSON for payments + totals, ADD session-changes log + agent reasoning trail + topic groupings (until CR-2026-05-09 follow-up v1.5 ships) + P&L summary (until CR-2026-05-09 follow-up v2 ships).
   - Required snapshot sections:
   - **A — Session changes**: empty at start, append every forecast change as it commits
   - **B — P&L summary** with columns: prior-month actual + current-month forecast + current-month budget + deviation + next-month forecast + next-month budget + deviation. Source the budget from `group_pl_budget` table (FY2026 has 19 lines defined, see `group_pl_budget_lines`)
   - **C — Current month totals**: outflows, revenue inflow, net change, min projected balance (all from JSON `totals`)
   - **D — Current month payment schedule** (full chronological with id refs — from JSON `payments[]`)
   - **E — Current month topic subsections**: India, DBT/loans, Skatteverket, Henrik, SEB Kort, EOM cluster (computed in skill until v1.5 follow-up adds them server-side)
   - **F — Next month totals** | **G — Next month payment schedule** | **H — Next month topic subsections**
   - Final lines link to outstanding TODOs

   Per CEO 2026-05-09: "I have no UI where I can see all payments planned with date and vendor for each month." The portal page now closes that gap; the snapshot remains the agent's reasoning trail.
4. **Read [`Forecast change process`](#forecast-change-process--mandatory-for-all-forecast-data-changes)** — the 5-step plan/review/gate/implement/audit flow that ALL forecast data changes must follow
5. **Read the most recent log entry's post-mortem** in `~/.claude/skills/cash-flow/log.md` — tells you what drifted, what's still open, and which process gaps the previous agent flagged
6. **Pull the current state via MCP** (`get_cash_flow_recurring`, `get_cash_flow_forecast`, `get_cash_position`) so you see live data, not what the docs claim
7. **If user asked for analysis only** — proceed with Steps 1-5 below. No edits required, no 5-step process triggered.
8. **If user asked to change anything in `recurring_payment` / `scheduled_payment` / cashflow_* business parameters** — use the 5-step process for every change. No exceptions, even tiny ones.

### Quick-reference: what's a forecast data change vs what isn't

| Activity | 5-step process required? |
|---|:---:|
| Reading bank CSVs, snapshots, forecasts | ❌ No — analysis only |
| Computing tillgängligt or running balance | ❌ No |
| Identifying drift / variances | ❌ No (but if you propose a fix, that's a change) |
| Editing `recurring_payment` table | ✅ Yes — even for typo in description |
| Editing `scheduled_payment` table | ✅ Yes |
| Editing `business_parameters` row `cashflow_cogs_percent` or `cashflow_revenue_override_msek` | ✅ Yes |
| Updating SKILL.md or log.md | ❌ No — documentation |
| Code changes to `cash_flow_forecast_service.py` etc. | Use real CR file in `docs/plans/` |

### When in doubt

- "Should I add this as recurring or scheduled?" → If it repeats predictably every month/quarter/year, it's a recurring. If it's a one-off, late, or month-specific deviation, it's scheduled.
- "Should I change the recurring or add a scheduled offset?" → If the change is structural (every future month differs from the old amount), update the recurring. If only THIS month differs, add a scheduled offset and leave the recurring alone.
- "Is this a CR or a forecast data change?" → If you're touching Python/YAML/SQL-schema, it's a CR (file in `docs/plans/`). If you're INSERTing/UPDATEing rows in `recurring_payment`/`scheduled_payment`/`business_parameters`, it's a forecast data change (5-step process inline).

---

## Step 0: Read the Log and Update the Skill

**ALWAYS start by reading `~/.claude/skills/cash-flow/log.md`** — this is the running log of previous analyses, budget corrections, patterns, and learnings. It contains institutional knowledge that prevents repeating mistakes.

### MANDATORY: Update after every analysis

After completing an analysis, you MUST:

1. **Append a new entry to `log.md`** with:
   - Date and scope of analysis
   - Findings: budget vs. actual for each matched item
   - Any unidentified entries and their resolution
   - Budget corrections applied (with recurring_payment IDs)
   - New learnings or pattern changes
   - **Post-mortem section** (see below) — REQUIRED on every run

2. **Update this skill file (`SKILL.md`) itself** if you discover:
   - New Corporate Access sub-types or payment patterns
   - Changes to which payments appear in CSV vs. other accounts
   - Budget amounts that have been corrected (update the reference tables)
   - New rules or gotchas learned from the analysis
   - Any information that would prevent future mistakes

The skill file is a living document. Every analysis should make the next one more accurate.

### Post-mortem section — MANDATORY in every log entry

Every cash-flow run MUST end with a post-mortem comparing today's actual EOM picture against the *previous* run's expectations. The CEO needs to know not just what is, but **what drifted vs. what was promised** — and why. Forecast accuracy is the single most important measurable output of this skill.

Include in every log entry:

1. **What did the previous run say?** Quote the verdict from the most recent prior log entry (e.g. "Apr 17 verdict was: 'remaining structural underbudgeting is ~40K/month'").
2. **What actually happened?** Compute the variance between the prior run's expected EOM position and today's actual. Explain the size and sign honestly.
3. **Drift drivers** — table with size in SEK, ranked largest first. For each: was it anticipated by the prior run? (Yes / Partial / No)
4. **Root cause** — why did the prior run miss it? Common patterns:
   - *Budget structure correct, timing wrong*: items hit a different week than scheduled
   - *Liquidity ≠ budget accuracy*: forecast right on totals but wrong on EOM clustering
   - *Hidden categories*: items not in any recurring bucket (e.g. 2890 utlägg, ad-hoc decisions)
   - *Trusted inflow that didn't arrive*: VAT refunds, customer payments, intercompany transfers
   - *FX/account-mismatch*: USD shortage despite SEK surplus, or vice versa
5. **Process gaps to close** — concrete items as checkbox list. These become inputs to the next run's first-pass review.
6. **Forward implications** — does the structural issue persist into next month? Does it require escalation (CFO, board, credit-line, payment-schedule renegotiation)?

**Tone:** direct accountability. The CEO is paying for honest analysis, not reassurance. If a prior run was over-optimistic, say so explicitly. If a structural fragility exists that no amount of budget tweaking will fix, name it.

When opening the *next* log entry, START by reading the most recent post-mortem's "Process gaps to close" list and confirm whether each was addressed before doing the new analysis.

---

## Visibility / UX limitations — show context BEFORE asking decisions

**Per CEO 2026-05-09**: "This is not a working model for me. I have no UI where I can see all payments planned with date and vendor for each month."

The portal `/analytics/cash-flow` shows the daily-balance projection chart but **does not surface payment-level detail** on that page (which entries make up the projection, vendor / day / amount). The new `/analytics/payment-schedule` page (CR-2026-05-09 v2, SHIPPED 2026-05-10) closes that gap by listing every payment with day, recipient, amount, currency, frequency, and id_ref — flagging internal transfers (yellow) and inflows (green) and excluding internal transfers from the cash-outflow total. Use it as the canonical view for the user; use the JSON endpoint as the canonical data source for the snapshot.

Operating principles still apply:

1. **Always present full context BEFORE asking the user to make a decision about a specific entry.** Don't ask "is X all of Y, or partial?" — the user may not remember Y exists in the model. Instead: pull from `payment-schedule.json` (or paste the relevant table from the snapshot) and ask the question with that context visible.

2. **When showing a payment schedule for a month, structure it as**:
   - Full chronological list (all entries day-by-day, with id refs) — use the JSON `payments[]`
   - **Subsections grouped by topic/vendor for scannability** — e.g. "India payments — May 2026" rolling up all India-related entries (cash + internal transfer) with a TOTAL CASH IMPACT line distinguishing real bank outflows from accounting-only entries (computed in the skill until the v1.5 follow-up CR adds them server-side)
   - Internal transfer entries flagged separately with note that they don't affect forecast cash burn

3. **Suggested topic groupings to always surface separately when relevant**: India, DBT/loans, Skatteverket (Skatt + VAT), Henrik (loan + utlägg + 2890), SEB Kort decomposition, EOM cluster (day 25-30). These are areas where multiple line items exist and the user thinks in aggregate terms.

4. **When making a forecast change**, in the same response also show:
   - The change itself (5-step plan as usual)
   - The "before" state of relevant entries (so user can validate context)
   - The "after" state (so user can confirm intent)

---

## HTML snapshot template — keep it simple

**The HTML is a validation worksheet, not a report.** Per CEO 2026-05-10: "I want something that allows me to easily validate the assumptions in the forecast. Not a novel with huge amounts of texts in different formats. Keep it simple and super clear."

The snapshot is rendered to BOTH a Markdown file (`snapshots/YYYY-MM-DD-cashflow.md` — agent reasoning trail) AND an HTML file (`snapshots/YYYY-MM-DD-cashflow.html` — the validation worksheet). After writing both, run `open <html-path>`.

### Required structure — two tables, nothing else

One table per month: current month + next month. **No prose between them, no lists, no commentary, no extra sections.** Just:

| Line | Avg Q1 2026 actual | Month forecast |
|---|---:|---:|
| Revenue | from SIE 30xx | from forecast |
| COGS (variable) | from SIE 4xxx | from forecast |
| **Net (Gross profit)** | computed | computed |
| --- header: Fixed costs — recurring monthly --- |  |  |
| (each recurring_payment, ordered by descending forecast amount, with id ref) | from `bank_outflow_transaction` matched (or "—") | recurring_payment.amount |
| --- header: Fixed costs — month-only one-offs (scheduled) --- |  |  |
| (each scheduled_payment for the month) | n/a | scheduled_payment.amount |
| **Total fixed costs** | sum of available actuals | sum |
| **Net cash flow impact (Net − Fixed)** | computed | computed |

All amounts in **K SEK** (no decimals, e.g. `-406` not `-406,000`). Inflows positive (green), outflows negative.

### Data sources

- **Revenue**: `SELECT SUM(-amount) FROM sie_monthly_balances WHERE account_number LIKE '30%' AND period IN (...)` for the 3 latest months with SIE data, then averaged
- **COGS**: same query, `account_number LIKE '4%'`
- **Fixed cost actuals (Avg column)**: `bank_outflow_transaction` joined to `recurring_payment` via `matched_payment_id`. Average across whatever recent months have data (often only Jan + Mar 2026 — that's fine). Show "—" if no match.
- **Forecast amounts**: `recurring_payment.amount` for monthly recurring; `scheduled_payment.amount` for one-offs in target month. Filter `is_internal_transfer = false` and `enabled = true`.

### Required HTML skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cash Flow Validation — YYYY-MM-DD</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 900px; margin: 1rem auto; padding: 1rem; color: #212529; }
  h1 { margin-top: 0; font-size: 1.4rem; }
  h2 { font-size: 1.15rem; margin-top: 2rem; border-bottom: 2px solid #dee2e6; padding-bottom: 0.25rem; }
  table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  th { background: #f1f3f5; padding: 0.4rem 0.6rem; text-align: left; border-bottom: 2px solid #adb5bd; }
  th.num, td.num { text-align: right; }
  td { padding: 0.3rem 0.6rem; border-bottom: 1px solid #f1f3f5; font-variant-numeric: tabular-nums; }
  tr.header td { font-weight: 600; background: #f8f9fa; padding-top: 0.5rem; padding-bottom: 0.5rem; }
  tr.subtotal td { font-weight: 600; border-top: 1px solid #adb5bd; padding-top: 0.4rem; }
  tr.total td { font-weight: 700; border-top: 2px solid #212529; border-bottom: 2px solid #212529; padding-top: 0.5rem; padding-bottom: 0.5rem; background: #f8f9fa; }
  .neg { color: #dc3545; }
  .pos { color: #28a745; }
  .muted { color: #adb5bd; }
  .note { color: #6c757d; font-size: 0.85rem; margin: 0.4rem 0 1rem 0; }
  .deviation-warn { color: #d68000; font-weight: 600; }
</style>
</head>
<body>
<h1>Cash Flow Validation — YYYY-MM-DD</h1>
<p class="note">Forecast vs Q1 2026 actuals. Bank-actual data sparse — items without bank match show "—".</p>

<h2>Current month YYYY-MM</h2>
<table>...</table>

<h2>Next month YYYY-MM</h2>
<table>...</table>

</body>
</html>
```

### Conventions

- **Deviation flag**: append `<span class="deviation-warn">⚠</span>` to the forecast cell when `|forecast - avg| / max(avg,forecast) > 0.25` AND the avg has actual bank data. Don't flag items with "—" avg.
- **No narrative tables** outside the two main tables. No P&L summary, no payment schedule chronological, no topic subsections, no session changes log, no TODOs section. The user reads those in the chat thread or the markdown snapshot.
- **The MD snapshot can still be verbose** — that's the agent's reasoning trail. The HTML is the user's worksheet.

### When to update the HTML

After each forecast change committed during the session: re-write the affected month's table only (Edit, don't full-rewrite). The user will refresh the browser when they want to see updates.

Reference: see `~/.claude/skills/cash-flow/snapshots/2026-05-09-cashflow.html` for canonical form.

---

## India intercompany — known data duplication

In `recurring_payment` there are TWO sets of India entries that conceptually overlap:

**Cash side (counts in forecast)**: `is_internal_transfer=false`
- id 54 India Operations T1 vendor 60K day 18
- id 55 India Operations T2 statutory 300K day 24
- id 56 India Operations T3 salaries 406K day 26
- = **766K total cash leaving Sweden to India each month**

**Intercompany book-entry side (filtered from forecast)**: `is_internal_transfer=true`
- id 2 Sonetel India 125K day 5
- id 8 Sonetel India 112K day 10
- id 14 Sonetel India 503K day 27 ("Monthly cost in India")
- id 15 Sonetel India 20K day 27 (dividend tax)
- = **760K total**, all filtered out of forecast cash burn

These represent the OLD intercompany accounting model. id 37's description (now disabled, replaced by 54-56) said "replaces internal transfers" — but ids 2, 8, 14, 15 were never disabled.

**Implications**:
- Forecast cash burn is correctly only counting 766K (cash side)
- But sum of all India recurring entries in DB = ~1.5M SEK, which can confuse anyone reading the recurring table
- Possible cleanup: disable ids 2, 8, 14, 15 since id 37 explicitly stated it replaced them. Pending confirmation with Jennifer/BDO that they're safe to disable (they may be referenced elsewhere for accounting/reporting purposes outside cash flow).

When showing India payments in any user-facing summary, always:
- Show cash side as the primary numbers
- Show intercompany side separately, flagged as "internal — excluded from cash burn"
- Explicitly state "TOTAL CASH IMPACT" (the cash-side sum, currently 766K)

---

## COGS taxonomy + how cogs_factor avoids double-count

**Per CEO 2026-05-10**: `full_cogs_percent` (default 21.8%) is calibrated from accounting (total 4xxx ÷ revenue), where ALL COGS — paid via PayPal, SEB Kort, AMEX, or Nordea — are accounted for.

**The forecast service handles this WITHOUT double-counting** via `get_effective_cogs_percent()` ([cash_flow_forecast_service.py:1898](../../libs/financial_core/services/cash_flow_forecast_service.py)):

```
effective_cogs_percent = full_cogs_percent − tracked_cogs_percent
```

Where `tracked_cogs_percent` = sum of enabled `recurring_payment` items whose `account_number` falls in the COGS range (4000-4999 per `config/analytics/group_pl_categories.yaml`) ÷ revenue. The forecast then applies `revenue × (1 − effective_cogs_percent / 100)` for inflow estimate — so **tracked items affect the forecast via their fixed-cost firing only; untracked items affect it via revenue-netting only**. Each cost is counted exactly once.

**LESSON LEARNED 2026-05-10**: An earlier draft of this section asserted that 4xxx recurring items (Voxbone id 1, Europlanet id 17, the 4xxx portion of SEB Kort id 7) were double-counted with cogs_factor and proposed disabling them. That diagnosis was WRONG. The system already nets tracked from full. Disabling those items would not save any cash flow projection — it would just shift the same money from a per-day netting to a fixed-day outflow. Future agents: before proposing to disable any 4xxx recurring item, READ `_get_tracked_cogs_monthly()` and `get_effective_cogs_percent()` first.

### COGS components and channels (CEO-confirmed taxonomy)

| Cost type | Vendors | Account(s) | Payment channel | Modeled where in forecast |
|---|---|---|---|---|
| Phone numbers | Voxbone | 4010 | AMEX or bank wire | id 1 fixed (tracked) → subtracted from full COGS via `effective_cogs_percent` |
| Phone numbers | DIDWW | 4018 | PayPal | revenue netting only (untracked, in `effective_cogs_percent`) |
| Phone numbers | Net2phone | 4014 | PayPal (likely) | revenue netting only |
| Phone numbers | Telintel | 4013 | PayPal (likely) | revenue netting only |
| Phone numbers | Global Connect | 4012 | PayPal (likely) | revenue netting only |
| Phone numbers | Telcoinabox iVox | 4017 | PayPal (likely) | revenue netting only |
| Provisions | Europlanet | 4015 | (unknown) | id 17 fixed (tracked) |
| Call termination | IDT, DIDWW, others | 4xxx | PayPal (mostly) | revenue netting only |
| Affiliate commissions | Awin (legacy "ShareASale") | 4020 | SEB Kort | inside id 7 fixed (but id 7's account_number = 6540, NOT 4xxx — so NOT in tracked_cogs subtraction; this is a real gap to investigate) |
| SMS termination | Direct7, Twilio Beepsend | 4021 | SEB Kort | inside id 7 (same gap as above) |
| AI production | OpenAI ONLY | 4030 | SEB Kort | inside id 7 (same gap as above) |
| Foreign telephony reverse charge | (cost side) | 4531 / 4535 | accounting plumbing | revenue netting only (offset by 4540) |

### What is NOT in cogs_factor (5xxx / 6xxx — modeled separately as fixed cost)

| Item | Account | Vendor | Channel | Forecast model |
|---|---|---|---|---|
| Marketing | 5990 | Google Adwords | bank | id 11 (120K) |
| Marketing | 5991 | META | SEB Kort | inside id 7 |
| Travel | 5800 | various | SEB Kort | inside id 7 |
| Dev SaaS | 6540 | Anthropic, OpenRouter, AWS, MongoDB, etc | mixed (SEB Kort + Tomas utlägg) | inside id 7 (Anthropic) + id 27 (OpenRouter) + id 3 (AWS Sweden) |
| India support | 6561 | India ops | bank wire (cash transfer) | id 54 + 55 + 56 |
| Various overhead | 6xxx, 7xxx | various | various | individual recurring lines |

### Channel typology — how each channel works

- **SEB Kort (autogiro, id 7)**: company credit card, charges hit SEB Kort in real-time (no catch-up possible), settled monthly via Nordea autogiro. **Source of truth for breakdown = SEB Kort invoice details**, NOT SIE aggregates. Catch-up reclassification to a 4xxx account is impossible via this channel.
- **Tomas utlägg (id 27 + ad-hoc)**: Tomas pays on personal card, submits expense claims, reimbursed via Nordea utlägg. **Catch-up IS possible** (multi-month receipts can be batched late). Underlying costs accounted to whatever the supplier `default_account_number` says.
- **Henrik AMEX → utlägg**: same pattern as Tomas utlägg.
- **PayPal**: PayPal nets COGS (DIDWW, IDT, etc) + fees from settlements before depositing to Nordea. Captured implicitly in cogs_factor; net deposit = `revenue × (1 − cogs_factor)`.
- **Bank wire (Nordea direct)**: vendor invoice paid via Nordea; e.g. Voxbone direct, DBT loans, BDO, salaries, India tranches.
- **SWIFT**: international wires (India tranches T1/T2/T3 — 3-day SWIFT lag).

### AI cost classification (CEO-clarified 2026-05-10)

- **OpenAI** = production (serving customers) → 4030 → in cogs_factor
- **Anthropic + OpenRouter** = dev tools (Claude/Cline for engineering) → **should be on 6540**, NOT 4030
- **Current bug**: supplier `default_account_number` for "Anthropic" is set to **4030** (wrong). This causes Tomas's Anthropic claims to flow to 4030, which is why Q1 2026 4030 accounting includes ~70K of misclassified dev tools. **Action needed**: ask Jennifer/BDO to (a) fix supplier default to 6540, (b) reclassify any historical Anthropic entries on 4030.

### id 7 SEB Kort split (RESOLVED 2026-05-10)

Per PLAN-C v2 (audited 85/84), id 7 was split into 4 entries to fix the partial double-count:

| id | Recipient | Amount | Account | Captured by tracked_cogs? |
|---|---|---:|---|---|
| 7 | Credit card company (renamed: SEB Kort non-COGS portion) | 100K | 6540 | No (correctly — non-COGS) |
| 57 | SEB Kort - Awin (split from id 7) | 30K | 4020 | ✓ Yes |
| 58 | SEB Kort - SMS providers (split from id 7) | 7K | 4021 | ✓ Yes |
| 59 | SEB Kort - AI prod (split from id 7) | 25K | 4030 | ✓ Yes |
| **Total** | | **162K** | | tracked uplift +62K vs pre-split |

Total fixed cost from "SEB Kort bundle" = 162K (was 140K → +22K matching 3-mo Feb-Apr 2026 actual avg of 161K). tracked_cogs uplift +62K → effective_cogs drops 2.4pp → revenue inflow netting reduced by 62K/mo. Net forecast improvement: +40K/mo (~+240K over 6 months).

**Bank reconciliation**: SEB Kort autogiro arrives as ONE bank lump → matches via "SEB Kort Bank" alias to supplier 133 → id 7 (only entry with supplier_id=133). The 3 split entries have supplier_id=NULL so don't compete.

**Future recalibration triggers**: Apr 2026 SEB total was 122K (lowest in 4 months); META declining trend (55→51→34→30); 6540 SaaS dev declining (84→88→47→28). If trend continues, the 100K (id 7 non-COGS) and 25K (id 59 AI) may need downward revision in 1-2 months. Quarterly recalibration cadence recommended (per TODO-10).

### Anthropic supplier classification (RESOLVED 2026-05-10)

Per PLAN-B (audited 88/82): `suppliers` table updated for vendor "Anthropic" — `default_account_number` 4030 → 6540. Future Tomas/Henrik expense claims for Anthropic now default to 6540 (Molntjänster dev SaaS), not 4030 (AI-tjänster production COGS).

**Pending follow-up**: Q1 2026 SIE entries on 4030 from past Anthropic claims (~70K SEK estimated across Jan-Mar) were booked under the old default. These need BDO reclassification to 6540 — task for Jennifer. Until done, historical 4030 will overstate "AI production COGS" until year-end and `full_cogs_percent` calibration based on 4xxx ÷ revenue is slightly inflated by this misclassification (small effect).

### Verification rule for SEB Kort items

Always look at the **SEB Kort invoice details** (not SIE aggregates) for true per-vendor breakdown of id 7. SIE 6571/6572 etc are pooled across vendors. SIE 4xxx accounts are pooled across channels. Only the SEB Kort invoice itemises the autogiro charges by vendor.

### Catch-up reclassification rule

- **Catch-up bookings (multi-month entries hitting one period)** can ONLY come from **expense claims** (Tomas/Henrik utlägg) — receipts may be submitted late.
- **SEB Kort cannot catch up** — autogiro charges hit in real time.
- **Direct invoices (bank wire / PayPal) cannot catch up** at the cash-flow level (the cash leaves when it leaves), but BDO accounting reclassification can move existing entries between GL accounts retroactively.

---

## Forecast philosophy — most probable path, no bias

**Per CEO 2026-05-09**: "I want the forecast to show the most probable path forward, given all facts. Neither conservative nor optimistic."

Implication for every calibration decision:
- **Don't pad amounts upward "for safety"** — that creates artificial pessimism that makes legitimate cash positions look worse than they are
- **Don't pick low-end estimates for cash burn "to look good"** — that creates artificial optimism that masks real liquidity risk
- **Use the median or expected value** of available data, not the worst-case or best-case
- When two data points conflict (e.g. P&L avg = X, recent invoice = Y), use the trend-aware best estimate (e.g. if Y is more recent and reflects a structural shift, use Y; if X is more representative of steady-state, use X)
- **State the basis explicitly** so the user can challenge — per Key Rule 6 "no sloppy defaults"

When in doubt: **what's the single most likely outcome?** Don't bias either direction.

This supersedes prior notes in this skill that suggested "conservative bias" or "forecast-low-cash bias for credit-line management." Those were wrong framings — we want accurate forecasts, not pessimistic ones.

---

## Model overview — how forecast numbers are built (read this FIRST)

This section is the single source of truth for what the cash flow forecast represents and how the pieces fit together. Future agents: read this before making any change. The detailed mechanics live in subsequent sections.

### Data flow at a glance

```
                 ┌─────────────────────────────────────────────────┐
                 │  Customer charges (gross, before any PSP fees)  │
                 │  Source: monthly sales report                   │
                 │           "Usage_currency-VAT Exclusion"        │
                 │  Stored in:  service_revenue_cogs table         │
                 │  Per-month:  ~2.6 MSEK net of VAT               │
                 └────────────────┬────────────────────────────────┘
                                  │
                                  ▼  daily run-rate (manual override 2.6 MSEK/30 ≈ 86,667 SEK/day)
                ┌─────────────────────────────────────────────────┐
                │  COGS deduction (cogs_factor = 1 - cogs_pct%)   │
                │  Source: business_parameters cashflow_cogs_pct  │
                │          OR auto from P&L accounts 4000-4999    │
                │  Currently: manual 21.8% (effective 18.6%       │
                │             after deducting tracked recurring   │
                │             on COGS accounts)                   │
                └────────────────┬────────────────────────────────┘
                                 │
                                 ▼  revenue_inflow = daily_run_rate × cogs_factor
                ┌─────────────────────────────────────────────────┐
                │  RECURRING outflows (recurring_payment table)   │
                │  - Monthly: Voxbone, AWS, Linn, SEB Kort,       │
                │             Bambora, Adyen, PayPal fees, etc.   │
                │  - Quarterly: G&W, MOSS, VAT refund (negative)  │
                │  - Annual: Forvis a conto + slut, Mazars, etc.  │
                │  Each fires on its day_of_month per its         │
                │  frequency + quarter_months/annual_month config │
                └────────────────┬────────────────────────────────┘
                                 │
                                 ▼  + scheduled overlays (one-offs)
                ┌─────────────────────────────────────────────────┐
                │  SCHEDULED payments (scheduled_payment table)   │
                │  - One-off invoices not in any recurring        │
                │  - Hejdad/delayed payment overlays              │
                │  - May-only offsets (when actual differs from   │
                │    recurring placeholder for one month only)    │
                │  - Loan repayments, ad-hoc transfers            │
                └────────────────┬────────────────────────────────┘
                                 │
                                 ▼  net cash flow per day
                ┌─────────────────────────────────────────────────┐
                │  Daily running balance                          │
                │  = starting_cash + Σ(net cash flow)             │
                │  starting_cash = EOM previous month from        │
                │                  cash_position_snapshot table   │
                └────────────────┬────────────────────────────────┘
                                 │
                                 ▼  ≠
                ┌─────────────────────────────────────────────────┐
                │  Bank reality (Nordea CSVs, PayPal balance,     │
                │  India bank, Utopia, etc.)                      │
                │  Sources: Plusgiro CSVs + manual snapshots      │
                └─────────────────────────────────────────────────┘
```

### Critical conventions

1. **Revenue is GROSS.** The forecast revenue figure (2.6 MSEK/month) is gross of payment processor fees. Bank reality is that PayPal nets fees from settlements before depositing — so bank cash inflow is ~3-5% lower than forecast revenue inflow. This systematic gap is currently modeled as a synthetic recurring outflow (id 53 PayPal fees 45K/month) until CR-2026-05-08 ships a continuous-deduction fix.

2. **Budget is EXCL VAT, bank is INCL VAT.** All recurring/scheduled budgets are entered as net-of-VAT amounts (the cost to the company). For Swedish suppliers, bank actually pays incl VAT (× 1.25). The model handles this asymmetry by:
   - Counting MOSS as a quarterly outflow (id 47, ~206K) — captures the VAT collected from EU customers that's flushed out
   - Counting input VAT refund as quarterly inflow (id 48, -100K) — captures the SEK supplier VAT that's reclaimed
   - Net quarterly VAT outflow ~80-150K depending on Corona offset

3. **Two complementary tables overlay**: `recurring_payment` is the **baseline** (what happens every month/quarter/year by default). `scheduled_payment` is for **one-offs and corrections**. Pattern when reality deviates from recurring for a single month: keep the recurring untouched, add a scheduled offset (positive or negative) for that month.

4. **Account number is the key**. Both `recurring_payment.account_number` and `scheduled_payment.account_number` map to the BAS chart of accounts. Used by:
   - `_get_tracked_cogs_monthly()` to identify recurring entries that already cover COGS (so they're not double-counted via cogs_pct)
   - P&L category aggregation in `group_pl_categories.yaml`
   - Future: any "is this in COGS or OPEX" classification

5. **The `is_internal_transfer: true` flag** excludes a recurring/scheduled item from net cash burn calculations (used for India intercompany transfers — the cash leaves the Swedish bank but stays within the group). Forecast still shows the outflow on the SEK saldo trajectory; just doesn't count it as "burn" in summary metrics.

### Where the forecast lives in code

```
libs/financial_core/services/cash_flow_forecast_service.py
├─ ForecastResult (dataclass)             — output container
├─ CashFlowForecastService
│  ├─ generate_forecast()                  — entry point
│  ├─ _get_run_rate()                      — daily revenue rate
│  ├─ get_auto_cogs_percent()              — auto from P&L (line 1783)
│  ├─ _get_tracked_cogs_monthly()          — sum of recurring on COGS accounts (1861)
│  ├─ get_effective_cogs_percent()         — full minus tracked (1898)
│  ├─ get_recurring_payments()             — load from DB
│  ├─ get_scheduled_payments()             — load from DB
│  └─ _convert_to_sek()                    — FX for non-SEK entries

libs/financial_core/services/cash_position_service.py — EOM snapshot
libs/financial_core/services/group_pl_service.py       — P&L category aggregation
config/analytics/group_pl_categories.yaml              — BAS account → category mapping
```

### Known modeling limitations (read before reasoning about variances)

| Issue | Status | Impact |
|---|---|---|
| PayPal fees as day-28 lump-sum (id 53) — should be continuous COGS deduction | **CR-2026-05-08 in progress** (paused at 55/100 — needs Fortnox journal trace + revision) | ±45K daily-clustering distortion around day 28 |
| Voxbone (id 1, 79K day 1) modeled as direct payment but actually flows via Henrik AMEX → utlägg → 2890 | Documented; not yet fixed | Daily-level mismatch, monthly net unaffected |
| Openrouter (id 27, 50K day 28) similar to Voxbone — flows via Tomas personal card | Documented; not yet fixed | Daily-level mismatch |
| India recurring 766K on day 25 — actual is multiple smaller tranches across the month | **A2 in progress** (split into tranches per user 2026-05-08) | ±150K mid-month timing error |
| Bambora (id 16) at 60K incl VAT/month overshoots P&L 6571 (~51K/mo excl) by ~10K incl | Tolerated noise | ~10K/month over-modeling |
| Bank fees (id 4) at 5K but actual ~6,700 | Tolerated noise | ~1.7K/month under-modeling |
| `business_parameters cashflow_cogs_percent` is manual (21.8%) — auto would compute from P&L | Manual override is in correct ballpark | <1% drift |
| Mangold (id 51) day_of_month=15 is placeholder — first invoice not yet received | TODO | Unknown until first invoice |

### What changes when the user reports a fact

| Fact category | Where it lands |
|---|---|
| Bank actuals (CSVs) | Reading-only — used to calibrate, not stored |
| Recurring vendor at new amount/day/frequency | `recurring_payment` UPDATE via 5-step process |
| One-off invoice from Fortnox | `scheduled_payment` INSERT via 5-step process |
| Delayed payment from prior period | `scheduled_payment` INSERT (do NOT alter recurring) via 5-step process |
| Hejdad payment to release | `scheduled_payment` INSERT for expected release date via 5-step process |
| Calibration variance (recurring vs P&L) | Adjust recurring amount via 5-step process |
| Channel mismatch (utlägg vs direct) | Document in skill, decide whether to restructure recurring |
| Structural model issue (PSP fees, COGS treatment) | CR file in `docs/plans/` for code/config changes |

### Calibration registry — P&L truth vs current model (snapshot 2026-05-08)

Source: SIE monthly balances CY2025 (Jan-Dec 2025, FY id=1), top expense accounts >100K SEK/year. Compared to current `recurring_payment` configuration. Status colors:
- ✅ within ±10% of P&L — model is well-calibrated
- ⚠️ 10-25% drift — known noise, tolerated
- ❌ >25% drift OR not modeled — needs attention

| BAS | Account name | Monthly P&L (excl VAT) | Currently modeled as | Modeled value (incl VAT where applies) | Status |
|---|---|---:|---|---:|:---:|
| **4018** | DIDWW (telecom) | 299,691 | COGS% factor (`tracked_cogs_monthly` includes recurring on 4xxx; if no DIDWW recurring, it's in `untracked_cogs` ~15.4% of revenue) | Implicit via cogs_pct | ✅ Decided 2026-05-08 (TODO-8): keep implicit. DIDWW is paid from PayPal balance (auto-refill), NOT from Nordea SEK. Adding explicit recurring would create phantom Nordea outflow. Continuous COGS-factor deduction correctly captures the cash impact via PayPal-to-Nordea sweep flow. |
| **4010** | Voxbone (telecom) | 84,127 | Recurring id 1 (79,205 SEK day 1) **but channel-mismatched** (flows via Henrik utlägg) | 79,205 | ⚠️ Channel mismatch |
| **4014** | Net2phone | 30,260 | COGS% factor (no recurring) | Implicit via cogs_pct | ⚠️ Not as recurring entry |
| **4019** | Kostnader för lev tjänster | 27,877 | COGS% factor (no recurring) | Implicit via cogs_pct | ⚠️ Not as recurring entry |
| **4020** | ShareAsale | 36,971 | COGS% factor (no recurring) | Implicit via cogs_pct | ⚠️ Not as recurring entry |
| **4021** | SMS providers (Twilio etc.) | 16,756 | COGS% factor (no recurring) | Implicit via cogs_pct | ⚠️ Not as recurring entry |
| **4030** | AI-tjänster | 22,150 | COGS% factor (no recurring; Openrouter id 27 is on 6540 not 4030) | Implicit via cogs_pct | ⚠️ Not as recurring entry |
| **5990** | Google Adwords | 249,244 (CY2025) | Recurring id 11 (120,000 SEK day 14) | 120,000 | ✅ Verified 2026-05-08 (TODO-4): CY2025 avg was inflated by H2 2025 spikes (Apr 343K, Oct 411K, Nov 353K). Recent FY2026 trend Jan-Mar 2026: 181/107/84 = ~124K avg. id 11 at 120K matches current run-rate. |
| **5991** | Facebook annonsering | 116,382 (CY2025); ~6-34K/mo recent trend declining | Recurring id 28 DISABLED — moved to SEB card (id 7) | 0 (via id 7) | ✅ Verified 2026-05-08 (TODO-6): META declining fast (Nov 150K → Mar 34K → Apr 6K). Absorbed in id 7 SEB Kort. id 7 may need reduction 190K → 150K if low-META trend persists. |
| **5992** | Microsoft Bing | 12,732 | Recurring id 28 DISABLED, in SEB card | 0 (via id 7) | ✅ Verified 2026-05-08 (TODO-6): ~10K/mo small noise, absorbed in id 7 |
| **6420** | Ersättningar till revisor | 8,417 | Recurring id 46 (Forvis a conto 100K April) + id 49 (slut 35,500 May) — annual cycle | 11,292 (avg) | ✅ Within range |
| **6490** | Övriga förvaltningskostnader | 24,785 | Recurring id 31 (G&W 34,500 quarterly day 14 q-months 1,4,7,10) + id 51 (Mangold 12,500 placeholder) + id 13 (Euroclear 3,500) | ~20,000 (avg) | ✅ Within range |
| **6530** | Redovisningstjänster (BDO) | 52,455 | Recurring id 20 (53,000 day 28) | 53,000 (incl ≈ 66,250) | ✅ Matches if compared excl |
| **6540** | Molntjänster (cloud) | 106,613 | Recurring id 3 AWS 2K + id 7 SEB Kort 190K + id 27 Openrouter 50K = 242K incl ≈ 194K excl | ~194,000 excl | ❌ Model 1.8x P&L — likely SEB Kort over-budget |
| **6550** | Konsultarvoden (consultancy) | 91,300 | Recurring id 19 (Tomas 92,500 day 26) + id 29 (Fluff 30,000 day 28) | 122,500 (avg) | ⚠️ ~30K over — Fluff was previously 25K, recently raised to 30K |
| **6561** | Sonetel India Support (intercompany) | 297,679 | Recurring id 37 (India Operations 766K day 25) external | 766,000 | ⚠️ Different scope: 6561 is intercompany "support" only; 766K covers full India ops (salaries, AWS, office). Reasonable. |
| **6570** | Bankkostnader | 7,908 | Recurring id 4 (Nordea 5,000 day 5) | 5,000 | ⚠️ ~37% under-budget |
| **6571** | Avgift Bambora & Adyen (PSP fees) | 50,956 (CY2025) | Recurring id 16 Bambora 60K day 25 + id 52 Adyen 14K day 30 = 74K incl ≈ 59K excl/mo going forward | 59,000 excl | ✅ Verified 2026-05-08: 16% overshoot vs CY2025 P&L is Adyen ramp (was partial year in 2025); CY2026 should align at ~59K/mo |
| **6572** | Bankavgift Paypal | 45,213 | Recurring id 53 PayPal fees 45K day 28 | 45,000 | ✅ Matches (CR-2026-05-08 will move to continuous) |
| **6590** | Övriga externa tjänster | 21,250 | Recurring id 5 Linn 22K day 5 + id 10 Cision 5K day 15 = 27K | 27,000 | ⚠️ ~30% over |
| **6996** | Betald utländsk inkomstskatt | 8,643 | Not modeled (annual India ATR ids 39-42 in INR) | TBC | ⚠️ Coverage unclear |
| **7220** | Löner till företagsledare | 53,357 | Recurring id 12 Salaries 98K day 24 (covers HT + KT + SA) | 98,000 (combined with 7210) | ✅ Combined matches |
| **7210** | Löner till tjänstemän | 43,448 | Same as above (combined with id 12) | (combined) | ✅ |
| **7240** | Styrelsearvoden | 36,667 (CY2025: 440K/year accrual ~41,902/mo) | Annual id 32 (140K Dec, "after-tax") + id 33 (95K Skatt extra Jan) | 235K total cash/year | ⚠️ Investigated 2026-05-08 (TODO-5): P&L is accrual basis (~440K/year gross). id 32's 140K is "net after-tax." Math: 140K net → ~200K gross at 30% tax vs P&L 440K = potential 240K/year unmodeled cash. **NEEDS USER INPUT**: confirm if 140K is chairman-only or if other board members receive additional cash payments not modeled. |
| **7510** | Arbetsgivaravgifter (employer tax) | 41,554 | Recurring id 9 Skatteverket 70,741 day 12 | 70,741 (avg) | ⚠️ Combines with 7511, 7512 etc. |
| **7811** | Avskrivningar (depreciation) | 591,168 | Not modeled (non-cash) | 0 | ✅ Correct exclusion (D&A is non-cash) |
| **7812** | Avskrivningar AI-plattform | 85,409 | Not modeled (non-cash) | 0 | ✅ Correct exclusion |

**Action items from registry**:
- A3: Bambora calibration — already on TODO
- A6: Bank fees calibration — already on TODO
- Investigate Google Adwords 5990 P&L vs id 11 model gap (P&L 249K/mo vs 120K recurring) — possibly historical higher spend or other channels not captured
- Investigate id 28 META & Bing replacement by SEB card — confirm 6540+5991+5992 fully covered by id 7
- Investigate Styrelsearvoden 7240 — P&L 398K full-year vs id 32 annual 140K — may be missing semi-annual board fees

This registry should be re-validated quarterly when fresh P&L data arrives. Discrepancies > 25% should trigger investigation, not silent acceptance.

### Forecast vs P&L total-outflux reconciliation — methodology + 2026-05-09 baseline

When the user asks "is the forecast in sync with the P&L?", apply the framework below. **Do NOT compare raw P&L 3-month avg to forecast** — multiple adjustments are required first.

#### Methodology

**P&L → cash-equivalent translation (per month, annualized basis):**
1. Sum all P&L cost accounts excl non-cash items:
   - **Exclude depreciation** (78xx accounts: 7811, 7812, 7814) — already paid in cash years ago
   - **Exclude FX losses/gains** (7960, 3960) — accounting realization, no cash
   - **Exclude accruals**: 7290 (semesterlöneskuld), 7240 monthly accrual portion of board fees (cash is annual via id 32 + id 33)
2. **Adjust 6561 Sonetel India for 20% intercompany markup**: P&L 6561 includes 20% markup on parent's intercompany invoice. Underlying cost = 6561 ÷ 1.2. The markup is real cash (stays in India sub as profit) but P&L overstates by 20% vs the standalone cost line.
3. **Add loan amortization** (124K/mo from ids 22 + 25 currently): cash outflow but BS movement, not P&L expense.
4. **Add capitalized investment cash** (~458K/mo from India dev work currently): Sweden→India transfer 766K = ~258K underlying op cost + ~50K markup + ~458K capitalized R&D (becomes intangible asset 1011/1012, depreciates as 7811/7812/7814 over years). Cash flow must include the full 766K; P&L only includes 6561 (operating portion).
5. **Add VAT net cash impact**: MOSS quarterly outflow (~206K) - VAT refund quarterly inflow (~100K) = ~+106K/quarter ≈ +35K/mo cash out.
6. **Annualize Q1 specials**: Q1 (Jan-Mar) includes annual items at full value spread over 3 months instead of 12. Inflates Q1 monthly avg by ~71K/mo currently. Items: id 30 Nasdaq (152K Mar), id 33 Skatt extra (120K Jan), id 38 Trygg Hansa (6K Jan), id 34 LetsLaw (~6K Jan). When using Q1 avg as steady-state proxy, subtract this inflation.

**Forecast → annualized monthly:**
- Sum monthly recurring (excl is_internal_transfer=true items)
- Add quarterly avg (each quarterly amount ÷ 3, since fires once per quarter)
- Add annual avg (each annual amount ÷ 12)
- Add COGS deduction (revenue × cogs_factor) — this captures untracked 4xxx items as continuous deduction

#### Snapshot 2026-05-09 reconciliation

| Side | SEK/mo |
|---|---:|
| **P&L Q1 Jan-Mar 2026 raw avg** | 2,313 |
| - Q1 specials inflation (annualization correction) | -71 |
| **P&L steady-state monthly (annualized)** | **2,242** |
| **Forecast model (already annualized)** | **2,508** |
| **Gap: forecast over-models by** | **+266 (~11%)** |

**Concentrated in**:
- id 7 SEB Kort (~40-70K over) — META declining 2025-2026
- India model vs underlying P&L (~50K — markup makes underlying lower; cash is correct)
- Salaries (~17K over)
- Konsult Tomas+Fluff (~14K over)
- Cogs over vs actual 4xxx (~10K)
- Other smaller (~50K)

Direction: forecast over-models burn. Per CEO 2026-05-09 philosophy ("most probable, not conservative"), this gap should be CLOSED via calibration, not accepted as a safety margin. ~250K/mo of artificial pessimism makes legitimate cash positions look worse than they are. Actions in progress: SEB Kort 190K → 150K (META decline), India underlying confirmation, salaries decomposition.

### Critical contexts for forecast-vs-P&L comparison

**(1) India 20% intercompany markup**: P&L 6561 = parent's cost of India services, INCLUDING 20% markup that the India sub charges parent on top of underlying cost. To compare to underlying: divide by 1.2. The markup is real cash (stays as India sub's profit) but distorts the P&L cost line. Cash flow correctly captures full transfer.

**(2) Capitalized R&D in India**: Indian dev work creates intangible assets on parent's BS (1010 Balanserade utgifter, 1011 Balanserade AI-plattform, 1012 Balanserade Sonetel Software). These DON'T expense to P&L when incurred — they capitalize. Then depreciate over years as 7811/7812/7814. **Cash flow must include this capitalization (it's real cash today); P&L excludes it (until depreciation years later).** Currently ~458K/mo flows into capex, balanced by ~780K/mo of historical capex depreciating now.

**(3) Loan amortization**: id 22 Nordea amort (26K) + id 25 DBT Lån 1 amort (98K) = 124K/mo cash outflow. NOT in P&L (BS movement: liability decreases, cash decreases). Must be added when comparing P&L to cash burn.

**(4) Q1 annual-items inflation**: Items that fire annually in Q1 inflate the Q1 3-month avg by their full value ÷ 3 vs annualized ÷ 12. Always normalize before treating Q1 avg as steady-state. List of currently-Q1-firing annuals: Nasdaq (Mar), Skatt extra (Jan), Trygg Hansa (Jan), LetsLaw (Jan), Forvis a conto (Apr — borderline Q2).

**(5) FX losses (7960) are non-cash**: Accounting realization of FX changes on outstanding USD/EUR receivables/payables. No cash moves until those receivables/payables actually settle. CY2025 was 199K/mo on average — this would massively distort cash burn if mistakenly included.

**(6) SEB Kort id 7 multi-account coverage**: id 7 (190K SEK) covers SEB company card spend across MULTIPLE P&L accounts:
- 4030 AI-tjänster (OpenAI direct API)
- 5991 Facebook annonsering (META)
- 4020 ShareAsale (Awin commissions)
- 6540 Molntjänster (portion: Superinterface, MongoDB direct, Twilio direct, Render, Stoplight)
- 5800 Resekostnader (portion: travel)

Don't compare id 7 budget to any single P&L account. Decompose across all 5 above for fair comparison. As of May 2026, META has declined sharply (Nov 150K → Apr 6K), making id 7 over-budgeted at current run-rate.

**(7) Voxbone payment pattern**: Per CEO 2026-05-08, paid before the 10th of each month (direct path). If credit-card route, deferred to utlägg cycle (~day 28-30). Recurring id 1 day_of_month=1 is the documented baseline pending TODO-12 channel-mix audit (end Oct 2026).

**(8) Skatteverket konto netting (VAT refund + monthly Skatt)**: Both id 48 (refund) and id 9 (Skatt) firing on day 12 is CORRECT — they're independent real cash flows. Empirical May 2025: +98,554 refund (May 1) + -70,741 Skatt (May 12) = +27,813 net. Forecast +29,259 net = match within noise. NOT a double-count.

**(9) PayPal fees lump-sum is wontfix per CEO**: id 53 (45K SEK day 28) is structurally wrong on daily distribution but correct on monthly net. CR-2026-05-08 closed wontfix. Re-open trigger: if drift detection (TODO-2) shows day-28 distortion causing material mis-decisions on EOM cluster planning.

**(10) Board fee structure (per CEO 2026-05-08)**: Sebastian (chairman) receives 20K SEK gross/month — flows through normal payroll (id 12 + id 9). Annika + Jenny receive 100K SEK gross each in December = 200K combined. id 32 (140K Dec) = net to A+J after 30% withholding. id 33 (120K Jan) = Skatteverket extra in Jan from Dec board fees = 30% withholding (60K) + 31.42% arbetsgivaravgift (63K) ≈ 123K. P&L 7240 ~440K/year reconciles: 240K Sebastian + 200K A+J = 440K. Caveat: if A/J qualify as non-employees (pensioners), särskild löneskatt 24.26% might apply instead of arbetsgivaravgift 31.42% — lowers id 33 to ~108K. Confirm with BDO if needed.

---

## Forecast change process — MANDATORY for ALL forecast data changes

Per user instruction 2026-05-08: **every edit to `recurring_payment`, `scheduled_payment`, or `business_parameters` for cashflow_*` MUST follow the 5-step process below.** Ad-hoc "edit-then-document" is no longer acceptable. The bank's credit line is at 99%+ utilization and a wrong forecast can cause a real liquidity miss; the discipline cost is justified.

**No `docs/plans/CR-*.md` files.** Per user 2026-05-08: avoiding the CR-file artifact keeps this flow uncluttered. Everything is inline in the chat — plan, reviews, audits, all in the conversation. The discipline is in the process, not in the document type. CR files remain reserved for actual codebase changes (separate from this skill).

### The 5-step flow (uniform — same for tiny edits and structural changes)

```
1. PLAN        Post the inline 6-line plan block in chat (template below).
2. REVIEW      Spawn 2 agents in parallel to review the plan and SCORE 0-100.
3. SCORE GATE  Both reviewer scores ≥ 70 → proceed. Either below 70 → revise plan and re-review.
4. IMPLEMENT   Run the SQL. Run the verify query immediately and show output.
5. AUDIT       Spawn 2 agents in parallel to audit the actual implemented change vs the plan.
               Both auditors must confirm: (a) plan matches what was applied,
               (b) verify result is consistent with plan,
               (c) no unintended side effects (no other rows touched, no double-count).
               Both audit scores ≥ 70 → done. Either below 70 → roll back and re-plan.
```

This same flow applies to ALL forecast data changes regardless of size — a 1-row scheduled payment goes through the same 5 steps as a recurring schedule change. No tiering, no skipping. The Apr 29 → May 8 DBT slippage was a "tiny" issue that became a 150K SEK gap; uniform discipline prevents that pattern.

### Inline plan template (use as-is, post in chat verbatim before any SQL)

```
FORECAST CHANGE PLAN
What:         <one sentence — what's being added/changed>
Why/source:   <bank CSV / Fortnox invoice / user statement / Padma email / SIE data>
Impact:       <SEK delta on EOM running balance, which date(s) shift, which accounts>
Rollback:     <how to undo — usually `UPDATE ... SET enabled = false WHERE id = X`>
Verify SQL:   <the exact SELECT that will be run after to confirm the change took>
Audit checks: <what the auditors should look for — e.g. "no double-count vs id 16",
               "SEK saldo trajectory recomputed correctly", "no other May entries shifted">
```

### Reviewer agent prompt (use for step 2)

Spawn 2 in parallel with the same prompt:

> Independent review of this Forecast Change Plan. Score 0-100 confidence.
> Identify: (a) hidden double-counting risk, (b) wrong source-of-truth assumption,
> (c) timing/day-of-month errors, (d) account-number mismatches,
> (e) anything that would surprise a future analyst reading this in 6 months.
> Be sharp. Plan text below: ...

### Auditor agent prompt (use for step 5)

Spawn 2 in parallel with the same prompt:

> Audit this implemented Forecast Change. The plan said X, the SQL ran, the verify
> query returned Y. Confirm: (1) the change applied matches the plan exactly,
> (2) the verify output is consistent with the plan's stated impact,
> (3) no other rows were affected unintentionally,
> (4) no double-count exists vs other recurring/scheduled entries for the same supplier/account.
> Score 0-100 confidence that the change is correctly applied. Plan + SQL + verify result below: ...

### Hard rules

1. **Never claim a change is "handled" without all 5 steps completed in the same response.** If steps 2 (review) or 5 (audit) take long enough that they need to be background, say so explicitly and treat the change as TODO — not done — until both gates pass.

2. **Score gate is hard at 70.** If even one reviewer scores < 70, plan must be revised. No "averaging" or "best of two".

3. **Delayed payments are a structural category.** When the user says "X is delayed from period Y to date Z" or "X charges at EOM but didn't this month," the assistant must execute all 5 steps in the same response — not log it for later. Recurring entries for that supplier stay UNCHANGED — the delayed payment is a one-off scheduled overlay.

4. **Mandatory end-of-session changelog entry to `docs/changelogs/YYYY-MM.md`.** Every cash-flow session that modifies forecast data ends with a changelog entry. The skill's own `log.md` is for analysis history — separate from the project changelog. Both are required. **A change that exists only in `log.md` is not actually committed to the change record.**

5. **The 5-step process is not optional even for tiny edits.** Per user 2026-05-08: same logical flow for all changes assures quality. Skipping any step is forbidden.

6. **No sloppy defaults — every number/cadence/threshold has a stated basis.** Per user 2026-05-08 after observing 10+ instances of plausible-sounding-but-unfounded choices in a single session: every number in a plan (amount, day_of_month, frequency, threshold, proportion, recalibration cadence) MUST cite its basis (data point, documented source, computed from actuals, last invoice, etc.). When the basis is thin or absent, say "speculative — single data point" or "no basis, heuristic" explicitly. Do NOT bury speculation in confident language like "midpoint is fair" / "quarterly seems reasonable" / "day X is representative." Common sloppy patterns:
   - "Quarterly recalibration" — say WHY quarterly vs monthly vs trigger-based, or admit it's a guess
   - "Midpoint is fair" — between WHAT endpoints, why those, what weighting?
   - "Day X seems representative" — based on what observation pattern, what range?
   - "Approximately Y%" — what was computed, what tolerance applied?
   - "Round to N" — what's the target precision, why round that direction?
   
   The 5-step review catches sloppy defaults, but relying on reviewers is the wrong economy. Aim to produce plans that pass review on first attempt because the basis is explicit. Reviewer agents are a safety net, not a thinking outsourcer.

### What this does NOT cover

- Reading the data (forecasts, snapshots, CSV parses, queries) — no plan needed; analysis-only
- Updating SKILL.md or log.md — no plan needed; documentation only
- Fixing typos or descriptions on existing recurring/scheduled entries — no plan, but verify after

---

## VAT Handling — CRITICAL

**All recurring payment budgets are EXCLUDING VAT (moms).** Revenue in the forecast is also net of VAT.

This means:
- **Bank CSV amounts include VAT** (25% Swedish moms on most domestic suppliers)
- **Budget amounts exclude VAT** (the actual cost to the company)
- When cross-checking: **divide bank amounts by 1.25** for Swedish suppliers before comparing to budget
- Some suppliers have NO Swedish VAT: Google (Ireland, reverse charge), loan payments (DBT, Nordea), salaries, bank fees, credit line interest

**VAT flow handling in the forecast:**
- **Revenue is NET of VAT.** The monthly revenue figure (~2.6 MSEK) comes from the "Revenue" column in the sales report, which excludes VAT. VAT (~82K/month) is tracked separately.
- **MOSS/OSS payment: Quarterly RECURRING payment (id 47), ~206K SEK, day 30, quarter_months 1,4,7,10.** Paid in EUR (~18,714 EUR as of Apr 2026). Grows naturally with EU revenue. Although revenue is net, the bank balance includes accumulated VAT collected from EU customers. The MOSS payment drains this every quarter. Without it, the forecast would overstate cash by up to ~250K. No VAT on MOSS itself (it IS the VAT).
- **Input VAT refund: Quarterly RECURRING inflow (id 48), -125K SEK, day 30, quarter_months 1,4,7,10.** Net of: ~168K input VAT paid to Swedish suppliers minus ~42K domestic output VAT on SEK sales (~55K/month × 25%). The bank pays costs incl. VAT even though budgets are excl., so this refund is real cash returning. Grows with Swedish supplier costs and shrinks if SEK revenue increases.
- **Known timing issue:** EOM cash position snapshots include accumulated MOSS VAT (0–246K depending on where in the quarter cycle). This means starting cash is slightly "inflated" at the start of months 2 and 3 of each MOSS quarter. The scheduled MOSS payment corrects this. Be aware of this when comparing forecast to actuals — up to ~164K of apparent "surplus" may just be accrued MOSS debt.

**Suppliers with 25% VAT (divide bank amount by 1.25):**
BDO, SEB credit card purchases, Tomas André, Linn Kristensson, CFO (Södra Lund), Cision, United Spaces, Fluff (Rainbow), Forvis Mazars, G&W, Europlanet, META/Bing, Trygg Hansa

**Suppliers WITHOUT VAT (bank amount = budget amount):**
Google Ireland (reverse charge), Openrouter (US, reverse charge), AWS (Ireland, reverse charge), Voxbone/Bandwidth (Belgium, reverse charge), LetsLaw SL (Spain, reverse charge), DBT loans (financial), Nordea loans/interest/fees (financial), Nordea amortization (financial), Skatteverket (tax), Salaries (no VAT), Styrelsen board fees (no VAT), Bambora (financial service), Euroclear (financial service), Nasdaq (financial service), India Operations (export), Sonetel India (internal transfer)

---

## Step 1: Collect Data

### From the user (REQUIRED)

**ALWAYS ask via plain chat, not via AskUserQuestion forms.** The user has stated they cannot paste screenshots into AskUserQuestion popups. Use direct chat prompts so they can paste images and tables freely.

Ask the user for these if not already provided:

1. **Nordea CSVs (all 5 accounts)** — typically downloaded together to `~/Downloads/`. The user often says "all 5 account csvs in download folder" — check there first. Files are named `PLUSGIROKONTO FTG <account> - <date>.csv`. The 5 account CSVs are:
   - `91 55 78-9` SEK (main, with credit line) — has the bulk of cost transactions
   - `91 55 78-9` EUR (small sub)
   - `91 55 78-9` USD (small sub)
   - `214 72 32-9` EUR (dedicated EUR — often used to stage MOSS payments)
   - `214 72 33-7` USD (dedicated USD)
   - Format: semicolon-delimited, columns: `Datum;Belopp;Avsändare;Mottagare;Namn;Ytterligare detaljer;Meddelande;Egna anteckningar;Saldo;Valuta`
   - Date format: `YYYY/MM/DD`, amounts use `,` as decimal separator
   - File is reverse-chronological (newest first)
   - The `Saldo` column is the running balance for that account only (not aggregate)

2. **Nordea tillgängligt** — derive from CSVs (latest Saldo per account + credit line headroom). The user has indicated this can be computed from the CSVs and does NOT need to be asked separately. Formula:
   - SEK headroom = 1,000,000 + SEK saldo (saldo is negative when overdrawn)
   - Foreign balances × FX → SEK
   - Tillgängligt = SEK headroom + Σ(foreign accounts in SEK)

3. **Registrerade betalningar (registered payments)** — REQUIRED. Future-dated outflows queued in Nordea. Ask the user to paste **all four tabs**: Osignerade, Kommande, **Hejdad**, Avvisade. All four impact the analysis.
   - **Kommande**: signed payments queued for future dates.
   - **Osignerade**: pending-signature, often back-dated awaiting approval.
   - **Hejdad — CRITICAL signal, never ignore.** A non-zero Hejdad count means Nordea automatically held a payment instruction because the credit line was insufficient at the scheduled debit date. This is silent loss of payment control to the bank's algorithm — not a discretionary delay. When Hejdad items exist: identify which payment, against which date and saldo it bounced; compute when SEK headroom recovers enough to release safely; treat the held items as deferred outflows in the EOM plan. **Any item due day 1 of next month against an EOM saldo within 50K of the credit limit will likely auto-Hejdad** — flag this risk explicitly *before* it triggers, in the EOM analysis.
   - **Avvisade**: bounced/rejected payments — investigate non-zero counts.
   - Note: Each registered payment is account-specific. EUR-account payments (e.g., MOSS) are funded from EUR balance, not from SEK headroom.
   - Always reconcile against the recurring/scheduled list — this catches duplicate payments, missing payments, and budget discrepancies before money moves.

4. **PayPal USD balance** — from paypal.com/mep/dashboard
   - **CRITICAL: maintain a 5,000 USD floor in PayPal at all times.** DIDWW (telecom vendor) auto-refills from this PayPal account — those funds are locked operationally and cannot be touched.
   - **Effective PayPal liquidity** = `balance − 5,000 USD`. If balance ≤ 5,000, PayPal contributes ZERO to available cash.
   - Always subtract the 5K floor when reporting tillgängligt or computing funding capacity for India transfers, USD vendor payments, etc.
   - **PayPal → Nordea transfer time: 2–3 banking days.** Funds withdrawn from PayPal today do NOT arrive in the Swedish bank in time for tomorrow's payments. Treat PayPal liquidity as **T+3 cash**, not same-day. For urgent same-day or next-day needs (e.g. India express transfers before EOM), PayPal cannot be the funding source — only Bambora/Adyen settlements that hit the Nordea USD account directly are available.
   - When recommending a PayPal withdrawal, state the expected arrival window (e.g. "Initiate today → arrives Mon–Tue") so the plan accounts for the lag.
   - **AVOID PayPal → Nordea withdrawals that span month-end (initiated late one month, arriving early the next).** They complicate monthly accounting — PayPal balance leaves in month N but lands in Nordea in month N+1, creating in-transit/reconciliation work for BDO. Schedule withdrawals so both legs sit inside the same calendar month. If a withdrawal would straddle month-end, prefer to wait until the new month begins or initiate it earlier so it arrives before EOM.
   - **Compute current PayPal from data, don't ask by default.** Starting balance from `get_cash_position` snapshot at EOM. Subtract any PayPal-to-Nordea sweeps visible in the SEK CSV (rows with Namn = `PAYPAL PTE LTD`). Add an estimate of PayPal revenue accumulated since EOM (typical ~2-4K USD/day across PayPal channels). Only ask the user for refresh if the calculation lands within 2K USD of the 5K DIDWW floor — then exact balance matters for usability decisions. Otherwise compute and proceed.

5. **Drill-down details for any unidentified Corporate Access entries** — ask for the Transaktionsdetaljer (Rubrik, Till namn/bank, Till konto, Belopp) screenshot for any line you can't decode from the CSV alone.

6. **Fortnox open-invoices ledger (when accessible) — strongly preferred for the forward outflow picture.** When the user can paste/screenshot the supplier-ledger view showing open invoices with `Faktnr / Faktdat / Förfall / Totalt / Saldo / MOMS`, this is the most accurate forward outflow source available — better than the recurring schedule because it shows actual invoice amounts (not budget assumptions) and exact förfallodatum. Cross-checks it enables:
   - **Budget drift**: e.g. SEB Kort actual 121K vs. 190K budget; Google March bill 84K vs. 120K budget — both observed May 2026
   - **Invoice cycle timing**: Google bills 1 month in arrears (service month X → due ~day 14 of X+1); BDO often issues two invoices per month (large ÅR work + smaller residual)
   - **Items not in any recurring entry**: Adyen Nordic Bank fees in USD, Kommissionären, Svensk e-identitet
   - **Two-invoice patterns** for vendors like Rainbow/Fluff (one invoice per service month, sometimes two open simultaneously)

### From MCP (fetch automatically)
Call these MCP tools:

- **`get_cash_flow_recurring`** — all recurring payment definitions with amounts, frequencies, day of month, recipients
- **`get_cash_flow_forecast`** — daily forecast including actual revenue data, projected outflows, running balance
- **`get_cash_position`** for previous month — EOM snapshot that seeded the forecast

### Monthly expense reimbursement data — REQUIRED

Expense reimbursements (utlägg) are a **recurring monthly activity**, not surprise outflows. Every cash-flow run must inspect the latest expense data before classifying utlägg payments as drift.

Two ways to get the data (use whichever is faster):

1. **Latest accountant bundle** — `~/Downloads/Accountant_Bundle_YYYY-MM_verYYYYMMDD_HHMM.zip`. Inside: `Accountant_Bundle_YYYY-MM/Expenses/` contains per-person batches with `expense_summary.txt` (line-items in SEK + original currency) and `Expense_Report_YYYY-MM.xlsx` (top-level totals). When multiple bundle versions exist, use the latest timestamp.
2. **Database query** (via `dbshell` over SSH) — gives 6+ months of history for trend baseline:
   ```sql
   SELECT b.year_month, b.original_filename,
          ROUND(COALESCE(SUM(t.settled_amount_sek), SUM(t.amount * COALESCE(t.fx_rate,1)))::numeric, 0) AS amount_sek
   FROM transaction_batches b JOIN transactions t ON t.batch_id = b.id
   WHERE b.file_type ILIKE '%expense%' AND b.year_month >= '<6-mo-ago>'
   GROUP BY b.year_month, b.id, b.original_filename ORDER BY b.year_month DESC, b.id;
   ```

What to do with it:
- Compute the **6-month rolling average of total monthly expense reimbursement** (Tomas + Henrik + Martin + Sebastian + others). This is the baseline.
- Compare the latest month against the average. **Anomalies** to flag:
  - A "backfill" batch covering > 1 month of dates (Tomas's Mar 2026 batch covered Dec 2025–Apr 2026 — added ~95K vs. normal)
  - A new person being added to the reimbursement flow
  - A vendor migration (e.g. moving from SEB-card-paid Anthropic to personal-card-paid Anthropic) — would shift the same spend from id 7 to utlägg without changing total cost
- **Treat the baseline (~78K SEK/mo as of 2026-04) as a recurring outflow when computing forecast accuracy**, even if it's not in `get_cash_flow_recurring`. Do not classify monthly utlägg payments as drift unless they exceed the baseline.

### Utlägg / 2890 — channel mapping (do not double-count)

The recurring budget contains entries that are budgeted as direct vendor payments but actually flow through personal-card → utlägg → 2890 reimbursement. The cash leaves once, not twice. Confirmed channel mapping (Apr 2026):

| Recurring entry | Budgeted channel | Actual channel |
|---|---|---|
| id 1 — Voxbone 79,205 SEK day 1 | direct payment to Bandwidth | Henrik AMEX → 2890 → Henrik utlägg reimbursement (typically late in month) |
| id 27 — Openrouter 50,000 SEK day 28 | direct payment | Tomas personal card → utlägg reimbursement |
| id 7 — SEB credit card 190,000 SEK day 10 | direct (SEB invoice settled by autogiro) | ✓ correct as budgeted — covers Anthropic, META, Awin, Superinterface etc. CHARGED TO COMPANY SEB CARD only |
| (no entry for) Tomas personal card Anthropic + OpenRouter + travel | — | utlägg reimbursement, not budgeted at all |
| (no entry for) Henrik personal Voxbone wallet top-ups + telecom + equipment | — | utlägg reimbursement (separate from id 1 if id 1 is intended to also cover Voxbone wallet) |

When computing actual-vs-budget for a month, **deduct the utlägg outflow against ids 1 + 27 + the unbudgeted personal-card spend before flagging anything as drift.** Otherwise you'll double-count: once via the recurring budget (assumes direct payment) and again via the utlägg reimbursement (actual flow).

**Better long-term fix (note for CR):** restructure recurring budget so that:
- ids 1 and 27 are re-tagged as "Henrik utlägg" / "Tomas utlägg" channel respectively
- A new recurring "Monthly expense reimbursements" line is added at the 6-month average for the residual unbudgeted personal-card SaaS + travel
- Forecast variance then measures real drift, not channel mis-categorization

### 2890 OLD debt — separate from monthly expense flow

The historical 2890 balance (e.g. ~307K SEK at one point) is **OLD accumulated debt** from prior periods. It is paid via SCHEDULED tranches (e.g. 100K + 100K + 107K across May–Aug 2026), not via the monthly utlägg flow. Do NOT confuse these:
- Monthly utlägg = current-period expenses (~78K/mo recurring)
- 2890 OLD debt repayment = scheduled lump-sum tranches, separately listed as scheduled payments in the forecast

Verify before reporting: when you see a Henrik/Tomas utlägg payment, check whether the line-items in the relevant batch are **for the current period** (= recurring activity) or **back-dated several months** (= partial backfill, anomaly).

---

## Step 2: Parse Bank CSV

Parse the Nordea SEK CSV to extract:

### Daily closing balances
- Find rows where `Saldo` is populated — these are closing balances
- Build a table: Date | Closing Balance (SEK account only)
- Opening balance = implied from first day's balance minus that day's net transactions

### Transaction categorization

**CRITICAL: "Corporate Access" is NOT a single cost type.** The bank groups multiple unrelated payments under the label "(N) Corporate Access" where N is a batch number. Each Corporate Access entry must be drilled into to identify the actual recipient. Common contents:

#### Corporate Access — known sub-types

| Actual recipient | How to identify | Budget match (excl. VAT) |
|---|---|---|
| **SEB Kort Bank AB** (credit card) | Namn = "SEB Kort Bank AB", account 494-7933 | Recurring: ~152K SEK excl. VAT (budget 190K bank amount, mixed VAT) |
| **Skatteverket** (tax payments) | Namn/Rubrik = "SKATTEVERKET", account 5050-1055 | Recurring: ~70,741 SEK (no VAT on tax) + scheduled items |
| **BDO Göteborg AB** (accounting) | Namn = "BDO Göteborg AB", account 829-4055 | Budget: 53K excl. VAT (bank pays ~66K incl.). Baseline ~33K/month, spikes to 90K+ excl. during ÅR/bokslut (Jan-Mar) and report months |
| **G&W Kapitalförvaltning** (advisor) | Namn = "G&W KAPITALFÖRVALTNING AB", account 5061-9550 | Quarterly: 34,500 excl. VAT (bank pays ~43,125 incl.). Quarter months: 1,4,7,10 |
| **Forvis Mazars AB** (auditor) | Namn = "Forvis Mazars AB", account 5377-8536 | Annual: 100K excl. VAT (bank pays ~125K incl.). Hits ~April when ÅR is finalized. |
| **Svensk e-identitet AB** | Namn = "Svensk e-identitet AB", account 377-1557 | ~300 excl. VAT, minor. Not budgeted. |

**When you see a Corporate Access entry you cannot identify from the CSV alone, ask the user to drill into it in Nordea (Kontohändelser > click the row > Transaktionsdetaljer).** The detail popup shows Rubrik, Till namn/bank, and Till konto which identifies the actual recipient.

#### Common Corporate Access bundles (confirmed Apr 2026)

| CSV signature | Decoded bundle | When |
|---|---|---|
| -34,750 (2) Corporate Access | Linn Kristensson 23,375 + Rainbow/Fluff 11,375 | day 1 |
| -315,527 (2) Corporate Access | SEB Kort Bank 190,527 + Forvis Mazars a conto 125,000 | mid-month (April when ÅR a conto hits) |
| -43,503 (2) Corporate Access | G&W 43,125 + Svensk e-identitet 378 | day 14 (G&W quarter months 1,4,7,10) |
| -14,021 (2) Corporate Access | Euroclear 4,527 + Schibsted Marketing 9,494 | day 27 (April only — Schibsted is annual) |
| -96,668 Skatteverket | Regular monthly 70,741 + Corona-anstånd ~26K (delayed-from-March schedule) | day 9 (when delayed) or day 12 (regular) |

**Pattern:** SEB credit card pays day ~10–14 ALWAYS bundled with another item via Corporate Access. The signature 190K + 125K = 315K is specific to April (annual ÅR month). Other months will show 190K SEB + smaller bundle partner.

### FX/inter-account conversions (NOT outflows)

Same-day, same-`Meddelande/OCR` ID appearing in multiple account CSVs as paired ±entries = **currency conversion, not a real cost outflow**. The SEK CSV will show "-X SEK" with rubrik like `0260429008007 260429008007`; the USD or EUR CSV will show "+Y USD/EUR" with the same `0260429008007` ID. These pairs net to a small FX-spread loss only (~0.5%). **Always cross-check all 5 account CSVs by Meddelande/OCR ID before flagging an outflow as unidentified.**

Confirmed FX-wash IDs in April 2026:
- `0260424003669` (-10,288 SEK) — paired with EUR/USD account inflows same day
- `0260429008007` (-19,000 SEK ↔ +2,034 USD) — SEK→USD conversion
- `0260429007840` (+18,400 SEK ↔ -2,000 USD) — USD→SEK conversion
- `0260429007794` (-3,557 USD ↔ +3,020 EUR) — USD→EUR (used to top up MOSS-funding EUR account)

**Rule:** Numeric-only `Rubrik` patterns like `02604NNNNN NNNNNNNN` with no recipient name are almost always FX conversions. Confirm by matching IDs across the SEK/EUR/USD CSVs before raising as a mystery outflow.

#### Revenue inflows (positive amounts — SKIP in cost matching)

| Pattern | Source |
|---------|--------|
| `ADYEN` in Namn | Adyen card payment settlements |
| `PAYPAL PTE LTD` in Namn | PayPal settlements to Nordea |
| `BG INBETALNING` in Meddelande | Bankgiro revenue |
| Numeric-only Meddelande (e.g. `0260413012822`) | PSP/Adyen batch settlements (large, typically 50K–300K) |
| `B` + digits in Meddelande (e.g. `B04162109227`) | Bambora/card settlements (small, typically 100–5,000) |

#### Cost outflows (negative amounts — direct matches, not via Corporate Access)

| Pattern | Likely match | VAT? |
|---------|-------------|------|
| `GOOGLE IRELAND LTD` in Namn | Google Adwords. **Cycle: 1 month in arrears.** Service month X is invoiced late month X with förfall ~day 14 of month X+1 (verified May 2026: March bill 83,652 due May 14; April bill 110,265 due June 11). The recurring schedule's day_17 is approximately right but the *month* must lag by one (May payment covers March service, not May). Amount varies 80-130K monthly with ad spend; 120K is mid-range. | No (reverse charge) |
| `DBT Capital` in Namn | DBT loan payments. Budget: interest 37,098 + amortization 98,000 = 135,098. May arrive as single combined payment. | No (financial) |
| `AVGIFTER NORDEA` in Meddelande | Bank fees (recurring, budget ~5,000 but actual ~6,700, day 5–7) | No (financial) |
| `Skuldränta` in Meddelande | Credit line interest (recurring, budget ~10,000 but actual ~14,000, day 1) | No (financial) |

#### Payments NOT visible in SEK CSV

These are paid from other Nordea accounts or other channels and will NOT appear in the SEK account CSV:
- **Voxbone (Bandwidth)**: paid by Henrik's personal AMEX (~79K SEK/month), accumulates on account 2890. Does NOT appear in any Nordea CSV.
- **Linn Kristensson**, **CFO**, **Cision**, **United Spaces**, **Europlanet**: may be paid via bankgiro from a different flow — check if they appear; if not, they may hit later or via another account
- **India Operations**: wire transfer, may show separately

**Internal/other:**
| Pattern | Type |
|---------|------|
| `Sonetel India` or India-related | Internal transfer (is_internal_transfer in forecast) |

---

## Step 3: Cross-Check Against Planned Payments

For each recurring payment from `get_cash_flow_recurring` that is due this month:

1. Check if a matching transaction exists in the CSV (by recipient pattern + approximate amount + date range)
2. **For VAT suppliers**: divide bank amount by 1.25 before comparing to budget
3. Classify as: **Paid** (matched), **Pending** (not yet, due date hasn't passed), **Overdue** (due date passed, no match), or **Deferred to other channel** (resolved via the chase-to-ground rule below).

Do the same for scheduled payments from the forecast's `outflow_details`.

#### Chase-to-ground rule — MANDATORY for every "not in CSV" recurring item

A recurring item past its due date and not visible in the SEK CSV is NOT a benign "not in CSV" entry. It is a **deferred outflow** that will surface later, often as a single large utlägg reimbursement in a future month — exactly the pattern that caused the Apr 2026 EOM squeeze (Voxbone wallet top-ups skipped Nov + Feb cycles, landed as a 77K backfill in Henrik's March batch).

For every recurring/scheduled item that fails the SEK CSV match, you MUST do all of:

1. **Cross-account search** — scan all 5 account CSVs (91-55-78-9 SEK/EUR/USD, 214-72-32-9 EUR, 214-72-33-7 USD) for the same supplier name or amount, in case the payment hit a different currency account.
2. **Channel mapping check** — consult the channel-mapping table (Voxbone id 1 → Henrik utlägg, Openrouter id 27 → Tomas utlägg, etc.). If the recurring is flagged as flowing via utlägg, the SEK CSV will *never* show a direct payment.
3. **Expense bundle check** — open the latest `~/Downloads/Accountant_Bundle_YYYY-MM_*.zip` and search the per-person `expense_summary.txt` files for matching line items by date and supplier. Note the date span of those line items.
4. **Compute the cumulative gap** — for each utlägg-flow recurring (Voxbone id 1, Openrouter id 27): sum the line items in the latest 6 months of expense bundles vs. cumulative budget over the same months. If reimbursement lags > 1 month behind, flag the gap as a deferred outflow.
5. **Estimate the deferred landing date** — when will the unreimbursed personal-card spend actually flow out of the bank? Typically: next monthly expense batch run. If batches are running monthly, ~end of next month. If batches are backlogged, this could land as a multi-month catch-up.
6. **Add the deferred outflow to the EOM cash-flow plan**, not as a "not in CSV" parking-lot entry. Show it as: `Deferred utlägg reimbursement (Voxbone catch-up): est. ~77K, expected ~end of [month]`. The forecast ought to plan for this even though it doesn't appear in `get_cash_flow_recurring`.

If after all checks the item is still missing entirely from every channel, classify it as **MISSING — escalate**. Could indicate supplier change, contract dispute, accounting error, or invoice not received.

#### Variance follow-up — every line, no exceptions

In addition to "not in CSV" follow-up, every matched recurring/scheduled item with meaningful variance vs. budget (>10% delta, or >5K SEK absolute) must be investigated:

- **Over-budget**: ask why. Is this a one-off (annual ÅR work, audit, travel)? A new structural cost? A miscategorized item? Document the cause.
- **Under-budget**: also investigate. Under-payment may indicate a missed invoice that will catch up next month — a deferred outflow disguised as a "saving". Check the supplier's invoice history.
- **Channel mismatch**: bank shows the supplier got paid, but via a different channel than the budget assumed (e.g. SEB card instead of bankgiro). Note for budget restructuring.

Document each variance in the MTD crosscheck table with a one-line explanation. Do not leave any line unexplained — silent acceptance of variances is what allows drift to compound into a quarter-million-kronor surprise.

Produce a table:

```
| # | Planned Payment       | Due Day | Budget excl. VAT | Bank amount | Excl. VAT | Delta  | Status     |
|---|-----------------------|---------|-----------------|-------------|-----------|--------|------------|
| 1 | Google Adwords        | 17      | 120,000         | 107,044     | 107,044   | -11%   | Paid       |
| 2 | BDO accounting        | 28      | 53,000          | 83,066      | 66,453    | +25%   | Paid       |
| 3 | SEB credit card       | 10      | 152,000         | 190,527     | 152,422   | +0.3%  | Paid       |
...
```

### BDO cost structure (from invoice audit, Apr 2026)

BDO costs vary significantly by month. Annual breakdown (all excl. VAT):

| Category | Annual est. | Note |
|---|---|---|
| Monthly baseline (bokföring, leverantörer, lön, licenser) | ~394,000 | ~33K/month |
| Årsredovisning / Bokslut (spread Jan–Mar) | ~121,000 | Concentrated in Jan-Mar invoices |
| Kvartalsrapport Q3 | ~38,000 | One-off, hits ~November invoice |
| Halvårsrapport (koncern) | ~32,000 | One-off, hits ~February invoice |
| Löpande konsultation FS (ad-hoc) | ~36,000 | Irregular |
| Other one-offs | ~15,000 | Projektledning, kundmöte, etc. |
| **Annual total** | **~636,000** | **Avg ~53K/month** |

### Annual report (Årsredovisning) total cost — across vendors

The ÅR is a multi-vendor cost. To verify all of it lives in recurring:

| Vendor | Cost (excl. VAT) | Timing | In recurring? |
|---|---|---|---|
| **Forvis Mazars** — audit fee FY2025 | **135,500** total | split a conto + slutfaktura | partial |
|   • A conto faktura | 100,000 | invoiced Mar/Apr, paid Apr 14 | id 46 ✓ |
|   • Slutfaktura | 35,500 | invoice ~Apr 14, due May 4 | id 49 (needs amount + month fix: 35,500 in May, day 4) |
| **BDO** — ÅR/bokslut work | ~121,000 | spread across Jan–Mar invoices | folded into id 20 baseline (53K/mo handles average) |
| **Schibsted Marketing** — AGM ads | ~7,595 | annual ~April, day 27 | **MISSING — to add as annual recurring** |

**Reference invoice (Forvis Mazars 20213987, Apr 14, 2026):**
- Beskrivning: "Arvode revision räkenskapsåret 2025 - slutfaktura"
- Totalt exkl. moms: 135,500 SEK
- A contofaktura already paid: -100,000 (excl. VAT) / -25,000 (VAT)
- Slutfaktura due: 44,375 SEK incl. VAT (2026-05-04)

**Action when ÅR cycle begins each year:** confirm both Forvis lines are in recurring (a conto + slutfaktura) and that the slutfaktura amount tracks the actual invoice (auditor fees can drift). The slutfaktura always hits ~3 weeks after the a conto, so split should be ~April + ~May.

### Schibsted Marketing Services — annual AGM ads

- Annual recurring cost, hits late April (day ~27) for the May AGM publication
- Apr 2026 actual: 9,493.75 SEK incl. VAT = ~7,595 SEK excl. VAT
- Bank pattern: appears bundled in Corporate Access entries (e.g. Apr 27 -14,020.98 = Euroclear 4,527 + Schibsted 9,494)
- Account: 496-4920 (Schibsted Marketing Services AB)
- **Status**: Not yet a recurring entry — add as annual SEK, day 27, annual_month 4, ~7,595 excl. VAT

### DBT loan payments — confirmed timing

Per user (Apr 29 2026): **DBT charges amortizations and interest at end of month (EOM)**, not on day 28 strictly. The recurring entries have day_of_month=28 (ids 22, 24, 25, 26) but actual hit may be Apr 28–30. Plan for these as an EOM block:
- id 25: DBT Lån 1 amortization 98,000
- id 24: DBT Lån 1 interest 37,098
- id 26: DBT Lån 2 interest 14,839
- id 22: Nordea amortering 26,042
- id 23: Nordea interest 9,375
- id 21: Nordea credit-line interest 10,000

Also note: when DBT payments are **delayed from the prior month**, they typically arrive as a single combined transaction in early-month (e.g. Apr 9 -136,050 = 98K + 37K combined for delayed-from-March charges).

### Known budget vs. actual patterns

These items consistently run over their budget line:

| Item | Budget excl. VAT | Typical actual excl. VAT | Note |
|---|---|---|---|
| Nordea bank fees | 5,000 | ~6,700 | 34% over |
| Credit line interest | 10,000 | ~14,000 | 38% over, depends on utilization |
| BDO accounting | 53,000 | 33K–103K | Huge variance — baseline ~33K, spikes during ÅR/reporting |

### Unbudgeted items that may appear

| Item | Amount excl. VAT | Frequency | Note |
|---|---|---|---|
| Svensk e-identitet | ~300 | Unknown | BankID service, minor |

Then list any **unmatched outflows** — negative amounts in the CSV that don't correspond to any planned payment or known pattern. Flag these for the user to identify via Nordea drill-down.

### CEO expense reimbursement (account 2890 "Utlägg Henrik Thome")

Henrik pays Voxbone (~79K SEK/month) from his personal AMEX and occasionally covers other company expenses (equipment, SaaS). These accumulate as company debt on Fortnox account 2890.

**To check current debt:**
```sql
SELECT period, amount, SUM(amount) OVER (ORDER BY period) as running_balance
FROM sie_monthly_balances WHERE account_number = '2890' ORDER BY period
```
The SIE data only covers periods uploaded to Fortnox. Add unbooked expenses from the `transactions` table (expense_owner = Henrik, dates after last SIE period) to get the true balance.

**Negative running balance = company owes Henrik.** This is a hidden cash flow liability not visible in the forecast unless explicitly scheduled as reimbursement payments. As of Apr 2026, reimbursement is scheduled in tranches (see scheduled payments).

**Separate from Henrik's loan to the company** (400K SEK, scheduled repayment May-Jun 2026).

### Skatteverket — recurring tax charges and VAT refund timing

**Confirmed via Skatteverket "Bokförda transaktioner" PDF, Apr 29 2026.**

#### Monthly tax payment (recurring id 9)

Every month, Skatteverket debits arbetsgivaravgift + avdragen skatt + debiterad preliminärskatt for the prior month, on day ~12. Payment must arrive by day 12. Typical amounts (2025-2026):

| Month | Total (SEK) |
|---|---:|
| Normal month | ~70,000 |
| Year-end month (January, for December salaries + bonuses) | ~190,000 |
| Quarter with Corona anstånd batch (Feb / Aug) | ~150-160,000 |
| Quarter with small Corona anstånd batch (Apr / Oct) | ~96,000 |

Recurring id 9 set at 70,741 day 12 — **correct for base monthly**. The spikes are handled separately via id 33 (board fees Jan extra) + scheduled Corona anstånd payments.

#### Annual board fee tax spike (recurring id 33)

December's pay run includes the 140K SEK styrelsearvode (recurring id 32, day 25 December). The associated arbetsgivaravgift (~37%) and avdragen skatt land on the January Skatteverket payment, adding roughly **+90-100K** above the normal 70K monthly. Recurring id 33 at 60,000 is **likely underbudgeted by ~30-40K**. Recommended: 95,000.

#### Corona anstånd ("Tillfälligt betalningsanstånd") — almost fully run off

Historical pattern was annual large batches (~75K, 6 tranches) in Feb + Aug, plus smaller supplementals (~26K) in Apr + Oct. **The big batches ended with Feb 2026.** Per the user's Dec 2025 anstånd schedule (verified Apr 29 2026):

| Date | Amount (SEK) | Status |
|---|---:|---|
| 2026-04-13 | 26,055 | ✓ Paid (actual) |
| **2026-08-12** | **8,107** | Future — single tranche, not the historical 75K batch |
| **2027-02-12** | **8,107** | Future |
| **2027-04-12** | **25,859** | Future |
| **Total remaining** | **~42,073** | |

The remaining Corona anstånd is now small enough that it should not materially affect EOM cash flow planning. After April 2027, Corona anstånd is fully done.

**Do NOT project the historical 75-80K Feb/Aug batches forward** — they're complete. Always verify against the latest anstånd schedule (user's annual list, or Skatteverket "Anstånd" portal view, NOT just "Kommande transaktioner" which shows only ~2 weeks ahead).

**To verify current schedule:**
```sql
SELECT id, pay_date, amount, description, enabled
FROM scheduled_payment
WHERE description ILIKE '%corona%anst%' AND pay_date >= CURRENT_DATE
ORDER BY pay_date;
```

#### VAT refund timing — CRITICAL

VAT is filed quarterly. The flow has TWO events that must be modeled separately:

1. **Moms credit appears on Skatteverket account** (Skatteverket "credits" the company for the refund) — typically:
   - Q1 (Jan-Mar) → late April / early May
   - Q2 (Apr-Jun) → mid August
   - Q3 (Jul-Sep) → mid November
   - Q4 (Oct-Dec) → early February
2. **Bank payout (Utbetalning)** — Skatteverket sends what's left after netting against pending tax debts. Typically **1-10 days after the credit**, most often 1-3 days.

Empirical history of bank payouts (2024-2026):

| VAT period | Moms credit | Bank payout | Lag |
|---|---|---|---:|
| Q4 2023 | 2024-01-26 | 2024-01-29 (-57,277) | 3 days |
| Q4 2024 | 2025-02-01 | 2025-02-04 (-119,255) | 3 days |
| Q1 2025 | 2025-04-30 | 2025-05-01 (-98,554) | 1 day |
| Q2 2025 | 2025-08-15 | 2025-08-20 (-25,207) | 5 days |
| Q3 2025 | 2025-11-13 | 2025-11-14 (-167,558) | 1 day |
| Q4 2025 | 2026-02-06 | 2026-02-16 (-46,142) | 10 days |

**Refund amount depends on netting against pending monthly tax debits + Corona anstånd in the window.** That's why Q4 (Feb payout, large Corona offset) and Q2 (Aug payout, large Corona offset) are smaller, while Q1 and Q3 (no big offset) are larger.

**Annual total VAT refund: ~325-500K SEK** depending on Corona anstånd timing. After Feb 2027, refunds will normalize and grow.

**Recurring id 48 (-125,000 SEK quarterly day 30, months 1/4/7/10) is WRONG on both timing and amount.**

**Refined model — "day 12 netting" (per user, May 2026):** Empirically, the bank utbetalning of a refund clusters around day 12 of the month after quarter end — the same day as the monthly Skatt debit (id 9). Skatteverket's own konto nets credits and debits before payout, so even when the refund and the monthly debit hit the bank on different days, the *net cash impact* lands within the day 5–16 window of the post-quarter month. Q4 2025 is the canonical case: credit Feb 6, monthly debit Feb 12, utbetalning Feb 16 (net -46K).

**Action when restructuring id 48:**
- Move payment-day from 30 to **12** (same as monthly Skatt) — models the netting pattern
- Move quarter_months from 1,4,7,10 to **2,5,8,11** (month after quarter end)
- Amount: set to a quarter-specific value or use ~100K midpoint. Q1/Q3 typically larger (~120-170K), Q2/Q4 smaller (~25-80K) due to Corona anstånd offset history. Post-Apr 2027, refunds normalize and Q1/Q3 should grow in line with revenue.
- Net cash impact in the post-quarter month = (refund amount) − (monthly tax debit ~70K) — typically a small inflow (+30 to +100K) on day 12, not the gross refund

**Why this matters:** The original day-30 timing made the forecast count on a refund inflow that was structurally landing 5-16 days later. EOM cash positions at the end of months 1/4/7/10 are over-stated by the modeled refund amount until reality catches up in the following month.

#### Implication for the Apr 2026 cycle

The forecast assumes -125K VAT refund inflow on Apr 30. **Reality: the refund will not arrive until ~May 1-10 and may be larger (~170K).** This is a 1-10 day timing risk for the EOM that's already at -999K SEK saldo. The 125K is being counted on as same-day coverage for BDO + DBT outflows; in practice, those need to wait or breach the credit line briefly.

### India monthly cash requirements

India sends a "Cash Requirements" email each month (from Padma Karanam, cc Prashant Pant). Typical total: ~90 KUSD (~945K SEK). This falls within the existing India recurring budget (~1.5M SEK/month ≈ ~143K USD), so it's not extra cost — but the transfer timing is critical since India's bank runs near zero.

**India advance tax payments** are scheduled as annual recurring payments (ids 39-42) in INR. These are included in the monthly cash requirement email — do NOT double-count by adding them as separate scheduled payments.

**India transfer mechanics (USD account 214 72 33-7):**
- Recipient: SONETEL SOFTWARE SERVICES PVT LTD (account 920020074299969 AXIS USD NEW)
- "Slow" payments take ~3 banking days; **express/SWIFT** takes 1 day but costs more
- Bank sometimes auto-selects slow over express — Henrik has been caught by this before
- Once a payment is registered, it can become **invisible in the bank UI** (cannot be deleted) — register a fresh express if blocked
- May 1 is **Labour Day in India** (bank holiday); transfers must arrive by Apr 29 to clear Apr 30 dependencies
- Padma's typical hard deadline: salaries by 30th, statutory payments by 28th-29th
- **Cross-reference monthly USD outflow total to Sonetel India recipient against Padma's request to track gap**
- Gaps of ~10K USD before EOM are common — usually closed by waiting 1-2 days for Bambora/Adyen USD settlements (~3-5K USD/day) and topping up from PayPal if needed

---

## Step 4: Produce the Report

### Section 1: Current Cash Position

```
| Account                    | Balance        | SEK Equiv  |
|---------------------------|----------------|------------|
| Nordea tillgängligt       | [user input]   | [amount]   |
| PayPal                    | [user input] USD | ~[amount] |
| TOTAL AVAILABLE           |                | [sum]      |
```

FX rates: use approximate (USD/SEK ~10.5, EUR/SEK ~11.0) and note "approximate rates" unless user provides exact figures.

**Important:** The "Nordea tillgängligt" number already contains the credit line. The SEK account saldo from the CSV shows the raw overdraft (typically -900K to -1M). These are two views of the same thing:
- Tillgängligt = credit line headroom + foreign account balances
- Saldo = actual debt position on SEK account

### Section 2: MTD Payment Status (the crosscheck table from Step 3)

Include both bank amount and excl. VAT amount so the comparison is transparent.

### Section 3: Remaining Outflows

```
| Payment                | Due Day | Amount excl. VAT | Bank amount (est.) | Confidence |
|-----------------------|---------|-----------------|-------------------|------------|
| [unpaid items]        | ...     | ...             | × 1.25 if VAT     | High/Low   |
| TOTAL REMAINING       |         | [sum]           | [sum]             |            |
```

Mark confidence as **Low** for items where actual consistently differs from budget (bank fees, credit interest, BDO in reporting months).

**Note:** "Remaining outflows" for cash impact should use the bank amount (incl. VAT where applicable), since that's what actually leaves the account. The excl. VAT column is for cost accuracy.

### Section 4: Forecast Comparison

- Forecast projected balance for today: [from get_cash_flow_forecast]
- Actual total available: [from Section 1]
- Delta: [+/- amount] — ahead/behind forecast
- **Root cause of delta**: break down into (a) revenue variance, (b) cost variance, (c) unbudgeted items

### Section 5: Funding Capacity

**Tillgängligt computation — REQUIRED with full deductions:**

```
Nordea SEK headroom (1,000,000 + saldo, where saldo is negative)
+ Foreign account balances (EUR + USD) × FX
- EUR earmarked for upcoming MOSS / pre-funded outflows  ← deduct earmarked
+ PayPal balance
- 5,000 USD floor for DIDWW auto-refill                  ← deduct floor
- (Do NOT count PayPal balance as same-day cash; it's T+3)
= TRUE tillgängligt
```

Always show both lines: gross tillgängligt AND tillgängligt-after-deductions. The user must see what's actually accessible *today* vs. what's stated on the dashboard.

**Funding capacity:**

```
True tillgängligt:                   [from above]
- Remaining outflows (bank amt):     [from Section 3, incl. VAT estimates]
- Deferred outflows discovered:      [from chase-to-ground rule]
- Safety buffer:                     200,000
= AVAILABLE FOR AD-HOC:              [result]
```

If negative: "Need [X] more days of revenue (~[daily rate] SEK/day) before ad-hoc transfers are possible."

### Section 5b: EOM-cluster stress test — REQUIRED

For every analysis, identify the most concentrated 7-day outflow window in the rest-of-month forecast and check whether it can be funded:

```
For each 7-day window {today..today+30}:
    Outflow_7d = sum of all recurring + scheduled + deferred outflows in window
    Inflow_7d  = run-rate revenue × 7 (use forecasted, not optimistic)
    Available_in_window = (true tillgängligt at window start) + Inflow_7d - Outflow_7d
    If Available_in_window < safety_buffer (200K) → flag RED
    If Available_in_window < 0 → flag CRITICAL (will breach credit limit)
```

Show the worst-case window in the report. If RED or CRITICAL, surface the data and use the priority tiering in Section 5b.1 to indicate which items can absorb the squeeze. Do not propose contacting the bank, requesting credit-line extensions, or other operational moves the user did not ask for — Nordea has stated the 1 MSEK facility is fixed (Key Rule 12). Stick to: which payments are protected (Tier 1), which can be re-timed within the month (Tier 2/3), and what dates the SEK saldo recovers naturally.

**This step exists because the Apr 2026 squeeze was a clustering failure (MOSS + BDO + DBT + India hitting same week against a 1M credit line at 99.99% utilization). A correct budget can still produce a liquidity crisis.**

### Section 5b.1: Payment criticality tiering — REQUIRED for any "what to defer" recommendation

Not all outflows are equal in a tight EOM cluster. When the stress test shows a window cannot fund all queued outflows, **never propose deferring people-payments to free capacity for vendors.** Apply this tier ranking:

**Tier 1 — Never late, must clear on time:**
- **Staff and near-staff contractors** — Tomas André, Linn Kristensson, Fluff/Rainbow, CFO Södra Lund, Sebastian, Henrik utlägg, Martin utlägg, board members. These are real people whose income depends on us. **Delaying their payments is not a cash-flow tactic.** If a contractor's payment is queued and would fail the credit-line check on the due date, the right framing is "this is a liquidity problem we need to solve another way" — not "let's delay the payment."
- **Statutory tax** — Skatteverket arbetsgivaravgift / avdragen skatt (penalty interest, possible Kronofogden escalation)
- **Salaries** — wages, payroll, employer obligations
- **MOSS/OSS VAT** — Skatteverket EU VAT (penalty interest)
- **DBT loan amortization + interest** — loan covenants, default risk
- **India transfers for salaries / statutory** — when Padma flags hard deadlines

**Tier 2 — Soft constraint, late is acceptable in tight weeks:**
- **SEB credit card autogiro** — has been late before without disaster. Nordea may charge overdraft if it pushes saldo past the limit, but the SEB relationship tolerates short delays.
- **BDO accounting** — flexible payment terms
- **Forvis Mazars (audit)** — flexible
- **G&W advisor** — flexible
- **Loopia, domain registrars** — flexible

**Tier 3 — Negotiable / discretionary:**
- **Cision, Euroclear, United Spaces, Schibsted Marketing, Mangold, Kommissionären** — small commercial vendors, can be re-timed within the month if needed

**Rule:** When recommending deferrals in a tight week, ALWAYS protect Tier 1, defer from Tier 2 first, only touch Tier 3 if Tier 2 alone doesn't free enough capacity. Never propose delaying contractor or staff payments to make room for vendor payments.

### Section 5c: Operational SEK saldo floor

The Nordea SEK credit line limit is 1,000,000. Operating practice: **do not let the SEK saldo drop below -950,000** (50K buffer). Any forecast scenario that would cross -950K requires explicit user decision and communication, not passive drift. Flag any day in the forecast where saldo would cross -950K as a risk in the report.

### Section 6: Forecast Reliability Assessment

Based on the crosscheck, rate the forecast:
- **Budget accuracy**: what % of matched items were within 10% of budget (excl. VAT comparison)?
- **Missing items**: how many SEK in costs appeared that have no budget line at all?
- **Verdict**: Can the rest-of-month forecast be trusted? If not, what's the estimated error margin?

---

## Key Rules — DO NOT VIOLATE

1. **Credit line (1 MSEK) is INSIDE Nordea tillgängligt.** Never add 1,000,000 on top.
2. **Revenue is lumpy.** Adyen and PayPal settle in batches (every 2-7 days). Do not model as smooth daily inflow.
3. **India cash is not visible.** We have no data on Sonetel India's bank balance. Do not guess.
4. **"Corporate Access" is NOT one payment.** It bundles multiple unrelated payments. Always drill into sub-items before matching against budget. Ask the user to check Nordea transaction details for any unidentified Corporate Access entry.
5. **The CSV Saldo column is the SEK account only.** It does NOT include EUR/USD accounts or credit line headroom. Use it only for SEK account tracking, not total position.
6. **Payments marked `is_internal_transfer: true`** (India transfers) are excluded from net cash burn in the forecast. They still represent real cash outflow from the Swedish bank account.
7. **When in doubt, show your math.** Better to show a transparent calculation the user can correct than to state a confident wrong number.
8. **Some planned payments won't appear in the SEK CSV.** They may be paid from EUR/USD accounts, or via personal-card → utlägg reimbursement, or via other banking channels. **Always run the chase-to-ground rule** (Step 3 above) — never accept "not in CSV" as a final state. Deferred outflows in this category caused the Apr 2026 EOM squeeze.
9. **Tillgängligt is always reported with full deductions.** Subtract the PayPal 5K USD floor (DIDWW lock), exclude EUR earmarked for upcoming MOSS, and exclude PayPal balance from same-day available cash (T+3 lag). Show both gross and net so the difference is visible.
10. **Operational SEK saldo floor: -950,000.** The 1M credit limit is the hard ceiling; -950K is the soft floor. Any scenario that crosses -950K must be flagged for explicit user decision, not allowed to drift silently.
11. **Always run the EOM-cluster stress test (Section 5b).** A correct budget plus a tight credit line still creates liquidity crises if outflows cluster in one week. Identify the worst 7-day window and verify it can be funded.
12. **The 1 MSEK Nordea credit line is fixed.** Nordea has indicated they cannot expand it. Do not propose "increase credit line" as a structural fix. Real structural options are: (a) renegotiate vendor payment timing to de-cluster EOM (e.g. move DBT to mid-month), (b) accelerate receivables, (c) reduce structural costs, (d) alternative funding (other banks, factoring, shareholder loans), (e) move to monthly VAT periods for faster refund cycles. Always frame mitigations in this set, never expanding the existing facility.
13. **Timing varies.** Planned "day of month" is approximate. Google often hits 2-3 days early, DBT may arrive as a single combined payment on a different day. Match by recipient + approximate amount, not exact date.
14. **Budget is excl. VAT, bank is incl. VAT.** Always divide bank amounts by 1.25 for Swedish VAT suppliers before comparing. See VAT Handling section for which suppliers charge VAT.
15. **Quarterly VAT flows.** MOSS/OSS outflow (id 47, ~206K) on day 30 of months 1/4/7/10. Input VAT refund inflow (id 48) on day 12 of months 2/5/8/11 (post-quarter month) per the netting model — see Skatteverket section. Net quarterly VAT outflow: ~80-150K depending on Corona offset and revenue mix. Both are real cash flows — the bank pays costs incl. VAT and collects VAT from customers even though the forecast uses net/excl. figures. EOM snapshots may include accrued MOSS debt — this is a known timing artifact.
16. **Hejdad detection mandatory.** A non-zero Hejdad count is never routine — it is Nordea silently holding a payment because the credit line was insufficient at the scheduled debit date. Trace the cause (which payment, which date, against what saldo), compute when SEK headroom recovers, and treat held items as deferred outflows to plan for. Whenever EOM SEK saldo is within 50K of the credit limit AND a payment is due day 1 next month, flag the Hejdad risk *before* it triggers. Never frame Hejdad as a discretionary delay — it is a leading indicator of credit-line saturation.
17. **No unsolicited operational advice.** When the analysis surfaces a constraint, report the data and the implication. Do not propose contacting the bank, requesting credit-line extensions, calling vendors to negotiate, or other operational moves the user did not ask for. Nordea has stated the 1 MSEK credit line cannot be extended (Rule 12); never speculate that they might. If the user wants suggestions, they will ask. Until then, stick to facts and forecast implications.
18. **Payment priority hierarchy is non-negotiable.** When recommending how to handle a tight cluster, follow Section 5b.1 tiering: protect staff and near-staff payments first (Tomas, Linn, Fluff, CFO, Henrik utlägg, Martin utlägg, salaries), statutory tax second, financial covenants third, then commercial vendors. **Never propose delaying contractor or staff payments to make room for vendor payments.** Fluff, Tomas, Linn, CFO etc. are people whose income depends on us — they get paid on time even when SEB Kort or BDO has to wait. SEB Kort late payment has happened before without damage; missing a contractor's payment damages the relationship and is structurally wrong.
19. **Always update log.md AND this skill file** after every analysis. The skill must improve with each use.

20. **CR discipline is non-negotiable.** Every change to `recurring_payment`, `scheduled_payment`, or `business_parameters` for cashflow_* goes through the tiered CR process documented at the top of this file (Change Request discipline section). Inline mini-CR for one-offs, mini-CR + 1 reviewer for recurring changes, full CR + 2 reviewers for structural changes. Every change ends with a verify query and a `docs/changelogs/YYYY-MM.md` entry. Skipping any step is forbidden — the Apr 29 → May 8 DBT slippage proved why.

21. **Delayed payments must be added in the same response they're mentioned.** When the user says "X is delayed from EOM month Y to date Z," the assistant adds the scheduled_payment immediately, verifies with SELECT, confirms in the response. Notes in `log.md` are not a substitute for actual model edits. Recurring entries stay unchanged — the delayed payment is always a one-off scheduled overlay.

---

## Account Reference

| Account | Currency | Type |
|---------|----------|------|
| Plusgiro 91 55 78-9 | SEK (multi-currency) | Main operating account, has 1 MSEK credit line |
| Plusgiro 91 55 78-9 | EUR | EUR sub-account |
| Plusgiro 91 55 78-9 | USD | USD sub-account |
| Plusgiro 214 72 32-9 | EUR | Dedicated EUR (swept nightly to main) |
| Plusgiro 214 72 32-9 | USD | — |
| Plusgiro 214 72 33-7 | USD | Dedicated USD (swept nightly to main) |
| PayPal | USD | Revenue collection, settled to Nordea periodically |
