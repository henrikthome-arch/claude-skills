---
name: infra
description: Manage all infrastructure for the Volos school project — Render (API backend), Cloudflare (DNS + Pages frontend), PostgreSQL database, and GitHub Actions workflows.
argument-hint: "[status | deploy | redeploy | env | logs | dns | purge]"
---

**DIRECTORY GUARD**: This skill is ONLY for the Volos school project. If the current working directory does NOT contain `international school in Volos`, STOP immediately and tell the user: "This skill is for the Volos school project only. Current directory: [cwd]". Do NOT proceed.

You help Henrik manage all infrastructure for the Volos school project (volos.school).

## Auth Setup

Always load keys like this — never use `$VAR` directly (trailing whitespace issue):

```bash
source ~/.zshrc
RENDER_KEY=$(printenv RENDER_API_KEY)
CF_TOKEN=$(printenv CLOUDFLARE_API_TOKEN)
CF_DNS=$(printenv CLOUDFLARE_DNS_TOKEN)
CF_ACCOUNT=$(printenv CLOUDFLARE_ACCOUNT_ID)
CF_ZONE=$(printenv CLOUDFLARE_ZONE_ID)
```

---

## Services Overview

| Layer | Provider | Service | URL |
|-------|----------|---------|-----|
| Frontend | Cloudflare Pages | volos-school | https://volos.school |
| Backend API | Render | volos-school-api | https://volos-school-api.onrender.com |
| Database | Render PostgreSQL | volos-school-db | Internal to Render |
| DNS | Cloudflare | volos.school zone | — |
| Email | Resend | volos.school domain | — |

**Render service ID:** `srv-d6h0teua2pns7388occg`
**Cloudflare Pages project:** `volos-school`

---

## Render Operations

### Check recent deploys

```bash
source ~/.zshrc && KEY=$(printenv RENDER_API_KEY) && \
curl -s -H "Authorization: Bearer ${KEY}" \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/deploys?limit=5" | \
python3 -c "
import sys,json
for d in json.load(sys.stdin):
    dep = d['deploy']
    print(dep['status'].ljust(20), dep['createdAt'][:19], dep.get('commit',{}).get('message','')[:60])
"
```

### Trigger a manual redeploy

```bash
source ~/.zshrc && KEY=$(printenv RENDER_API_KEY) && \
curl -s -X POST -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" -d '{}' \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/deploys" | \
python3 -c "import sys,json; d=json.load(sys.stdin)['deploy']; print('Triggered:', d['id'], d['status'])"
```

### List env vars

```bash
source ~/.zshrc && KEY=$(printenv RENDER_API_KEY) && \
curl -s -H "Authorization: Bearer ${KEY}" \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/env-vars" | \
python3 -c "
import sys,json
for e in json.load(sys.stdin):
    ev = e['envVar']
    val = ev.get('value','')
    display = val[:30] + '...' if len(val) > 30 else val
    print(ev['key'].ljust(28), display)
"
```

### Update a single env var (preserving all others)

```bash
source ~/.zshrc && KEY=$(printenv RENDER_API_KEY) && \
EXISTING=$(curl -s -H "Authorization: Bearer ${KEY}" \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/env-vars") && \
UPDATED=$(echo "$EXISTING" | jq --arg k "VAR_NAME" --arg v "new_value" \
  '[.[] | {key: .envVar.key, value: (if .envVar.key == $k then $v else .envVar.value end)}]') && \
curl -s -X PUT -H "Authorization: Bearer ${KEY}" -H "Content-Type: application/json" \
  -d "$UPDATED" \
  "https://api.render.com/v1/services/srv-d6h0teua2pns7388occg/env-vars"
```

### Health check

```bash
curl -s https://volos-school-api.onrender.com/health
```

### Render deploy statuses

| Status | Meaning |
|--------|---------|
| `live` | Running and serving traffic |
| `build_in_progress` | Building |
| `update_in_progress` | Deploying |
| `deactivated` | Superseded by newer deploy |
| `build_failed` | Build error — check Render dashboard logs |

---

## Cloudflare Operations

### Check Pages deployments (frontend)

```bash
source ~/.zshrc && CF_TOKEN=$(printenv CLOUDFLARE_API_TOKEN) && CF_ACCOUNT=$(printenv CLOUDFLARE_ACCOUNT_ID) && \
curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT}/pages/projects/volos-school/deployments?per_page=5" | \
python3 -c "
import sys,json
for d in json.load(sys.stdin)['result']:
    print(d['latest_stage']['status'].ljust(12), d['created_on'][:19], d.get('deployment_trigger',{}).get('metadata',{}).get('commit_message','')[:60])
"
```

### Purge Cloudflare cache (entire zone)

```bash
source ~/.zshrc && CF_TOKEN=$(printenv CLOUDFLARE_API_TOKEN) && CF_ZONE=$(printenv CLOUDFLARE_ZONE_ID) && \
curl -s -X POST -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" \
  -d '{"purge_everything":true}' \
  "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/purge_cache" | \
python3 -c "import sys,json; r=json.load(sys.stdin); print('Cache purged:', r['success'])"
```

### List DNS records

```bash
source ~/.zshrc && CF_TOKEN=$(printenv CLOUDFLARE_API_TOKEN) && CF_ZONE=$(printenv CLOUDFLARE_ZONE_ID) && \
curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records" | \
python3 -c "
import sys,json
for r in json.load(sys.stdin)['result']:
    print(r['type'].ljust(6), r['name'].ljust(30), r['content'][:60])
"
```

---

## GitHub Actions

Workflows in `henrikthome-arch/volos-school`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `sync-render-env.yml` | Push to main + manual | Syncs `RESEND_API_KEY` from GitHub secrets → Render env vars |
| Cloudflare Pages deploy | Push to main | Builds Astro site, deploys to Cloudflare Pages |

### Check recent workflow runs

```bash
PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH" \
  gh -R henrikthome-arch/volos-school run list --limit 8
```

### Trigger sync workflow manually

```bash
PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH" \
  gh -R henrikthome-arch/volos-school workflow run sync-render-env.yml
```

---

## Database

PostgreSQL managed by Render — `volos-school-db` (Basic-256mb, pg16).
Connection string is in Render env vars as `DATABASE_URL`.
Migrations run automatically on deploy via `flask db upgrade`.
For emergency manual access: Render dashboard → Shell tab.

---

## Notes

- Both Render and Cloudflare Pages auto-deploy on push to `main`
- `RESEND_API_KEY` is injected into Render by `sync-render-env.yml` — never set manually
- Render dashboard: https://dashboard.render.com/web/srv-d6h0teua2pns7388occg
- Cloudflare dashboard: https://dash.cloudflare.com

$ARGUMENTS
