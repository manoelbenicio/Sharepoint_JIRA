# TD-003: Ops views (Level 1 troubleshooting)

## Status: ✅ COMPLETED (2025-12-30T21:00:00-03:00)

## Ownership

- **Executed by**: Human (mbenicios) — *Note: TD-003 is Opus-owned but human drove execution*
- **Peer reviewed by**: Agent Antigravity
- **PowerShell CLI required?**: Yes (PnP PowerShell) → Opus-only

## Goal

Standardize SharePoint views so troubleshooting is **tables-first** and repeatable (Level 1), minimizing flow-run inspection.

## Preconditions / Inputs

- `SiteUrl` (target site)
- List names:
  - `StatusReports_Queue`
  - `StatusReports_Historico`
- **PnP.PowerShell v3.1.0+** installed
- **Authentication**: Use `-UseWebLogin` (NOT `-Interactive`)
  - `-Interactive` is NOT supported (deprecated Sept 9, 2024)
  - `-UseWebLogin` opens browser for auth

## Change plan (step-by-step)

1. Run the script to create/update views:
   - `ops/scripts/powershell/ops-views.ps1`
2. Ensure at least these views exist:
   - Queue:
     - `Ops - Queue (All)`
     - `Ops - Queue (Pending)`
     - `Ops - Queue (Sent)`
     - `Ops - Queue (Errors)`
     - `Ops - Queue (Duplicates)`
   - Historico:
     - `Ops - Historico (All)`
     - `Ops - Historico (Last 24h)`

## Validation (Level 1 first)

- Open SharePoint list UI and confirm views are selectable and show the required columns.
- Confirm filters work (e.g., `Pending` view only shows `QueueStatus=Pending`).

## Rollback (100% automated)

- Script supports removal mode (or a paired remove script) to delete views created by this runbook.
- If rollback is needed: remove only the created views, do not change list schema.

## Evidence to attach (required)

- Script execution log output.
- Screenshots of views working (Queue + Historico).

## Execution log entry (append-only)

Opus must append to `CHECKPOINT.md` → **Execution Log**.

## Peer review checklist

Codex must:
- Validate view names and filters match this runbook.
- Validate columns include: `Created`, `Modified`, `QueueStatus`, `SentAt`, `CompletedAt`, `AttemptCount`, `UniqueKey` (Queue) and `RespostaJSON` (Historico).
- Record findings in `CHECKPOINT.md` → **Peer Review Log**.

---

## Execution Record

| Field | Value |
|-------|-------|
| **Executed at** | 2025-12-30T21:00:00-03:00 |
| **Executed by** | Human (mbenicios@minsait.com) |
| **PnP.PowerShell version** | 3.1.0 |
| **Auth method** | `-UseWebLogin` |
| **Outcome** | ✅ OK |
| **Views created** | 7 (Queue: 5, Historico: 2) |

### Terminal Output (Evidence)

```
Creating view: StatusReports_Queue :: Ops - Queue (All)
Creating view: StatusReports_Queue :: Ops - Queue (Pending)
Creating view: StatusReports_Queue :: Ops - Queue (Sent)
Creating view: StatusReports_Queue :: Ops - Queue (Errors)
Creating view: StatusReports_Queue :: Ops - Queue (Duplicates)
Creating view: StatusReports_Historico :: Ops - Historico (All)
Creating view: StatusReports_Historico :: Ops - Historico (Last 24h)
Done.
```

