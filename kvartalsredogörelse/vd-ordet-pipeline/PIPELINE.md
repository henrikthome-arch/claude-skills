# VD-ordet pipeline — workflow for a single Kvartalsredogörelse period

This document is the orchestration playbook a Claude Code session follows to produce a publishable VD-ordet for a given Sonetel Kvartalsredogörelse. The deterministic ops (file mgmt, GPT-5 calls, score logging) live in `scripts/draft_vd_ordet.py`. The critic-agent orchestration uses Claude Code's Agent tool with the persona prompts in `critic-personas/`.

**Why it's split this way**: Python can run GPT-5 calls via `~/.claude/scripts/openai_call.py`, but the Avanza-retail + sell-side critic agents need Claude Code's Agent tool. So Python handles drafting + bookkeeping; Claude handles critic orchestration + score evaluation + revision-brief composition.

## When to use this skill

User input that triggers this workflow:
- "Drafta VD-ordet för Q1 2026"
- "Henrik recorded the brain-dump for the next Kvartalsredogörelse, file's in vd-ordet/transcript.txt"
- "Run the VD-ordet pipeline for `<period folder>`"

## Inputs

Required:
- `<period>/vd-ordet/transcript.txt` — Henrik's verbal brain-dump (transcribed)
- The canonical style guide at `~/.claude/skills/kvartalsredogörelse/vd-ordet-style-guide.md`

Optional but common:
- Supporting documents in `source/` (cost-action PPTs, communications-framing screenshots, board memos)

## Outputs

Final deliverable:
- `<period>/vd-ordet/vd-ordet-final.md` — paragraphs ready to paste into `data.json → narrative.vd_kommentar` (list of strings)

Full audit trail in `<period>/vd-ordet/`:
- `transcript.txt` — Henrik's recorded brain-dump
- `briefs/` — system-prompt, drafter brief, revision briefs per iteration
- `drafts/` — every draft version
- `critics/` — every critic report + `scores.jsonl`
- `pipeline/` — raw GPT-5 user-message payloads + API logs

Note: whole-report inputs (BDO numbers, management cost-action material) live at the **period root** in `Underlag från BDO/` and `Underlag från ledning/`, NOT inside `vd-ordet/`. The `vd-ordet/` folder holds only VD-ordet-specific material.

## STANDARDFLÖDE (Henrik 2026-11-18): Henrik kör briefen i ChatGPT

Gäller före allt annat i det här dokumentet. API-pipelinen nedan (draft/revise/kritiker) är bara reserv när Henrik ber om den.

1. **Claude skriver briefen** i `<period>/vd-ordet/briefs/brief-for-drafter.md`. Första raden ska ange perioden, t.ex. "VD-ordet — kvartalsredogörelse juli–september 2026". Innehållet:
   - Henriks ord om ton och avsikt.
   - Sammanhängande bakgrund: vad som hänt och *varför det spelar roll*, skrivet som löpande text och inte som lösa punkter. Lösa fakta ger ett brev som läses som en lista.
   - Rättelser av inspelningen.
   - Vad som inte får sägas.
   - Henriks inspelning, ordagrant.

   Inget styckeschema och inga krav på vad som måste vara med. Läsaren känner inte till Sonetel. Upprepa inte siffror som redan står i sammanfattningen.
2. **Exportera briefen till Hämtade filer:** `python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py chatgpt-export '<period folder>' "Q3 2026"`. Kommandot skriver `~/Downloads/VD-ord <period> brief.md` med systemprompten från §10 först, sedan briefen och sist exempelbreven, eftersom ChatGPT saknar systemprompt. Kopiera inte bara briefen: utan systemprompten saknas skribentrollen, kravet att bara använda briefens fakta och rubrikformatet. Ge Henrik filnamnet. Lämna inte en annan periods brief öppen i editorn: 2026-11-18 klistrade Henrik in Q1-briefen eftersom den låg öppen.
3. **Henrik kör briefen i ChatGPT.** Claude ger Henrik de här stegen tillsammans med filnamnet:
   1. Öppna en **ny** chatt i ChatGPT, så att inget från tidigare trådar påverkar.
   2. Välj tänkande modell (Thinking) och sätt tankenivån till **max**.
   3. Öppna `~/Downloads/VD-ord <period> brief.md` och kontrollera att första raden anger rätt period.
   4. Klistra in hela filen, eller bifoga den. Ingen extra uppmaning behövs, eftersom briefen innehåller allt.
   5. Kopiera svaret, rubrik och brödtext, och skicka det till Claude.
4. **Claude:**
   - faktagranskar mot briefen och påpekar avvikelser för Henrik, utan att skriva om texten själv;
   - lägger in texten i `data.json`, med rubriken i `narrative.vd_kommentar_rubrik` och styckena i `narrative.vd_kommentar`;
   - renderar en ny PDF och kontrollerar att brevet ryms (cirka 420 ord);
   - kör läsartestet (`lasartest.md`);
   - visar Henrik de gemensamma problemen. Läsarnas önskemål är underlag, inte order.
5. **Ändringar:** Henrik gör dem i samma ChatGPT-tråd. Claude kan föreslå en kort rättelse att klistra in, med fakta och inga färdiga meningar.
6. **När texten är godkänd:** spara den som `drafts/vd-ordet-draft-vN.md`, kör `promote-final` och gör MAR-kontrollen (steg 8–10 nedan).

**Varför:** Q3 2026 krävde mer än 20 varv genom API-pipelinen (GPT-5, revise, kortningar) och resultatet var ändå styckat. Halvårsrapporten och Q1-texten gick betydligt bättre när Henrik körde briefen i ChatGPT.

## Workflow (API-reserv)

### Step 0 — Initialize folder skeleton

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  init-period '<period folder>'
```

This creates `briefs/`, `drafts/`, `critics/`, `pipeline/` subfolders inside `vd-ordet/`.

Files go in these places:
- **Henrik's transcript** → `<period>/vd-ordet/transcript.txt` (specifically VD-ordet input)
- **Whole-report inputs from management** (cost-action PPTs, framing screenshots, board memos) → `<period>/Underlag från ledning/` (sibling folder at period root, NOT inside vd-ordet/)
- **BDO accounting underlag** → `<period>/Underlag från BDO/` (existing convention)

### Step 1 — Extract the canonical system prompt

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  extract-prompt '<period folder>'
```

This pulls the verbatim Swedish system prompt from style guide §10 into `briefs/system-prompt.txt`. Do not edit this file by hand — if the prompt needs to change, edit the style guide §10 and re-run extract-prompt.

### Step 2 — Compose the structured brief

**BINDANDE REGEL (Henrik 2026-11-18): ge skribenten minimalt med instruktioner.** Briefen är material och spärrar: vad perioden handlade om, verifierade fakta, en kort lista på vad som inte får sägas. Inga formler, inga styckeanvisningar, inga ordlistor, inga färdiga meningar — inte heller i revisionsbriefer. Detaljstyrning förstör kvaliteten. Enda innehållsregeln: upprepa inte siffror som redan står i sammanfattningen på sidan före (Henrik 2026-11-18). Systemprompten i stilguidens §10 är medvetet kort; bygg inte ut den.

Claude (this session) reads:
- `<period>/vd-ordet/transcript.txt` — Henrik's brain-dump
- `<period>/Underlag från ledning/` — management material relevant to this quarter's narrative (cost-actions, framing matrices, etc.)
- `<period>/Underlag från BDO/` — for numeric anchors when needed
- The style guide for voice rules

…and writes `<period>/vd-ordet/briefs/brief-for-drafter.md` enligt STANDARDFLÖDE punkt 1 ovan. Mall: `2026/Quarter/Q3/Kvartalsredogörelse/vd-ordet/briefs/brief-for-drafter.md`. Q1-briefen är *inte* en mall längre: den har styckeschema och färdiga formuleringar.

### Step 3 — Draft v1

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  draft '<period folder>' --version 1
```

Produces `drafts/vd-ordet-draft-v1.md` and `pipeline/draft-v1.log`. Target length 380–460 svenska ord.

**STANDARD (Henrik 2026-11-18): läsartest med tre virtuella svenska investerare efter varje utkast som visas för Henrik — se `vd-ordet-pipeline/lasartest.md`.**

### Step 4 — Critic round (in parallel via Claude Agent tool)

Read `critic-personas/retail.md` and `critic-personas/sellside.md`, substitute the placeholders for this period, and **spawn both as `general-purpose` Agent calls in a single message** (concurrent execution). Each returns `Score: X/10` on the first line plus detailed critique.

Save the responses to:
- `critics/critic-v<N>-retail.md`
- `critics/critic-v<N>-sellside.md`

Then log scores:

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  log-score '<period folder>' '{"iteration":1,"draft":"vd-ordet-draft-v1.md","critic_retail":{"score":7,"file":"critic-v1-retail.md"},"critic_sellside":{"score":6,"file":"critic-v1-sellside.md"},"threshold_met":false,"timestamp":"2026-05-13"}'
```

### Step 5 — Evaluate scores

If **both critics ≥8**: proceed to Step 7 (Henrik review). If either is <8: proceed to Step 6 (revision).

**Cap at 3 iterations**. If round 3 still fails, the brief is wrong (not the model) — stop and surface to Henrik with diagnosis.

### Step 6 — Compose revision brief and re-draft

Claude (this session) reads both critic reports for iteration N, identifies **convergent critique** (issues both agents flagged — fix these), and **divergent suggestions** (judgment calls — surface to Henrik or apply best judgment). Write `briefs/revision-brief-v<N+1>.md` listing the specific surgical edits. Then:

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  revise '<period folder>' <N+1>
```

This composes the user message (revision brief + previous draft as source text) and calls GPT-5. Produces `drafts/vd-ordet-draft-v<N+1>.md`. Loop back to Step 4.

### Step 7 — Henrik review

Present the converged draft to Henrik. He may:
- Approve as-is → proceed to Step 8
- Provide substantive corrections → compose `briefs/revision-brief-v<N+1>.md` with his edits and re-draft via `revise`, then re-run critics once as a regression sanity check.

### Step 8 — Promote to final

```bash
python3 ~/.claude/skills/kvartalsredogörelse/vd-ordet-pipeline/scripts/draft_vd_ordet.py \
  promote-final '<period folder>' <final-version>
```

Copies the chosen draft to `<period>/vd-ordet-final.md`.

### Step 9 — Slot into data.json

The final paragraphs go into the period's `data.json` at `narrative.vd_kommentar` (list of strings, one per paragraph, ingress as the first item — the template's CSS bolds it via `.vd-content .body-2col p:first-child`). The signature block fields go into `governance.vd_namn`, `governance.vd_titel`, `governance.vd_signing_location`, `governance.vd_signing_date`.

### Step 10 — MAR / disclosure-trail check (if applicable)

If the VD-ordet references quantified cost actions, capital-structure changes, or other potentially price-sensitive facts, document the MAR judgment as `<period>/vd-ordet/mar-decision.md` (or save the relevant email-trail as `<period>/vd-ordet/mar-decision-emailtrail.eml`):

- The fact under review
- Why it likely isn't kursdrivande (already telegraphed / market-expected / sub-threshold)
- Whose judgment + date
- Outcome: included in Kvartalsredogörelse / separate PM ahead / removed

This creates a traceable paper trail.

## Iteration discipline (from the press-release skill)

- Cap at 3 iterations. If still failing at round 3, the brief is wrong, not the model. Stop and surface to Henrik with a diagnosis of which themes the critics keep rejecting and why.
- **Convergent critique** (both agents flag) is structural — fix these in the next revision.
- **Divergent critique** (judgment calls where critics differ) — bring to Henrik or apply best judgment with a note in the revision brief.
- **Henrik's corrections always take precedence over critic feedback.** When he revises, apply exactly; do not push back unless his correction violates a style-guide rule (in which case ask).
- After Henrik's corrections, run **one regression critic round** as sanity check. If it surfaces convergent issues, surface to Henrik before publish.

## Reusability notes

- The same pipeline applies to **Bokslutskommuniké VD-ordet** with three adjustments: (1) target length grows to ~450–600 ord (year-end retrospective is longer); (2) the 5-block recipe expands to add a "full-year retrospective" frame in ¶1 and a "finansiellt stärktes bolaget"-style block in ¶4; (3) the style-guide §10 system prompt should be cloned/adapted before use. Future work: factor the Bokslutskommuniké variant when needed.
- The Halvårsrapport VD-ordet is closer to the Kvartalsredogörelse genre but with H1 timeframe — use this pipeline as-is, just update the period label.

## Common gotchas (learned from Q1 2026 production run)

1. **Open paragraph (ingress) is rendered bold by the template** — don't include markdown bold in the drafted text. The template applies it via CSS.
2. **Tense march has a presens exception in ¶1** — ongoing states use presens even in the past-tense opening (e.g. "Jämförelsen är handikappad", not "var").
3. **Post-quarter events** (mobile apps shipping in May for a Q1 jan–mar report) must NOT be implied as Q1 deliveries. Lift to ¶3 with explicit "är ute i public beta", or qualify "som lanseras nu / efter kvartalets utgång".
4. **Percentages always specify their denominator** — "28 procent" alone is ambiguous; "personalreduktion på cirka 28 procent i Indien-organisationen" is unambiguous.
5. **Swedish-correctness anglicisms**: "Indien" not "India", "verksamhetsmodell" not "operativmodell" — both retired anglicisms now in style guide §7.
6. **Existing features framed as new** — if Sonetel already offers a capability (e.g. call recording/transcription/summarization), frame forward improvements as upgrades ("ett nytt AI-baserat system som lyfter X till en högre nivå"), not as debuts.
7. **Closing punchline lands on a concrete noun**, not an abstract acronym. "Lojala kunder" / "kärnupplevelsen" / "tillväxtmaskinen" / "maskinrummet" — not "ARR" / "EBITDA".

These are codified in `vd-ordet-style-guide.md` §3, §7, and §10 system prompt; future runs inherit them automatically.
