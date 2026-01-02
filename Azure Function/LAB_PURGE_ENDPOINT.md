# LAB Purge Endpoint (Admin‑only)

This Azure Function adds a **LAB-only** admin endpoint to purge SharePoint list data for testing without affecting PROD.

## Endpoint

- `POST /api/lab/purge-lists?code=<FUNCTION_KEY>`

## Required App Settings (Azure Function)

SharePoint (Graph App Registration):

- `SP_TENANT_ID`
- `SP_CLIENT_ID`
- `SP_CLIENT_SECRET`
- `SP_SITE_URL` (ex: `https://indra365.sharepoint.com/sites/<site>`) **or** `SP_SITE_ID`

Safety:

- `ENVIRONMENT` = `LAB` (must NOT be `prod`/`production`)
- `LAB_PURGE_ENABLED` = `true`
- `LAB_PURGE_ADMIN_TOKEN` = random secret value (sent in header `x-admin-token`)
- `LAB_PURGE_CONFIRMATION` = confirmation string required in the request body
- `LAB_PURGE_MAX_ITEMS_PER_LIST` = safety limit (default 500)
- `LAB_PURGE_ALLOWED_LIST_IDS` = comma-separated GUID allowlist (recommended per environment)

## Request

Headers:

- `x-admin-token: <LAB_PURGE_ADMIN_TOKEN>`

Body:

```json
{
  "confirm": "YOUR_CONFIRMATION_STRING",
  "dry_run": true,
  "lists": ["Ofertas_Pipeline", "Atualizacoes_Semanais", "StatusReports_Historico"],
  "max_items_per_list": 200
}
```

Notes:

- `dry_run=true` returns how many items would be deleted.
- Set `dry_run=false` to actually delete.

## Permissions

The App Registration used by `SP_CLIENT_ID` must have sufficient Graph permissions to enumerate and delete list items in the target site (prefer least privilege, e.g. `Sites.Selected` + granted to the site).

