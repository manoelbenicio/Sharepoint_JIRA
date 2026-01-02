# TD-008: Cutover da lista da fila (blue/green) — **sem rename "no susto"**

**Status**: ✅ COMPLETED (2025-12-30)

## Ownership

- **Executed by**: Human (mbenicios) with Agent Antigravity
- **Peer reviewed by**: Agent Antigravity
- **PowerShell CLI required?**: Yes (PnP PowerShell) → User drove execution
- **M365 MCP/Docker MCP available**: Yes (Opus can use for docs/troubleshoot/knowledge as needed)

## Goal

Replace `StatusReports_Queue_TEST` with a production name `StatusReports_Queue` **without breaking anything**, with:

- double-check of every reference
- canary cutover
- rollback that is immediate and safe

## Non-negotiables

- **Do not rename** the existing list in place as the primary strategy.
- Use **blue/green**:
  - Blue = new list `StatusReports_Queue`
  - Green = existing list `StatusReports_Queue_TEST` (kept intact for rollback)
- **Recipient safety (hard constraint)**: during validation, the only allowed Teams recipient is `mbenicios@minsait.com`.
  - If there is any possibility of other recipients receiving messages, mark **BLOCKED (business hours validation required)**.

## Preconditions / Inputs

- Site URL (target)
- List name (current): `StatusReports_Queue_TEST`
- List name (new): `StatusReports_Queue`
- Flow1 + Flow2 exports available for rollback (keep previous `_vNN-1` enabled-ready)
- Flood control (TD-002) already applied to Flow2
- Dedupe/uniqueness (TD-006) already applied (recommended before cutover)

## Double-check (mandatory before any cutover)

1. Run repo audit for stale references:
   - `python tools/audit_queue_list_references.py --needles StatusReports_Queue_TEST`
   - Review `tools/reports/queue_list_reference_audit.json`
2. Confirm Power Automate references:
   - Flow1 queue creator: every SharePoint action must point to the correct list
   - Flow2 queue processor: queue read + updates must point to the correct list
3. Confirm there is a **rollback package**:
   - Old Flow1/Flow2 versions exported and ready to enable
   - Old list remains untouched (this is the main rollback guarantee)

## Cutover procedure (step-by-step)

### A) Freeze

1. Disable Flow1 and Flow2 recurrences (or set schedule to future).

### B) Backup

1. Export schema + items of `StatusReports_Queue_TEST` (scripted).
2. Export current Flow1/Flow2 versions (package).

### C) Provision “blue” list

1. Create `StatusReports_Queue` with same schema as `_TEST`.
2. Apply required columns and indexes (UniqueKey uniqueness if policy requires).

### D) Migrate data

1. Copy items from `_TEST` → `StatusReports_Queue`.
2. Do not delete anything from `_TEST`.

### E) Cutover flows

1. Update Flow1/Flow2 to point to `StatusReports_Queue`.
2. Keep old Flow1/Flow2 versions disabled but ready.

### F) Canary

1. Ensure Flow2 flood control is set to:
   - `QueueStatus eq 'Pending' and RecipientEmail eq 'mbenicios@minsait.com'`
   - `Order By Created asc`
   - `Top Count 1`
2. Create exactly 1 pending item for `mbenicios@minsait.com`.
3. Run Flow2 once and confirm exactly 1 card is received.

### G) Resume

1. Re-enable recurrences after canary approval.

## Validation (Level 1 first)

From SharePoint lists:

- New queue items are created in `StatusReports_Queue`.
- Status transitions occur only in `StatusReports_Queue`.
- `StatusReports_Historico` continues to receive responses.
- No user besides `mbenicios@minsait.com` receives Teams cards (verify by recipient filter + evidence).

## Rollback (100% automated in practice)

Rollback is fast and safe because:

- Old list remains untouched (`StatusReports_Queue_TEST` still exists with data).
- Old flow exports exist.

Procedure:

1. Disable the new Flow1/Flow2 versions.
2. Enable the old Flow1/Flow2 versions that still point to `StatusReports_Queue_TEST`.
3. Keep the new list for analysis; do not delete it during incident response.

## Evidence to attach (required)

- Output of `tools/audit_queue_list_references.py`
- Backup artifacts paths + timestamps
- Screenshots proving:
  - only 1 card received by `mbenicios@minsait.com`
  - queue transitions in the correct list

## Logs

- Opus must append to `CHECKPOINT.md` → **Execution Log**
- Codex must append findings to `CHECKPOINT.md` → **Peer Review Log**

## Execution Record (2025-12-30)

| Step | Status | Evidence |
|------|--------|----------|
| Schema + items backup | ✅ | `queue_schema_backup_20251230_215236.xml`, `queue_items_backup_20251230_214837.json` |
| Create new list | ✅ | `StatusReports_Queue` created |
| Copy fields | ✅ | Best-effort field copy |
| Migrate items | ✅ | 63 items migrated (`queue_migration_report_20251230_215236.csv`) |
| Flow1/Flow2 update | ✅ | User confirmed pointing to new list |

### Script Fixes Applied

| Issue | Fix |
|-------|-----|
| `-Interactive` deprecated | Changed to `-UseWebLogin` |
| `$PSCmdlet.ShouldProcess()` | Replaced with `$WhatIfPreference` checks |
| `Get-PnPProvisioningTemplate` not found | Replaced with `Get-PnPField` + JSON export |
| Field type errors | Whitelist approach - copy only known business fields |
| `.ContainsKey()` not allowed | Changed to `-contains` operator |
