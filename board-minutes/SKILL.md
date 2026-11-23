---
name: board-minutes
description: Write and produce board meeting minutes for Sonetel AB. Use when drafting minutes from transcripts or notes, generating PDFs, or versioning signed minutes.
argument-hint: "[draft | pdf | update]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel board meetings. If the current working directory does NOT contain `Sonetel/Board` or `Sonetel/Corporate`, STOP immediately and tell the user: "This skill is for Sonetel board meetings only. Current directory: [cwd]". Do NOT proceed.

You produce board meeting minutes for Sonetel AB (publ) board meetings. Minutes are written in **English**.

---

## Meeting types

| Type | Description | Minutes? |
|------|-------------|----------|
| **Ordinary board meeting** | Quarterly, physical in-person | Yes — always |
| **Board update call** | Between quarterly meetings, via Teams | Typically no. Exception: if a formal decision is taken (e.g., budget approval), minutes are produced. |
| **Per capsulam** | Written resolution circulated by email | Yes — short form |

The title of the minutes reflects the meeting type:
- Ordinary board meeting → **"Minutes from the board meeting (N) in Sonetel AB (publ)"**
- Board update call with decisions → **"Minutes from the board update call (N) in Sonetel AB (publ)"**

---

## Minutes Format

The canonical format is the December 18, 2025 ordinary board meeting (meeting 12). Match that format exactly.

### File naming

```
Minutes board meeting Sonetel AB 556486-5847 - YYYY MM DD - meeting N ver V.md
Minutes board meeting Sonetel AB 556486-5847 - YYYY MM DD - meeting N ver V.pdf
```

Save to `minutes/` in the meeting folder.

### Document structure

```
[CENTERED BOLD TITLE]
Minutes from the board meeting (N) in Sonetel AB (publ)

[TWO-COLUMN META TABLE — bold labels, no borders]
Company reg. no. | 556486-5847
Date             | [D Month YYYY]
Location         | [venue, city]
Chair            | Sebastian Ahlskog (SA)

[PARTICIPANTS]
Participants

| Board members present          | Guests (management and others) |
|--------------------------------|-------------------------------|
| Sebastian Ahlskog (SA)         | Prashant Pant (PP)            |
| Henrik Thomé (HT)              | Thomas André (TA)             |
| ...                            |                               |

Absent: [Name (initials)] — if anyone absent

§ 1  Opening of the meeting
[1–2 short paragraphs]

§ 2  Appointment of minute-keeper and verifier
Minute-keeper (Secretary): [Name (initials)].
Verifier (Justeringsman): [Name (initials)].

§ 3–N  [Substantive agenda items]
[1–2 short paragraphs + bullets as needed per section]
[Inline: "Board decision: ..." when a decision is taken]

§ N  Closing of the meeting
[1 sentence. Include next meeting date if stated.]

Decisions
• [Bullet list of all decisions taken at the meeting]

Action points (AP)
| AP  | Action point | Responsible | Due |
|-----|-------------|-------------|-----|
| AP1 | ...          | HT/PP       | ... |

Signatures

Chairman of the meeting:        Secretary (Minute-keeper):
______________________________  ______________________________
Sebastian Ahlskog               Henrik Thomé

Verifier (Justeringsman):
______________________________
[Verifier name]
```

### Key formatting rules

- Title: centered, bold, ~13pt
- Meta block: two-column table, bold labels, no grid lines
- § section headers: bold, same size as body
- Body: mix of short paragraphs and bullet points; bold key terms inline
- Absent board members noted below participants table in italics
- Decisions: aggregated bullet list at end
- Action points: table with AP#, action, responsible, due — only if actions were assigned
- Signatures: two-column (Chairman | Secretary), then Verifier below

### Length & tone — hard limits

- **Total length: 2–3 PDF pages MAX.** Includes everything from title through signatures. Non-negotiable.
- **Each § section: 1–3 short sentences, or a compact bullet list.** No play-by-play, no quotes, no rhetorical scene-setting.
- **Plain, easy-to-read language.** Short words. Short sentences. No filler ("the board discussed at length…").
- Bullets > paragraphs when listing.

**Do not duplicate the slide deck.** The deck carries the numbers, percentages, road-map detail, methodology breakdowns. The minutes record:

- Decisions taken
- Action points (owner + due)
- The key conclusion per agenda item (1–2 sentences)
- Formalities: chair, secretary, verifier, attendance, opening/closing

**Do NOT include** in the minutes:
- Slide-level detail (financial line items, percentage breakdowns, multi-step methodology)
- Back-and-forth quotes or "X said Y, then Z said W"
- "FYI" background context
- Anything already in the deck

If a § section runs longer than 3 sentences without containing a decision, a number tied to a decision, or an action point, cut it.

### Recurring roles

| Name | Initials | Typical role |
|------|----------|--------------|
| Sebastian Ahlskog | SA | Chairman |
| Henrik Thomé | HT | CEO / minute-keeper |
| Annika Lidne | AL | Board member / typical verifier |
| Tim Hansen | TH | Board member |
| Martin Jönsson | MJ | Board member |
| Jenny Karlsson | JK | Board member |
| Prashant Pant | PP | COO (guest) |
| Thomas André | TA | Chief AI Officer (guest) |

---

## Input sources

| Source | Action |
|--------|--------|
| **VTT transcript** | Read in chunks (file can be large >256KB — use offset/limit); extract content per agenda item |
| **Agenda** | Read `agenda/agenda.json` to structure the §-numbered sections |
| **Direct input** | Use Henrik's notes/bullets as the source |
| **Previous minutes** | Reference for style and tone |

When given a VTT file:
1. Read `agenda/agenda.json` first
2. Read VTT in offset/limit chunks if needed
3. Extract decisions, outcomes, and discussion points per agenda item
4. Keep summaries brief — 1–2 paragraphs or a short bullet list per §

---

## PDF generation

Generate PDF using **fpdf2** (Python, available on this machine). Use Unicode TTF fonts from `/System/Library/Fonts/Supplemental/`.

### Setup
```python
from fpdf import FPDF
from fpdf.enums import XPos, YPos
font_dir = "/System/Library/Fonts/Supplemental/"
# Add fonts: "Times New Roman.ttf", "Times New Roman Bold.ttf", "Times New Roman Italic.ttf"
```

### Layout rules (ordinary meeting)
- Font: Times New Roman (TTF, Unicode-capable)
- Page margins: 25mm all sides
- Title: TNR Bold 13pt, centered
- Meta table: bold 10pt labels, plain 10pt values, no grid
- Section headers: TNR Bold 10pt
- Body text: TNR 10pt
- Participants table: compact, gridlines, bold header row
- Signatures: Table with 2 columns (Chairman | Secretary), no grid; Verifier stacked below

### Layout rules (per capsulam)
- Same font (Times New Roman TTF)
- Header: filename in italic 7pt, right-aligned
- Footer: Box 647 / 114 11 Stockholm / Sweden / tel +46 852506000 / www.sonetel.com (7pt)
- § sections as bold 11pt headers
- Body 10pt, tables with equal column widths
- Use `-` instead of `•` for bullet points (avoids Unicode issues with some fonts)

**Note:** Do NOT use weasyprint (missing native libraries). Do NOT use core PDF fonts (latin-1 only – no Swedish characters). Always use `add_font()` with TTF files.

### Alternative: LibreOffice headless

If minutes are authored in DOCX (e.g. copied from a previous protokoll and edited via python-docx), convert to PDF via LibreOffice instead of rewriting in fpdf2:

```bash
/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless --convert-to pdf --outdir <utmapp> <file.docx>
```

Installed via `brew install --cask libreoffice`. More reliable than `docx2pdf` or Word AppleScript on macOS (both fail with sandboxing issues on Word 16+).

---

## Two-agent review process

After drafting ver 1 (markdown) and **before** generating the PDF, run a mandatory two-agent review. Both agents run **in parallel** (one message, two `Agent` tool calls).

### The two reviewers

**Agent A — Transcript faithfulness**
- Compares every factual claim in the minutes against the source (VTT/transcript/notes)
- Flags hallucinations (claims not supported by source)
- Flags significant omissions (substantive items discussed but missing)
- Verifies names, initials, numbers, dates, decisions, action attributions
- Tools: Read, Grep, Glob (read-only)

**Agent B — Format, length & board protocol**
- Compares document against the SKILL.md format spec (title, meta block, participants table, §-numbering, Decisions block, AP table, signatures)
- **Enforces the length & tone hard limits**: PDF ≤3 pages; each § = 1–3 short sentences or a compact bullet list; plain language; no slide duplication. **Any draft that exceeds 3 pages or duplicates slide-level detail is an automatic REVISE regardless of other quality.**
- Checks completeness vs. `agenda/agenda.json` — every agenda item gets a brief §
- Flags style drift, missing absent-member notes, AP-table mismatches with the body
- Tools: Read, Grep, Glob, Bash (read-only; Bash needed to count PDF pages if a PDF exists)

### What the reviewers return

Each agent returns a structured report:

```
CONFIDENCE_SCORE: <integer 1–10>

Critical issues (must fix):
1. ...
2. ...

Suggested improvements (nice to have):
1. ...
2. ...

Verdict: <PASS | REVISE>
```

**Scoring rubric** (both agents use the same scale):
- **10** — Flawless. Send as-is.
- **9** — Perfect substance; only polish opportunities.
- **8** — Solid; one or two minor improvements possible.
- **7** — Has 1–2 issues that should be addressed.
- **≤6** — Multiple issues or one serious issue.

### Pass threshold and cycles

- **Pass threshold**: both agents must score **>8** (i.e., 9 or 10).
- **Max cycles**: 2.
  - **Cycle 1**: spawn both reviewers in parallel against the draft. If both pass (>8) → proceed to PDF.
  - If either is ≤8 → consolidate critical issues, apply edits to the markdown, then run **cycle 2** (both reviewers again in parallel against the revised draft).
  - If after cycle 2 either reviewer is still ≤8 → **escalate to the user**. Present: each reviewer's score, the remaining critical issues, your proposed resolution, and ask how to proceed. Do NOT silently ship a sub-threshold draft.
- The review happens on **ver 1** (the first draft). Applying review fixes does **not** bump the version — ver 1 is what reaches the user.

### Logging

Append a brief note to `CHANGELOG.md` summarising the review outcome per cycle: scores, key issues found, what was changed. This is the audit trail for future signed-minutes references.

---

## Versioning

**Hard rules — no exceptions:**

- `ver 1` = first draft delivered to the user (after the two-agent review passes).
- **Every change after a version exists on disk creates a new version number.** Never overwrite or reuse `ver N` — bump to `ver N+1`. Applies to all changes: user corrections, typo fixes, CRs, follow-up edits, anything. There is no exception for "small" changes.
- The two-agent review cycles are internal to producing a single version — cycles 1 and 2 against the same draft do **not** bump the version, because the draft has not been delivered yet.
- **Always generate the PDF alongside the markdown.** A versioned `.md` without a matching `.pdf` is broken state. Both files share the same `ver N` suffix and live side-by-side in `minutes/`.
- Once signed: archive the signed PDF to `minutes/Signed/` inside the meeting folder. Filename convention: `Styrelseprotokoll YYYY MM DD (N).pdf` (Swedish — matches the eAvtal export). Drafts in `minutes/` are kept; only signed copies live in `Signed/`. Create a new version only if corrections are subsequently needed.
- Update `CHANGELOG.md` after writing or updating minutes (one entry per version, and one entry when the signed copy is archived).

---

## Workflow

1. Read `agenda/agenda.json`.
2. Read source (VTT, notes, or direct input).
3. Determine the next version number: look at existing `minutes/Minutes … ver N.{md,pdf}` files; pick `N+1` (or `1` for a brand-new meeting). **Never reuse an N that already exists on disk.**
4. Draft `minutes/Minutes ... ver N.md`.
5. **Run two-agent review (see "Two-agent review process" above)** — cycle until both reviewers score >8, max 2 cycles, then escalate if not converged. Reviews run on the same `ver N` draft and do not bump the number.
6. **Generate the PDF** using fpdf2 with the matching `ver N` suffix. Markdown and PDF must always be produced together.
7. Update `CHANGELOG.md` with a single entry per version (include review-cycle summary).
8. Present to Henrik for review.

**For any subsequent change** (Henrik's feedback, CR, follow-up edit): repeat the workflow from step 3 to produce `ver N+1` — never edit `ver N` in place.
