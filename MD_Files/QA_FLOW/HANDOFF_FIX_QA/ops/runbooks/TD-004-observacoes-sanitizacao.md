# TD-004: Observações sem HTML (sanitização + backfill)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Guarantee `Observacoes` is stored/displayed as **plain text** (no HTML tags/entities) across:

- `Ofertas_Pipeline.Observacoes` (source)
- Teams card prefill
- `StatusReports_Historico.Observacoes` (downstream)

## Preconditions / Inputs

- Azure Function is deployed and reachable.
- You have permission to change Function App settings.
- You have real JIRA Observation samples containing HTML (`<div>`, `<br>`, `&gt;`, etc).
- You can reimport via Flow4 (CSV → Function → SharePoint upsert).

## Change plan (step-by-step)

1. In Azure Function App Configuration, set:
   - `IMPORT_STRIP_HTML_OBSERVACOES=true`
2. Restart the Function App.
3. Reimport offers via Flow4 (use the latest CSV).

## Validation (Level 1 first)

1. In `Ofertas_Pipeline`, open at least 10 offers with known HTML-y observations:
   - Confirm field contains only text (no `<`/`>` tags; no raw `&gt;` entities).
2. In Teams card (next send), confirm Observações prefill is plain text.
3. Submit a card and confirm in `StatusReports_Historico.Observacoes` it remains plain text.

## Rollback (100% automated)

1. Set `IMPORT_STRIP_HTML_OBSERVACOES=false`
2. Restart the Function App

Rollback does not delete cleaned data already written; it only stops further sanitization.

## Evidence to attach (required)

- Screenshot (or exported settings) showing the flag enabled
- Before/after example of the same observation (raw vs cleaned)
- Sample list of 10 JiraKeys validated

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

