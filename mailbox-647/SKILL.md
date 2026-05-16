---
name: mailbox-647
description: Process weekly scanned mail received via Sonetel AB Mailbox 647 forwarding service. Triage PDFs, log to register, flag follow-ups, file to processed/<year>/. Use when working in the "Mailbox 647" folder.
argument-hint: "[triage | extract <topic> | status]"
---

**DIRECTORY GUARD**: This skill is for the Mailbox 647 mail-processing folder at `~/Library/CloudStorage/Dropbox/Sonetel/Mailbox 647/`. If the current working directory is NOT that folder (or a subfolder of it), STOP and tell the user the skill only runs from that directory. Do NOT proceed.

## What this folder is

A weekly batch of scanned post received via the **Sonetel AB (publ) Box 647, 114 11 Stockholm** mail-forwarding service. Mail is delivered as a bundle of PDFs to `~/Downloads/`, then processed here.

## Mail recipients

The mailbox receives mail for multiple addressees who share Box 647:
- **Sonetel AB (publ)** — org-nr 556486-5847 (most mail)
- **Swedish General Consulting AB** — org-nr 556071-0229 (occasional)
- **Henrik Thomé** personally — Amex statements addressed to Solna home but routed via this PO box
- **Wrong addressee** — occasional misdirected mail (e.g. German doctor's correspondence)

A single scanned PDF often bundles letters to multiple addressees — note recipient explicitly per item.

## Folder structure

```
Mailbox 647/
├── inbox/                  # newly-received PDFs awaiting triage
├── processed/<year>/       # filed PDFs (YYYY-MM-DD_sender_topic.pdf)
├── extracts/<topic>/       # standalone extracts when forwarding sub-documents
├── register.md             # master log: one row per PDF received
├── followups.md            # open action items by priority
├── activity.md             # append-only chronological event log
└── README.md               # human-readable process doc
```

When invoked, **first read `register.md`, `followups.md`, `activity.md`, `README.md`** to understand current state.

## The weekly process

### 1. Drop into `inbox/`
User moves new PDFs into `inbox/` (or asks the skill to do it from `~/Downloads/`).

### 2. Triage each PDF
Use the Read tool on each PDF (it returns vision-extracted content). Identify:
- **Sender** (PTS, Skatteverket, BDO, SEB, Nordea, RTR-GmbH, SCB, etc.)
- **Recipient** (Sonetel AB / SGC / Henrik / wrong addressee)
- **Category** — pick one:
  - `regulatory-telecom` 🔴 — telecom regulator, **always followup**
  - `regulatory-statistics` 🟡 — SCB / mandatory statistics, **always followup**
  - `tax` 🟡 — Skatteverket, Bolagsverket
  - `bank` — SEB, Nordea, PlusGirot
  - `invoice` — vendor or auditor invoices and reminders
  - `personal-card` — Henrik's personal correspondence
  - `noise` — marketing, scam, wrong addressee, greeting cards, PlusGirot annulleringslista (see below)

### 3. Append to `register.md`
One row per PDF in the appropriate year section. Include date received, sender, category, recipient, one-line summary (with amounts and deadlines for invoices), status (`done` / `followup` / `noise`), and target filename.

### 4. Update `followups.md` if action needed
Add to the right priority section (🔴 P0, 🟡 P1, 🟢 P2/P3). Include deadline, what needs to happen, where to take action (URL, contact, login), reference numbers. When resolved, mark ✅ and leave in place — do NOT delete (audit trail).

### 5. Append to `activity.md`
One line per discrete action: `YYYY-MM-DD  <verb-led description>`. New events at the bottom of the year section.

### 6. Rename and move to `processed/<year>/`
Filename pattern: `YYYY-MM-DD_sender_topic.pdf`
- For mixed PDFs: `YYYY-MM-DD_mixed_<sender1>_<sender2>_...pdf`
- Examples:
  - `2026-04-15_bdo_påminnelse_112kSEK.pdf`
  - `2025-12-02_rtr_austria_planumsatz_initial.pdf`
  - `2026-02-19_mixed_rtr_seb_cision.pdf`

### 7. Inbox empty = batch done
If `inbox/` is empty, the batch is fully triaged.

## High-priority senders (always followup)

**Foreign telecom regulators** — anywhere Sonetel holds numbers, licences, or services:
- 🇦🇹 RTR-GmbH (Austria) — annual Planumsatz / Finanzierungsbeitrag → **forward to Vamshi**
- 🇸🇪 PTS (Post- och telestyrelsen, Sweden)
- 🇬🇧 Ofcom (UK)
- 🇺🇸 FCC (US)
- 🇧🇪 BIPT (Belgium)
- 🇵🇹 ANACOM (Portugal)
- Any other country regulator

**Swedish authorities**:
- Skatteverket (tax)
- Bolagsverket (companies registry)
- SCB / Tillväxtanalys — mandatory statistics, vite (fine) risk for non-response

**Banking / finance**:
- SEB påminnelse / overdraft notices
- Nordea loan amorteringsavi (monthly, ~30 000 SEK for credit 3356 80 08726)
- BDO (auditor) påminnelse

## Hard-learned classification rules

### PlusGirot annulleringslista = noise
PlusGirot cancelled-payment notices (insufficient funds or "annullerad on customer demand", typically USD to Sonetel Software Services or SEK to Google Ireland) arrive frequently and should be classified as **noise / done**, NOT followup. Cash flow management handles these day-to-day, separately from this mailbox process. Do NOT add them to followups.md or alarm the user about the pattern.

### Austrian RTR-GmbH → forward to Vamshi
Vamshi handles Sonetel's Austrian RTR-GmbH (Rundfunk und Telekom Regulierungs-GmbH) correspondence — Planumsatz declarations, Finanzierungsbeitrag, § 34 KommAustria-Gesetz obligations. When an RTR letter arrives:
1. Extract the letter as a standalone PDF (often bundled with unrelated mail) using `pdfseparate` + `pdfunite` (see "Extracting bundled letters" below).
2. Place in `extracts/rtr-austria/NN_YYYY-MM-DD_rtr_<topic>.pdf` numbered chronologically.
3. Tell user it's ready to forward to Vamshi.
4. In followups.md, log as P1 with "forwarded to Vamshi YYYY-MM-DD" rather than as a P0 owned by Henrik.

### Known scam / solicitation senders — file as `noise`
Do NOT pay, do NOT sign, do NOT add to followups beyond a one-line "scam — ignored" note:
- **OMPS / Mandat Consulting** — fake trademark "publication" service, Slovak IBAN
- **Trademarks Worldwide (UK)** — fake trademark monitoring (worldwidetrademark.co.uk)
- **Johansson & Partners Intellectual Property** — overpriced trademark renewal solicitations (real trademark deadlines, vastly inflated prices vs EUIPO direct renewal at €850 base)

### Personal Amex (Henrik) → log briefly, no action
Personal SAS Amex Premium statements addressed to Henrik in Solna but scanned via this mailbox. Log in register, file to `processed/<year>/` as `YYYY-MM-DD_amex_henrik_personal_<month>.pdf`, status `done`. Only flag the **most recent unpaid month** as P3 followup (with due date). Suggest redirecting Amex to home address if it keeps cluttering the mailbox.

## Extracting bundled letters

The scanning service often bundles unrelated letters into one PDF. To extract a sub-document for forwarding:

```bash
# Tools available: pdfseparate, pdfunite (poppler, /opt/homebrew/bin/)

# Extract pages 5-6 from a 6-page bundle:
pdfseparate -f 5 -l 6 "processed/2026/2026-02-04_mixed_nordea_plusgirot_rtr.pdf" /tmp/p%d.pdf
pdfunite /tmp/p5.pdf /tmp/p6.pdf "extracts/rtr-austria/02_2026-01-19_rtr_planumsatz_reminder.pdf"
rm /tmp/p*.pdf
```

When extracting multiple related letters, number them `01_`, `02_`, `03_` so they sort chronologically when forwarded.

## Reading PDFs

Use the **Read tool** directly on each PDF — it does vision OCR. For PDFs >10 pages, pass `pages: "1-10"` parameter. Read multiple PDFs in a single message in parallel for speed; don't sequentialize. Many "long" PDFs are mostly blank pages between bundled documents — be ready to extract sub-page ranges.

## When the user asks for status

Read register.md, followups.md, activity.md and report:
- How many PDFs in inbox awaiting triage
- Top 3 P0/P1 followups
- Most recent activity-log entries
- Any approaching deadlines from followups

Don't re-do the triage if everything is already in `processed/`.

## When new mail arrives

1. Confirm with user before moving from `~/Downloads/` (they may have other unrelated PDFs there).
2. Move PDFs to `inbox/`.
3. Run the triage workflow.
4. End with a status report: counts by category, P0/P1 highlights, anything novel.

## Recipient identification cheat sheet

| If addressee shows... | Then it's for... |
|---|---|
| `Sonetel AB (publ)` or `BOX 647` only | Sonetel AB |
| `Swedish General Consulting AB` or `Mailbox 647 SWEDEN` | SGC |
| `Carl Henrik Thomé`, `Henrik Thomé`, `FRAMNÄSBACKEN 1` | Henrik personally |
| `Sebastian Ahlskog` | Sonetel CFO (cc only — still log as Sonetel AB) |
| Other natural person name | Likely wrong addressee — verify and probably discard |
