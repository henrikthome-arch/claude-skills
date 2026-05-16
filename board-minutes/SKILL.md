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

## Versioning

- `ver 1` = first draft
- `ver 2`, `ver 3` = revisions before signing
- Once signed: archive; create a new version only if corrections needed
- Update `CHANGELOG.md` after writing or updating minutes

---

## Workflow

1. Read `agenda/agenda.json`
2. Read source (VTT, notes, or direct input)
3. Draft `minutes/Minutes ... ver 1.md`
4. Generate PDF using fpdf2
5. Update `CHANGELOG.md`
6. Present to Henrik for review
