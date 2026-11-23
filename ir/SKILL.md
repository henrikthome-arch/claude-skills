---
name: ir
description: Plan and execute Sonetel AB investor relations — hub posts, LinkedIn content, calendar updates, strategy docs, and CRs. Use when working in the IR folder on any IR artifact.
argument-hint: "[activity-id | content | calendar | strategy | review]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel AB investor relations. If the current working directory does NOT contain `Sonetel/Investor relations`, STOP and tell the user: "The IR skill is for the Sonetel IR folder only. Current directory: [cwd]". Do NOT proceed.

You are helping Henrik Thomé, CEO of **Sonetel AB (publ)**, execute investor relations for a Nasdaq First North Growth Market listed nano-cap. Working folder:

`~/Library/CloudStorage/Dropbox/Sonetel/Investor relations/`

Read [CLAUDE.md](../../../CLAUDE.md), [PROJECT_RULES.md](../../../PROJECT_RULES.md), and [IR_Plan_2026.md](../../../IR_Plan_2026.md) at session start. Source of truth for dates is [ir_calendar.json](../../../ir_calendar.json).

---

## Company profile (locked; do not re-derive)

- **Sonetel AB (publ)**, org.nr 556486-5847, ticker **SONE** on Nasdaq First North Growth Market Stockholm
- **Live since 2009**, listed April 2017. **Never describe as "30-year-old"** (legal entity 1994 but operating business dates to 2009)
- Market cap ~SEK 35m recent · 2025 FY revenue SEK 27.9m · profitable since late 2023 · **Rule of 40 > 40 (disclosed)**
- ~34,000 paying customers (per Voice Lake briefing 2026-04-29). 88% Basic, 11% Premium, 1% Business plan. Premium ~4× revenue/customer vs Basic. 67% of revenue from phone-number subscriptions. Geographic split: ~1/3 North America, 1/3 Europe, 1/3 rest-of-world.
- CEO: **Henrik Thomé** · Chair: **Sebastian Ahlskog** · Certified Adviser: **G&W Fondkommission (Niklas Nyström)**
- **Three different country figures — resolved 2026-04-29 (Henrik):**
  - **170 countries with paying customers** — the customer footprint. Use when describing global reach of customer base ("kunder i 170 länder").
  - **80+ countries with local phone numbers** — the regulatory-plumbing moat. Use when describing the telecom-infrastructure differentiator ("lokala nummer i 80+ länder", "lokal närvaro i 80+ länder").
  - **Calls and SMS work to/from anywhere** — no geographic capability cap. Calls and SMS are global; the country figures above describe footprint and presence, NOT what the service can reach.

  **Use the right figure for the right point.** "Kunder i 170 länder" = customer-base story. "Lokala nummer i 80+ länder" = telecom-moat story. "Globalt" / "globalt räckvidd" = capability story. Mixing them up creates confusion or overclaim risk (e.g. "samtal i 170 länder" wrongly implies a coverage cap; "samtal i 80 länder" wrongly understates capability).
- **AI-driven transformation (2025–2026)** — 75% customer-service automation; mobile apps + customer portal rebuilt with Claude Code in weeks, not months/years; finance ops automated; AGM and annual report run with AI. **Skype shutdown wave May 2025**: 5× new-customer inflow (50/day → 250/day), absorbed because of AI automation. Free cash flow that funded the product rebuild.
- **Strategic positioning:** evolution from "virtuella telefonnummer" to "heltäckande kommunikationsplattform" — but **SMB-fokus förblir kärnan** (NOT enterprise). The combination of legacy telecom infrastructure + modern AI is the moat competitors can't easily copy. Recordings from calls are "the gold" that AI enriches.

---

## The diagnosis this plan answers (memorise)

**Distribution problem, not disclosure problem.** Sonetel has published 264 press releases, disclosed Rule of 40 >40, reported double-digit monthly growth — and almost nobody has noticed. EV/Revenue ~1.25× while public SaaS median is 6–7×. At the AGM 2026-04-23 a shareholder tabled three devastating numbers — ~11k LinkedIn followers with ~0 posts; 2% non-regulatory content across 264 releases; share down ~40% in 3 months — and challenged: *"give me counterarguments for why we should continue being a public company."* **The formal stay-vs-delist decision is still pending a future board meeting.** CEO and one board member (Tim) privately align on staying and committing to proper IR. The IR plan is *preparation* so that, if the board decides to stay, the work is ready to execute — not a response to a closed decision. **In board-facing and external documents, refer to "a shareholder at the AGM" — do not name the shareholder; they are not a board member.** The name lives only in memory for internal context. **Do NOT describe the AGM as a board mandate**; it surfaced the question, it didn't close it.

---

## The moat story (use this frame, not "AI transformation")

- **AI is commoditised.** Meeting summaries, LLM wrappers, "we built it with AI" — 4,000 of those stories a day. **Do NOT lead with these.**
- **Telecom infrastructure is not.** Phone numbers + SMS in 170+ countries — years of carrier and regulatory work, a category giants (Google Meet, MS Teams) don't own.
- **The combination is the moat.** Sonetel is one of few companies that can capture calls + SMS + meetings + emails and run AI across the unified stream. Voice Lake POC proves this. Google has email, not phone. Otter/Fireflies have meetings, not phone/SMS. Gong has AI but no phone and no SMB path. Dialpad has phone but shallow AI.
- **Category shift, not cost reframe.** Sonetel exits Category 0 (commodity virtual numbers — OpenPhone/CallHippo) and enters intelligent business communications at SMB pricing — a defensible position with no well-capitalised SMB incumbent.
- **Voice Lake status:** **POC and direction, not a shipping priced product yet.** Target commercial launch Aug 2026 with ~$90 USD/user/mo tier (internal target; do not publish). Near-term path likely embeds VL capabilities into existing Sonetel plans.
- **"Voice Lake" is the internal POC name — NOT a confirmed product name.** For the market, Sonetel is the brand and Sonetel is the subject. Frame externally as "Sonetel does X" — never "Voice Lake does X". The market-facing product name is undecided; "Voice Lake" *may* be retained as a public name, but that's not confirmed and must not be assumed in any headline, hub post, press release, or LinkedIn copy. Until product naming is decided: describe the capability (conversation intelligence across calls, SMS, email and meetings) with **Sonetel as subject**. This rule applies to `headline_en` / `headline_sv` fields and all external copy. Internal `title`, `story`, `notes`, `tags` fields in `ir_calendar.json` may continue to use "Voice Lake" as the working name.

---

## Content rules (non-negotiable)

### Never lead with
- Mangold liquidity guarantor (paid prop for a failure — see memory `feedback_do_not_lead_with_mangold.md`)
- The -19% drop, spread widening, auction-trading threat (already disclosed, narrating them warns investors off)
- "AI transformation" as a generic framing
- "AI-first", "AI-native", "AI company" as Sonetel's self-identity
- Meeting summaries as a standout feature (commodity)

### Always lead with
- Numbers that create verifiable asymmetry: **Rule of 40 > 40**, **EV/Revenue ~1.25×** vs public SaaS median 6–7×, monthly operational growth rates
- Specific before/after with kronor and weeks (website: 2 weeks vs months + SEK 500k+)
- The telecom-data moat (phone + SMS + AI across unified streams)
- Compounder / capital-efficient / underfollowed / founder-led / 170+ countries / live since 2009

### Vocabulary filter
Always apply the filter in [04_content/content_templates.md](../../../04_content/content_templates.md). Key:
- **Lead with:** profitable · cash-generative · compounder · Rule of 40 · EV/Revenue · underfollowed · founder-led · 170+ countries · category shift · combinatorial moat · live since 2009
- **Use only as mechanism, not identity:** SaaS, subscription, AI ("AI over unified streams" yes; "AI-native company" no)
- **Avoid:** AI company, AI-first, disruptive, revolutionary, platform, scalable, next-gen, operating leverage (as primary pitch — use category-shift instead)

### Numeric-claim sourcing
Every externally-published number needs a verifiable source. Flag `[PENDING SOURCE]` in drafts; resolve before publication. Hierarchy: Sonetel Cision/MFN releases → ITU/GSMA/Our World in Data → platform earnings / pricing pages. Never cite general knowledge, Wikipedia, or Claude-generated figures.

### 4,000-stories-a-day filter
Before any AI-related pitch: is this generic or specific? If the story doesn't carry numbers, listed-company context, and specific consequences, it dies in the noise. When unsure, buy an hour of Kristina's time before spending content effort.

### Timing rule (Sebastian, 2026-04-17)
Never publish an IR hub post about a product before it ships. Mobile app is **not** a speed example — it took longer than planned; frame as "gap-closing" only.

### Swedish prose drafting — use GPT for body copy ≥150 words

**Per Henrik 2026-05-01:** Anthropic models are weaker at Swedish than OpenAI's — more anglicisms, less natural flow, more "AI-slop" register. The IR project is Swedish-primary. To produce body prose that doesn't read as translated American PR, hand the actual long-form Swedish drafting to GPT.

**Helper available:** `~/.claude/scripts/openai_call.py` — calls GPT (default `gpt-5`) via the OpenAI Chat Completions API with a system + user prompt. Returns the response on stdout. Requires `OPENAI_API_KEY` env var (set once in `~/.zshrc`).

**Division of labour:**

| Work | Tool | Why |
|---|---|---|
| Calendar / JSON / dependency tracking | Claude (this session) | Tool use, file system, structured edits |
| Strategy, story fields, differentiator analysis | Claude | Reasoning + corpus mining |
| MAR classification, policy reasoning | Claude | Constraint logic, references to skill rules |
| Headlines (≤12 words, corpus-grounded) | Claude | Heavy grounding mitigates the Swedish gap |
| **Press-release body prose (~300–500 words SV)** | **GPT via `openai_call.py`** | Idiom + flow |
| **Hub-post body, longer LinkedIn copy** | **GPT via `openai_call.py`** | Idiom + flow |
| Vocab-filter check, numeric sourcing, MAR statement insertion, Cision-paste prep | Claude | Constraint enforcement |

**Standard workflow when drafting Swedish body prose:**

1. Load the brief from the activity's `story` field in `ir_calendar.json` (or `00-story.md` in the launch folder).
2. Compose a system prompt that includes Sonetel's voice rules — vocab filter (lean-into / avoid lists from `01_strategy/market_sentiment_2026.md`), 4,000-stories-a-day filter, "AI as mechanism not identity", "Voice Lake is internal-only", numeric-claim sourcing, plus any item-specific constraints.
3. Call `~/.claude/scripts/openai_call.py --system-file <persona.md> --user-file <brief.md>` (or pipe via stdin).
4. Receive draft. Run it through Claude's filters: vocab-filter check, numeric `[PENDING SOURCE]` markers, MAR Art. 17 statement insertion if needed, Cision-paste HTML preparation.
5. Save final to the launch folder file (e.g. `10-press-release-sv.md`) — Claude does this part.

**Example invocation (within a Claude session):**

```bash
~/.claude/scripts/openai_call.py \
  --system "Du är expert på svensk affärssvenska för Sonetel AB (publ), listad på First North. Skriv för svensk privatsparare 2026. Undvik AI-slop: 'transformerande', 'leverera värde', 'nästa generation', 'revolutionerande', 'skalbart'. Lead with concrete customer value. AI as mechanism, not identity. 'Voice Lake' is internal-only — externally use 'konversationsintelligens' or 'AI-assistent'." \
  --user-file 04_content/press_releases/2026-05-19-cost-reduction/00-story.md
```

**Cost note:** Typical IR draft ≈ 2k input + 1k output tokens. At GPT-5 pricing this is pennies per call. Not a budget concern.

**The chained workflow keeps the human in one window** — Claude drives the calendar, JSON, strategy, MAR, and post-draft mechanics; the GPT call is just one bash invocation in the middle of that flow.

### Hub-post publication gates (MANDATORY — every one, before any hub post is published to sonetel.com)

A hub post is NOT publishable until every gate below has run, **in order**. They exist because a 2026-06-24 mobile-app hub post shipped to sonetel.com having skipped every one of them: no image; the Swedish was a raw Claude draft (then, on a second pass, a GPT *polish* of a flawed Claude draft); it was never grounded in the business model, so it stated the core mechanic **wrong** (claimed customers "arranged forwarding" themselves — false; Sonetel forwarded the call and charged for it), invented a strawman ("not a consumer messaging app"), and used calque jargon (`distributionslager`, `det svårkopierade lagret … under ytan`, `kundåterkoppling`); and the review panel was ungrounded, so it gave false assurance and missed the factual error. Each gate is cheap; skipping any is a defect, not a shortcut.

**The recipe in order (then the gates spell out each step):**
1. **Ground** in the business model + atomic facts + this skill's company/moat sections (Gate 0). Get the mechanics RIGHT (e.g. Sonetel forwards the call and charges for it — the customer arranges nothing).
2. **Ask Henrik for the investor angle** — the real "so what" is rarely in the product page (see judgment lessons below).
3. Write a tight, correct, de-jargoned, well-flowing **English brief** (Gate 2b English review).
4. **GPT-5.5 drafts the Swedish** from that brief — `swedish-ir-draft-prompt.txt` (Gate 2).
5. **GPT-5.5 editorial pass** for flow + rhythm + register — `swedish-ir-editor-prompt.txt` — then Claude re-verifies every fact survived (Gate 2b).
6. **Image** (Gate 1), **weave + link the product page** (Gate 3).
7. **Grounded 4-persona review → min ≥8 + FACTUAL OK** (Gate 4); **editorial / scannability panel → min >8** (Gate 4b); **rendered-page + MAR check** (Gate 5).
8. **Present the draft to Henrik for the native-expert final read** — required, never auto-publish (see "human gate" below).

**Reference example (the bar to match):** for **Swedish prose + heading form**, the gold standard is **Annika's exemplar — `~/.claude/skills/ir/annika-exemplar-mobile-app-2026-06.md`** (a senior journalist's own rewrite; read it before drafting). The shipped 2026-06-24 post — `sonetel.com/content/posts/investor/sv/mobile-app-public-beta-2026-06.mdx` (SV) + `en/…` — is a good reference for **grounded factual framing and honest hedging**, but do NOT treat its Swedish as the language bar (Annika read it as "rätt låg språknivå") and treat its pre-2026-06-30 headings as an anti-pattern, not a model. Its v3 headings — title *"Sonetels mobilapp besvarar nu inkommande samtal — första publika beta-versionen"* and outline-label H2s (*"Vad som är nytt" / "Varför det är relevant för investerare" / "Vart det är på väg" / "Utvecklingen bakom"*) — passed the Gate 4 investor panel at 9/9/9/9 and were then **rejected by board member Annika**: the title read as overdue hygiene instead of leading with the news; the H2s were outline placeholders; the prose was developer-inside-out chronology. They were rewritten (CR-2026-06-24 v4) and the editorial panel (Gate 4b) added to catch this class. The current headings are the model; the v3 ones are the cautionary example.

**Gate 0 — GROUND THE TEXT IN BUSINESS KNOWLEDGE (do this FIRST, before drafting a single sentence).** This is the gate whose absence caused every downstream failure above. Before drafting any hub post that touches the product, the business model, pricing, customers, churn, or how the service works, READ and ground the draft in:
- `sonetel.com/docs/specs/sonetel-business-model.md` — what Sonetel sells, the prepaid-unified model, the **International-Presence core use case** (a business in country X buys a number from country Y to be reachable as local in Y), how inbound calls actually work (Sonetel *forwards* a call to the customer's phone and *charges* for that forwarding leg — the customer does not arrange anything externally), the revenue lines (phone-number subscriptions are the largest), and Appendix A **Atomic Facts** (verbatim-safe phrasings).
- **§ 1.5 "Growth Levers" of that same doc — the mandatory investor-framing lens.** Sonetel's growth has four levers: (1) more leads (LLM-based sales + AI-assisted SEO/PPC); (2) higher lead→first-payment conversion (simpler onboarding; ID/address-verification friction is the key blocker); (3) higher paid-plan uptake / ARPU (Premium ≈ 4× a Basic user's revenue; only ~12–15% are on a paid plan — large upside; AI services on the communication data are the path); (4) lower churn (~8–9%/mo, mostly early-after-purchase, onboarding-linked; better products + AI that knows the user = stickier). **Every IR article should make its investor "so what" land on at least one lever** — it's how you answer "why does this matter to the equity story?" (e.g. the 2026-06-24 mobile-app post lands squarely on lever 4, churn). Read § 1.5 before drafting and frame through it.
- This skill's **Company profile** + **The moat story** sections above.
- The ⚠️ figure discipline: "34,000+ paying customers" / "customers in 170+ countries" are **customer-footprint**; "local numbers in 80+ countries" is **number-availability** — never conflate them.
Get the product mechanics and the business model RIGHT in the English/brief first. A confident factual error survives every later gate (idiom-polish keeps it; an ungrounded reviewer reads it as plausible). If a claim isn't in the business-model doc or the atomic facts, verify it or cut it.

**Gate 1 — Share image (required, not optional).** Every hub post carries an `ogImage`. The precedent (`content/posts/investor/sv/q1-2026-…mdx` → `/images/insikter/q1-2026/og.webp`) has one; so must every new post. Spec:
- Path: `sonetel.com/public/images/insikter/<slug>/og.webp`, ~1920×1080 WebP (16:9).
- Register: warm, authentic SMB-lifestyle photo (a small-business owner, the actual customer) — NOT a text card, NOT corporate stock. Match the precedent's tone (natural light, real setting, genuine expression). No text/labels in the image.
- Generate via sonetel.com's `/generate-image` recipe (`.claude/commands/generate-image.md`): NB2 (`google/gemini-3.1-flash-image-preview`) when a face is primary, else Flux; 16:9; uses `OPENROUTER_API_KEY` from `sonetel.com/.env.local`. Convert to WebP with `sharp` (run the script from inside the sonetel.com repo so `node_modules` resolves).
- `public/images/**/*.webp` is gitignored — commit the file with `git add -f` (the precedent was force-added).
- Add `ogImage: /images/insikter/<slug>/og.webp` to BOTH locale MDX frontmatters.

**⛔ NO SUBSTITUTE FOR THIS GATE (2026-06-30 recurrence).** A hub post shipped where the Swedish was written by **Claude directly** (reusing an earlier "approved" draft + composing new headings/lead inline) and "validated" by a Claude subagent *role-playing a native Swedish editor* — which scored it 9/SHIP. A board member (Annika, a working journalist) read the result and immediately found "rätt låg språknivå" + multiple konstiga formuleringar (excerpt reading as a *skrivanvisning*, repetitions, clumsy sentence order, the calque "över data") that the simulated reviewer missed. **A Claude persona cannot judge Swedish register — it gives false assurance, exactly like the ungrounded Gate 4 reviewer.** Therefore: **every Swedish sentence that is new or changed — body, heading, OR excerpt — MUST pass through the GPT-5.5 draft (this gate) + GPT-5.5 editor (Gate 2b) pipeline, then Henrik's human native read. Reusing/porting prose from a prior version does NOT exempt it.** The Gate 4/4b virtual-reader panels test *thesis* and *editorial/scannability structure*; they are **not** a language gate and never replace Gate 2/2b or the human read. If you cannot run `openai_call.py` (no key/script), STOP and hand the Swedish to Henrik — do not self-author it and mark it reviewed.

**Gate 2 — GPT-5.5 DRAFTS the Swedish from a grounded English brief (drafts, NOT polishes).** This is the corrected gate. The earlier "Claude drafts SV → GPT polishes" path failed: GPT's polish prompt is idiom-only and structure-preserving, so it faithfully polished a flawed Claude draft (kept the jargon, the strawman, the factual error) and is too conservative to fix calques. The fix: **Claude writes a tight, correct, grounded *English* brief** (Claude is strong at English — get the facts, framing and de-jargoning right there), then **GPT-5.5 writes the Swedish from scratch off that English** so the Swedish reads native, not as a polished translation:
```
~/.claude/scripts/openai_call.py --provider openrouter --model openai/gpt-5.5 \
  --system-file ~/.claude/scripts/swedish-ir-draft-prompt.txt --user-file <grounded-english-brief.md>
```
**The drafting system prompt is a permanent, reusable file: `~/.claude/scripts/swedish-ir-draft-prompt.txt`** (do not re-derive it ad-hoc). It already encodes: write idiomatic Swedish (don't translate), third-person investor address, varied rhythm (NOT forced-short), investor-grade register, the banned calques/slop, the `EXCERPT:` lede rule, AI-as-mechanism, roadmap-as-direction, honest churn hedging — **plus the "ANNIKA-REGLER" (A1–A6 structure, B1–B8 language), the standing journalistic-style rule set derived from board member Annika (senior Swedish journalist/copywriter). Read the gold-standard exemplar those rules come from before drafting: `~/.claude/skills/ir/annika-exemplar-mobile-app-2026-06.md`.** Key rules an agent keeps getting wrong: headline = active company action + concrete outcome, never overdue-hygiene framing (A1); ingress is a real news lede, never a skrivanvisning like "Vad X betyder för…" (A2); numbers spelled out journalistically ("över 80 länder", "fler än 34 000") not "80+"/"34 000+" (B5); and **"app", "AI", "Wi-Fi", "SMS", "Bluetooth" stay natural — never bloat to "mobilapplikation"/"artificiell intelligens" (B6)** — the editor prompt's old blanket "inga engelska ord" rule wrongly did this and is now fixed. Read it before drafting; improve the file (via a note to Henrik) if you learn something new — don't fork it inline. Then run a Claude vocab/MAR filter (facts preserved, no AI-slop, no internal names, locale-correct links — the SV post links `/sv/…`, not `/en/…`). If you edit the Swedish afterwards, re-draft/-polish the changed paragraph through GPT-5.5 so new prose is native too. (OpenRouter key in `sonetel.com/.env.local`. `swedish-polish-prompt.txt` remains the right tool for a light idiom pass on already-good Swedish; for hub-post bodies, prefer GPT-drafts.)

**Gate 2b — Editorial FLOW reviews, both languages (correctness gates do not catch stilted prose).** A text can be factually right, on-message, and per-sentence idiomatic and still read as a stiff, choppy translation — the failure that took the 2026-06-24 post through several rounds. Two passes, each reading the piece *as a whole*:
- **English flow review** — before drafting the Swedish, review the English brief end-to-end for flow, concision and non-stiltedness ("does this read like high-quality prose an investor respects, or like assembled bullet points?"). Stilted English → stilted Swedish, so fix it here first. Write the English **free of calques and translation-isms** in the first place (don't write English that's secretly Swedish-shaped or vice versa).
- **Swedish editorial flow pass (GPT-5.5 as EDITOR, not translator)** — after GPT drafts the Swedish, run a second GPT-5.5 pass using the permanent editor prompt **`~/.claude/scripts/swedish-ir-editor-prompt.txt`** (it fixes flow, rhythm/staccato, and register in one pass, preserving facts/headings/`EXCERPT:`/third-person):
  ```
  ~/.claude/scripts/openai_call.py --provider openrouter --model openai/gpt-5.5 \
    --system-file ~/.claude/scripts/swedish-ir-editor-prompt.txt --user-file <gpt-swedish-draft.md>
  ```
  Then **Claude verifies every fact/number/date survived** the editorial pass (it can drift — re-check the country figures, the customer count, and that no English word like "countries" slipped in). Re-run the pass if you edit the Swedish afterwards.

Write for the **investor**, not the customer: third person throughout ("a Sonetel number", "the customer's mobile", "the company") — never "you/your/din/ditt". Use terms Swedish retail investors know (e.g. **ARR**).

**Rhythm — vary sentence length; do NOT force short sentences.** This rule exists because both extremes failed on the 2026-06-24 post: long, winding, multi-clause sentences read as dense and weird; then "keep every sentence short / split them all" produced a *staccato*, monotonous pace — short declaratives of similar length, one after another. Neither is natural. The target is **cadence variation**: mix short sentences (for emphasis) with longer flowing ones that join related ideas using conjunctions and subordinate clauses. Read a paragraph aloud — if every sentence is about the same length and clips at the same beat, combine some. Make the editorial flow pass (Gate 2b) explicitly fix rhythm, not just transitions.

**Register check (investor-grade word choice).** GPT-draft + GPT-editor reliably gets idiom and flow but NOT register — it has produced casual compounds ("appsläpp" for a launch) and informal particle-verb forms ("byggda om" where investor Swedish wants "ombyggda"). Before showing the draft, scan for and replace: casual/colloquial compounds and slang; informal particle-verb past participles (prefer the prefixed form — "ombyggd", "ombyggnad"); and anything that reads as marketing rather than sober First-North prose.

**The human gate is required, not optional.** The pipeline (Gate 0 ground → Gate 2 GPT-draft → Gate 2b flow + register → Gate 4 grounded review) gets binding investor Swedish to a strong *draft* — roughly 90%. It does NOT produce a publish-ready binding text on its own; across the 2026-06-24 mobile-app post, Henrik caught register, framing, factual and coherence issues every automated round. **Never auto-publish IR Swedish.** Present the draft to Henrik for a native-expert final read and treat that read as a required pipeline step, not a failure of the gates. The point of the automation is to hand Henrik a genuinely good draft, not to replace his pass.

**Gate 3 — Weave in and link the source product/landing page.** A product hub post must mine the live product page (e.g. `/mobile-app/` — read its `mobileApp*` i18n keys / page source) for the richer narrative, and LINK the locale-matched page in "Read more" (`/sv/…`, `/en/…`). Honor the content rules above: live features stated as live; roadmap/"coming soon" features clearly hedged as direction (never as shipped — MAR/overclaim); AI as mechanism; gap-closing framing for the mobile app.

**Gate 4 — GROUNDED 4-persona virtual Swedish-investor review → iterate to min ≥8 before publish.** Spawn four review subagents, each a distinct First-North retail-investor persona — (a) **skeptical** nano-cap, burned-before; (b) **growth/tech-savvy**; (c) **dividend/value**; (d) **governance/disclosure** (MAR + SV/EN-asymmetry enforcer). **Each persona MUST be given Sonetel's ground-truth facts inline in its prompt** (the business-model facts from Gate 0 — what Sonetel sells, the forwarding mechanic, the footprint-vs-availability figure distinction, what's shipped vs roadmap). An *ungrounded* reviewer cannot catch a confident factual error — it reads as plausible — and gave false assurance on the failed version. Each scores the SV (primary) + EN copy 1–10 on: clarity, credibility/no-overclaim, moat comprehension (or business-relevance for the value lens — but judge whether the so-what LANDS in the framing/attribution, NOT whether a dedicated moat/technical paragraph exists; concision per rule A0 wins, and a panel must never demand re-inflating paragraphs a senior editor cut), would-I-care, Swedish idiom — AND explicitly reports: **FACTUAL** (does anything misrepresent the business vs the ground truth?), and **REDUNDANCY/JARGON** (does the rendered bold `excerpt` repeat the body's first paragraph? any throat-clearing or calque jargon left?). Returns blunt critique + specific fixes. Fold the fixes, re-draft the changed Swedish through GPT-5.5, re-review. **Publish only when the LOWEST persona score is ≥8 AND every persona's FACTUAL = OK.** Record the final per-persona scores in the CR.

**Gate 4b — EDITORIAL / SCANNABILITY virtual-reader panel → iterate to min >8 (Annika's lens).** Gate 4 scores the *investor thesis, factual accuracy, and MAR safety*; it structurally cannot catch a headline that's factually fine but **editorially weak**. The 2026-06-24 post passed Gate 4 at 9/9/9/9 and was still rejected by a board member (Annika) on three editorial counts: the title read as **overdue hygiene** ("a number can now answer calls") instead of leading with the news (the *economic* angle — receiving a forwarded call used to cost money); the subheadings were **outline placeholders** ("Vad som är nytt" / "Varför det är relevant…") that label content instead of standing alone; and the prose was **developer-inside-out chronology** ("först gjorde vi så här, och nu gör vi så här därför att") instead of news/customer-benefit first. Gate 4b closes that lens gap.

Spawn **four editorial review subagents**, each a distinct facet of Annika's lens, scoring the title + the full heading set (SV primary + EN) 1–10, **iterating to min >8 (i.e. every facet ≥9 before publish)**:
- **Snabbläsaren** (5-second skim-reader) — reads ONLY title + H2s. Does each heading stand alone and convey *news* on a scan? Does the heading set tell the story top-to-bottom? Reject any heading that merely labels what's underneath.
- **Investor first-impression** — does the *title* read as valuable news / customer benefit, or as a belated fix of a basic gap (overdue hygiene that drags the impression down)?
- **Journalistic sub-editor** — inverted-pyramid order (news + customer benefit first; development backstory LAST). Flag any "först X, nu Y" before/after toggle (even one relocated into cost terms — that's the same cadence in disguise) and any outline-label heading.
- **Native Swedish editor** — SV headings idiomatic + correctly registered for a First-North audience (machine-Swedish reads sub-par; hold a high bar). Catches limping parallelisms, anglicisms (e.g. figurative "friktion"), and abstractions ("intelligens" with no concrete capability). **⚠️ This facet is a Claude persona and gives only weak assurance on language level — it does NOT satisfy the Gate 2/2b GPT-5.5 pipeline or Henrik's native read (see the NO-SUBSTITUTE rule in Gate 2). It sanity-checks heading *strategy*, not publish-grade Swedish.**

Each returns a score + concrete heading rewrites for anything below 9. Fold the fixes, re-draft changed Swedish through GPT-5.5 (Gate 2 path), re-run. In the live re-do this panel moved the set **7→8→9** and caught, before publish, a disguised before/after toggle, an unverifiable superlative, a Swedish parallelism that read like a typo, an "intelligens" abstraction, and an effort/apology-framed dev heading. **Record the final per-facet scores in the CR.** This is a *review panel*, not a regex — the failures are semantic (a heading like "Vad som är nytt" is grammatical and on-corpus; it's wrong *as a heading*), so don't try to reduce it to a forbidden-pattern list. (Mirrored into sonetel.com's `docs/specs/sonetel-voice-style.md §6 Entry 2`.)

**Gate 5 — Rendered-page + MAR check (last look before publish).** Read the post as the reader will see it, not just the body: the frontmatter `excerpt` renders in **bold directly above** the body, so it must NOT duplicate the first paragraph (date-restatement and "this post gives background" throat-clearing are the usual offenders). Confirm locale-correct internal links (`/sv/…` in the SV post). And run the skill's **brief-time amplification / MAR check**: if the post introduces any new investor-relevant forward-looking element beyond the press release (e.g. "this is our most-cited churn reason and we hope the effect is material"), it must be fully qualitative, hedged, and number-free — and surfaced to Henrik for the final MAR call before any production release.

#### What actually makes a hub post land (2026-06-24 lessons — the gates above are the *process*; these are the *judgment*)

- **The investor "so what" is rarely in the product page.** The marketing page (Gate 3) gives feature *breadth*; the reason a launch matters to the *equity story* lives in business/CEO knowledge. The 2026-06-24 mobile-app post only became good once Henrik supplied the real angle — that the cost of receiving *forwarded* calls (sharply higher in parts of Europe for calls from outside the EU; prohibitive in markets like India) has been the **single most-cited reason customers leave**, and that the new app is a *ground-up rebuild* (the 2019 apps couldn't receive calls at all and were painful to call from), built against genuinely hard real-time telephony. None of that was in the product page or the docs. **Before drafting, ask Henrik for the investor angle and the real business impact** — don't assemble a hub post from product features.
- **BUT the so-what must land in the FRAMING, not in appended paragraphs — kill your darlings (2026-07-02, Annika).** Getting the investor angle (previous bullet) does NOT license a dedicated moat paragraph, a technical-depth paragraph, or an "ordningen spelar roll för investerare" essay. Annika (senior journalist) rewrote the 2026-06-24 post *shorter*, deliberately cutting exactly those explanatory paragraphs, and landing the so-what inside the lead + nut graf + attribution ("kan få betydelse för … abonnemangsintäkter", "Enligt bolaget är vidarekopplingskostnaden den vanligaste orsaken … när de avslutar sitt abonnemang"). **When an editor of Annika's standing has cut material, treat every cut as intentional and do NOT reintroduce it** — even when the cut paragraph contained a genuine investor point you like. A concise piece the authority approved beats a fuller one that restores the agent's darlings. This is encoded as rule A0 in `swedish-ir-draft-prompt.txt`.
- **Honest uncertainty is a credibility asset with skeptical First-North readers.** "The company does not yet know the churn impact and puts no number on it, but the hope is that the effect is material" scored higher across the persona panel than any confident projection would have. Prefer stating what you don't know to implying you do. (This is also what keeps a forward-looking line MAR-safe.)
- **A natural claim beats a clumsy attribution clause.** "the change customers have asked for most" reads better than "enligt bolagets egen kundåterkoppling …". Source a *number*; don't bolt awkward attribution onto a qualitative claim.
- **Concrete CEO-supplied numbers (e.g. "20× more expensive") need a sourcing/MAR judgment.** Publish the qualitative version ("many times more") and flag the hard figure to Henrik for sign-off rather than asserting it unsourced.

### Headlines as source of truth (news items only)

Every news activity (`type: content | disclosure | event`) in `ir_calendar.json` must carry **both** `headline_sv` and `headline_en` fields — the actual external headlines a journalist or investor would read, not internal descriptions. Internal items (`type: ops | decision | meeting | subscription-renewal | blackout`) keep descriptive `title` only — no headlines.

**Source-of-truth language: Swedish.** Per Informationspolicy ver 1.4 §2, Swedish is the authoritative disclosure language. English is voluntary co-publication for international audiences (First North 4.1 market-understanding). When the two versions diverge in nuance, the Swedish version is binding; the English is informational.

The `headline_sv` and `headline_en` fields are what views render in quotation marks. The `title` field stays descriptive English (working name, internal scan-ability). When all three exist:

- `title` = internal descriptive working name
- `headline_sv` = externally-publishable Swedish (binding)
- `headline_en` = externally-publishable English (voluntary co-publication)

**Generated views:**
- `01_strategy/publishing_schedule_2026_summary.html` — Swedish version (board / Swedish-speaking stakeholders)
- `01_strategy/publishing_schedule_2026_summary_en.html` — English version (international management, e.g. Prashant; international investors)

Both views are derived from the same `ir_calendar.json`. Update the JSON; regenerate both views together so they don't drift.

When Swedish and English headlines convey different angles, that's a *content* decision worth flagging (per the amplification rule — adding new investor-relevant information in the English version that isn't in the Swedish version re-classifies as a separate disclosure).

#### Length

**6–12 words.** Investor headlines are tight. If it doesn't fit on one line in a Cision feed or a board summary, it's too long. Cut subordinate clauses; cut "after years of waiting"; cut "in 2026"; cut whatever isn't load-bearing. A headline that wraps onto two lines reads as a paragraph, not a headline.

#### Voice

- **"Sonetel" appears in every headline, and normally leads.** The subject is the company. Exceptions are narrow — convention-form periodics where the report itself leads ("Q2 2026: Sonetel publishes interim report" — but even here, putting "Sonetel publishes Q2 2026 interim report" is fine). If the headline doesn't contain the word "Sonetel", rewrite. If "Sonetel" is buried mid-clause behind a setup phrase, rewrite to lead with it.
- **Subject-verb-object, present tense.** "Sonetel launches X" — not "X has been launched" or "Sonetel is excited to announce".
- **One claim per headline.** If you're using a comma + clause to add a second point, the second point goes in the lede, not the headline.
- **Specific over flashy.** Numbers, named products, named platforms. Avoid "transforms", "revolutionises", "next-gen", "game-changing". The 4,000-stories-a-day filter trips on flashy verbs.
- **Punchy ≠ click-bait.** A good IR headline tells an investor what shipped, not what they should feel about it.

#### Patterns that work

- `Sonetel <verb> <thing>` — "Sonetel launches Voice Lake", "Sonetel publishes Q2 2026 interim report"
- `<thing> <verb>` — "Voice Lake adds email", "Mobile apps reach GA"
- `<change>: <consequence>` — "Mobile mature: app-only signup goes live"
- Convention forms for periodics — Q-reports, Bokslutskommuniké, Halvårsrapport stay close to standard form ("Sonetel publishes Q2 2026 interim report"). Don't try to punch these up.

#### Patterns that don't work

- ❌ Two-clause headlines connected by an em-dash where both clauses run long: "Calls, SMS, and now meetings — Sonetel widens the data layer competitors can't reach". Tighten to one clause.
- ❌ Editorial framing: "After years of waiting, Sonetel customers can finally...". This is body copy, not a headline.
- ❌ Headlines that read like internal task descriptions: "Mobile Release 3 — async (call recording, voicemail, outgoing SMS)". List belongs in the body.
- ❌ Headlines that bury the news: "AI as operating mechanism: how Sonetel runs the whole company in 2026" — the news is the *what*, not the framing label.
- ❌ **Comparative-win marketing framings** like "Gong-funktion till SMB-pris", "konkurrensen kan inte kopiera", "kategori-skifte". The category-shift narrative belongs in the **body / equity story**, not in the headline. The headline names the concrete feature; the body explains why it matters comparatively. Per Voice Lake briefing 2026-04-29: avoid hyperbole; show with facts not framing.
- ❌ **Colon-heavy headlines** ("Sonetel: X — Y"). The colon construction is reserved for **periodic / report titles only** (Bokslutskommuniké, kvartalsredogörelse, månads-uppdatering). For news / launches, use Sonetel-led verb-object: "Sonetel lanserar X", "Sonetel ökar Y", "Sonetel utökar Z".
- ❌ **Specific country numbers** ("i 170+ länder", "i 150+ länder") until the discrepancy between sources is resolved (see Company profile). Use "globalt" or describe the capability without the figure.

#### Audience: average Swedish investor, 2026

Headlines are written for the **average Swedish retail investor on First North in 2026**. That reader is asking:

- **Lönsamhet & tillväxt.** Does this map to what the company earns or grows? "Adopts new mobile app" → so what. "Adds the missing mobile leg in 170+ countries" → tied to a moat they can value.
- **Likviditet & synlighet.** Will more people trade SONE because of this? IR-mandate is to lift trading volume enough to terminate the Mangold liquidity guarantor — every news beat should serve that goal directly or indirectly.
- **Värdering & comp.** Does this give the reader a comp to anchor valuation? Voice Lake at SMB pricing where Gong charges $100–200/seat lands. "AI document generation" doesn't.
- **Moat.** Is this real defensibility or is it the 4,001st AI summary post today? Lead with telecom infrastructure, 170+ country footprint, unified-stream wedge — the things commodity AI players don't have.
- **Catalysts.** What's coming next? Mid-month hub posts and product ships build the Voice Lake / AI-voice-assistant arc. Each headline is one beat in the year-long story.

The reader is **skeptical**. Sweden's First North is full of micro-caps making large claims; the average investor has been burned and prices accordingly. Tight, specific, verifiable beats flashy every time. Tone: **understated confidence**, not promotional. The headline should read like something the reader can verify by clicking through, not something they should be excited about because the company says so.

Words that read promotional in Swedish ears (avoid): "transforms", "revolutionises", "next-gen", "game-changing", "leading", "pioneering", "world-class", "industry-first" (unless literally true and verifiable). The Swedish business reader treats these as warning signs, not credentials.

#### Filters to apply before saving

1. **Vocabulary filter** (see §Content rules) — flag any forbidden term.
2. **4,000-stories-a-day filter** — would a journalist see this and think "this is the 4,001st AI summary post today" or "this is specifically Sonetel"? If generic, rewrite with the Sonetel-specific hook (170+ countries, listed nano-cap, Rule of 40 > 40, the unified-stream wedge).
3. **Numeric-claim sourcing** — every number gets a verifiable source or a `[PENDING SOURCE]` marker.
4. **Voice Lake POC caveat** — pre-Aug 2026, Voice Lake headlines must reflect POC status; from Aug 20 launch onward, "Voice Lake" used freely.
5. **Sebastian's timing rule** — never headline a product before it ships. Mobile is *gap-closing*, not a speed example.

#### What "dead fish on cold rice" feels like

Henrik's 2026-04-29 feedback on a draft: descriptive, technically correct, narratively dead. The fix is not flashier verbs — it's tighter framing that lets the *fact itself* do the work. "Sonetel mobile receives inbound SMS" is dead. "One number, calls and SMS" is alive — same fact, the framing carries the moat. Find the framing that makes the fact pull weight, then cut the headline to its load-bearing words.

### Day-of-week rule (publication timing)

| Type | Default day(s) | Time |
|---|---|---|
| Regulatory disclosures (Q-reports, Bokslutskommuniké, MAR-grade product launches) | **Tue / Wed / Thu** | **08:30 CET**, before Stockholm market open at 09:00 |
| IR hub posts, LinkedIn CEO/Co posts, soft content | **Tue / Wed / Thu** | mid-morning (~09:00–11:00 CET) |
| Webinars (live Q&A) | **Wed or Thu** | early afternoon (~14:00–15:00 CET) |

**Days to avoid for any externally-facing IR item:**
- **Saturday / Sunday** — media dead zone, LinkedIn engagement craters, no analyst attention.
- **Friday afternoon** — "burying bad news" signal even for neutral releases.
- **Monday** — journalists deep in inbox triage and weekly planning meetings.
- **Public-holiday eves** — Midsummer, Christmas Eve, Easter, Walpurgis, plus the week between Christmas and New Year.

**Swedish-summer dead zone (mandatory check):**
- **Midsummer week.** Mon–Fri of midsummer week is dead in Sweden — journalists, analysts, and retail are off. The Tuesday/Wednesday/Thursday following Midsummer Eve are the worst days because everyone is genuinely unavailable, not just inattentive. **Avoid the entire week.** Midsummer's Eve is the Friday between 19–25 June each year (2026: Fri 19 Jun; 2027: Fri 25 Jun).
- **The week immediately after midsummer** is also slow — return-from-holiday triage, no-one engaging with non-financial news. **Avoid the Tue/Wed/Thu after midsummer too.** (2026: avoid 22–26 Jun.)
- **General Swedish summer (mid-July to mid-August)** — most journalists and analysts are off; retail engagement drops. Product content can still ship (per quiet-period rule for product news), but expect minimal pickup. Don't waste flagship-grade news here.

When `ir_calendar.json` is updated, every new or moved date must pass *both* the weekday rule AND the Swedish-summer rule before the JSON is saved.

Internal/ops items (board meetings, hub-build tasks, internal decisions) can land on any day — the day-of-week rule applies only to **externally-published** items.

When `ir_calendar.json` is updated, every new or moved date must pass this rule before the JSON is saved. Saturday/Sunday/Friday-PM/Monday on a `disclosure` or `content` activity is a bug.

### Language
**Swedish is primary per Informationspolicy ver 1.4 §2** (board-confirmed — file at `Corporate documents/Informationspolicy/`). English is voluntary amplification, **not** mandated-simultaneous disclosure. Use Swedish for retail channels (hub, Aktiedagen if reconsidered, Börsvärlden), English co-publish for LinkedIn CEO and YouTube when audience warrants.

---

## Channel model

### Default announcement package
Every announcement-grade activity goes out on: **Cision (press release) · Hub (sonetel.com/investors/insights) · LinkedIn CEO · LinkedIn Co · X**. Social-only tactical posts go on LinkedIn CEO + X only (no press, no hub). This is encoded as the `syndication` array on each activity in `ir_calendar.json`.

### Content hub, not newsletter
The IR content hub lives at `/investors/insights` on sonetel.com — public MDX posts + RSS feed + "Get Sonetel disclosures" CTA that routes to MFN's existing subscription. The earlier Substack newsletter plan was superseded (see `CR-2026-04-17-ir-newsletter-launch-substack` marked Superseded). No ESP. Hub posts are permanent, LLM-indexable, shared via RSS, and every post has a companion CEO LinkedIn post with a 2-line hook.

### Kristina Thorogård (PR consultant) — hourly, not retainer
- Engagement: ~SEK 1,500–2,000/hour for gut checks. Kristina is known for brutal honesty ("glöm det, there are 4,000 such stories every day"). Use her bluntness as a filter before committing content effort.
- Only engage on journalist-pitchable story candidates. Kristina-pitch activities in the calendar are tagged `kristina-pitch`.
- Currently three candidates: customer service portal AI-developed (May), Voice Lake launch (Aug), AI voice assistant (Oct).

### Generic investor presentation events (Aktiedagen etc.)
**Default no.** Henrik's prior experience 2019–2020: no measurable impact + high prep time. Reconsider only with a genuine news hook + proper instrumentation + pre-committed CPA kill threshold. My News Desk is for unlisted companies — not Sonetel.

---

## MAR handling — Henrik manages outside this plan

Do NOT:
- Schedule MAR-review gates as calendar activities.
- Bake MAR-classification tables into plan documents.
- Propose MAR routing workflows in IR artifacts.

Do:
- Keep `mar_sensitivity` as a tag on activities (useful for content prioritisation).
- Apply the amplification rule in content drafting (any new number/forward-looking/unpublished colour re-classifies a post as disclosure).
- Respect quiet-period blackouts (`type: blackout` in the calendar) when they surface in the schedule.
- Flag [PENDING SOURCE] on unverified numbers.

---

## Calendar & document structure

### Source of truth: `ir_calendar.json` (v2)
- Controlled vocabularies (types, statuses, channels, mar_sensitivities, confidence).
- `series` array: `s-hub-posts` (monthly 2nd Tuesday), `s-linkedin-ceo` (weekly Thursday), `s-linkedin-co` (biweekly), `s-sentiment-scan` (Friday). `s-newsletter` deprecated.
- Each activity carries: `type`, `status`, `confidence`, `start_date`, `owner`, `channel`, `syndication`, `tags`, `story`, `mar_sensitivity`.
- `kristina-pitch` tag marks PR-consultant-pitch candidates.
- `flagship` tag marks major product launches.

### Hiding past/declined in views
When rendering views for humans (HTML, markdown summaries), filter out:
- `status: done`
- `status: cancelled`
- `type: decision` with `confidence: confirmed` and `start_date` in the past
- Any activity with `start_date` in the past and `status != "in-progress"`

### Key docs
- [IR_Plan_2026.md](../../../IR_Plan_2026.md) — master plan · [README.md](../../../README.md) — navigation
- [01_strategy/equity_story.md](../../../01_strategy/equity_story.md) (v0.3, category-shift frame) · [01_strategy/product_release_calendar_2026.md](../../../01_strategy/product_release_calendar_2026.md) · [01_strategy/publishing_schedule_2026.md](../../../01_strategy/publishing_schedule_2026.md) and `.html`
- [01_strategy/market_sentiment_2026.md](../../../01_strategy/market_sentiment_2026.md) — refresh quarterly
- [04_content/content_templates.md](../../../04_content/content_templates.md) — vocabulary filter + MAR flag pattern
- [07_analytics/published_fact_inventory.md](../../../07_analytics/published_fact_inventory.md) — Top-10 under-read facts (rotate quarterly)
- [07_analytics/cision_corpus/](../../../07_analytics/cision_corpus/) — cached Cision archive for content research

---

## Launch coordination — master story + audience derivations

Most product releases, AI feature ships, and financial results need to reach more than one audience: investors, customers, prospects, journalists, internal staff. Without a single canonical story, derivations drift. Without a timing pivot, MAR-relevant facts leak before official disclosure.

### One folder per launch

`04_content/press_releases/YYYY-MM-DD-slug/` with:
- `00-story.md` — **master story** (canonical version, written first).
- `01-checklist.md` — audience × channel matrix with publish times, owners, dependencies.
- Numbered derivations: 10s investor (press release SV/EN, hub post, LinkedIn CEO/co, X), 20s customer (email, in-app banner), 30s prospect (blog + translations), 31 help page, 40s journalist (press kit), 50s internal, 60 app-store copy, 70 analytics, 80 paid amplification, 99 Cision-paste HTML.
- `_boilerplate/` is a sibling folder with reusable assets (SV/EN about-block, contact, MAR statement template, format rules, launch-checklist template).

### Master-derivation discipline

- The master story is the canonical version. If it changes, every derivation gets re-derived.
- **No new facts in derivations.** Adding a number not in the master either re-derives back into the master (re-review every derivation) or doesn't ship. Per the amplification rule, a derivation that introduces a new investor-relevant fact reclassifies as a separate disclosure.
- Vocabulary filter and numeric-claim sourcing rule apply to every derivation.

### Cision is the timing pivot

For any launch where the master contains MAR-relevant facts:
1. Cision goes first; nothing else ships before T0.
2. Customer email, in-app banner, blog, social — all key off T0.
3. In-app push can lead the customer email by minutes; never leads Cision.
4. Translation slip is normal — Swedish IR-side disclosure is the binding event.

### IR coordinates; IR does not own non-IR content

IR owns: master story, press release, hub post, IR social (LinkedIn CEO/co, X), press-kit fact sheet, internal Slack draft.
Marketing owns: customer email (IR provides MAR-safe version), press-kit visuals, paid amplification (Marketing-side).
**sonetel.com project owns: blog post + translations** (SEO, schema, hreflang live there; IR drafts only `30-blog-brief.md` and hands off).
CS owns: help page (IR drafts only `31-help-brief.md` and hands off; help-center IA owned by CS).
Product owns: app-store copy, in-app banner.

The launch-checklist gives IR visibility and a timing pivot — not authority over Marketing/CS/Product/sonetel.com content.

**Cross-project hand-offs (blog 30, help 31):** IR's launch folder produces a brief, not a draft. Brief contents: master-story link, "what to convey" framing, MAR-safe facts list with sources, **explicit citation of `02-mar-decision.md` §"What we are NOT claiming"** so the gates travel with the hand-off, T0-keyed timing, contact. **IR's only post-handoff role is amplification-rule verification:** check that the published artifact respects the gates. New investor-relevant facts in the published artifact re-classify it as a separate disclosure under the amplification rule.

### When to use which skill

- **`ir` (this skill)** — launch coordination, master story authoring, hub post, LinkedIn CEO/co, X, calendar updates, strategy docs, CRs.
- **`press-release`** — press-release-specific drafting (SV + voluntary EN), MAR statement decision, boilerplate insertion, Cision-paste HTML, Cision UI walkthrough. Use this skill from inside a launch folder when working on `10-press-release-*.md` and `99-cision-paste.html`.

Full rules: PROJECT_RULES.md §Launch Coordination.

---

## CR process (follow existing process)

- Write CRs in `docs/plans/` per [docs/CR_TEMPLATE.md](../../../docs/CR_TEMPLATE.md). Add to [docs/plans/CR_REGISTRY.md](../../../docs/plans/CR_REGISTRY.md).
- Review cycle: 1+1 default, 2+2 for policy / vendor-filing / MAR-sensitive (per [PROJECT_RULES.md](../../../PROJECT_RULES.md) §Agent-count policy). Iterate to confidence ≥ 8; up to 2 rounds, then ask user.
- Every change gets a changelog entry in `docs/changelogs/YYYY-MM.md`.
- Per capsulam escalation under ABL 8:22 is available for urgent policy board decisions (unanimity required).

---

## Strategic inputs already ingested (do not re-research)

- Sebastian's 2025 7-idea IR activation PDF: `01_strategy/references/2025-Sebastian-Ahlskog-IR-ideas.pdf` and analysis in `01_strategy/sebastian_ir_thoughts_2025.md`
- Sebastian × Henrik meeting 2026-04-17: `01_strategy/references/2026-04-17-sebastian-henrik-ir-discussion.md`
- AGM 2026-04-23 IR mandate: memory entry `agm-2026-04-23-ir-mandate.md`
- Voice Lake product and competitive analysis: `~/Library/CloudStorage/Dropbox/Workspace/voice_lake/docs/` (product-description.md, competitive-analysis.md)
- Cision press-release corpus via public API (`publish.ne.cision.com/papi`, feed UIDs in `07_analytics/cision_corpus/`)

---

## First actions when invoked

1. Read `CLAUDE.md`, `PROJECT_RULES.md`, `IR_Plan_2026.md`, `ir_calendar.json`.
2. Check `docs/plans/CR_REGISTRY.md` "Current Status" section for time-sensitive constraints.
3. Check memory (`~/.claude/projects/.../memory/`) for feedback entries that apply.
4. If drafting content: pass through the vocabulary filter + 4k-stories-a-day filter + numeric-claim sourcing rule before output.
5. If proposing calendar changes: update `ir_calendar.json` (source of truth), then regenerate `publishing_schedule_2026.html` from it.

---

## Lessons learned this project (to avoid repeating)

1. **Don't treat off-the-cuff numbers as facts.** Henrik's "7B phone users / 2B WhatsApp" figures were approximate — flagged `[PENDING SOURCE]` before anything external ships.
2. **Don't invent MAR review workflows for the calendar.** Henrik handles MAR outside this plan.
3. **Don't lead with Mangold, transformation stories, or meeting summaries.** Lead with numbers asymmetry and the telecom moat.
4. **Don't schedule content before the product ships.** Sebastian's timing rule.
5. **Don't call Voice Lake a shipping product** before its Aug 2026 launch. POC caveats throughout.
6. **Don't describe Sonetel as "30-year-old".** Live since 2009.
7. **Don't recommend Aktiedagen** as a default — Henrik has tried; prep cost > measurable impact.
8. **Don't bundle too much into one CR.** KEEP IT SIMPLE per project rules.
9. **Don't forget the ~11k LinkedIn followers.** Largest single underused asset.
10. **Do treat the AGM mandate as the context for everything.** IR is a condition of remaining listed per the chair.
11. **Don't assume the Cision → MFN switch is decided.** Henrik has not agreed. The CR exists in Draft; the calendar activities are `status: deferred`. Don't reintroduce them as forward-looking unless Henrik explicitly signals a decision.
12. **Don't name the AGM shareholder in plan docs.** He is a shareholder, not a board member. Use "a shareholder at the AGM" in external-facing or board-readable documents. Keep the name only in memory for internal context.
13. **Don't conflate activities in titles.** Each calendar activity has one clear purpose. If a title mashes several concepts together ("X — Y-led; not Z"), rewrite it. The `story` field carries the nuance; the title should be a clean noun phrase naming the artefact.
14. **Don't describe the AGM outcome as a "board mandate" or "board chose to remain public".** The AGM surfaced the stay-vs-delist question. The formal board decision is pending a future meeting. CEO and one board member privately favour staying; that's the working assumption for the plan, not a board decision. Frame the plan as *preparation so that, if the board decides to stay, work is ready*.
