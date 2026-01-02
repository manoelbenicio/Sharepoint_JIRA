# TD-005: Flow2 state machine (robustness)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Make Flow2 impossible to “silently lose” work by ensuring deterministic and auditable state transitions:

`Pending → Processing → Sent → Completed` (or `Error`)

## Required queue fields

Queue list must support these columns (create if missing):

- `QueueStatus` (Choice): `Pending`, `Processing`, `Sent`, `Completed`, `Error`
- `SentAt` (DateTime)
- `CompletedAt` (DateTime)
- `AttemptCount` (Number, default 0)
- `LastError` (Multiple lines text) (optional but recommended)

## Change plan (step-by-step)

1. **Read step** (`Get items`):
   - Filter: `QueueStatus eq 'Pending'` (plus flood-control allowlist during tests)
   - Order By: `Created asc`
   - Top Count: start with `1`
2. **Lock step** (first action inside loop):
   - Update item:
     - `QueueStatus = Processing`
     - `AttemptCount = AttemptCount + 1`
3. **Post step**:
   - Post adaptive card to Teams (`PostCardAndWaitForResponse`)
   - If post succeeds:
     - Update item: `QueueStatus = Sent`, `SentAt = utcNow()`
4. **Wait/response step**:
   - When response exists:
     - Persist into `StatusReports_Historico`
     - Update item: `QueueStatus = Completed`, `CompletedAt = utcNow()`
5. **Error handling**:
   - If Teams post fails:
     - Update item: `QueueStatus = Error`, `LastError = <message>`
   - If persistence fails:
     - Update item: `QueueStatus = Error`, `LastError = <message>`
6. **Retry policy**:
   - Define a max attempts threshold (e.g., 3). If exceeded, keep in `Error` and stop auto retries.

## Validation (Level 1 first)

In queue list:

- A processed item must show:
  - `AttemptCount >= 1`
  - `SentAt` stamped only if Teams post succeeded
  - `CompletedAt` stamped only if history write succeeded
- No item may remain `Sent` with no `SentAt`.
- No item may move to `Sent` before Teams post succeeds.

## Rollback (100% automated)

Rollback is version rollback:

1. Disable the modified Flow2.
2. Enable the previous exported Flow2 version (kept as `_vNN-1`).
3. If new queue columns were created, keep them (schema additions are backward-compatible).

## Evidence to attach (required)

- Flow2 run screenshot(s) showing successful branch and error branch behavior.
- Queue item screenshots showing status + timestamps + attempt count.
- One `StatusReports_Historico` row created from a completed item.

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

