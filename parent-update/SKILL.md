---
name: parent-update
description: Send a mass email update to all registered families of the Volos International AI School. Use when Henrik wants to communicate news, status, or invitations to the ~29+ families who have registered interest at volos.school. Handles drafting the body, publishing it to the public updates page, and sending the email broadcast via Resend with deliverability safeguards (throttling, List-Unsubscribe, HTML+text, audit log). Distinct from /pm-school (status/PM reporting) and /infra (hosting/DNS).
argument-hint: "[draft <topic> | dry-run <slug> | test <slug> <email> | send <slug>]"
---

# Parent update — mass email to registered families

You are sending a written update from Henrik (founder) to all families registered at volos.school. The audience is parents who have indicated interest in enrolling their child in the future school. Tone is honest, plainspoken, founder-voice. They have made a quiet commitment by registering; this email honors that.

## Directory guard

Confirm the working directory contains `international school in Volos`. If not, stop and tell the user to switch.

## How sending works (one-paragraph summary)

A generic Python script at `code/backend/scripts/send_parent_update.py` loads a campaign config from `code/backend/scripts/parent-updates/<slug>.json` and sends one personalized email per registered family via Resend directly. Every recipient gets the same template: `Dear {first_name}`, body with `{n_families}` / `{n_children}` substituted from live counts, primary CTA pointing to `https://volos.school/account`. Audit log lives at `docs/07_MARKETING/send-logs/<slug>.json` — **outside** the `code/` git repo (recipient PII must not enter git). Resume is idempotent per recipient *for the same body* — if the body changes, move the audit log aside before re-running.

The very first campaign that built this pipeline is documented in `docs/08_CHANGE_REQUESTS/CR-20260514-001_Founder_Update_May_2026.md` — read it once for the full design rationale (deliverability decisions, why `/account` CTA instead of reply tokens, why direct Resend for everyone).

## Workflow

When invoked, follow this workflow strictly. Do not auto-execute send actions; gate each one on explicit user go.

### Step 1 — Understand the update

Ask the user what the update is about. Then:
- Pull current state for accuracy:
  - `GET /api/admin/leads` (lead count, ages, recent additions)
  - `GET /api/admin/children/summary` (total children, by level)
  - `git log -20 changelog/CHANGELOG.md` (recent project decisions)
- Check `docs/05_OPERATIONS/PM_LOG.md` if it exists for any open follow-ups parents should hear about.
- Read recent CRs in `docs/08_CHANGE_REQUESTS/` for anything that should/shouldn't be mentioned.

### Step 2 — Draft the body (tone rules)

- **First-person founder voice.** Henrik writes; do not use "we" for things that are really just Henrik.
- **Honest about pace.** If the project has slowed, say so. Parents deciding for 2026/2028 will respect honesty over polish.
- **Three to five short sections with bold leads.** No long paragraphs. Use `<strong>` headings.
- **End with one line acknowledging Greek speakers:** "You are welcome to write in Greek — I read everything via translation." Mandatory until `Lead.locale` ships.
- **Primary CTA = sign in to your account at volos.school/account.** Not "reply to this email." Reply tokens would expire mid-summer; `/account` works forever.

**Hard tone constraints from past iterations:**

- **Mayor / municipality:** Henrik holds an arm's-length stance on Mayor Mpeos (memory: `project_mayor_mpeos_stance.md`). Public mentions of "cooperation with the city" position the school toward the Mpeos administration in writing. Use *"made initial contact with the City of Volos to explore what support and assistance may be available"* — exploration, not partnership. Never name officials. Never commit to outcomes before they exist.
- **Sister projects (Sonetel, Epivo, etc.):** Mentioning them is fine if relevant to the message. Do **not** turn the email into a tour of Henrik's other companies — for a parent audience deciding about their child's school, "what is this guy actually building" is a brand risk. Mention only if it bears directly on the school's pace or capabilities.
- **No marketing-speak.** No "exciting news", "thrilled to announce", exclamation marks in subject lines, all-caps. Subject line under 50 chars so it doesn't truncate on mobile.

### Step 3 — Follow the CR process for non-trivial updates

For substantive updates (anything beyond a one-line announcement), follow the project's standard process per `CLAUDE.md`:

1. Write a CR in `docs/08_CHANGE_REQUESTS/CR-YYYYMMDD-NNN_<Topic>.md`. Use CR-20260514-001 as the template — it has the deliverability sections you can carry over verbatim.
2. Spawn a Plan subagent to review the CR.
3. Incorporate review feedback (especially: tone for parent audience, conflicts with arm's-length-on-mayor stance, accuracy of any counts/dates).
4. User approves (or pre-authorizes via "follow the process").
5. Implement: create the campaign config + draft the site update body (see below).
6. Changelog entry under `[UNRELEASED]`.
7. Mark CR Implemented once site is published and bulk send is reconciled.

For trivial updates (single-paragraph announcement), skip the CR and just write the campaign config + changelog entry.

### Step 4 — Create the campaign config

Write `code/backend/scripts/parent-updates/<YYYY-MM-slug>.json` with this schema:

```json
{
  "campaign_slug": "<YYYY-MM-slug>",
  "send_date": "YYYY-MM-DD",
  "subject": "<short subject, <50 chars>",
  "audience": "all_leads",
  "include_live_counts": true,
  "body_html": "<p>Dear {first_name},</p>...",
  "body_text": "Dear {first_name},..."
}
```

**Optional fields:**
- `throttle_seconds` (number, default 60) — pause between sends. **60s is the project default** to avoid burst patterns that look bulk to receiver-side spam heuristics. Lower it (e.g. 5–10s) only for genuinely time-sensitive sends.
- `bcc` (string or array) — BCC every send to this address. Standard practice for parent-update campaigns is to BCC `henrik.thome@gmail.com` so he receives a real-time copy of each parent email as it goes out (verifies rendering, personalization, headers per recipient).

**Placeholders supported in body_html / body_text:**
- `{first_name}` — extracted from the lead's stored name via `clean_first_name()` (strips Dr/Mr/Mrs/Ms/Prof/Mx; title-cases ALL-CAPS)
- `{n_families}` — live count from `GET /api/admin/leads`
- `{n_children}` — live count from `GET /api/admin/children/summary` (total_children)
- `{btn_style}` — pre-baked CTA button CSS (HTML only)

The script wraps `body_html` in a viewport-safe outer `<body>` and appends the standard footer; **do not** repeat the wrapper or footer in the config.

### Step 5 — Publish the site update (operator-gated)

Publish the same text on the public updates page (`https://volos.school/updates`).

**Body format:** markdown is rendered on the site — use `**bold**` for section leads, `[link](url)` for links, `_italic_` for the Greek-welcome line, `\n\n` for paragraph breaks. Max 10,000 chars. Strip the email's `Dear {first_name}` and any HTML tags; the site post does not have a personalized greeting.

**API call** (heredoc pattern keeps newlines and quotes intact):

```bash
ADMIN_KEY=$(printenv VOLOS_ADMIN_API_KEY)
curl -sS -X POST \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d @- \
  https://volos-school-api.onrender.com/api/admin/updates <<'JSON'
{
  "title": "An update from Henrik — May 2026",
  "body": "A short update on where the project stands.\n\n**Interest keeps growing.** 29 families with 30 children have now registered their interest in the school...\n\n**Outreach to the city.** I have made initial contact with the City of Volos...\n\n_You are welcome to write in Greek — I read everything via translation._\n\n— Henrik Thomé, Founder",
  "is_public": true,
  "publish": true
}
JSON
```

`is_public: true` makes it visible on the public updates page (no auth required to read). `is_public: false` makes it authenticated-parents-only. `publish: true` sets `published_at` to now; omit (or `false`) to save a draft.

**Worked example:** the May 2026 founder update was published this way and became update id 8 (visible in `GET /api/updates`). Use the same field shape for future campaigns — just swap title + body.

**Get user go before firing this curl.** Site updates are public and visible to anyone signed in to the parent portal (or to anyone at all if `is_public: true`). Whether to publish *before* or *after* the email send is a per-campaign call:
- *Before* lets the email reference "see the latest at volos.school/updates" (good for engagement).
- *After* keeps the email the first place parents hear the news (good for the "founder writing directly to me" feeling).
- The May 2026 campaign published in parallel — site and email both went live mid-day on 2026-05-14.

### Step 6 — Test send (mandatory)

Always do an inbox QA before the bulk send. Run:

```bash
python3 code/backend/scripts/send_parent_update.py <slug> --send-to henrik.thome@gmail.com
```

Then ask Henrik to:
1. Open the email in Gmail and check rendering (mobile + desktop)
2. Click the `/account` CTA — confirms it lands on the portal sign-in
3. View → Show original → confirm `SPF: PASS`, `DKIM: PASS`, `DMARC: PASS`, and that `List-Unsubscribe` + `List-Unsubscribe-Post` headers are present
4. Verify subject line isn't truncated on mobile

If `RESEND_API_KEY` isn't in the local env, pull it from Render via the admin API:

```bash
RENDER_KEY=$(printenv RENDER_API_KEY)
export RESEND_API_KEY=$(curl -sS -H "Authorization: Bearer $RENDER_KEY" \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/env-vars" | \
  python3 -c "import json,sys; [print(e['envVar']['value'],end='') for e in json.load(sys.stdin) if e['envVar']['key']=='RESEND_API_KEY']")
```

### Step 7 — Check Resend quota before bulk send

Open https://resend.com/settings/usage. On the Free plan:
- **Transactional Daily:** 100/day — confirm `(100 - used) ≥ recipient_count`
- **Transactional Monthly:** 3,000/month — confirm same

If quotas are tight, upgrade Resend or split the send across days (the script's idempotent resume handles a re-run the next day).

### Step 8 — Bulk send (operator-gated, phased)

Best time: **Tuesday or Wednesday, 09:00–11:00 Athens time** (best inbox engagement window).

**For the first campaign on a new template/audience, use phased rollout** — send a canary, verify via BCC + dashboard, then expand. Recommended phases for ~30 recipients:

`--limit N` sends up to N *new* recipients in this invocation (not "ensure N total sent so far"). The audit log makes each phase idempotent. Recommended phases for ~30 recipients:

| Phase | Command | New sends this run | What to verify before continuing |
|---|---|---|---|
| Canary | `python3 code/backend/scripts/send_parent_update.py <slug> --limit 1` | 1 | BCC arrives, looks right, no bounce/complaint in Resend dashboard after a few minutes |
| Expand | `python3 code/backend/scripts/send_parent_update.py <slug> --limit 3` | 3 (total 4) | Spot-check personalization on different first-name shapes (Greek names, all-caps cases) |
| Expand | `python3 code/backend/scripts/send_parent_update.py <slug> --limit 10` | 10 (total 14) | Watch for bounces/complaints accumulating |
| Finish | `python3 code/backend/scripts/send_parent_update.py <slug>` | all remaining | Final summary in audit log |

For subsequent campaigns where the template is well-validated, skip the phasing and just run unflagged.

Script prints recipient summary (including throttle, ETA, batch size, BCC if set), asks for `yes` to proceed, then sends one email per `throttle_seconds` (default 60s), writing the audit log after each send. Keep the terminal open or run under tmux/screen so the process survives a disconnect.

### Step 9 — 24h reconciliation

**Three verification surfaces:**
1. **Local audit log** at `docs/07_MARKETING/send-logs/<slug>.json` — the script's view (what was sent, with Resend message IDs).
2. **BCC inbox** at `henrik.thome@gmail.com` (or whatever `bcc` is set to) — one copy of each parent email lands here in real time.
3. **Resend dashboard** at https://resend.com/emails — Resend's view of delivery state (delivered / bounced / complained), filterable by date and From address.

Note: the production Resend API key (`RESEND_API_KEY` on Render) is restricted to send-only and cannot read email status programmatically. If we need scripted reconciliation in future, request a full-access read key from Resend.

Within 24h after the bulk send:
- Filter the Resend dashboard by `From: noreply@volos.school` and the send date.
- Update audit log entries for any bounced recipient: change `status: sent` to `status: bounced`, add a `bounced_at` field.
- If complaint rate >0, dig into which recipient and why before the next campaign.

### Step 10 — Wrap up

- Update changelog: `## [UNRELEASED] → ### Added → (CR-YYYYMMDD-NNN) Parent update <topic> — sent to N families, audit log at docs/07_MARKETING/send-logs/<slug>.json`
- Mark the CR as Implemented
- Note the campaign in PM_LOG.md if pm-school is in use, under "Contacts & Follow-ups"

## Hard rules

1. **Never auto-execute the bulk send.** Always require explicit "yes" / "send" from the user. The script's interactive prompt enforces this; do not bypass it programmatically.
2. **Audit log path must be outside `code/`.** The script enforces this via `REPO_ROOT/docs/07_MARKETING/send-logs/`. If you ever change the path, double-check it's not inside the git repo — recipient PII (email + name) in git is a GDPR-flavored problem.
3. **No new recipients invented.** The script pulls live from `GET /api/admin/leads`. Never hardcode a recipient list, never email someone who isn't a registered lead.
4. **Idempotent resume only applies to the same body.** If the body changes mid-campaign (typo fix), move the audit log aside (`mv <slug>.json <slug>.json.bak`) before re-running, or recipients who already got the typo'd version will be silently skipped.
5. **No reply-token fields in the email.** This campaign style uses `/account` CTA. The `reply_to` header points at henrik.thome@gmail.com so direct replies still land somewhere monitored, but the visible CTA is the portal sign-in.

## Files and references

- Script: `code/backend/scripts/send_parent_update.py`
- Campaign configs: `code/backend/scripts/parent-updates/*.json`
- Audit logs: `docs/07_MARKETING/send-logs/*.json` (outside git repo)
- Reference CR: `docs/08_CHANGE_REQUESTS/CR-20260514-001_Founder_Update_May_2026.md`
- Backend admin endpoints used: `code/backend/app/routes/admin.py` (`list_leads`, `children_summary`, `create_update`)
- Resend account: henrik.thome@gmail.com — dashboard at https://resend.com/settings/usage
- Resend Render env var: `RESEND_API_KEY` on service `srv-d6h0teua2pns7388occg`
- From address: `International School of Volos <noreply@volos.school>` (verified domain, SPF/DKIM/DMARC via Resend)
- Reply-To: `henrik.thome@gmail.com`

## When NOT to use this skill

- Sending a 1:1 message to a specific parent — use the admin parents view in the portal, or the per-user message endpoint `POST /api/admin/users/<id>/messages`. That path uses the reply-token system and is the right channel for individual conversations.
- Sending to a *subset* of registered families (e.g. only families with primary-age children). Today the script audience is "all_leads". If subset support is needed, extend the script — don't filter the recipient list by hand.
- Anything to non-registered prospects, partners, suppliers, or officials. This skill is for families who registered interest on volos.school and have an implicit opt-in. Other audiences need a different channel.
