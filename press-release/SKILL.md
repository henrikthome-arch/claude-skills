---
name: press-release
description: Draft and finalise Sonetel AB press releases (Swedish primary, voluntary English co-publication) for Cision distribution. Use from inside a launch folder when working on `10-press-release-*.md` and `99-cision-paste.html`. Knows the boilerplate folder, format rules, MAR statement decision, and Cision-paste workflow.
argument-hint: "[launch-folder-slug | sv | en | mar | cision-paste]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel AB press releases. It expects the current working directory to be inside `Sonetel/Investor relations/04_content/press_releases/YYYY-MM-DD-slug/` (a launch folder). If the cwd is outside that path, STOP and tell the user: "The press-release skill runs inside a launch folder under `04_content/press_releases/`. Current directory: [cwd]. Either cd into a launch folder, or use the `ir` skill for general IR work."

You are helping Henrik Thomé draft press releases for **Sonetel AB (publ)**, ticker SONE, Nasdaq First North Growth Market Stockholm. Press releases are the regulated channel — they are the **timing pivot** for every coordinated launch (per PROJECT_RULES.md §Launch Coordination).

This skill is downstream of the `ir` skill. The launch folder, `00-story.md` master, and `01-checklist.md` are produced by `ir`. This skill takes the master story and produces:

- `10-press-release-sv.md` — Swedish press release (primary).
- `10-press-release-en.md` — voluntary English co-publication (when audience warrants).
- `99-cision-paste.html` — Cision-paste-ready HTML body.

---

## Authoritative source

**Sonetel's board-confirmed Information Policy ver 1.4** is the authoritative source for press-release format and MAR rules. See `Corporate documents/Informationspolicy/Informationspolicy - Sonetel AB, ver 1.4.pdf` and PROJECT_RULES.md §MAR & Disclosure.

Key references for this skill:
- **Policy §2 Allmänt** — Swedish is the official disclosure language.
- **Policy §6.1** — Delayed disclosure procedure.
- **Policy §7.1** — Distribution channel (currently Cision).
- **Policy §7.2** — Press-release format.
- **Policy §7.3** — Spokespeople (CEO / CFO / Chair only).
- **MAR Art. 17** — disclosure obligation; statement required where applicable.

---

## Boilerplate folder (single source of truth)

`04_content/press_releases/_boilerplate/` contains:

| File | Purpose |
|---|---|
| `om-sonetel-sv.md` | Swedish company boilerplate (auto-appended in Cision UI as CompanyInformation; verify before each release) |
| `om-sonetel-en.md` | English company boilerplate |
| `kontakt.md` | Contact block (Henrik Thomé, VD, 08-525 060 11, henrik@sonetel.com) |
| `mar-statement-sv.md` | MAR Art. 17 statement template |
| `format-rules.md` | Style rules extracted from Cision corpus analysis |
| `launch-checklist.md` | Launch-checklist template (used by `ir` skill, not here) |

**Do not re-derive these from scratch.** Read the boilerplate file and insert it. If a boilerplate file looks wrong for the current release, raise it — don't silently rewrite.

---

## Format rules (canonical — see `_boilerplate/format-rules.md`)

### Structure (in order)

1. **Headline** — factual, concrete, no marketing puffery. **Typical 30–55 chars; preferred max 70 chars** (per Cision-corpus analysis — see headline-length section in `_boilerplate/format-rules.md`). The technical Cision email-subject preview cap is ~100 chars but Sonetel's house norm is materially tighter; 80+ chars is exceptional.
2. **Lead paragraph (ingress)** — the 5W's in ≤ 2 sentences.
3. **Supporting paragraphs** — concrete detail, in plain prose. **No bullet lists in the body.** Numbered lists allowed sparingly; bullet lists rarely if ever (Sonetel's house style is prose).
4. **CEO quote** — one or two paragraphs, in quotes, attributed to "Henrik Thomé, VD" (SV) / "Henrik Thomé, CEO" (EN). Quote must be authorised by Henrik before publish (he is the spokesperson per policy §7.3).
5. **Currency note** (if applicable) — e.g., "Samtliga belopp avser SEK." (Tax avoid where redundant with "kr".)
6. **Audit caveat** (if applicable) — e.g., "Informationen i pressmeddelandet är inte granskad av bolagets revisor."
7. **Boilerplate (Om Sonetel / About Sonetel)** — insert from `_boilerplate/om-sonetel-{sv|en}.md`.
8. **Contact block** — insert from `_boilerplate/kontakt.md`.
9. **MAR statement** — insert from `_boilerplate/mar-statement-sv.md` **only if** the release falls into the MAR-statement decision rule below.

### Tone and language

- Swedish first; English co-publication is voluntary amplification (not parallel-mandatory disclosure).
- Plain prose. Numbers first. Short paragraphs (2–4 sentences).
- No filler ("vi är glada att meddela", "we are excited to announce") — start with the news.
- No emoji. No exclamation marks. No "platform", "scalable", "next-gen", "AI-first", "AI-native", "disruptive", "revolutionary".
- Use vocabulary filter from [04_content/content_templates.md](../../../04_content/content_templates.md): lead-with terms, descriptor-only terms, avoid terms, never-claim terms.

### Sonetel-specific don'ts

- Do NOT call Sonetel "30-year-old" or invoke 1994 incorporation. Use "live since 2009" or "listed since 2017".
- Do NOT name the AGM shareholder in any external content.
- Do NOT state Voice Lake pricing ($35 / $90) externally — those are internal targets, not commitments.
- Do NOT claim Voice Lake is generally available.
- Do NOT lead with Mangold, the -19% drop, the Nasdaq spread widening, or the auction-trading threat.
- Do NOT introduce new investor-relevant facts in a press release that aren't already in the master story (`00-story.md`). If a fact appears here that wasn't in the master, fix the master first.

---

## MAR decision log per launch (MANDATORY)

Every launch folder must contain `02-mar-decision.md` recording the classification and reasoning — **even when the call is "not MAR".** This is institutional record-keeping; the reasoning is the artifact, not the verdict.

Write `02-mar-decision.md` **before** drafting the press release. The classification drives:
- Whether the MAR statement (`_boilerplate/mar-statement-sv.md`) is appended.
- Whether CA pre-notification (G&W / Niklas Nyström) is required per policy §6.2/§6.3.
- Whether an Art. 18 insider-list event is recorded.
- Whether closed-window §7.6 discipline applies.

Required fields (mirrored from PROJECT_RULES.md §Launch Coordination):

1. **Classification** — `MAR` / `not MAR (non-regulatory product news)` / `not MAR (governance/structural)` / `material but sub-threshold (§8)`.
2. **Reasoning** — walk through the MAR Art. 7 four-prong test (precise · non-public · reasonable-investor-relevant · likely-significant-price-effect). State which prong fails (or all are met) and why.
3. **What we are NOT claiming** — the specific facts that, if added, would re-classify the release. Gates against drift.
4. **Decided by** — Henrik (CEO) per policy §5; record date and any consultation (CFO, CA).
5. **Pre-publish CA notification** — required for MAR-classified releases per policy §6.2/§6.3; record either way.
6. **References** — prior public disclosures that establish "non-public" prong fails (if applicable), policy sections, related CRs.
7. **Post-launch verification** — checklist for T0 + 7 days that retrospectively supports the call.

The file stays in the launch folder permanently. Retained indefinitely per disclosure-records retention rule.

---

## MAR statement decision rule

The MAR statement (`_boilerplate/mar-statement-sv.md`) is appended to releases that disclose **inside information** under MAR Art. 7 — the Art. 17 disclosure obligation kicks in. **The decision is recorded in `02-mar-decision.md` (above), not re-derived in the release draft.**

**Append MAR statement when** the release is:

- Periodic financial report (Bokslutskommuniké, halvårsrapport, kvartalsrapport).
- Material financial event (revenue revision, profit warning, write-down, capital raise).
- Material operational event with quantitative price-sensitive impact (large customer loss/win with disclosed financial effect, regulatory action affecting operations).
- Anything that meets the MAR Art. 7 four-prong test: precise · non-public · reasonable-investor-relevant · likely-significant-price-effect.

**Do NOT append MAR statement when** the release is:

- Structural / governance news that is regulatory-required (board appointments, AGM notice, share-buyback authorisation) — these are disclosure requirements but not under MAR Art. 17.
- Pure product news (mobile app release, feature ship) where no quantitative financial impact is being disclosed.
- Marketing/PR news (partnerships without financial terms, customer stories).

**When in doubt:**
- Ask the CEO. The CEO sets the MAR class on the launch checklist.
- Default to **omit** for non-financial/non-quantitative product news; default to **include** for anything touching the financial number stream.

The decision is recorded in the launch folder's `01-checklist.md` MAR-class field and re-confirmed in `02-final-mar-assessment.md` post-launch.

---

## English co-publication decision

Per Informationspolicy §2, Swedish is the official disclosure language. English is **voluntary co-publication**, used when:

- The release is investor-relevant and the international audience needs immediate access (First North Rulebook 4.1 market-understanding consideration).
- The product news has international customer reach.

For each release, decide and record in the checklist:

- **SV-only** — typical for governance/structural news with primarily Swedish audience.
- **SV + EN simultaneous** — typical for inside-information disclosures with international investor audience.
- **SV first, EN follows within hours** — acceptable for product news where translation slip doesn't create disclosure asymmetry.

**Both versions cite the same Cision release timestamp.** Do not present EN as a separate later news event.

---

## Drafting workflow

Run from inside the launch folder. The master story (`00-story.md`) is your input.

### Step 1 — Read inputs

1. Read `00-story.md` (master story for this launch).
2. Read `01-checklist.md` (MAR class, headline angle, language decision, T0).
3. Read `02-mar-decision.md` (classification + reasoning). **If missing, stop and write it first** — the press-release draft cannot be finalised without the MAR call recorded.
4. Read `_boilerplate/format-rules.md` (in case it changed).
5. Read `_boilerplate/om-sonetel-sv.md` (and `om-sonetel-en.md` if EN).
6. Read `_boilerplate/kontakt.md`.
7. If MAR statement applies (per `02-mar-decision.md`): read `_boilerplate/mar-statement-sv.md`.

### Step 2 — Draft Swedish (`10-press-release-sv.md`)

**🚨 PROCESS RULE (CEO directive 2026-05-12) — Claude drafts, then iterates with GPT-5 until Claude judges the draft ready for the Step 3 investor-lens review. Do NOT shortcut to "GPT drafts from a brief alone" or to "Claude drafts alone".**

This **overrides** the Tier 1 "GPT drafts" classification in [`05_ai_workflow/openai_swedish_drafting.md`](../../../05_ai_workflow/openai_swedish_drafting.md) for press-release bodies specifically (a follow-up CR will formalise the workflow-doc update). Reasoning: Claude holds the full session context (master story, equity story, conversation history, headline angle, MAR class, customer-base nuances, vocab rules, CEO-committed framing). A Claude-written first Swedish draft preserves all of that. GPT-5 then refines for native Swedish fluency, removing anglicisms, juridiska passiva konstruktioner, and AI-slop register that an attentive Swedish reader spots immediately. Claude evaluates each GPT pass and iterates until satisfied.

**Workflow:**

1. **Claude writes the initial Swedish draft.** Full body + CEO quote(s), using all session context. Apply vocab rules from `_boilerplate/format-rules.md` and the project vocabulary filter. This is the rough draft, not the published version — expect it to be stiff on first pass.
2. **Claude ↔ GPT-5 iteration loop:**
   - Compose a brief or use the polish-only system prompt at `~/.claude/scripts/swedish-polish-prompt.txt`. Pass the Claude draft via `--user-file` to `~/.claude/scripts/openai_call.py`. Always set `--max-tokens 12000` minimum (gpt-5 is a reasoning model; lower budgets truncate with `finish_reason=length` and no usable output).
   - Read the GPT output. Evaluate against four criteria:
     - **Facts preserved** — every number, date, name, quote, hedge, and `[PENDING SOURCE]` marker unchanged.
     - **Vocab clean** — no AI-slop (`format-rules.md` avoid list + project vocabulary filter).
     - **Idiomatic Swedish** — no anglicisms, no juridisk passivkonstruktion ("förenat med kostnader"), no stilted hanging "framåt", no AI-slop register.
     - **Structure preserved** — paragraph count, fact ordering, CEO-quote structure intact.
   - If issues: refine the brief (state specifically what GPT got wrong this pass), or apply targeted Claude edits, or both. Re-call GPT. Typical convergence is 1–3 passes.
3. **Claude judges the draft ready when it can credibly survive an investor-lens review at the Step 3 quality bar (both agents ≥8).** If you can already see issues an agent will catch, don't submit yet — refine.
4. **Record provenance in the file trailer**: each gpt-5 call's model, request-id, timestamp; what each pass addressed; any surgical Claude edits with one-line justification. The audit trail is mandatory — do not skip.
5. **Assemble the file**: Claude-written headline + dateline + Claude-then-GPT-refined body + Claude-then-GPT-refined CEO quote(s) + verbatim `om-sonetel-sv.md` + verbatim `kontakt.md` + (if applicable) `mar-statement-sv.md` + provenance trailer.

**Stays with Claude alone (no GPT pass needed):**

- **Headline** (target 30–55 chars per `_boilerplate/format-rules.md` headline-length section — Claude's corpus-grounding mitigates the Swedish gap on short factual constructions).
- **Dateline.**
- **Boilerplate sections** — verbatim from `_boilerplate/`.
- **MAR statement** — verbatim from `_boilerplate/mar-statement-sv.md` if applicable.
- **Trailer / provenance note.**
- **All vocab filtering, source checking, MAR mechanics, Cision-paste HTML.**

**Skip the GPT iteration loop ONLY when:**

- Release body is <150 words AND has no narrative content (PDMR Art. 19 insider-trade notifications, major-holdings flagging, pure calendar updates). Templated-statutory; no Swedish-prose disadvantage.

**Common failure modes to watch for in the loop:**

- *GPT adds elaborations not in the brief* — drop them in Claude evaluation (it's an additive disclosure risk and undermines fact-preservation discipline).
- *GPT over-formalises* — sometimes the second pass goes from natural to bureaucratic; rewind to a previous pass + re-brief.
- *GPT preserves Claude's stilted phrasing because the brief didn't flag it* — name the stilted phrases in the brief explicitly ("avoid 'förenat med kostnader', 'avser att hålla framåt'").

**This is the new ground rule (CEO 2026-05-12):** *Claude drafts, iterates with GPT until Claude thinks it's good, then runs agent review to the score threshold. Reach quality bar before showing CEO.* Do not regress to GPT-only drafting or Claude-only drafting on grounds of speed or simplicity.

**Mandatory fact-check before draft reaches Step 3:**

- **Any comparative claim** in the draft ("competitors lack X", "first to market", "industry-leading", "få aktörer", "andra aktörer saknar", "kategoristandard hos…") triggers a mandatory WebSearch verification BEFORE the draft is submitted to the investor-review agents.
- Save findings to `01_strategy/competitor_research_<topic>_<YYYY-MM>.md` as a permanent reference (per-release research compounds into a competitive-intelligence corpus over time).
- If verification finds the claim is false or unsupportable, **drop the claim** — don't water it down to a hedged version. False or hedged comparative claims (a) damage credibility with informed analysts, (b) approach MAR territory as misleading value-claims, (c) violate `_boilerplate/format-rules.md` ("No competitor naming. No comparisons…"). Hard-learned 2026-05-12: a proposed "Sonetel får en tydlig konkurrensfördel" sentence was fact-checked against five SMB-VoIP competitors — all five had the capability already. Claim dropped, near-miss documented in `01_strategy/competitor_research_inbound_calls_2026-05.md`.

**Polish-call CEO-phrase preservation pattern:**

When calling `openai_call.py` on a body that contains CEO-supplied verbatim phrases (multi-word swaps from a prior session turn), the system prompt MUST explicitly list those phrases as "preserve exactly". The standard polish prompt's bevaringsregler covers numbers, dates, names, and quotes — but NOT arbitrary CEO-mandated word choices. Example explicit instruction:

```
BEVARA STRIKT (utöver standardreglerna): följande CEO-formulerade fraser ändras INTE under några omständigheter:
- "Huvuddelen" (byt INTE mot "Majoriteten" eller annat)
- "till kundens mobilnummer eller annat lokalt telefonnummer" (lägg INTE till "till ett" eller annan parallellisering)
- [list each CEO-supplied phrase verbatim per release]
```

Hard-learned 2026-05-12: GPT polished "annat lokalt telefonnummer" → "till ett annat lokalt telefonnummer" (added "till ett" for parallel construction). Minor stylistically but it modified CEO's verbatim phrasing. Required Pattern B revert. The polish prompt template at `~/.claude/scripts/swedish-polish-prompt.txt` doesn't list CEO-mandated phrases (they vary per release); the calling skill must add them inline in each polish call's `--system` argument.

### Step 3 — Investor-lens review with quality gate (mandatory)

**🚨 ORDER RULE (CEO directive 2026-05-12):** the investor-lens review + iteration to a documented quality threshold happens BEFORE the CEO sees the draft. Never present a draft to the CEO that hasn't cleared this gate. The review IS the quality gate.

**Quality threshold for CEO presentation: BOTH review agents must score the draft ≥8/10** on their respective top-line investor-relevance dimension:

- **Prompt A (retail investor):** *"would I, as a Swedish retail investor on Avanza/Nordnet, find this interesting and act-able?"* — score 1–10 at top of response.
- **Prompt B (institutional analyst):** *"investor-relevance and execution-signal quality"* — score 1–10 at top of response (derived from the structured questions; agent also produces the verdict + Y/N model-update call).

If **either** agent scores <8, iterate the draft and re-submit. **Maximum 3 review cycles.**

**Cycle structure (mandatory):**

1. **Submit current SV draft to both agents** — single message, two `Agent` tool calls in parallel (`general-purpose` subagent type). Persona prompts in [`investor-review-prompts.md`](investor-review-prompts.md); fill in the placeholders (launch folder, release type, headline angle, T0, MAR class, language decision, killer fact, known risks).
2. **Read both responses.** Record the two scores.
3. **If BOTH ≥8 → quality gate passed.** Skip to "Quality gate passed" below.
4. **If EITHER <8 → synthesize convergent feedback, iterate, re-submit:**
   - **Convergent feedback** (both agents flag the same issue) must be addressed — usually structural (framing, headline, contradictions, vocab slips).
   - **Divergent feedback** is judgment-call material — apply only what improves the draft per Claude's evaluation against the equity story / vocab filter / fact discipline.
   - **Apply via Pattern A (preferred for substantive fixes):** refine the Step-2 brief with explicit new guidance; re-loop Claude ↔ GPT-5 per Step 2 mechanics.
   - **Or Pattern B (allowed for narrow corrections that do NOT introduce new Claude-formulated Swedish prose):**
     - **Pure deletions** of words, phrases, or sentences (you can't worsen Swedish by removing).
     - **CEO-supplied verbatim swaps** — single-word or multi-word, as long as the replacement is the CEO's exact phrasing, not Claude-formulated. Examples: single-word swap "Majoriteten" → "Huvuddelen"; multi-word phrase swap "till en lokal telefon" → "till kundens mobilnummer eller annat lokalt telefonnummer" (CEO supplied 2026-05-12). The integrity is: the new prose is CEO-authored, not Claude-authored. **Do not GPT-polish CEO-supplied swaps** — GPT might revert the CEO's specific phrasing.
     - **NOT for sentence merges, paragraph restructures, or anything where Claude formulates new Swedish phrasing (even ≤3 sentences).** If a fix introduces new Claude prose, it MUST go through a GPT-5 polish pass before the file is considered ready. Otherwise Claude-formulated Swedish leaks into the final text and you lose the entire point of running Step 2.
   - Record each Pattern B edit in the trailer with one-line justification + classification (deletion / CEO-verbatim-swap / Claude-prose-then-GPT-polished).
   - Then increment the cycle counter and re-submit to BOTH agents.
5. **Hard cap: 3 review cycles total.**

**If 3 cycles fail to reach the both-≥8 threshold → STOP and escalate to CEO with:**

- The final draft.
- All three cycles' scores (per-agent trajectory) so the CEO can see whether the score is rising, stuck, or oscillating.
- The specific structural critique that didn't get resolved across iterations.
- A 1-sentence diagnostic — what's blocking the score (`"brief insufficient on X — need CEO input"`, `"missing fact requires CEO sign-off"`, `"framing decision needs CEO call"`, `"this story may not be PR-worthy"`, etc.).
- A direct question: does the CEO want to (a) provide the missing input and re-attempt cycle 4, (b) override the threshold and publish anyway, (c) abandon this release? **Don't decide for the CEO; surface the choice.**

**Disclosure-discipline guard inside the loop:**

Do NOT auto-apply agent additions that introduce new investor-relevant facts (customer counts, cost numbers, cycle-time comparisons, percentages, forward dates) not previously disclosed externally. These need CEO sign-off per the First-North price-moving test (see `~/.claude/projects/<project-hash>/memory/feedback_disclosure_first_north_flexibility.md`). When a missing fact is *critical* to crossing the score threshold, surface to CEO at cycle 3 as part of the escalation — not silently during a cycle.

**Quality gate passed (both agents ≥8):**

1. **If the agents recommend post-pass surgical edits ("ship after these edits"), apply them per Pattern A/B rules:** deletions and CEO-mandated word swaps can be applied directly (Pattern B narrow); any edit that introduces new Claude-formulated Swedish phrasing requires a final GPT-5 polish pass before the file is considered ready. **Do not let Claude prose leak into the final file post-gate just because the score is met.**
2. Update `02-mar-decision.md` with documented not-kursdrivande rationale for any newly-included facts.
3. Present the iterated SV draft to the CEO for sign-off, accompanied by:
   - Both agents' final scores (e.g. "Retail 8.5/10, Institutional 8/10").
   - One-paragraph summary of what the reviews caught + how it was addressed.
   - Any divergent judgment-calls flagged for CEO decision.
   - Open MAR/disclosure questions if any.
4. After CEO sign-off, proceed to EN translation and Cision HTML.

**Scope by release type:**

- **Full review with quality gate (both personas, ≥8 threshold):** Type 2 (periodic reports), Type 4 (capital markets), Type 7 (strategy/product news), and any release where the MAR class is borderline.
- **Abbreviated review (one combined agent, ≥7 threshold):** Type 1 (operational metric — templated drafting; check landing, not modellability), Type 5 (liquidity provider), Type 8 (calendar/admin).
- **Skip review:** Type 3 (kommuniké/meeting minutes — statutory templates) and Type 6 (PDMR Art. 19 / major-holdings flagging — very short, formulaic). Run a single sanity-check read instead.

### Step 4 — Draft English (`10-press-release-en.md`) if applicable

- Translate, do not re-author. Same facts, same numbers, same paragraph order.
- Use `om-sonetel-en.md` for the boilerplate block.
- Render the MAR statement in English on the EN version (translation of the standard text). The Swedish statement on the SV version is the legally binding one.

### Step 5 — Build Cision-paste HTML (`99-cision-paste.html`)

Cision's "Distribute Press Release" form takes an HTML body. Produce a single HTML file with:

- `<h1>` for the headline.
- `<p>` for paragraphs.
- `<blockquote>` for the CEO quote (or styled `<p>` if the receiving Cision template doesn't render blockquote).
- `<h2>` for "Om Sonetel" / "About Sonetel" subheading before the boilerplate.
- `<h2>` for "Kontakt" / "Contact" subheading.
- The MAR statement as a final paragraph in italics (`<p><em>...</em></p>`).
- No inline styles, no scripts, no tracking pixels.

The boilerplate auto-appended by Cision UI is configured at the account level (CompanyInformation field). If the auto-append matches `om-sonetel-sv.md` exactly, **do not duplicate it in the HTML body** — verify in the Cision draft preview, then leave it out of the paste. If it differs, paste the correct version into the body and override the auto-append for that release.

### Step 6 — MAR Assessment

Update the CR's MAR Assessment section (or the launch folder's `02-mar-assessment.md` if you keep one pre-launch):

- Q1: Is this inside information per MAR Art. 7? → drives MAR statement decision.
- Q2: Insider list impact (Art. 18 logbook)? → flag Henrik if yes.
- Q3: Closed-window status (trettiodagarsregeln, policy §7.6)? → defer if currently within 30 days of a periodic report unless this *is* the periodic report.
- Q4: Language decision (SV-only / SV+EN / SV-first-EN-follows).
- Q5: Distribution time (T0 = publish timestamp).
- Q6: Spokesperson authorised the quote? (CEO/CFO/Chair only per policy §7.3).
- Q7: Pre-notification to CA (G&W) and Handelsplatsen (Nasdaq First North) per policy §6.2/§6.3 — required for inside-information releases; CA receives a courtesy copy ahead of publish.

### Step 7 — Pre-publish checks

**Pre-publish blocker checklist (all must clear before Step 8 publish):**

- [ ] Headline within corpus norm (target 30–55 chars, max 70 — see `_boilerplate/format-rules.md` headline-length section).
- [ ] **Step 2 GPT provenance recorded in file trailer** (gpt-5 request-id, invocation timestamp, any Claude-applied edits with justification). If this line is missing, the SV body was drafted directly in Claude — return to Step 2 and re-run via `openai_call.py` per `05_ai_workflow/openai_swedish_drafting.md`.
- [ ] Investor-lens review (Step 3) completed; both agents scored ≥8/10 (Type 2/4/7); structural convergent critique resolved.
- [ ] **Master story `00-story.md` aligned with final framing** of the press release. Any framing changes that emerged through review cycles must be reflected back in the master before publish — otherwise next session reading the master will get the wrong context.
- [ ] **Final headline propagated to all four canonical locations** (per Step 7.5): `10-press-release-sv.md` (source) = `00-story.md` `## Slutgodkänd headline` (SV + EN) = `ir_calendar.json` (`headline_sv`, `headline_en`) = `01_strategy/publishing_schedule_2026_summary.html` + `_en.html` (line for the T0 date). Verify each — do not assume.
- [ ] **Folder name reflects firm T0 date** (e.g. `2026-05-15-mobile-public-beta` not `2026-05-08-mobile-public-beta`). Rename only after all internal cross-references are updated.
- [ ] **All numbered derivations in the launch folder re-derived against current `10-press-release-sv.md` and `00-story.md`** (per Step 7.6). No derivation carries an earlier-iteration headline, date, time, framing word ("Release N" vs "first public beta"), CEO quote wording, or key fact. This includes — at minimum — `11-hub-post.md`, `12-linkedin-ceo.md`, `13-linkedin-co.md`, `14-x.md`, `20-customer-email.md`, `21-in-app-banner.md`, `50-internal-slack.md`, `60-app-store-copy.md`, and **`99-cision-paste.html`** (the actual Cision-paste artifact — its H1 and dateline must match `10-press-release-sv.md` exactly). Re-derive from scratch per derivation; do not search-and-replace.
- [ ] **Step 7.7 Swedish grammar-pass executed** on all Swedish quote blocks + every post-Step-3-gate body-prose edit. Any flagged issues fixed before save. Skip only if entire body has been re-polished via Step 2 Tier 1 since last edit AND zero issues were flagged in that polish. Don't ship Swedish quotes that haven't been grammar-validated since their last edit — Claude's Swedish blind spot is documented (CLAUDE.md rule 9) and Claude-agent reviewers share it.
- [ ] **`01-checklist.md` carries no open "date sweep" / "headline sweep" / "framing sweep" warning.** If any such warning is open, the press release is not ready to ship — clear the warning by completing the sweep, or escalate to CEO.
- [ ] **Brief handoffs (`30-blog-brief.md`, `31-help-brief.md`) point downstream owners at current framing.** Each brief explicitly references `10-press-release-sv.md` as the source of truth so sonetel.com / CS draft against the current text, not an earlier iteration.
- [ ] EN-spegel `10-press-release-en.md` translated from final SV; numbers and facts identical.
- [ ] Cision-paste HTML `99-cision-paste.html` built; auto-append boilerplate behaviour verified.
- [ ] No forbidden vocabulary (run vocabulary filter).
- [ ] Every external number has a verifiable source (no `[PENDING SOURCE]` left in draft).
- [ ] Numbers consistent between SV and EN.
- [ ] Boilerplate inserted (or confirmed auto-appended by Cision).
- [ ] Contact block inserted.
- [ ] MAR statement inserted (and dated) if required, omitted if not.
- [ ] No bullet lists in body unless explicitly approved by CEO.
- [ ] CEO has reviewed and authorised the quote.
- [ ] If inside information: CA (Niklas Nyström, G&W) has received the pre-notification copy.
- [ ] Cision draft preview matches the source `.md` file.
- [ ] **Any comparative claim has been fact-checked** and the verification saved to `01_strategy/competitor_research_*.md`.
- [ ] No forbidden vocabulary (run vocabulary filter).
- [ ] Every external number has a verifiable source (no `[PENDING SOURCE]` left in draft).
- [ ] Numbers consistent between SV and EN.
- [ ] Boilerplate inserted (or confirmed auto-appended by Cision).
- [ ] Contact block inserted.
- [ ] MAR statement inserted (and dated) if required, omitted if not.
- [ ] No bullet lists in body unless explicitly approved by CEO.
- [ ] CEO has reviewed and authorised the quote.
- [ ] If inside information: CA (Niklas Nyström, G&W) has received the pre-notification copy.
- [ ] Cision draft preview matches the source `.md` file.

### Step 7.5 — Propagate final headline (MANDATORY pre-publish gate)

**🚨 The skill is NOT "done" with a press release until the final headline in `10-press-release-sv.md` (and `-en.md` if applicable) matches in all four canonical locations.** This is a hard gate — the iteration loop typically advances the SV PR headline past the master story's recorded version, leaving stale headlines in the master, the calendar JSON, and the bilingual HTML calendar summaries.

**Targets (all must match the final SV / EN headline):**

1. **`10-press-release-sv.md`** (and `-en.md` if EN co-publication) — the source of truth.
2. **`00-story.md` → `## Slutgodkänd headline`** — record both SV and EN. If EN is still TBD, mark explicitly: `EN: TBD (placeholder until translation finalised)`.
3. **`ir_calendar.json`** — the activity for this launch: `headline_sv` and `headline_en` fields.
4. **`01_strategy/publishing_schedule_2026_summary.html`** (SV view) and **`publishing_schedule_2026_summary_en.html`** (EN view) — the line for the launch's T0 date.

**When to run:** after CEO sign-off on the SV (and EN, if applicable) draft, before the Cision-paste HTML is finalised — i.e. between Step 6 (MAR Assessment) and Step 7 (Pre-publish checks). The pre-publish checklist (Step 7) verifies these targets are in sync; this step does the propagation.

**Hard-learned 2026-05-14:** the SV PR for the mobile-public-beta launch iterated to ~14 polish/review iterations past the master story's `Slutgodkänd headline` section. The calendar JSON carried the master's stale headline; the bilingual HTML calendar summaries displayed it. The CEO spotted the divergence in the published HTML calendar — *"is this updated with the latest wording from the pressrelease?"* — three places out of sync. From now on this step is non-skippable; if the four targets disagree, the press release is not ready to ship.

### Step 7.6 — Re-derive all numbered launch-folder derivations (MANDATORY pre-publish gate)

**🚨 Step 7.5 propagates the *headline* to the four canonical surface locations. Step 7.6 propagates the *full current framing* (headline + lead + key facts + framing words + CEO quote wording + publish date/time) to every numbered audience-derivation living inside the launch folder.** Without this step, the press release ships with stale LinkedIn copy, stale customer email, stale in-app banner, stale internal Slack, stale App Store copy — and worst of all, a stale `99-cision-paste.html` that is the actual artifact pasted into Cision.

**Trigger:** any change to `10-press-release-sv.md` or `10-press-release-en.md` body that affects a load-bearing field — headline, publish date, publish time, framing words ("Release N" vs "first public beta", "ombyggd" vs "ny app"), CEO quote wording, key facts (customer count, country count, feature list, scale anchors). Also triggered by any change to `00-story.md` master that propagates downward.

**Propagation targets (every numbered derivation present in the launch folder — read `01-checklist.md` to see the full canonical list, since the numbering convention is shared across launches). Typical set:**

1. `11-hub-post.md` — investor hub post.
2. `12-linkedin-ceo.md` — CEO LinkedIn post.
3. `13-linkedin-co.md` — company LinkedIn post.
4. `14-x.md` — X post.
5. `20-customer-email.md` — customer email subject + body.
6. `21-in-app-banner.md` — in-app banner copy.
7. `50-internal-slack.md` — internal Slack message (verify T0 in the staff message matches the firm publish time).
8. `60-app-store-copy.md` — App Store / Play Store "What's New" copy.
9. `99-cision-paste.html` — **the actual paste-into-Cision HTML.** Headline (H1) and date in the dateline must match `10-press-release-sv.md` exactly.
10. Any other numbered derivation present in the folder (e.g. `15-`, `40-`, `51-`, `70-`, `80-`).

**Out-of-scope process docs (do NOT re-derive — these are historical/process records):**

- `00-story.md` — master story (covered by Step 7's "Master story aligned" bullet, not by this step).
- `01-checklist.md` — process record.
- `02-mar-decision.md` — MAR decision record.
- `30-blog-brief.md`, `31-help-brief.md` — handoff briefs to sonetel.com / CS. **Lighter-touch update:** make sure each brief explicitly tells the downstream owner to use the *current* framing (point them at `10-press-release-sv.md` as the source of truth) — but do NOT try to fully re-derive the brief, because the actual blog/help-page draft lives in the receiving project, not here.

**Propagation discipline — re-derive, don't search-and-replace:**

Each derivation has its own audience and length. **Do NOT edit derivations field-by-field hoping to hit the stale strings — re-read the master story and `10-press-release-sv.md`, then re-express each derivation from scratch for its specific audience and channel.** Field-by-field edits leak earlier-iteration framing because the framing isn't always carried by a single quotable string; it's carried by the structure of the paragraph.

**The `01-checklist.md` warning is a STOP signal.** If `01-checklist.md` carries an open "date sweep needed", "headline sweep needed", or any equivalent open warning about stale derivations, **the press release is not done.** Treat the warning as a non-skippable blocker; clear it (by completing the sweep) or escalate to CEO. Do not proceed to Step 8 publish with the warning still open.

**When to run:** after Step 7.5 (headline propagated to four surface locations), before Step 7's pre-publish blocker checklist is signed off. The pre-publish checklist verifies the targets are in sync; this step does the re-derivation.

**Hard-learned 2026-05-14:** the mobile-public-beta launch folder went through two retones — CEO master-story rewrite on 2026-05-12 and a headline change on 2026-05-14. Step 7.5 was added the same day to handle headline propagation to surface locations, but the per-folder derivations were not re-derived. Audit found **9 of 13 derivations stale**: `99-cision-paste.html` had the wrong H1 + wrong date (THE Cision artifact!); `11-hub-post.md` / `12-linkedin-ceo.md` / `13-linkedin-co.md` / `14-x.md` all carried "Release 2" framing; `20-customer-email.md` + `21-in-app-banner.md` had wrong subject and body; `50-internal-slack.md` had the wrong T0 in the staff message; `60-app-store-copy.md` had Release 2 in the App Store release notes. CEO's verdict: *"Skill needs updating to not leave such mess behind."* The skill is not "done" with a press release until every numbered derivation in the launch folder reflects the current `10-press-release-sv.md`.

### Step 7.7 — Final Swedish grammar-pass on quote blocks + post-Step-3 edits (MANDATORY pre-publish gate)

**🚨 Step 2's Tier 1 GPT polish is a per-pass operation, not a per-iteration guarantee.** Subsequent iterations driven by CEO / chair / board feedback (Pattern A re-brief or Pattern B surgical edits) modify other parts of the file without re-polishing CEO quotes or unrelated body-prose lines. **Subtle Swedish grammar bugs that survived Step 2's first pass continue to live in the file across all subsequent iterations until something forces a re-polish of that specific line.** Claude-agent reviewers (Step 3 investor-lens + audit agents) have the same Swedish blind spot as Claude itself per CLAUDE.md rule 9 — they can verify MAR / voice / framing but not catch missing articles, broken parallel constructions, or genus/numerus errors.

**Run an isolated GPT-5 grammar-pass on every Swedish body-prose line in scope.** Lines in scope:

1. **All Swedish quote blocks** in `10-press-release-sv.md` and `99-cision-paste.html` — CEO quotes, CFO quotes, chair quotes, third-party quotes. Quotes are particularly prone to spoken-language artifacts that read correct on first scan but contain grammar issues (article-drops, parallel-construction breaks, "har varit … i flera år" tempus tangles).
2. **Body-prose lines edited via Pattern A or Pattern B AFTER Step 3 score-gate** — even short edits. CEO-supplied verbatim swaps are CEO-authored, not Claude-authored, but the CEO may have drafted them quickly and grammar errors may slip in.
3. **Newly added sentences in any iteration after Step 3 gate** — chair/board feedback often introduces 1–2 new sentences that haven't been through Tier 1 polish.
4. **Lines that contain a noun-pair with a quantifier modifier** (e.g., "lägre kostnader och X vardag", "färre samtal och Y app") — these are the structural shapes where article-drops most often hide.

**How to run:** call `~/.claude/scripts/openai_call.py` with model `gpt-5` and a focused grammar-check system prompt:

```bash
echo "<sentence(s) to check>" | python3 ~/.claude/scripts/openai_call.py --model gpt-5 --system "Du är svensk språkvårdare. Granska följande mening(ar) ord för ord. Hitta varje grammatikfel: saknad bestämd/obestämd artikel, felaktig genus (en/ett), felaktig kongruens (numerus, bestämdhet), felaktig verbform/tempus, felaktiga prepositioner, felaktiga parallel-konstruktioner. För varje fel: peka ut det, förklara, ge korrekt version. Om ingen fel: säg det rakt ut."
```

Apply any grammar fixes that GPT-5 flags **before saving the file**.

**Decision rule — when can you skip?**

Only skip Step 7.7 if **both** of the following are true:
- (a) The file's entire body has been re-polished via Step 2 Tier 1 flow since the last edit (i.e., a full new gpt-5 polish call covered every line).
- (b) The grammar-pass output from that full re-polish flagged zero issues.

Otherwise, run the grammar-pass. The marginal cost is ~$0.01–0.05 per call.

**When to run:** between Step 7.6 (derivation re-derivation) and Step 7 final pre-publish checklist sign-off. The pre-publish checklist (Step 7) verifies this step was executed; this step does the verification.

**Hard-learned 2026-05-16:** CEO Henrik caught *"innebär lägre kostnader och enklare vardag"* — missing indefinite article "en" before "enklare vardag" (countable singular noun in parallel construction with plural "kostnader"). The bug had survived iterations 14 (Tier 1 GPT polish focused on different reformulations), 15 (board-feedback CR on §3), 16 (chair-feedback CR on headline + §3 + §4), and 17 (chair text-edit on §1). Four iterations, multiple Step 3 agent reviews, two audit cycles — none caught it because Claude-agents share Claude's Swedish blind spot. GPT-5 caught it on first focused grammar-pass. Step 7.7 now codifies focused grammar-pass on every Swedish quote block + every post-Step-3-edit before final pre-publish sign-off.

### Step 8 — Publish

- Henrik (or Henrik with Niklas's coordination) publishes via Cision UI.
- Capture the actual publish timestamp.
- Trigger the launch checklist (hub post, LinkedIn, etc., per `01-checklist.md`).
- Update `ir_calendar.json` activity status and `completed_at`.
- Add changelog entry per [docs/CHANGELOG_FORMAT.md](../../../docs/CHANGELOG_FORMAT.md).

---

## What this skill does NOT do

- **Does not write the master story.** That's the `ir` skill's job. If `00-story.md` is missing, stop and tell the user to run `ir` first.
- **Does not coordinate non-press derivations.** Hub post, LinkedIn, customer email, blog post are owned per the launch checklist (Marketing/CS/Product own their lanes). This skill produces only the press release artifacts.
- **Does not draft `30-blog-brief.md` or `31-help-brief.md`** — those are IR-side briefs (handed off to the **sonetel.com project** for the blog and to **CS** for the help page); the actual blog and help-page drafts live in the receiving projects with their own SEO / IA disciplines. The `ir` skill writes the briefs.
- **Does not publish to Cision automatically.** Henrik publishes; this skill produces paste-ready output.
- **Does not bypass the MAR statement decision.** When uncertain, ask the CEO. Do not omit the statement on a release that needs it; do not append it on a release that doesn't.
- **Does not write CRs.** A coordinated launch CR is owned by the `ir` skill (one CR per launch, not one per derivation).

---

## First actions when invoked

1. Verify cwd is inside `04_content/press_releases/YYYY-MM-DD-slug/`. If not, halt with the directory-guard message above.
2. Read `00-story.md` and `01-checklist.md` from the current launch folder.
3. **Verify master-story currency.** Check the master's last-modified timestamp / its "drafted on" line if present. If older than ~1 week, **product reality may have drifted from the master** — surface to CEO before drafting any derivations. Hard-learned 2026-05-12: master said "R2 + R1 shipped 2026-04-13" while actual reality was "first public beta after a year of internal work". Drafts built on a stale master cost multiple review cycles to correct.
4. Read the boilerplate folder's `format-rules.md`, `om-sonetel-sv.md`, `kontakt.md` (and `om-sonetel-en.md`, `mar-statement-sv.md` per launch needs).
5. **Gather CEO directives upfront.** Ask Henrik: (a) headline angle; (b) MAR class; (c) EN co-publication decision; (d) T0 publish time; (e) **any specific words/phrases to use or avoid in this release** (e.g. "huvuddelen" not "majoriteten"; "ny app" not "ombyggd"; no forward-cadence-commitments). Capture these in the brief so they appear in Step 2 from the start. Hard-learned: drip-feeding CEO directives one-per-cycle creates 5+ iterations; gathering upfront converges faster.
5b. **🚨 Validate T0 against the Swedish working-day calendar — MANDATORY pre-draft gate.** Klämdagar (single workday sandwiched between a röd dag and a weekend) + röda dagar are the **worst days of the year** for press-release pickup — readers offline, brokerage feeds quiet, analyst desks thin. **Disqualified date types:**
   - **Röda dagar:** Nyårsdagen (1/1), Trettondedag jul (6/1), Långfredag, Annandag påsk, Första maj (1/5), Kristi himmelsfärd (alltid torsdag), Sveriges nationaldag (6/6), Midsommarafton + Midsommardag, Alla helgons dag, Julafton (24/12), Juldagen (25/12), Annandag jul (26/12), Nyårsafton (31/12).
   - **Klämdagar:** Fredag efter Kristi himmelsfärd; måndag efter Alla helgons dag (om det infaller på en söndag finns annan klämdag); fredagar mellan 1 maj och helg om 1/5 är torsdag; m.fl.
   - **Generellt svaga:** Fredag eftermiddag, vecka 28–31 (semestermånader), 22/12–7/1 (jul/nyårsperiod).
   - **Optimala:** Tisdag, onsdag, torsdag (icke-klämdagar).
   - **Acceptabla:** Måndag (om inte efter helgdag-helg), tidig fredag.
   
   Om föreslaget T0 träffar en disqualified-dag, **STOPPA och föreslå alternativ** till CEO före drafting startar. Hard-learned 2026-05-13: planerade T0 = fredag 2026-05-15 = klämdag efter Kristi himmelsfärd torsdag 14/5. Styrelseordförande fångade misstaget och kallade det *"sämsta dagarna på hela året"*. Master story + dateline + alla 13 derivationer hade hunnits skrivas mot fel datum innan klämdags-felet upptäcktes.
5c. **🚨 Validate T0 against 2-working-day minimum-gap rule — MANDATORY pre-draft gate.** Check `ir_calendar.json` for adjacent comms items and **reject any T0 that is 0 or 1 working days from another comms item**. Two press releases / hub posts / LinkedIn posts / X posts within 24h dilute both — readers don't absorb back-to-back signal density.
   - **"Comms item"** = activities with `type: content` or `type: disclosure`. **Exclude**: `blackout`, `ops`, `event`, `subscription-renewal`, `decision` (these are not externally-published items).
   - **"Working days"** = Tue / Wed / Thu per the established Sonetel publishing rhythm (per `CR-2026-04-29-publishing-day-of-week-and-calendar-cleanup`). Mon and Fri are not normal publishing days; weekends are not working days.
   - **Anchored items override**: regulatory disclosures (periodic reports, AGM-notice, MAR-flagged events) and product release dates tied to actual ship dates cannot move. Non-anchored items (hub posts, LinkedIn topics, voluntary product news) must move to clear the gap.
   - **Corollary — respect dependencies when re-scheduling.** Many calendar activities have `depends_on` relationships (a LinkedIn post depends on its hub post; a hub post depends on the press release). Sliding A forward may force B and C forward too. Walk the dependency chain when proposing the new date; don't break it silently.
   - **Action when violation detected**: STOP, surface the conflict to CEO with (a) the proposed T0, (b) the conflicting adjacent item(s) and their dates, (c) the next valid Tue/Wed/Thu that clears the 2-working-day gap and respects all `depends_on` chains.
   
   Hard-learned 2026-05-14: CEO flagged Tue 28/7 SMS + Wed 29/7 AI-assistant cluster as "Sprid ut" — two comms-events in 24h dilute both signals. An earlier 22/7 + 21/7 cluster had already been moved away from during review-r1, but no minimum-gap rule existed to prevent the next one. The rule now exists; apply it before any new comms-item date is set.
6. **Flag narrative-splitting candidates.** If the master story carries two distinct investor-relevant threads (e.g. product news + AI-transformation; product news + financial-impact), surface to CEO: *should these be two separate releases?* A focused single-thread release usually lands better than a bundled one. CEO decides; the skill prompts the question. Hard-learned 2026-05-12: the sonetel.com AI-speed comparison was bundled into a mobile-app product release and only after multiple agent reviews + CEO feedback did we split it into a separate future AI-transformation release.
5. Draft SV first per Step 2: **Claude writes the initial Swedish draft, then iterates with GPT-5 (`~/.claude/scripts/openai_call.py`) until Claude judges the draft ready for the Step 3 review threshold.** Per CEO directive 2026-05-12.
6. Run the **investor-lens review with quality gate** (Step 3 — two parallel agents per `investor-review-prompts.md`). **Both agents must score ≥8/10 before the draft is presented to Henrik.** Max 3 review cycles. If cycle 3 fails the threshold, escalate to Henrik with score trajectory + diagnostic (do not show as a "ready" draft). **Never bypass the gate or present a sub-threshold draft as ready.**
7. Then draft EN (if applicable), then build the Cision-paste HTML.
8. Run the pre-publish checklist before handing off.

---

## Lessons learned (from the IR project — apply here)

1. The press release is the **timing pivot**. Don't let Marketing/CS/Product publish their derivations before T0.
2. Don't introduce new investor-relevant facts not in the master. The amplification rule reclassifies that as a separate disclosure.
3. Don't "improve" boilerplate silently. If the auto-appended Cision boilerplate looks wrong, raise it; don't rewrite it inline.
4. Sonetel's house style is **prose**, not bulleted feature lists. The Cision corpus consistently uses paragraph form. Don't propose bulleted product release notes for the body.
5. Source every number. `[PENDING SOURCE]` is fine in draft; never in published copy.
6. The MAR statement is a legal artifact, not a courtesy. Wrong on/off classification is a regulatory exposure. When uncertain, ask.
7. **Swedish body prose goes via GPT-5 (Tier 1), not Claude.** Anthropic models are weaker at Swedish than OpenAI's. The skill ships an opinionated mandatory Tier 1 step (Step 2) that calls `~/.claude/scripts/openai_call.py`; don't bypass it on grounds of speed or simplicity. Drafting directly produces visibly stiffer Swedish — anglicisms, juridiska passiva konstruktioner, AI-slop register — that an attentive reader spots immediately. The pre-publish checklist includes a "Step 2 GPT provenance recorded" gate; don't skip it.
8. **Pre-publish checklist must verify provenance.** Step 7 includes a check that the file trailer contains the GPT-5 model and request-id for the Tier 1 drafting call. If that line is missing, the SV body wasn't generated through the correct workflow — return to Step 2.
9. **Never show the CEO a first draft.** The Step 3 investor-lens review is the mandatory quality gate. Iterate convergent feedback first (Pattern A re-GPT, Pattern B surgical edits), then present to CEO with a one-paragraph synthesis. Hard-learned 2026-05-12: CEO read iter-1, reacted with "extremely boring", review was run only then. The right sequence is review-first, CEO-second.
10. **The drafting flow is Claude-then-GPT, not GPT-alone.** Per CEO directive 2026-05-12: Claude writes the initial Swedish using full session context, then iterates with GPT-5 for native Swedish fluency. Earlier sessions had this reversed (GPT drafts from brief, Claude filters) — that drops Claude's session context and produces drafts that need more review-cycle correction. The new flow front-loads context preservation and reduces review-cycle work.
11. **The Step 3 quality gate has a numeric threshold (≥8/10 from both agents).** Don't ship sub-threshold drafts to the CEO. If 3 cycles can't reach the threshold, escalate with score trajectory + diagnostic — let the CEO decide whether to provide missing input, override, or abandon. This codifies the implicit "is it good enough?" judgment.
12. **Pattern B leaks Claude prose if used carelessly — keep it narrow.** Hard-learned 2026-05-12: post-cycle-3 surgical "merge two sentences into one" felt small but introduced Claude-formulated Swedish into the final file, defeating the entire point of Step 2's Claude-then-GPT flow. CEO caught it. Pattern B is now restricted to **pure deletions and CEO-supplied verbatim swaps only** (single- or multi-word — the new prose is CEO-authored, not Claude-authored). Any edit that produces new Claude-formulated Swedish — even short — MUST go through a GPT-5 polish pass before the file is considered ready. If in doubt, re-run polish (~$0.05).
13. **Comparative claims need pre-draft fact-checking, not post-draft.** Hard-learned 2026-05-12: a proposed "Sonetel får en tydlig konkurrensfördel gentemot andra aktörer som saknar denna möjlighet" was fact-checked via WebSearch against five direct competitors (Dialpad / RingCentral / Grasshopper / OpenPhone / Aircall) — all five had the capability. Claim was false; dropped before publish. The findings are now in `01_strategy/competitor_research_inbound_calls_2026-05.md` as a permanent reference. Going forward: ANY comparative claim in a draft triggers mandatory WebSearch verification BEFORE Step 3 review. Drop the claim if unsupported; do not water it down.
14. **Master stories can rot — re-verify if older than ~1 week.** Hard-learned 2026-05-12: master story for the mobile launch was drafted ~2 weeks before publication; in that time, product reality changed (closed beta vs first public beta) and the master became stale. Building drafts on a stale master cost multiple review cycles. Step 1 now includes a master-story-currency check; surface to CEO if the master may have drifted.
15. **GPT polish modifies CEO-supplied verbatim phrases unless you explicitly list them.** Hard-learned 2026-05-12: GPT polished "annat lokalt telefonnummer" → "till ett annat lokalt telefonnummer" (added "till ett" for parallel construction). Minor, but it modified CEO's verbatim wording. Required Pattern B revert. Step 2 polish-call system prompts MUST list CEO-supplied verbatim phrases explicitly as "preserve exactly" — the default polish prompt only covers numbers/dates/names/quotes, not arbitrary CEO word choices.
16. **Drip-fed CEO directives create iteration drift.** Hard-learned 2026-05-12: across one session, CEO surfaced ~10 specific directives (huvuddelen, no forward, no rebuilt, no error messages, no telephone-net jargon, drop sonetel.com, AI-back-in qualitatively, "annat lokalt telefonnummer", drop tautology, etc.) one at a time over many iterations. Each iteration was a Step 2/3 cycle. Best practice: at Step 1 gather a "directives & don'ts" snapshot from CEO before drafting starts. Won't catch everything (CEO may not remember every preference upfront) but converges faster than drip-feed.
17. **Disclosure-discipline scales to company size — don't apply enterprise-paranoia to a microcap.** Sonetel is a small First North microcap with a hands-on founder-CEO as spokesperson, not a Main-Market large-cap with a compliance department. **Qualitative regional context, customer-segment colour, operational achievements, soft positioning** (e.g. "effekten märks särskilt i Europa och Indien", "huvuddelen av kunderna", "den största luckan i vårt erbjudande") do **NOT** require 02-mar-decision.md addenda, MAR re-classification, or "documented price-moving rationale". Reserve that documentation for genuinely investor-relevant new facts — revenue revisions, margin guidance, capital structure changes, churn quantification, large customer contracts with disclosed terms, regulatory actions. Hard-learned 2026-05-12: CEO repeatedly had to push back on Claude's reflexive "we need to document this in 02-mar-decision.md" suggestions for qualitative regional/segment colour additions. CEO's verdict: *"det här är larvigt — vi är inte ett miljardbolag på en stor lista"*. The First North price-moving test (memory: `feedback_disclosure_first_north_flexibility.md`) is the operative standard, and when CEO judges something as not price-moving, **accept that judgment without proposing additional process**. Default to: include qualitative colour, skip the addenda. Process scales to the company.
18. **Stop suggesting 02-mar-decision.md addenda for soft additions.** Concretely: do NOT propose updating 02-mar-decision.md for (a) qualitative regional/geographic colour, (b) customer-base scale colour figures already broadly understood ("huvuddelen", "många"), (c) operational descriptors (timing, complexity), (d) CEO judgments about company state ("erbjudandet är starkare än tidigare"). DO propose updating it for (a) specific new numbers introduced for the first time (only when material), (b) borderline-MAR releases, (c) AGM/governance content, (d) anything with forward-looking financial implications. The default is "no addendum needed" — flip the burden of proof from "every new line needs documentation" to "only material disclosure-events need documentation".
19. **News-first ingress is the default structure.** Sentence 1 of the lead confirms / elaborates the headline (the news event). Sentence 2 carries scale/context. Sentence 3 (if used) carries audience anchor or implication. Only flip to context-first when the audience anchor is genuinely the harder-to-grasp half of the news (rare for product/strategy releases). The Cision-card preview shows only the first sentence or two — make those the news event, not demographic or contextual setup. Hard-learned 2026-05-12: investor-review-agent cycle 2 recommended "cross-border first" as scale anchor; we applied it; CEO later flagged the resulting lead as "inte tydlig" because the news event arrived in sentence 2 of the lead, after the headline. Fix was to put the news event first and the audience anchor second. **Agent suggestions for "lead with X audience" are tactics, not the default structure** — apply only when the audience anchor genuinely strengthens the news-event landing, otherwise stick to news-first.
20. **The Step 3 quality gate applies to getting *to* CEO, not *every* CEO edit afterwards.** Once both agents score ≥8 and the iterated draft has been presented to CEO, subsequent CEO-directed edits (Pattern A re-brief or Pattern B surgical) do NOT trigger new review cycles. CEO is now the editor and their judgment is authoritative; the gate's purpose (catching issues before CEO time is spent) is already served. Apply CEO edits per the normal Step 2 mechanics (GPT polish for new Claude prose, none for deletions or CEO-verbatim swaps), save, present, repeat as CEO directs. The 3-cycle cap applies to **score-convergence**, not to editorial iteration. Hard-learned 2026-05-12: a recurring confusion was whether each CEO-directed change required another full review cycle. It doesn't. The gate is one-way: it admits the draft to CEO; after that, CEO is in charge.
21. **Swedish holiday calendar discipline — validate T0 BEFORE drafting starts.** Klämdagar + röda dagar are the worst days of the year for press-release pickup. The skill must catch this in Step 1 (item 5b) — not after the entire draft package has been built against a disqualified date. Hard-learned 2026-05-13: a full launch package (master story + 13 derivations + investor-review-iterated press release reaching score ≥8) was built against fredag 2026-05-15 — which is klämdag after Kristi himmelsfärd. The Chairman caught it during the press-release review with the verdict *"sämsta dagarna på hela året"*. Cost: full date sweep across master + all derivations + 02-mar-decision + folder name. Going forward: Step 1 item 5b is non-skippable, must execute before any drafting begins.
22. **Holistic > feature-level for product-launch headlines.** Hard-learned 2026-05-13: Chairman Sebastian reviewed iteration 10's headline "Sonetels mobilapp besvarar nu inkommande samtal" and called it hygiene-factor-level — *"som att säga att man kan dricka mjölk ur ett glas"*. Investors aren't customers; they care about strategic substance, not user-experience increments. **For Type 7 product launches that constitute a meaningful re-baseline of a product surface**, prefer holistic framings ("ny generation", "ny teknisk grund", "kompletterar erbjudandet") that signal the magnitude of the change rather than naming one specific feature. The specific feature can land in the lead paragraph or first body sentence. Feature-level headlines are acceptable for pure metric / operational-update releases (Type 1), but not for genuine product re-baselines. Watch-for: investor-review agents may converge on the feature-level headline because it scores well on first-30s-clarity, but Chairman/CEO judgment about strategic substance is the override.
23. **Gap-admission reframes have a magnitude trade-off — preserve magnitude in forward-framed form.** Hard-learned 2026-05-13: Board member Annika flagged that "stänger en lucka som funnits i åratal" + "tillkortakommande" + "hämmat kundkonverteringen" admit-of-gap-stack made investors ask *"hur kunde detta inte finnas redan?"* instead of *"vad betyder detta strategiskt?"*. We applied the reframe (drop all gap-admission), but **score dropped vs prior iteration** — retail noted "Annika was right that the frame was wrong, but the solution isn't to remove magnitude, it's to express magnitude forward-tense". When reframing: preserve magnitude anchors via forward-framed factual signals — "den enskilt mest efterfrågade funktionen sedan flera år" preserves years-signal without gap-admission; "berör huvuddelen av kundbasen" preserves audience-scope; "strukturell förbättring för kunder som arbetar över gränserna" preserves significance. **Don't strip both gap-admission AND magnitude — strip only the gap-admission framing while keeping magnitude facts.**
24. **Concrete nouns > abstract nouns in headlines.** Hard-learned 2026-05-13: "Sonetel stärker mobilerbjudandet med inkommande samtal i appen" (abstract noun "mobilerbjudandet") read as positioning-speak to institutional persona; "mobilappen" / "appen" / "kundtjänsten" / "samtal" land harder. Watch-for abstract-noun-suffix patterns: "erbjudandet", "plattformen", "lösningen", "konceptet" — these are placeholders that signal IR-speak. For product news, name the concrete product or audience.
25. **Quantification ceiling for not-MAR product releases.** Hard-learned 2026-05-13: Institutional-agent score caps at ~7–8 for unquantified Type 7 product news regardless of polish — "the ceiling of an unquantified product release in Type 7 caps at ~7–8 for this persona". Cause: no model-update input possible without a number. **Implication for the Step 3 quality gate:** for releases where CEO has chosen not to quantify (e.g. SEK saving deferred to next periodic report, or product-progress without P&L attribution), the institutional ≥8 threshold may be structurally unreachable. Two valid responses: (a) **accept the ceiling** — ship at retail ≥8 + institutional 7–8 with documented rationale (the institutional ceiling is structural to the absent-quantification choice, not a draft-quality failure); (b) **commit one defensible quantification** — even a band ("uppskattningsvis 70–80 %" of customer base affected, "kortar cykeltid med X månader") that lets the analyst size the effect without crossing into forward guidance. **Don't iterate endlessly trying to hit institutional ≥8 by polishing prose when the ceiling is a number-absence ceiling.** Surface this trade-off to CEO at cycle 2 if institutional stays at 7–8 across cycles.
26. **The score gate isn't the final gate — board/chairman review is a separate stage.** Hard-learned 2026-05-13: a release that passed the Step 3 score gate (Retail 8.5, Institutional 8.0) was then subjected to (a) Chairman Sebastian's "drinking-milk-from-a-glass" framing critique, requiring full reframe; (b) Board member Annika's "wrong investor question" critique, requiring another full reframe. The score gate admits the draft to CEO; **after CEO sees it, board/chairman/external feedback may force further reframes that are categorically different from agent feedback** (strategic positioning vs draft polish). Build the process expectation: cycle-3 pass means "ready for CEO review", not "ready to ship". Don't communicate "ship-ready" or "iteration done" to Henrik until at minimum: CEO read + (if applicable) chairman/board feedback applied. Treat the Step 3 score gate as one of three sequential gates (agents → CEO → board), not as final approval.
27. **Headline propagation has four canonical targets — not just the press release file.** Hard-learned 2026-05-14: SV PR iterated to ~14 polish/review iterations past the master story's `## Slutgodkänd headline` section; the `ir_calendar.json` `headline_sv`/`headline_en` fields carried the master's stale headline; the bilingual HTML calendar summaries (SV + EN) displayed it. CEO spotted the divergence in the published HTML calendar — *"is this updated with the latest wording from the pressrelease?"*. The press-release file is the source of truth, but the master, the calendar JSON, and the two HTML summary views all surface the headline to different audiences (CEO scan, calendar consumers, public-facing schedule). Step 7.5 now makes propagation a hard pre-publish gate; do not treat the press release as "done" until all four match.
28. **2-working-day minimum gap between comms items — calendar discipline.** Hard-learned 2026-05-14: CEO flagged Tue 28/7 SMS + Wed 29/7 AI-assistant cluster as "Sprid ut"; an earlier 22/7 + 21/7 cluster had already been moved during review-r1, but no rule existed to prevent recurrence. Two press releases / hub posts / LinkedIn / X posts within 24h dilute both — readers don't absorb back-to-back signal density. Step 1 item 5c now enforces a 2-working-day minimum gap (where working day = Tue/Wed/Thu); anchored items override, non-anchored items must move; respect `depends_on` chains when re-scheduling. The rule exists as a pre-draft gate, not a "discover during review" check — set the date right the first time.
29. **Headline propagation to four surface locations is not enough — every numbered derivation in the launch folder also needs re-derivation.** Hard-learned 2026-05-14 (same day as lesson 27): Step 7.5 was added to propagate the final headline to four canonical surface locations (`10-press-release-*.md`, `00-story.md` Slutgodkänd, `ir_calendar.json`, bilingual HTML calendar summaries). That fix was incomplete. An audit of the mobile-public-beta launch folder later that day found **9 of 13 derivations still stale** after two retones (CEO master-story rewrite 2026-05-12 + headline change 2026-05-14): wrong H1 + wrong date in `99-cision-paste.html` (THE Cision artifact), wrong "Release 2" framing in all four social derivations (`11`, `12`, `13`, `14`), wrong subject + body in `20-customer-email.md` + `21-in-app-banner.md`, wrong T0 in `50-internal-slack.md`, wrong "Release 2" in `60-app-store-copy.md`. CEO's verdict: *"Skill needs updating to not leave such mess behind."* Step 7.6 now codifies the per-derivation re-derivation gate — re-read master + PR, re-express each derivation from scratch (do NOT search-and-replace, framing isn't always carried by a single quotable string), treat `01-checklist.md` open warnings as STOP signals, and don't ship until every numbered derivation in the folder reflects the current PR. Process docs (`00-story.md`, `01-checklist.md`, `02-mar-decision.md`, brief handoffs) are out of scope for re-derivation — they record process, not ship copy.

30. **Step 2 Tier 1 GPT polish doesn't carry forward to subsequent iterations — Swedish grammar bugs survive across cycles unless explicitly re-polished.** Hard-learned 2026-05-16: CEO Henrik caught *"innebär lägre kostnader och enklare vardag"* — missing indefinite article "en" before "enklare vardag" (countable singular noun in parallel construction with plural "kostnader"). The bug had survived four iterations: iteration 14 (Tier 1 GPT polish; that polish-pass focused on different reformulations and didn't word-for-word scrutinise this sentence), iteration 15 (board-feedback CR on §3 — quote untouched), iteration 16 (chair-feedback CR on headline + §3 + §4 — quote untouched), iteration 17 (chair text-edit on §1 — quote untouched). Each iteration modified other parts of the file but left the CEO quote frozen at its iteration-14 state. Step 3 investor-lens agents + audit agents are Claude models with the same Swedish blind spot per CLAUDE.md rule 9 — they can verify MAR/voice/framing but not catch missing articles, broken parallel constructions, or genus/numerus errors. **Lesson 12 ("Pattern B narrow") covered Claude-formulated new prose; it didn't cover Claude-formulated old prose that survives iterations untouched.** Step 7.7 now codifies a focused GPT-5 grammar-pass on every Swedish quote block + every post-Step-3-edit Swedish body-prose line before save. The marginal cost is ~$0.01–0.05 per call; the cost of a published grammar bug in a CEO quote is far higher. **Trust GPT-5 for Swedish grammar verification, not Claude or Claude-agent reviewers.**
