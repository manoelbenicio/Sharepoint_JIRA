# TD-010 (part): Azure Function App Settings for test baseline

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No (Azure Portal/CLI acceptable)

## Goal

Set the Azure Function app settings required to:

- safely purge lists for QA baseline (LAB-only)
- sanitize Observações (no HTML)
- enrich AssigneeEmail

## Required settings (recommended)

### LAB purge (pre-QA reset)

- `ENVIRONMENT=qa` (or any value not `prod/production`)
- `LAB_PURGE_ENABLED=true`
- `LAB_PURGE_ADMIN_TOKEN=<secret>`
- `LAB_PURGE_CONFIRMATION=<secret>`
- `LAB_PURGE_ALLOWED_LIST_IDS=<comma-separated allowlist>`
  - Include:
    - `6db5a12d-595d-4a1a-aca1-035837613815` (Ofertas_Pipeline)
    - `f58b3d23-5750-4b29-b30f-a7b5421cdd80` (StatusReports_Historico)
    - `172d7d29-5a3c-4608-b4ea-b5b027ef5ac0` (Atualizacoes_Semanais)
    - Queue list id (if you want purge to clear queue too)

### Data quality

- `IMPORT_STRIP_HTML_OBSERVACOES=true`

### Assignee enrichment

- `IMPORT_ENRICH_ASSIGNEE=true`
- `SP_SITE_URL=https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA`

## Validation

- Call `POST /api/lab/purge-lists` first with `dry_run=true`.
- Reimport via Flow4 and validate Level 1 fields in SharePoint.

