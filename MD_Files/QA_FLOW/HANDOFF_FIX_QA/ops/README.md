# Ops (Runbooks + Scripts)

This folder contains **production-safe runbooks** and scripts for executing technical debt (TD) items with **explicit agent ownership** and **mandatory peer review**.

## Golden rules

- If a runbook says **“Executed by Agent Opus 4.5”**, then **Agent GPT-5.2 Codex must not run it** unless the user explicitly requests it in writing.
- Any task requiring **PowerShell CLI (PnP / tenant scripting)** is **Opus-only**.
- **Recipient safety (hard constraint)**: during QA/tests, the only allowed Teams recipient is `mbenicios@minsait.com`. If there is any possibility of another recipient receiving messages, the activity must be marked **BLOCKED (business hours validation required)**.
- Every execution must append evidence to the project **Execution Log** (see `CHECKPOINT.md`).
- Every execution must be **peer-reviewed by the other agent** and recorded in the **Peer Review Log**.

## Runbooks

- `ops/runbooks/TD-001-assigneeemail-backfill.md`
- `ops/runbooks/TD-002-flow2-flood-control.md`
- `ops/runbooks/TD-003-ops-views-level1.md`
- `ops/runbooks/TD-004-observacoes-sanitizacao.md`
- `ops/runbooks/TD-005-flow2-state-machine.md`
- `ops/runbooks/TD-006-queue-dedupe-uniqueness.md`
- `ops/runbooks/TD-007-versao-report.md`
- `ops/runbooks/TD-008-queue-list-cutover-blue-green.md`
- `ops/runbooks/TD-009-single-source-template.md`
- `ops/runbooks/TD-010-secrets-config-hygiene.md`
- `ops/runbooks/TD-011-flow1-performance-refactor.md`

## Scripts

### PowerShell (PnP) — Opus-only

- `ops/scripts/powershell/ops-views.ps1`
- `ops/scripts/powershell/queue-dedupe.ps1`
- `ops/scripts/powershell/queue-cutover.ps1`
- `ops/scripts/powershell/queue-rollback.ps1`

### Python (repo-local auditing)

- `tools/audit_queue_list_references.py`
