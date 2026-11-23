---
name: expense-batch
description: Reconcile Henrik's personal-card expense reimbursement batches (AMEX, etc) against the financial-ops monthly batch. Cross-checks card statement lines against parsed receipts, identifies what's already in the batch and what's missing, and prepares per-transaction documentation (card statement page + provider receipt) for reimbursement.
---

## What this skill is for

Henrik pays many Sonetel and Epivo business expenses on personal cards (mainly the SAS AMEX Premium ending in **92000**). Each month the financial-ops portal builds an expense **batch** that reimburses these. Each transaction in the batch needs:

1. The **card statement page** showing the SEK amount actually debited
2. The original **provider receipt/invoice**

Use this skill when Henrik asks to:
- Reconcile an AMEX (or other) statement against the current month's batch
- Identify which card charges still need receipts uploaded
- Check what's already booked vs. still missing for a given month

This skill operates on the **financial-ops** repo. Working directory should contain `financial-ops`.

---

## Card identification (payment_identifier in receipts)

| `payment_identifier` | Card | Owner | Notes |
|---|---|---|---|
| `2000` or `92000` | AMEX SAS Premium ending `…92000` | Henrik personal | Statement files in `~/Downloads/YYYY-MM-02.pdf` (cycle ends 2nd of next month) |
| `1003` | Another AMEX card | Henrik personal | Some Anthropic, Vy Buss, Finnair charges |
| `8627` | Mastercard ending `…8627` | Sonetel company | Already a company card — not reimbursed through expense batch |
| `3784`, `3421`, `9469` | Various | (case-by-case) | Check with Henrik |

When `payment_identifier` is `2000` on a receipt, that's the same card as AMEX statement `…92000` — the receipt parser captures only the last 4 of `92000`.

---

## Which month does a charge belong to?

**Rule: use the AMEX *transaction/processing date*, not the statement date.**

The AMEX cycle ends on the 2nd of each month — so the `2026-04-02.pdf` statement contains charges from `03.03.26` through `02.04.26`. Charges dated `01.04.26` and `02.04.26` belong to the **April batch**, even though they're on the "April statement". The rest of that statement belongs to the March batch.

Practical implication: for the April batch you usually need **both** the statement dated `YYYY-04-02.pdf` (for charges that hit on 01-02 April) **and** the statement dated `YYYY-05-02.pdf` (for charges 03 April through 30 April).

---

## SEK amount rule

**Always claim the SEK amount on the card statement** — the SEK actually debited from the cardholder. Do **NOT** re-convert the foreign-currency amount via Riksbanken rates.

This is per Henrik's standing preference (memory: `feedback_expense_fx_use_card_sek`). The card statement already has SEK on every line including the AMEX FX markup, so that's the reimbursable amount.

**Reaffirmed by Henrik 2026-11-03:** *"claims via AMEX should always use the AMEX charges in SEK as the FX basis."*
Consequence: **never claim an AMEX line before it appears on an AMEX statement.** Batch 108 (Aug 2026) broke this:
Bandwidth (4846) and Claude were claimed ahead of the statement and reimbursed at Riksbank FX, about 1,328 SEK short.
Henrik wrote that shortfall off ("Never mind August"). Don't raise it again, and don't repeat the pattern. A charge not
yet on a statement waits for the next batch.

### Portal "FX Unconfirmed" status (batch detail page)

On `/receipts/batches/<id>`, foreign-currency lines show "Pending" with an "FX Unconfirmed" red badge until SEK is supplied. The portal has a 🔄 convert button that uses **Riksbanken** rates — **DO NOT use it for AMEX charges**. AMEX adds a ~2-3% FX markup on top of interbank rates; if you accept the Riksbanken conversion, the SEK figure in the batch will be lower than what AMEX actually debited, and Henrik eats the difference out of pocket.

**Extracting SEK from the AMEX PDF**: each foreign-currency line shows `Köp i utländsk valuta XXX [USD|EUR]` and `Summa Avgifter SEK YY,YY  Valutakurs 0.NNNN`. The headline SEK total of the entry (top-right of the entry block) is the figure to claim — NOT the "Summa Avgifter" (which is only the AMEX fee portion, not the full SEK debit).

### MANDATORY: apply AMEX-actual SEK automatically (no portal UI needed)

**Default behavior**: when a batch contains AMEX foreign-currency lines that are still `fx_source IS NULL` / `settled_amount_sek IS NULL`, immediately apply the SEK figures from the AMEX statement via direct DB write — do NOT leave them for Henrik to enter in the portal UI, and do NOT suggest he click the 🔄 convert button.

**Why direct DB write**: the portal's `POST /receipts/transactions/<id>/manual-fx-override` endpoint requires Flask-Login session auth (`@login_required`). The MCP API token does not authenticate Flask-Login sessions. So `dbshell` over SSH is the only programmatic path, and it writes exactly the same columns the endpoint writes.

**SQL template** (single transaction, atomic, audit-logged):

```sql
BEGIN;

-- One UPDATE per transaction:
UPDATE transactions SET
  settled_amount_sek = <SEK from AMEX>,
  fx_rate = ROUND(<SEK> / <foreign>, 6),
  fx_source = 'manual_override',
  confirmed_at = NOW(),
  confirmation_mode = 'manual_override'
WHERE id = <txn_id>;
-- ... repeat for each transaction ...

-- One audit-log row summarising the batch update:
INSERT INTO activity_logs (module, action, status, user_id, meta_data, created_at)
VALUES (
  'receipts-handling', 'fx_manual_override', 'success', 1,
  '{"batch_id": <N>, "transactions": [{"id": <id>, "sek": <amt>}, ...],
    "source": "AMEX statements YYYY-MM-02 and YYYY-(MM+1)-02",
    "applied_by": "claude-cli session for henrik"}'::json,
  NOW()
);

COMMIT;
```

Wrap in a single SSH `dbshell` invocation. Verify after with `SELECT id, original_amount, original_currency, settled_amount_sek, fx_rate, fx_source FROM transactions WHERE batch_id=<N>`.

**Recipe**:
1. Get the 6-ish batch transactions: `SELECT id, transaction_date, description, original_amount, original_currency, settled_amount_sek, fx_source FROM transactions WHERE batch_id=<N> ORDER BY transaction_date, id;`
2. For each row with `fx_source IS NULL` and `original_currency != 'SEK'`, find the matching AMEX statement line by (date ± 2 days, vendor, foreign amount+currency).
3. Extract the headline SEK from the AMEX PDF.
4. Run the BEGIN…COMMIT block above.
5. Verify.

`user_id = 1` is Henrik's account (`henrik@sonetel.com`). `fx_rate` column is `numeric(10,6)`. `settled_amount_sek` is `numeric(10,2)`.

**Don't skip the activity_logs INSERT** — that's the audit trail that lets Henrik (or Jennifer at BDO) see why these SEK figures came from manual_override instead of the rate service. Reference the AMEX statement filenames in `meta_data.source` so future auditors can trace.

**Don't ask Henrik to do it in the UI** unless something blocks the SQL path (e.g. batch is `delivered` / `locked`). Asking him is the recurring foot-gun this skill exists to eliminate.

---

## Project allocation — always ASK

Henrik runs **Sonetel** and **Epivo** (and personal). Same card. Same vendor sometimes appears in both projects. **Don't assume — ask** which charges belong to which project before booking.

**⚠️ Epivo-allocated vendors must be kept OUT of the Sonetel expense batch entirely — not just labelled.** This batch feeds Sonetel/BDO books, so an Epivo line put here is a booking error that has to be unwound. Per the table below, **OpenRouter, Cloudflare (small), Google\*play, small Anthropic Ireland, ElevenLabs, and GitHub charges are Epivo** — do not add them to the Sonetel batch. (Regression: the May 2026 batch #98 wrongly included the OpenRouter 264,81 USD and Cloudflare 0,56 USD lines; Henrik flagged it 2026-07-03.) **"Google Cloud Emea Limit Ireland" on the AMEX is NOT Google Cloud infrastructure** — the recurring **24,30 EUR/month** line is **Google Workspace for the Epivo email account**, and is **Epivo**. Do not claim it. The AMEX descriptor is misleading; judge by the amount and the recurrence, not the vendor string. (Confirmed by Henrik 2026-08-13, after three of these — 01.06, 01.07, 01.08 — were added to batch #107 on the old "Cloud defaults Sonetel" reading and had to be removed.)

Known patterns (subject to confirmation each month):

| Vendor | Default project | Confirm? |
|---|---|---|
| Voxbone Sa | Sonetel | usually |
| Inmotionhosting.Com | Sonetel | usually |
| Claude.Ai Subscription (180 EUR) | Sonetel | usually (Henrik's own use for Sonetel work) |
| Openrouter, Inc | **Epivo** | confirmed 2026-05-26 |
| Google*play | **Epivo** | confirmed 2026-05-26 |
| Google Cloud Emea Limit Ireland — 24,30 EUR/mo (= Google Workspace, Epivo email account) | **Epivo** | confirmed 2026-08-13 |
| Anthropic Ireland (small charges like $6, $59) | **Epivo** | confirmed 2026-05-26 |
| Cloudflare (small) | **Epivo** | confirmed 2026-05-26 |
| ElevenLabs (`Elevenlabs`, `Eleven Labs`) | **Epivo** | confirmed 2026-08-14 |
| GitHub (`Github, Inc`, `Msft*Github`) | **Epivo** | confirmed 2026-08-14 |
| OpenAI Ads (`OpenAI Ads Invoice INV-…`, `Ads \| ChatGPT campaign spend`) | Sonetel — **marketing 5910, supplier 778 `OPENAI ADS`, NOT COGS 4030** | Henrik 2026-11-03: "Ad spending is not COGS". OpenAI API/ChatGPT stay supplier 74 (4030) |
| Anthropic **San Francisco** on AMEX (API auto-recharge ~63 USD, several a month) | **Epivo** | Henrik 2026-11-03 ("Sounds like Epivo all of it") |
| `Anthropic* Claude Sub San Francisco` (USD, e.g. 1,879 SEK) | **Epivo** | Henrik 2026-11-03. The 180 EUR Dublin one stays Sonetel |
| Deepgram on AMEX (`Www.Deepgram.Com`) | **Epivo** | Henrik 2026-11-03. Deepgram on the SEB company card is Sonetel |
| `Google*ads7062786013` on AMEX | **Epivo** | Henrik 2026-11-03 |
| Backblaze | **Epivo** | Henrik 2026-11-03 |
| `Facebk *…` on AMEX (small) | **Epivo** | Henrik 2026-11-03. Meta on the SEB company card is Sonetel |
| Tre / HI3G (mobile, autogiro) | Sonetel — **partial claim** (see below) | confirmed 2026-06-22 |
| Periodens del av årsavgift (annual card fee) | not claimed | personal card fee |

If a vendor isn't in the list above, ask before booking.

---

## Partial claims — receipts mixing business + personal/family (e.g. Tre mobile)

Some receipts cover **both company and personal/family cost**. Claim only the business portion using the transaction's partial-claim fields — do NOT just reduce `amount`.

**Fields** (`transactions` table):
- `gross_amount` — full receipt amount (what was actually paid)
- `reimbursable_amount` — business portion (this is what gets exported/reimbursed)
- `personal_amount` — excluded portion (personal/family)
- `personal_reason` — required when `personal_amount > 0`

**Invariant** (enforced by `/transactions/<id>/update-partial-claim`): `gross_amount = reimbursable_amount + personal_amount` (±0.01).

**Export logic** (verified `libs/financial_core/services/export_service.py:3915`): the export uses `reimbursable_amount` when set, else falls back to `original_amount`/`amount`. So setting `reimbursable_amount` is what actually lowers the reimbursement.

### Tre / HI3G mobile — standing rule (confirmed 2026-06-22)

Henrik's Tre invoice is a **family plan**. The **5× "3Extra Användare" lines (129 kr/mån each = 645 SEK/invoice)** belong to **family members (Karima, Amir, Erik, Israa, Gabriel) — NOT a company cost**. Henrik's own mobile line, the bredband line, and the device installments (delbetalning) ARE claimed.

**Standing rule: subtract a flat 645 SEK from every Tre invoice** as `personal_amount`. So per invoice:
- `gross_amount` = invoice "Belopp att betala" (rounded amount paid via autogiro)
- `personal_amount` = 645.00
- `reimbursable_amount` = gross − 645
- `personal_reason` = `5x 3Extra Anvandare (129 SEK/mo) = family members subscriptions, not company cost`

Tre supplier_id = **2** ("3 Tre", account 6212, vat_type SE, origin `sweden`; receipt VAT set to 0, see below). Invoices arrive as `~/Downloads/faktura-*.pdf` (one per month, "Föregående månad" = bills the prior service month). The per-line breakdown is in the multi-page "Specifikation" / "Fakturaöversikt" pages.

#### MANDATORY: set receipt VAT or the export blocks (Swedish supplier)

Because Tre is `origin='sweden'`, the export's A3 blocker (`expense_batch_blockers._check_swedish_vat`) requires **every** receipt to carry `extracted_fields.vat`. And the SIE generator (`reverse_charge_sie.py`, Swedish branch) books **input VAT (2641) = the receipt's `extracted_fields.vat`**, with net expense = `reimbursable_amount − vat`. **Tre receipt VAT = 0 (BDO 2026-10-21, ACCOUNTING_RULES §2.1).** The Tre invoice is made out to Henrik privately
("Carl Henrik Thomé", private customer no. 12265687314), so Sonetel AB may not deduct its VAT, not even on the
business share. Set `vat` = 0 on every Tre receipt. The SIE then books the whole claimed amount to 6212 and writes
no 2641 line. Keep the invoice's own VAT in `invoice_total_vat` for reference only. (Until 2026-09 we deducted the
business-share VAT. BDO flagged it on 2026-10-21; earlier delivered batches were left as they are.)
If the subscription is ever moved to Sonetel AB's name, deduct the business-share VAT again.

Set it on each Tre receipt doc after attaching it:
```sql
UPDATE transaction_documents
SET extracted_fields = '{"vat": 0, "currency":"SEK", "supplier":"3 Tre",
    "invoice_total_incl_vat":<gross>, "invoice_total_vat":<full_vat>,
    "vat_basis":"invoice made out to Henrik privately - no VAT deduction (BDO 2026-10)"}'::json,
    updated_at = NOW()
WHERE transaction_id = <txn> AND document_type='receipt';
```

Verify zero blockers remain (mirrors the three checks) before telling Henrik it's exportable:
```sql
SELECT t.id, s.vendor_name FROM transactions t JOIN suppliers s ON s.id=t.supplier_id
WHERE t.batch_id=<N> AND t.expense_owner_id IS NOT NULL AND s.origin='sweden'
  AND COALESCE(t.vat_treatment,'')<>'no_swedish_vat'
  AND left(COALESCE(t.account_override,s.default_account_number,''),1) NOT IN ('1','2')
  AND EXISTS (SELECT 1 FROM transaction_documents d WHERE d.transaction_id=t.id
              AND (d.extracted_fields->>'vat') IS NULL
              AND (d.extracted_fields->'restaurant_vat_split') IS NULL);
```
(General rule: any `origin='sweden'` supplier receipt you attach needs `extracted_fields.vat`. Foreign/EU suppliers — Anthropic, OpenRouter, Cloudflare, Google, OpenAI, Bandwidth→1686 — are exempt: reverse-charge or balance-sheet routed.)

**Insert template** for a Tre line (direct DB write, same rationale as the FX override — portal needs Flask-Login):

```sql
INSERT INTO transactions (batch_id,transaction_date,description,amount,currency,status,supplier_id,expense_owner_id,
  gross_amount,reimbursable_amount,personal_amount,personal_reason,is_late_claim,late_claim_reason,comment,created_at,updated_at)
VALUES (<batch>,'<forfallodag>','Tre mobile - <Mon YYYY> (faktura <nr>)',<gross>,'SEK','matched',2,1,
  <gross>,<gross-645>,645.00,'5x 3Extra Anvandare (129 SEK/mo) = family members subscriptions, not company cost',
  <true if late>,'<reason>','Project: Sonetel | Tre mobile, family lines excluded',NOW(),NOW());
```

After inserting new transactions into a batch, **update the counter**: `UPDATE transaction_batches SET total_transactions=(SELECT count(*) FROM transactions WHERE batch_id=<N>), updated_at=NOW() WHERE id=<N>;` and write an `activity_logs` row (module `receipts-handling`, action `add_expense_transactions`).

---

## Attaching receipts — MANDATORY, do it directly (don't ask for the UI)

The expense export (`/expenses/export`) only includes transactions that have **at least one document attached** (`Transaction.documents.any()` — receipts.py:2767). A transaction with no document is invisible to the export. So every transaction you add MUST get its evidence attached:

- **Every line needs the actual vendor invoice/receipt** (`document_type='receipt'`) — e.g. Tre `faktura-*.pdf`, OpenRouter/Anthropic/Google/OpenAI/Cloudflare invoices. **The AMEX/bank statement is NOT sufficient underlag on its own** (standing rule, Henrik 2026-07-03: BDO can't book/audit a cost from a card statement — it needs the provider invoice). A line backed only by `bank_statement` is what BDO flags as "saknade underlag".
- **AMEX charges** → *additionally* attach the AMEX statement PDF (the SEK-debit evidence) as `document_type='bank_statement'`. The `YYYY-MM-02.pdf` statement covers charges dated 03 prior-month → 02 this-month; the `YYYY-(MM+1)-02.pdf` statement covers 03 this-month → 02 next-month. Attach whichever statement contains that charge's transaction date. This is the SEK proof, **not** a substitute for the vendor invoice.
- The one documented exception: BDO may waive the vendor invoice for a specific line if they already hold the bank record (e.g. Jennifer, May 2026: "Inbetalningen till Bandwith kan du bortse från, där har jag ju kontoutdraget"). Waivers come from BDO per-line — don't assume them.

The portal upload route is `@login_required`, so — exactly like the FX override — the only programmatic path is **direct storage placement + a `transaction_documents` row over SSH**. Don't ask Henrik to upload in the UI.

**Storage layout** (local backend; base = `settings.PERSISTENT_STORAGE_ROOT`, prod `/opt/accounting-app/storage` → symlink → `/mnt/financial-ops-storage/`). The download route does `storage.load(file_path)` = `base / file_path`, so `file_path` in the DB is **relative to the storage root**:

```
file_path (DB)  = receipts-handling/receipts/<batch_id>/<txn_id>/<hash8>_<secure_name>
physical file   = /mnt/financial-ops-storage/<file_path>
```
`<hash8>` = first 8 chars of the file's sha256; `<secure_name>` = Flask `secure_filename` (spaces→underscores; the AMEX/Tre filenames are already safe).

**Recipe**:
1. Locally: `shasum -a 256 <file>` (→ content_hash, hash8) and `stat -f%z <file>` (→ size).
2. `scp -i github-actions-deploy <files> ubuntu@44.194.218.109:/tmp/`
3. Place each (files are root-owned in `/mnt`; write as the `accounting` user):
   ```sh
   ssh ... ubuntu@44.194.218.109 'bash -s' <<'SH'
   ROOT=/mnt/financial-ops-storage/receipts-handling/receipts/<BATCH>
   sudo -u accounting mkdir -p "$ROOT/<TXN>"
   sudo -u accounting cp /tmp/<src> "$ROOT/<TXN>/<hash8>_<src>"
   SH
   ```
   (The same statement PDF can attach to several txns — each lives under its own `<TXN>/` dir; there is **no** unique constraint on `content_hash`.)
4. Insert one row per attachment (atomic BEGIN…COMMIT), then an `activity_logs` `upload_document` row:
   ```sql
   INSERT INTO transaction_documents
     (transaction_id,document_type,status,filename,content_hash,file_path,mime_type,file_size_bytes,
      uploaded_by_user_id,uploaded_at,created_at,updated_at)
   VALUES (<txn>,'<receipt|bank_statement>','matched','<name>','<sha256>',
      'receipts-handling/receipts/<batch>/<txn>/<hash8>_<name>','application/pdf',<size>,1,NOW(),NOW(),NOW());
   ```
   Required NOT-NULL cols: `document_type,status,filename,content_hash,file_path,uploaded_at,created_at,updated_at`. `status` ∈ {`matched`,`unassigned`,`locked`} — use `matched`. Leave `normalized_file_hash` NULL (that's the app's semantic-dedup key; skipping it just bypasses dedup).
5. Verify every txn in the batch has ≥1 doc:
   ```sql
   SELECT t.id, t.description, count(d.id) docs
   FROM transactions t LEFT JOIN transaction_documents d ON d.transaction_id=t.id
   WHERE t.batch_id=<N> GROUP BY t.id,t.description ORDER BY t.id;
   ```

---

## Workflow

### Step 1: Pull the AMEX statement(s)

The two statements that bracket the target month are typically in `~/Downloads/`:
- `YYYY-MM-02.pdf` (covers 03 prior month through 02 of this month)
- `YYYY-(MM+1)-02.pdf` (covers 03 of this month through 02 of next month)

Read both with the Read tool. Extract per-line: transaction date, vendor, foreign amount + currency, SEK amount.

### Step 2: Pull existing receipts in the batch

```
mcp__financial-ops__get_receipts(year_month="YYYY-MM", status="all")
```

The response is large — write to file and use `jq` to filter. Useful filters:

```sh
# Card 92000 charges only
jq -r '.receipts[] | select(.extracted_fields.payment_identifier == "2000" or .extracted_fields.payment_identifier == "92000")'

# Specific vendor
jq -r '.receipts[] | select((.extracted_fields.supplier // "") | test("Anthropic"; "i"))'
```

Receipt statuses (per `get_receipts` enum):
- **`locked`** — already in a submitted/closed bundle, do not touch
- **`matched`** — assigned to a transaction in the current batch
- **`unassigned`** — parsed and stored, but not yet assigned to a transaction (Henrik or admin must assign in portal)
- **`parsed`**, **`duplicate`**, **`rejected`** — self-explanatory

### Step 3: Build the cross-reference table

For each AMEX-92000 charge in the target month:

| Date | Vendor | Foreign | SEK | Receipt status | Project |
|---|---|---|---|---|---|

Match each AMEX line to a receipt by **(date ± 2 days, vendor name, currency+amount)**. The currency+amount match is the strongest signal (e.g. exactly 180 EUR is almost certainly the Claude.Ai monthly subscription).

### Step 4: Identify gaps

- Charges with no receipt → ask Henrik to forward the provider receipt
- Receipts with status `unassigned` but matching a charge → Henrik (or admin) assigns in the portal UI: **Admin > Receipts > assign to transaction**
- The card statement page itself needs to be attached as supporting documentation per transaction — that's done via the portal UI (no MCP tool for it currently)

### Step 5: Present the reconciliation

Show two tables to Henrik:
1. **Already in batch** — date, vendor, SEK, receipt id, status
2. **Still missing** — date, vendor, SEK, what's needed (receipt? assignment? card statement attachment?)

Separate by project (Sonetel vs Epivo) if relevant. Don't ask "is this Sonetel or Epivo?" up front — show the breakdown using the default patterns above, then ask Henrik to confirm only the uncertain ones.

### Step 6: Missing-underlag report — MANDATORY, always volunteer it

**Never wait to be asked "which charges are missing receipts?"** Every run of this skill ends with this report, unprompted, even when the answer is "none". It is the single question Henrik asks most often, and it is the thing BDO flags ("saknade underlag") when it goes unanswered.

A line backed **only** by `document_type='bank_statement'` is a line with no underlag. The AMEX statement proves the SEK debit; it does **not** prove what was bought. Run this after attaching documents:

```sql
SELECT t.id, t.transaction_date::date AS date, s.vendor_name,
       t.original_amount, t.original_currency, t.settled_amount_sek AS sek,
       count(d.id) FILTER (WHERE d.document_type='receipt')        AS vendor_receipt,
       count(d.id) FILTER (WHERE d.document_type='bank_statement') AS stmt
FROM transactions t
LEFT JOIN suppliers s ON s.id = t.supplier_id
LEFT JOIN transaction_documents d ON d.transaction_id = t.id
WHERE t.batch_id = <N>
GROUP BY t.id, t.transaction_date, s.vendor_name, t.original_amount, t.original_currency, t.settled_amount_sek
HAVING count(d.id) FILTER (WHERE d.document_type='receipt') = 0
ORDER BY t.transaction_date;
```

Present every zero-receipt row as a table — txn id, date, vendor, amount, SEK, and **where Henrik fetches the missing document** (vendor billing console, invoice email, etc.). Name the source concretely; "get the receipt" is not actionable.

Two documented exceptions — list them as *waived*, not as missing:
- **Voxbone/Bandwidth wallet top-ups** — no vendor receipt exists; AMEX statement alone is valid underlag (`feedback_voxbone_wallet_no_receipt`).
- **Per-line BDO waivers** — e.g. Jennifer, May 2026: "Inbetalningen till Bandwith kan du bortse från, där har jag ju kontoutdraget". Waivers come from BDO per line; never assume one.

Also report in the same block, because they are the same class of "this delivery is not complete yet" problem:
- **Expected inputs not present in `~/Downloads`** — e.g. the Tre invoice for the current service month.
- **Charges claimed but not yet AMEX-billed** — these export at Riksbanken rates and under-reimburse; recommend deferring (`feedback_claim_only_amex_billed`).

---

## Where things live

| Artifact | Location |
|---|---|
| AMEX statements (PDF) | `~/Downloads/YYYY-MM-02.pdf` (Henrik downloads monthly) |
| Portal receipts | Admin > Receipts in financial-ops portal (`http://44.194.218.109:8000/`) |
| Receipt list via API | MCP `mcp__financial-ops__get_receipts` |
| Expense bundle (ZIP) | `~/Downloads/Accountant_Bundle_YYYY-MM_*.zip` after batch is finalized |

---

## Don't do

- Don't re-convert FX from foreign amount using Riksbanken — use the SEK on the AMEX line.
- Don't book the AMEX annual card fee (`Periodens del av årsavgift`) as a business expense.
- Don't assume a vendor's project allocation — confirm with Henrik for any vendor not in the table above.
- Don't try to attach the AMEX statement PDF via MCP — there's no tool for it; portal UI only.
- Don't touch receipts in status `locked` — that batch is already submitted.
- Don't finish a run without the Step 6 missing-underlag report. Henrik should never have to ask "which charges are missing receipts?" — that question means the skill under-delivered.

---

## Related memory

- `feedback_expense_fx_use_card_sek` — SEK-from-card rule (this skill enforces it)
- `reference_expense_bundles` — where finished bundles end up
- `project_bdo_bandwidth_rule` — Jennifer's mandatory Bandwidth/Voxbone bookkeeping rule (applies after expense batch is closed, in BDO's books)
