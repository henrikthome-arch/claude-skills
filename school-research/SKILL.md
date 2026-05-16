---
name: school-research
description: Research a topic for the Volos international school project. Spawns parallel research agents, writes structured reports to docs/09_RESEARCH/, has them reviewed, and updates the changelog.
argument-hint: "[topic description]"
---

**DIRECTORY GUARD**: This skill is ONLY for the Volos school project. If the current working directory does NOT contain `international school in Volos`, STOP immediately and tell the user: "This skill is for the Volos school project only. Current directory: [cwd]". Do NOT proceed.

You are performing deep research for the Volos International AI School project. The research topic is provided as `$ARGUMENTS`. If no topic is given, ask the user what to research.

## Project Context

Planning and establishment of a Cambridge International school in Volos, Greece. Key facts:
- Target curriculum: Cambridge International (Primary → IGCSE → A-levels) with mandatory Greek subjects
- Location: Volos, city in Magnesia prefecture, Thessaly, Greece
- Legal framework: Foreign School licence (Ξένο Σχολείο) under Law 4862/1931 as amended by Law 4713/2020
- ~12 interested families as of early 2026; no international school currently exists in Volos
- Working directory: `/Users/henrik/Library/CloudStorage/Dropbox/international school in Volos/`
- Existing research reports: `docs/09_RESEARCH/` (check what's already there before starting)
- Master project plan: `PLAN.json` at project root — 10 phases (P0–P10), ~60 tasks with dependencies, target dates, and refs to research docs. Check it before researching to understand context and avoid duplicating work already captured there.

## Research Workflow

### Step 1 — Check Existing Research
Before starting, read `docs/09_RESEARCH/README.md` and list any existing reports that partially cover the topic. Avoid duplicating work.

### Step 2 — Decompose the Topic
Break the topic into 3–5 research sub-topics that can be researched independently. Examples for typical school research:
- Legal/regulatory requirements at national level
- Local/regional requirements
- Physical/facility standards
- Staff/HR requirements
- Financial/cost dimensions
- Curriculum/accreditation requirements

### Step 3 — Launch Parallel Research Agents
Spawn multiple background `general-purpose` agents simultaneously — one per sub-topic. Write detailed prompts for each agent:
- Specify exactly what to find
- Name specific laws, organisations, websites to check (Greek sources: minedu.gov.gr, eugo.gov.gr, mitos.gov.gr, eurydice.eacea.ec.europa.eu; Cambridge: cambridgeinternational.org)
- Ask for source URLs in the output
- Ask agents to flag areas of uncertainty needing professional advice

### Step 4 — Compile Reports
For each major sub-topic, write a structured Markdown report. Follow the report format below. Number sequentially (check existing R0X files, use next available number). Save to `docs/09_RESEARCH/`.

### Step 5 — Peer Review
Launch a `Plan` agent to review the reports. The review agent should assess:
- Confidence score (1–10) per report
- Most important findings (top 3)
- Gaps and risks (top 3)
- Internal consistency across reports
- Corrections needed
- Topics not covered that should be

### Step 6 — Incorporate Feedback
Make targeted edits to the reports based on review findings. Do not rewrite wholesale — fix specific issues.

### Step 7 — Update Index and Changelog
- Update `docs/09_RESEARCH/README.md` with new report entries, key findings, and any new follow-up items
- Add entries to `changelog/CHANGELOG.md` under `[UNRELEASED] > ### Added`

---

## Report Format

### File naming
```
R{NN}_{ShortTitle}.md
```
Examples: `R01_Cambridge_Approval_Process.md`, `R05_Financial_Model.md`

Use sequential numbering — check existing files and use the next available number.

### Report structure

```markdown
# R{NN} — {Full Title}

> **Research date:** YYYY-MM-DD
> **Status:** Research summary — not [legal/financial/etc.] advice. Verify [what] before acting.
> **Sources:** [list key sources used]

---

## Overview
[3–5 sentence summary of the most important findings. Include any critical caveats at the top.]

---

## 1. [First major section]
...

## N. [Areas Requiring Professional Advice]
[Always include this section when the topic has legal, financial, or regulatory dimensions. Use a table: Issue | Risk Level | Action]

---

## Sources
[Bullet list of sources with markdown hyperlinks]
```

### Formatting conventions
- Use tables for comparisons and decision matrices
- Use blockquotes (`>`) for important caveats and warnings
- Use `**bold**` for laws, key terms, and critical constraints
- Flag items needing professional advice explicitly with "FLAG FOR LEGAL REVIEW" or similar
- Include specific contact information (phone, email, address) for relevant Greek authorities
- Always include a "Quick Reference" table for reports with many numbers/metrics

---

## Key Sources by Topic

### Greek regulatory / legal
| Source | What it covers |
|--------|---------------|
| eugo.gov.gr | Official administrative procedures (EUGO single gateway) |
| mitos.gov.gr | Greek administrative procedure descriptions |
| minedu.gov.gr | Ministry of Education — laws, circulars, contact |
| eurydice.eacea.ec.europa.eu/eurypedia/greece | EU overview of Greek education system |
| kodiko.gr / nomoskopio.gr | Greek law full text |

### Cambridge International
| Source | What it covers |
|--------|---------------|
| cambridgeinternational.org/why-choose-us/join-cambridge/ | School registration process |
| cambridgeinternational.org/programmes-and-qualifications/ | Programme details |
| schoolsupporthub.cambridgeinternational.org | Resources (requires school login) |

### Local Volos / Magnesia contacts
| Authority | Contact |
|-----------|---------|
| Primary Education Directorate Magnesia — Private Education Office | +30 2421026715 |
| Secondary Education Directorate Magnesia | 24210-47386, mail@dide.mag.sch.gr |
| Volos Urban Planning (Πολεοδομία) | 2421356812, gr.poleod@volos-city.gr |
| Ministry of Education — Private Education Directorate | 210-3443464, adie@minedu.gov.gr |

---

## Existing Research (check before starting)

The following reports already exist in `docs/09_RESEARCH/`:
- R01: Cambridge International approval process (4-step, fees, quality standards)
- R02: Greek legal framework (licence types, Q1 window, student access restrictions, Law 4713/2020)
- R03: Staff regulations (DOATAP, work permits, Blue Card, salary, background checks)
- R04 (named `Facility_Requirements_Greece_Private_School.md`): Building standards, zoning, fire safety, Cambridge lab/exam room requirements

Open questions not yet researched (see `docs/09_RESEARCH/README.md` and `PLAN.json` tasks P0.5–P0.12):
- Cambridge A-levels and Greek university entry (Critical) — P0.5
- Legal entity structure for Foreign School licence (Critical) — P0.6
- Financial model / minimum viable enrolment (High) — P0.7
- Combined model mechanics in practice (High) — P0.8
- Insurance requirements (Medium) — P0.9
- GDPR/data protection compliance (Medium) — P0.10
- Provisional operation as tutoring centre (Medium) — P0.11
- Greek employment contract law for school staff (Medium) — feeds P4.10
- Greek accounting obligations: VAT, AADE filings, payroll for private schools (Medium) — feeds P1.7

Next research report number: R05 (R01–R04 already exist).

$ARGUMENTS
