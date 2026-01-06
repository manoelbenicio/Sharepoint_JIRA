# HANDOFF_FIX_QA (single-folder bundle)

This folder is a **copyable snapshot** containing everything needed to execute the **Technical Debt (fix) plan** and, only after that, the **QA plan**.

## Non‑negotiables (must follow)

1. **Do not run QA until ALL TDs are fixed + peer‑reviewed** (no mixing implementation and QA).
2. **Recipient safety (hard constraint)**: during any testing, the only allowed Teams recipient is:
   - `mbenicios@minsait.com`
   If there is any possibility of other users receiving messages, mark **BLOCKED (business hours validation required)**.
3. **Ownership**:
   - Any task requiring **PowerShell CLI (PnP / tenant scripting)** is **Agent Opus 4.5 only**.
   - Agents must not execute tasks owned by the other agent unless the user explicitly requests it in writing.
4. **Peer review required**:
   - Codex reviews Opus deliverables; Opus reviews Codex deliverables.
   - All findings must be logged.

Source of truth for rules/logging: `CHECKPOINT.md`.

## Start here

1. Open `CHECKPOINT.md`:
   - Technical debt backlog table includes **execution order**, **owner agent**, and **runbook/script** per TD.
   - Append evidence to **Execution Log** and **Peer Review Log**.
2. Execute TD items in order using runbooks in `ops/runbooks/`.
3. Only after all TDs are completed + peer‑reviewed, execute QA using `QA_PRODUCTION_TEST_PLAN.md` (Opus-owned).

## Offline preflight (recommended before any tenant import)

From this folder root:

- Validate flow export zips:
  - `python tools/validate_flow_exports.py --zips dist_zips/*.zip`
- Ensure Flow2 flood-control defaults are applied in the Flow2 package (optional):
  - `python tools/patch_flow2_queue_query.py --zip dist_zips/flow2_queue_wait.zip --recipient-email mbenicios@minsait.com --top 1 --orderby "Created asc"`
- Ensure Flow2 state machine stamps are applied (optional, recommended):
  - `python tools/patch_flow2_state_machine.py --zip dist_zips/flow2_queue_wait.zip`
- Ensure Flow6 does NOT post to Teams channels during QA prep (optional, recommended):
  - `python tools/patch_flow6_remove_teams_notify.py --zip dist_zips/flow6.zip`
- Audit references to the queue list name (TD‑008 double check):
  - `python tools/audit_queue_list_references.py --needles StatusReports_Queue --zip-pattern 'flow*.zip' --out tools/reports/queue_list_reference_audit.json`

## What’s included

- Plans / governance:
  - `CHECKPOINT.md`
  - `QA_PRODUCTION_TEST_PLAN.md`
- Ops runbooks + scripts:
  - `ops/runbooks/`
  - `ops/scripts/powershell/` (Opus-only)
- Tools:
  - `tools/validate_flow_exports.py`
  - `tools/audit_queue_list_references.py`
- Flow artifacts to import:
  - `dist_zips/flow1.zip`
  - `dist_zips/flow1_queue_creator.zip`
  - `dist_zips/flow2.zip`
  - `dist_zips/flow2_queue_wait.zip`
  - `dist_zips/flow3.zip`
  - `dist_zips/flow5.zip`
  - `dist_zips/flow6.zip`

## Required manual settings (before running Flow6 / purge)

### Flow6 HTTP action (premium-analytics)

For security, `dist_zips/flow6.zip` ships with a placeholder:

- `https://sharepoint-jira-functions-br.azurewebsites.net/api/premium-analytics?code=<FUNCTION_KEY>`

After import, set the real Function Key in the Flow6 HTTP action URI.

### Azure Function purge endpoint (pre-QA baseline)

The purge endpoint requires these env/app settings to be enabled (see `ops/runbooks/TD-010-azure-app-settings-flags.md`):

- `LAB_PURGE_ENABLED=true`
- `LAB_PURGE_ADMIN_TOKEN` + `LAB_PURGE_CONFIRMATION`
- allowlist `LAB_PURGE_ALLOWED_LIST_IDS`
