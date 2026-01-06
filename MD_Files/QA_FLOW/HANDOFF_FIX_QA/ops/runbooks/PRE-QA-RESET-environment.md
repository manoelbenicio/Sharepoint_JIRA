# PRE-QA: Reset environment + reimport (clean test baseline)

## Ownership

- **Executed by**: Agent Opus 4.5
- **Peer reviewed by**: Agent GPT-5.2 Codex
- **PowerShell CLI required?**: Yes → Opus-only

## Goal

Before any QA, reset the tenant test data to a **known clean baseline**:

1) purge lists (delete all items) using Azure Function admin endpoint  
2) reimport a fresh JIRA CSV via Flow4 trigger (SharePoint `JIRA_Imports` folder)

## Non-negotiables

- QA starts only after **all TDs** are fixed + peer reviewed.
- **Recipient safety (hard constraint)**: the only allowed Teams recipient during any validation is `mbenicios@minsait.com`.
- If purge endpoint is not enabled/safe in this environment: mark **BLOCKED (business hours validation required)**.

## Inputs

- CSV file (already in bundle):
  - `HANDOFF_FIX_QA/JIRA PBI (JIRA Indra) 2025-12-30T03_17_34-0300.csv`
- SharePoint site:
  - `https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA`
- Library/folder for Flow4 trigger:
  - `Documentos compartilhados/JIRA_Imports` (a.k.a. `/Shared Documents/JIRA_Imports`)

## Step 1 — Enable Flow4 safely (no channel flood)

Flow4 must not post to channels during QA prep. Use the patched artifact:

- `HANDOFF_FIX_QA/dist_zips/flow4.zip`

If any Teams notification in Flow4 is not restricted, do **not** proceed outside business hours.

## Step 2 — Purge lists (Azure Function)

### What to purge (minimum)

- `Ofertas_Pipeline`
- `StatusReports_Historico`
- `Atualizacoes_Semanais`
- Queue list (`StatusReports_Queue`) if allowed (recommended)

### Endpoint

Azure Function route exists:

- `POST /api/lab/purge-lists`

### Required safety controls (all required)

From the function code:

- `ENVIRONMENT` must NOT be `prod/production`
- `LAB_PURGE_ENABLED=true`
- Header `x-admin-token` must match `LAB_PURGE_ADMIN_TOKEN`
- Body `confirm` must match `LAB_PURGE_CONFIRMATION`
- List must be allowed by `LAB_PURGE_ALLOWED_LIST_IDS` (or default allowlist)

### Execution

Use script:

- `ops/scripts/powershell/preqa-reset-and-import.ps1`

Run first with `-DryRun $true` and review the report, then run with `-DryRun $false`.

## Step 3 — Upload CSV to trigger Flow4

Upload the CSV into the folder that triggers Flow4:

- `Documentos compartilhados/JIRA_Imports`

Use the same script (`preqa-reset-and-import.ps1`) or upload via browser.

## Validation (Level 1 only)

1) After purge:
- Lists have 0 items (or expected baseline minimal items only).

2) After reimport:
- `Ofertas_Pipeline` is populated with current offers.
- `Observacoes` looks clean (plain text) if `IMPORT_STRIP_HTML_OBSERVACOES=true` is enabled.
- `AssigneeEmail` populated if `IMPORT_ENRICH_ASSIGNEE=true` is enabled.

## Rollback

- If purge caused unexpected issues:
  - stop and restore from backups (Opus should capture CSV/JSON exports before deletion)
  - do not proceed to QA

## Logs (append-only)

- Append execution evidence to `CHECKPOINT.md` → **Execution Log**
- Append peer review findings to `CHECKPOINT.md` → **Peer Review Log**

