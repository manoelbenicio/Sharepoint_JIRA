# TD-001: Populate `AssigneeEmail` (backfill)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Ensure `Ofertas_Pipeline.AssigneeEmail` is populated and stable so flows can reliably address Teams recipients by email.

## Background (what is true)

- JIRA “Assignee” commonly comes as a **login** (e.g., `mbenicios`), not an email.
- The Azure Function `/api/import-jira` can enrich assignee data **when enabled**:
  - `IMPORT_ENRICH_ASSIGNEE=true`
  - It maps `Assignee(login)` → `AssigneeEmail` using the `ARQs_Teams.Login` mapping list.

## Preconditions / Inputs

- `ARQs_Teams` list includes:
  - `Login` (text, e.g., `mbenicios`)
  - an email field (e.g., `Email`/`E-mail`/`field_3` depending on list schema)
- Azure Function is deployed and reachable
- You have permission to change Function App settings
- You have a recent JIRA CSV ready for re-import (or can reprocess the latest)

## Change plan (step-by-step)

1. In Azure Function App Configuration, set:
   - `IMPORT_ENRICH_ASSIGNEE=true`
   - Ensure `SP_SITE_URL` is correct for the target tenant/site
2. Restart the Function App (to apply settings).
3. Run Flow4 (import) to reimport offers so the function upserts items in `Ofertas_Pipeline` with `AssigneeEmail`.

## Validation (Level 1 first)

In SharePoint list `Ofertas_Pipeline`:

1. Filter for a handful of items where `Assignee` is populated.
2. Confirm `AssigneeEmail` is populated and matches a real user email.
3. Validate at least 15 samples (or 100% if small dataset).

## Rollback (100% automated)

1. Set `IMPORT_ENRICH_ASSIGNEE=false`
2. Restart Function App

Rollback does not delete data already written; it only stops further enrichment.

## Evidence to attach (required)

- Screenshot (or exported settings) showing `IMPORT_ENRICH_ASSIGNEE=true`
- Before/after counts: `AssigneeEmail` filled vs empty (sample size and time)
- At least 3 example items showing `Assignee` + `AssigneeEmail`

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

