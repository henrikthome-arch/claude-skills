---
name: board-meeting
description: Preparing board meetings for Sonetel AB. Use when producing agenda, processing topic inputs, merging presentation decks, or managing board meeting documentation.
argument-hint: "[agenda | content | slides | minutes | status]"
---

**DIRECTORY GUARD**: This skill is ONLY for Sonetel board meetings. If the current working directory does NOT contain `Sonetel/Board` or `Sonetel/Corporate`, STOP immediately and tell the user: "This skill is for Sonetel board meetings only. Current directory: [cwd]". Do NOT proceed.

You help Henrik Thomé, CEO of **Sonetel AB (publ)**, prepare and manage board meetings. Board meetings are held approximately quarterly, conducted in **English**.

The working directory for a board meeting is:
`~/Library/CloudStorage/Dropbox/Sonetel/Board/Board meetings/[YYYY]/[YYYY MM DD Board meeting (N)]/`

---

## Company Profile

- **Company:** Sonetel AB (publ), org. no. 556486-5847
- **Listed:** Nasdaq First North Growth Market
- **CEO:** Henrik Thomé
- **Fiscal year:** January–December (changed from July–June at EGM 2025-05-22)

---

## Board Meeting Participants (recurring)

| Name | Role | Contribution |
|------|------|-------------|
| Henrik Thomé | CEO / typically Chair | Topic inputs, CEO section, meeting lead |
| Prashant | COO | Own deck (contributions/prashant/) |
| Tomas | Chief AI Officer | Own deck (contributions/tomas/) |

---

## Folder Structure

Every board meeting uses this structure:

```
[YYYY MM DD Board meeting (N)]/
├── .claude/
│   └── settings.local.json      # Pre-approved permissions
├── CLAUDE.md                    # Meeting-specific rules and conventions
├── CHANGELOG.md                 # All changes tracked
├── change-requests/             # Formal CRs for material changes
├── agenda/
│   ├── agenda.json              # Single source of truth – machine-readable
│   └── agenda.md                # Human-readable (generated from agenda.json)
├── content/
│   ├── raw/                     # Raw inputs: transcripts, files, notes (any format)
│   └── [topic]-input.md         # Structured content (Claude produces from raw inputs)
├── slides/
│   ├── contributions/
│   │   ├── prashant/            # Prashant's .pptx
│   │   └── tomas/               # Tomas's .pptx
│   └── archive/                 # Previous merged versions
└── minutes/                     # Post-meeting minutes
```

---

## Content Input Processing

Content inputs can arrive in any form. **Claude's job is always to produce a structured `content/[topic]-input.md` from whatever is provided.**

### Input types

| Type | How Henrik provides it | What Claude does |
|------|----------------------|-----------------|
| **Direct input** | Prose or bullets typed in conversation | Capture and structure immediately into `content/[topic]-input.md` |
| **Transcript** | Voice note or meeting recording transcript | Save raw to `content/raw/[topic]-transcript.md`, extract key points into structured file |
| **File** | Document, PDF, spreadsheet, existing presentation | Read the file, extract relevant content, produce structured file |
| **Project reference** | "See [project] in workflow" | Read CLAUDE.md / README / summary of that project, extract board-relevant points |

### Naming conventions

- Raw inputs: `content/raw/[topic]-[type].[ext]`
  - e.g. `content/raw/financials-transcript.txt`
  - e.g. `content/raw/strategy-notes.md`
- Processed output: `content/[topic]-input.md` (always structured with frontmatter)

### Processing rule

When given any input, always produce the structured `content/[topic]-input.md`. Record the source(s) in the `sources` frontmatter field. If the raw input is worth keeping, save it to `content/raw/` first.

---

## Content File Schema

Every `content/[topic]-input.md` uses YAML frontmatter + structured sections. This is what drives slide production.

```markdown
---
agenda_item: 6
title: "Exact title as in agenda.json"
presenter: "Name"
duration_minutes: 20
status: draft
key_message: "One sentence – the single most important takeaway. Maps to the hero/opening slide."
decisions_needed:
  - "Decision description (feeds into item 7 – Decisions & resolutions)"
sources:
  - "content/raw/topic-transcript.md"
  - "conversation"
  - "/path/to/source/project"
---

## Talking points
- One bullet per main point (each may map to one slide or one key statement)
- Be concrete: numbers, comparisons, outcomes

## Key data points
| Label | Value | Context |
|-------|-------|---------|
| Example metric | 250 KSEK | Old cost, coding only |

## Slide outline
1. Hero slide title
   - Supporting bullet
2. Second slide title
   - Bullet

## Background / context
Free-form prose for Claude's reference when producing slides. Not necessarily shown to the board verbatim.
```

### Field rules
- `key_message` → always becomes the opening slide for this section
- `talking_points` → Claude maps these to slide bullets
- `key_data_points` → Claude produces a data/comparison slide
- `slide_outline` → Claude follows this if provided; otherwise derives from talking points
- `decisions_needed` → Claude aggregates these across all items into agenda item 7
- `background` → context only; Claude decides what, if anything, goes on slides

---

## Workflow

### Phase 1 – Content Collection
- Henrik provides inputs in any format: direct text, transcripts, files, or project references
- Claude processes each into a structured `content/[topic]-input.md`
- Raw inputs saved to `content/raw/` when they have standalone value

### Phase 2 – Agenda Finalization
- `agenda.json` is the single source of truth
- After updating `agenda.json`, always regenerate `agenda.md`
- Agenda is sent to board members once approved by Henrik

### Phase 3 – Slide Production
- For Henrik's sections: transform content inputs into structured slide outlines
- For contributor sections: Prashant and Tomas drop their `.pptx` in their contribution folder
- Claude can read `.pptx` metadata but cannot directly edit binary files

### Phase 4 – Merge & Finalize
- Merged deck versioning: `Sonetel board meeting [Month Day], [Year] v1.pptx`, `v2.pptx`...
- Final version exported as PDF before distribution
- Previous versions moved to `slides/archive/`

### Phase 5 – Post-Meeting
- Draft minutes within 48 hours in `minutes/`
- Update CHANGELOG.md with key decisions and actions

---

## Agenda JSON Schema

`agenda.json` structure:

```json
{
  "meeting": {
    "title": "Board Meeting #N",
    "company": "Sonetel AB",
    "meeting_number": N,
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "location": "...",
    "language": "English",
    "status": "Draft | Under review | Final | Distributed",
    "attendees": []
  },
  "agenda_items": [
    {
      "number": 1,
      "title": "...",
      "presenter": "...",
      "duration_minutes": 10,
      "type": "procedural | ceo-update | financial | operational | strategic | decision | aob",
      "content_file": "content/filename.md or null",
      "slides_section": "Section title in deck or null",
      "decisions": [],
      "notes": "..."
    }
  ],
  "total_duration_minutes": 0
}
```

Always recalculate `total_duration_minutes` when items change.

---

## Typical Agenda Structure

Board meetings typically cover:
1. Opening & formalities (~5 min)
2. CEO update (~15 min)
3. Financial overview (~15 min)
4. COO update – Prashant (~20 min)
5. AI & Technology update – Tomas (~20 min)
6. Strategic items (~20 min)
7. Decisions & resolutions (~10 min)
8. Any other business (~5 min)
9. Closing (~5 min)

Adjust based on content inputs and meeting goals.

---

## Document Status

| Status | Meaning |
|--------|---------|
| Draft | Working copy, freely editable |
| Under review | Awaiting Henrik's approval |
| Final | Approved – requires CR to change |
| Distributed | Sent to board – requires CR + approval |
| Archived | Superseded |

---

## Changelog Conventions

Update `CHANGELOG.md` after every change. Use English. Format:

```markdown
## [UNRELEASED]
### Added
- content/financials-input.md

### Changed
- agenda.json: added item 3 – Financial overview, 15 min

### Removed
- Removed placeholder item
```

---

## Change Request Process

A CR is required when changing content after it has been **distributed** to the board.

Save as: `change-requests/CR-YYYY-MM-DD-NNN-short-description.md`

```markdown
# CR-YYYY-MM-DD-NNN: Title

**Date:** YYYY-MM-DD
**Status:** Draft | Under review | Approved | Implemented | Rejected
**Requested by:** Henrik

## Background
Why is this needed?

## Proposed change
What exactly changes?

## Affected documents
- agenda/agenda.json

## Decision
[Leave blank until reviewed]
```

---

## Slide Versioning

- `Sonetel board meeting [Month Day], [Year] v1.pptx` → `v2.pptx` → ...
- v0.x = internal drafts
- v1.0+ = shared with contributors
- Final always exported as PDF
- Never delete versions – archive them

---

## Minutes Format

Post-meeting minutes in `minutes/` should cover:
- Date, location, attendees
- Agenda items with brief summary of discussion
- Decisions taken (numbered resolutions)
- Action items (owner, due date)
- Next meeting date

---

## How to Work

1. **Always read `CLAUDE.md` and `CHANGELOG.md`** in the project folder first
2. **Check `agenda.json`** for the current state of the agenda
3. **Check document status** before editing – Final/Distributed items require a CR
4. **Update `CHANGELOG.md`** after every change
5. **Regenerate `agenda.md`** whenever `agenda.json` changes
6. **Never distribute** anything without Henrik's explicit approval

$ARGUMENTS
