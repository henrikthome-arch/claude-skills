---
name: arsredovisning
description: Create or update Sonetel AB's Årsredovisning (annual report). Use when working on the ÅR — merging framvagn from Bokslutskommuniké with bakvagn from CFO Göran, iterating layout versions, or preparing for signing.
argument-hint: "[draft | update | status | merge]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel Årsredovisning work. If the current working directory does NOT contain `Sonetel/Financial`, STOP immediately and tell the user: "This skill is for Sonetel Årsredovisning only. Current directory: [cwd]". Do NOT proceed.

You are helping Henrik Thomé, CEO of **Sonetel AB (publ)**, prepare the company's Årsredovisning (annual report). The company is listed on Nasdaq First North Growth Market. The working directory is the relevant **Year** folder under `~/Dropbox/Sonetel/Financial/`.

---

## What is the Årsredovisning?

The Årsredovisning (ÅR) is the formal annual report filed with Bolagsverket. It consists of two major parts:

### Framvagn (front section) — from Bokslutskommuniké
The narrative/business content, sourced from the latest layouted version of the Bokslutskommuniké for the same fiscal year. Sections include:

| Section | Description |
|---------|-------------|
| Om Sonetel | Company description (updated each year) |
| Headline summary | e.g. "Rekordtillväxt med Skype-effekten" |
| Key financials summary | Koncernen — bullet points for the full period |
| VDs kommentarer | CEO letter (multi-page) |
| Kommentarer till verksamheten | Operational commentary: Verksamhet, Intäkter, Kostnader, EBITDA, Resultat före skatt, Abonnemang, Premium, ARR, Kundanskaffning, Aktiva kunder, Kundnöjdhet, AI-omställning, Interndebitering, etc. |

### Bakvagn (back section) — from CFO Göran
The formal financial/legal content, prepared by the CFO. Sections include:

| Section | Description |
|---------|-------------|
| Förvaltningsberättelse | Board of directors' report — Allmänt om verksamheten, Omsättning och Resultat, FoU, Likviditet, Aktien, Personal, Väsentliga händelser, Flerårsöversikt, Vinstdisposition |
| Resultaträkning | Income statement (koncern + moderbolag) |
| Balansräkning | Balance sheet (koncern + moderbolag) |
| Förändring i eget kapital | Changes in equity |
| Kassaflödesanalys | Cash flow statement |
| Noter | Notes 1-25+ with accounting policies and details |
| Revisionsberättelse | Auditor's report (placeholder until Forvis Mazars signs) |
| Definitioner | Definitions of financial terms |

---

## File structure and naming

```
YYYY YYYY/Year/ÅR/
├── Från Göran/                    # Bakvagn from CFO
│   └── Sonetel FY YY-YY Årsredovisning ver 1.0.docx
├── Från BDO/                      # Auditor materials
│   └── YYYY MM DD Underlag från Anne/
├── Layoutad/                      # Versioned drafts (created during process)
│   ├── Sonetel FY YY-YY Årsredovisning ver 0.1.docx  # First draft
│   ├── Sonetel FY YY-YY Årsredovisning ver 0.2.docx
│   └── ...
├── Bokföringsunderlag ÅR attest/  # Accounting attestation documents
└── Påskriven/                     # Signed final version
```

### Source files

- **Bakvagn**: `ÅR/Från Göran/Sonetel FY YY-YY Årsredovisning ver 1.0.docx`
- **Framvagn source**: `Bokslutskommuniké/Layoutad/Sonetel FYYY-YY Bokslutskommuniké Layoutad vNN.docx` (highest version number)
- **Previous year's final ÅR**: `../YYYY YYYY/Year/ÅR/Layoutad/Sonetel FY YY-YY Årsredovisning ver 1.0.docx`

---

## How the ÅR is composed — the merge process

### Key insight
Göran's bakvagn is typically a **copy of the previous year's final ÅR** with **financial tables updated** but **narrative text unchanged**. Therefore:

1. Start with Göran's bakvagn as the base document (it has the full structure + updated financials)
2. Identify the framvagn sections (everything before Förvaltningsberättelse)
3. Replace those sections with corresponding content from the current Bokslutskommuniké
4. Update the Förvaltningsberättelse narrative text (dates, periods, key figures)
5. Verify all financial figures match between framvagn narrative and bakvagn tables

### Section mapping: Bokslutskommuniké → ÅR

| Bokslutskommuniké section | ÅR section | Action |
|---------------------------|------------|--------|
| Om Sonetel AB (boilerplate at end) | Om Sonetel (opening) | Adapt and move to front |
| Headline + Koncernen summary | Headline + Koncernen summary | Copy, remove quarterly references |
| VDs kommentarer | VDs kommentarer | Copy as-is |
| Kommentarer till verksamheten (all subsections) | Kommentarer till verksamheten | Copy, adjust period references from "kvartalet" to full year |
| Affärsmodell | Affärsmodell (if included) | Copy if relevant for ÅR |
| AI-omställning | AI-omställning (if included) | Copy if relevant for ÅR |
| Nyckeltal charts | Nyckeltal charts | Copy charts (full-year versions) |
| N/A | Förvaltningsberättelse onwards | Keep from bakvagn |

### Content adjustments when copying from Bokslutskommuniké to ÅR

1. **Remove quarterly comparisons** — ÅR only covers the full period
2. **Adjust period references** — "kvartalet oktober-december 2025" → remove; keep "räkenskapsåret juli 2024 - december 2025"
3. **Remove "Verksamheten efter perioden"** — not part of ÅR (covered in Förvaltningsberättelse if needed)
4. **Remove financial statement tables** — the ÅR uses the bakvagn's more detailed tables with notes
5. **Keep charts/images** — Nyckeltal page charts carry over

---

## Merge implementation (python-docx)

### Strategy: Paragraph-level merge

```python
from docx import Document
from docx.oxml.ns import qn
from copy import deepcopy

def find_heading(doc, text_pattern):
    """Find paragraph index containing heading text."""
    for i, p in enumerate(doc.paragraphs):
        if text_pattern.lower() in p.text.lower() and p.style.name.startswith('Heading'):
            return i
    return None

def copy_elements(source_doc, dest_doc, start_idx, end_idx):
    """Copy paragraphs and their XML elements from source to dest."""
    body = dest_doc.element.body
    for i in range(start_idx, end_idx):
        elem = deepcopy(source_doc.paragraphs[i]._element)
        body.append(elem)
```

### Merge order
1. Open bakvagn document
2. Find the "Förvaltningsberättelse" heading (marks start of bakvagn content)
3. Open Bokslutskommuniké document
4. Find equivalent sections to extract for framvagn
5. Build new document: Bokslutskommuniké sections (up to but not including financial statements) + Bakvagn sections (from Förvaltningsberättelse onwards)

---

## Replacing the Revisionsberättelse placeholder

When Jonas Helleklint (Forvis Mazars) delivers the official revisionsberättelse, replace the placeholder in the ÅR.

### Style mapping — Forvis Mazars Word documents use Swedish style IDs:
| Forvis Mazars style | ÅR style to use |
|---------------------|-----------------|
| `Normal` | `Normal` |
| `Normal (Web)` / id=`Normalwebb` | `Normal` |
| `Heading 4` / id=`Rubrik4` | `Heading 4` (subsection headings: Uttalanden, Grund för uttalanden, etc.) |
| `Heading 3` / id=`Rubrik3` | `Heading 3` (Rapport om andra krav...) |
| First para "REVISIONSBERÄTTELSE" | `Heading 1` (to match ÅR heading structure) |

### CRITICAL: Do NOT use deepcopy of XML elements from the Forvis Mazars document
Copying `paragraph._element` XML via `deepcopy` and inserting into the ÅR causes Word to show "unreadable content" errors. The foreign XML carries namespace declarations and resource references that don't exist in the ÅR document.

### Correct approach — use python-docx's `add_paragraph()` API:

```python
from docx import Document
from copy import deepcopy
import shutil

shutil.copy("ver_prev.docx", "ver_new.docx")
doc = Document("ver_new.docx")
doc_j = Document("Från Forvis Mazars/Revisionsberättelse Sonetel AB 2024-2025.docx")

style_map = {
    'Normal': 'Normal', 'Normal (Web)': 'Normal',
    'Heading 4': 'Heading 4', 'Heading 3': 'Heading 3',
}

# Find RB placeholder heading and Definitioner heading
rb_heading_elem = next(p._element for p in doc.paragraphs
                       if p.text.strip() == 'Revisionsberättelse' and p.style.name == 'Heading 1')
definitioner_elem = next(p._element for p in doc.paragraphs
                         if p.text.strip() == 'Definitioner' and p.style.name == 'Heading 1')

# Remove all elements from rb_heading up to (not including) Definitioner
body = doc.element.body
children = list(body)
for elem in children[children.index(rb_heading_elem):children.index(definitioner_elem)]:
    body.remove(elem)

# Insert Jonas's paragraphs using add_paragraph (clean XML, no foreign references)
new_elements = []
for jp in doc_j.paragraphs:
    ar_style = style_map.get(jp.style.name, 'Normal')
    if jp.text.strip() == 'REVISIONSBERÄTTELSE':
        ar_style = 'Heading 1'
    new_p = doc.add_paragraph(style=ar_style)
    if jp.text:
        new_p.add_run(jp.text.replace('\n', ''))
    new_elements.append(new_p._element)

# Move all new paragraphs from end of body to before Definitioner (in order)
for elem in new_elements:
    elem.getparent().remove(elem)
    definitioner_elem.addprevious(elem)

doc.save("ver_new.docx")
```

---

## Datering och underskrifter (ÅRL 2 kap. 7 § — nytt krav från 2024)

**This is a hard requirement Bolagsverket enforces, and it is easy to miss because it did not exist before.**

Årsredovisningslagen 2 kap. 7 § was amended (in force **1 July 2024**) to read:

> *"Årsredovisningen ska dateras och innehålla uppgift om den dag då den undertecknades."*

It applies **first time to the räkenskapsår that begins immediately after 30 June 2024** — for Sonetel that was the extended FY **2024-07-01 – 2025-12-31**, so **FY 24-25 was the very first ÅR covered.** Every ÅR from here on is covered.

The rule requires **two distinct dates**, both of which must be unambiguous in the filed document:

| Date | Meaning | Where it lives |
|------|---------|----------------|
| **Datering / färdigställande** | The day the board agreed on the final content and the report was ready for signing ("gjordes klar") | An explicit dated line on the underskrifter page |
| **Undertecknandedatum** | The date each person actually signed | Next to each signature (paper) or in the Penneo verifikatsida/logg (electronic) |

### What to put on the underskrifter page — do this every year

The old template used a single `Stockholm den DD månad ÅÅÅÅ` line above the signatures. **That line alone is ambiguous** under the new rule — Bolagsverket read it as a signing date and issued a föreläggande that the *färdigställande* date was missing (see lesson below). Make the finalization date **explicit and separate**.

**Order matters: the *färdigställande* line comes FIRST, then the `Stockholm den …` påskrift line, then the signatures** — the report is finalized, *then* signed. (Bolagsverket confirmed this ordering by phone 2026-07-03.) Recommended layout above the signature block:

```
Årsredovisningen färdigställdes den 26 mars 2026.

Stockholm den 26 mars 2026

[signature block: names + roles]

Vår revisionsberättelse har lämnats den 26 mars 2026.
```

The datering and the signing date **may be the same date** (BFN: it is an advantage to sign in close connection to the datering). If all signatures land on the same day, one date carries both — but still state the *färdigställande* explicitly so it cannot be misread as only a signing date.

### Electronic signing (Penneo)

With Penneo, each signatory's date comes automatically in the signature log. Bolagsverket accepts a *"logg, verifikatsida eller något annat bevis"* when the signing dates are not visible in the document body itself. **Therefore: when filing an electronically signed ÅR, the Penneo verifikatsida/appendix MUST be included in what is sent to Bolagsverket** — do not strip it. Confirm the appendix pages are present in the final PDF before filing.

### Hard-learned lesson (2026-07, Bolagsverket föreläggande on FY 24-25)

Bolagsverket issued a föreläggande claiming the FY 24-25 ÅR *"saknar uppgift om datum när den gjordes klar."* The signed report **did** carry `Stockholm den 26 mars 2026` above the signatures and Penneo timestamps — but the single line was ambiguous under the then-brand-new ÅRL 2:7, and FY 24-25 was the first report the rule applied to. Fix going forward: always add the explicit *färdigställandedatum* line and always include the Penneo verifikatsida in the filing. If a föreläggande arrives, note the response deadline immediately and call Bolagsverket if it is tight — the deadline on this one was missed.

---

## Versioning conventions

- **ver 0.1** — First automated draft (Claude merge)
- **ver 0.2-0.9** — Iterations with Henrik's feedback
- **ver 1.0** — Final version for signing
- **ver 1.1+** — Post-signing corrections (rare)

Always save as a new version, never overwrite.

---

## Checklist — ÅR first draft

- [ ] Bakvagn from Göran received and placed in `Från Göran/`
- [ ] Latest Bokslutskommuniké identified (highest version in `Layoutad/`)
- [ ] Create `Layoutad/` directory if not exists
- [ ] Merge framvagn + bakvagn into ver 0.1
- [ ] Verify period references are correct (not quarterly, correct fiscal year)
- [ ] Verify "Om Sonetel" section is current
- [ ] Verify VD kommentarer are from current period
- [ ] Verify Förvaltningsberättelse dates match the fiscal year
- [ ] Verify financial tables have current year's numbers
- [ ] Check that Revisionsberättelse is marked as placeholder
- [ ] Remove any Bokslutskommuniké-specific content (quarterly tables, post-period events section)

---

## Checklist — ÅR finalization

- [ ] All narrative sections reviewed and approved by Henrik
- [ ] Förvaltningsberättelse narrative updated by Göran
- [ ] All financial figures cross-checked against BDO's bokslut
- [ ] Flerårsöversikt includes current year
- [ ] Vinstdisposition matches board proposal
- [ ] **Uttalande från företagsledningen** signed by CEO (Henrik) and CFO/authorised signatory (Sebastian) → store in `Påskriven/`
- [ ] Revisionsberättelse received from Forvis Mazars (Jonas Helleklint) → insert into ÅR (see section above)
- [ ] Underskrifter page has correct board member names and roles
- [ ] **Datering (ÅRL 2:7):** explicit *färdigställande* date line present, placed **before** the `Stockholm den …` påskrift line and above the signatures — not just a `Stockholm den …` line (see "Datering och underskrifter" section)
- [ ] **Signing dates present:** either next to each signature, or via the Penneo verifikatsida included in the final PDF
- [ ] Final PDF exported (Word → File → Save As → PDF)
- [ ] Penneo verifikatsida/appendix confirmed present in the PDF that will be filed with Bolagsverket
- [ ] Signed ÅR PDF stored in `Påskriven/`
- [ ] Published via Cision → appears on sonetel.com under Rapporter

### Påskriven/ folder contents
All signed documents for the ÅR are stored in `ÅR/Påskriven/`:
- `Uttalande från företagsledningen Sonetel AB YYYY-YYYY.pdf` — management representation letter (signed by CEO + Sebastian)
- `Sonetel FY YY-YY Årsredovisning [final].pdf` — the signed annual report

---

## Key differences from Bokslutskommuniké

| Aspect | Bokslutskommuniké | Årsredovisning |
|--------|-------------------|----------------|
| Purpose | Market communication (Nasdaq) | Legal filing (Bolagsverket) |
| Audience | Investors, analysts | Regulatory, shareholders |
| Financial detail | Summary tables | Full statements + 25+ notes |
| Quarterly data | Yes (Q comparisons) | No (full period only) |
| Auditor's report | No | Yes (Revisionsberättelse) |
| Signing | CEO only | Full board + CEO |
| Charts | Yes (Nyckeltal) | Yes (same charts) |

---

## PDF export (Mac)

**Do NOT use Print → Save as PDF** — causes floating image displacement on Mac.

**Do NOT use `docx2pdf` or AppleScript automation** — Word on Mac times out.

**Manual workflow:**
1. Word → **File → Save As** → choose **PDF** as file format
2. If file is large: open in **Preview → File → Export → Quartz Filter: Reduce File Size**

---

$ARGUMENTS
