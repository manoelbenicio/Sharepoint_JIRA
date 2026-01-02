# TD-010: Secrets/config hygiene (produção)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Ensure production runs with:

- no secrets committed to repo
- Power Platform using **connection references + environment variables**
- Azure Function using app settings (not hardcoded)
- documented rotation and rollback procedures

## Scope

- Power Automate flows (Flow1..Flow4): use solution packaging with environment variables/connection references.
- Azure Function: app settings in Function App configuration.

## Change plan (step-by-step)

1. Inventory config inputs:
   - SiteUrl, List names/IDs, Teams targets, Azure Function base URL, etc.
2. Power Platform:
   - Move hardcoded values to Environment Variables
   - Replace connectors with Connection References
3. Azure:
   - Confirm required app settings exist (documented)
   - Confirm no secrets are stored in flow definitions
4. Rotation:
   - Document how to rotate: credentials, connection refs, app settings
5. Rollback:
   - Export previous solution + provide re-import instructions

## Validation

- Export solution and verify placeholders exist (no tenant IDs, no secrets).
- Smoke test (business hours): run Flow4 import + Flow2 single canary.

## Rollback

- Re-import last known-good solution package and restore previous app settings snapshot.

## Evidence to attach (required)

- Solution export showing env vars/connection refs used
- App settings snapshot (redacted if needed)

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

