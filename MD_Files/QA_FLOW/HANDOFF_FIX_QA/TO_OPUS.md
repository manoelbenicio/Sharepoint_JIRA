# Handoff to Agent Opus 4.5 (Execution + QA)

## Rules (must follow)

- **Do not run QA until ALL TDs are completed + peer-reviewed** (no mixing implementation and QA).
- **Recipient safety (hard constraint)**: only `mbenicios@minsait.com` may receive Teams messages during validation.
  - If there is any possibility of another recipient receiving messages: **BLOCKED (business hours validation required)**.
- **PowerShell CLI (PnP / tenant scripting)** tasks are **Opus-only**.
- Record everything in `CHECKPOINT.md`:
  - **Execution Log** (what was done + evidence)
  - **Peer Review Log** (review findings + evidence)

## What Opus must execute (owned by Opus)

Execute in this order (from `CHECKPOINT.md`):

1. **TD-003** — Ops views (Level 1)
   - Runbook: `ops/runbooks/TD-003-ops-views-level1.md`
   - Script: `ops/scripts/powershell/ops-views.ps1`
2. **TD-006** — Queue dedupe + uniqueness
   - Runbook: `ops/runbooks/TD-006-queue-dedupe-uniqueness.md`
   - Script: `ops/scripts/powershell/queue-dedupe.ps1`
3. **TD-008** — Queue list cutover (blue/green)
   - Runbook: `ops/runbooks/TD-008-queue-list-cutover-blue-green.md`
   - Scripts: `ops/scripts/powershell/queue-cutover.ps1`, `ops/scripts/powershell/queue-rollback.ps1`
   - Repo audit (double-check): `tools/audit_queue_list_references.py`

## QA execution (Opus-only)

Only after all TDs are completed + peer-reviewed:

- QA Plan: `QA_PRODUCTION_TEST_PLAN.md`

## Helpful tooling available to Opus

- Microsoft 365 MCP Server (Knowledge / Troubleshoot / Docs)
- Docker MCP Server (automation possibilities)

Use them for:
- confirming OData filter syntax for SharePoint choice fields
- validating Power Automate connector behavior
- troubleshooting Teams card delivery and “Post and wait for response” nuances

