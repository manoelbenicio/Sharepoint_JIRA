# TD-002: Flood control (prod safety)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Guarantee Flow2 can be tested at night with **zero risk of flooding** other recipients.

## Preconditions / Inputs

- You have access to edit Flow2 in Power Automate.
- You have your test recipient email (your own).
- Queue list exists and contains items with `QueueStatus` (Choice) and `RecipientEmail`.
- **Hard constraint**: during QA/tests, the only allowed Teams recipient is `mbenicios@minsait.com`.

## Change plan (step-by-step)

1. Open Flow2 in edit mode.
2. Locate the SharePoint action that reads the queue (usually `Obter_itens_fila` / `Get items`).
3. Apply deterministic + safe settings:
   - **Filter Query**:
     - Start with: `QueueStatus eq 'Pending' and RecipientEmail eq 'mbenicios@minsait.com'`
     - Optionally add an ID constraint for canary: `and ID eq <QUEUE_ID>`
   - **Order By**: `Created asc`
   - **Top Count**: `1`
4. Save Flow2.
5. Execute a canary:
   - Manually set exactly 1 queue row for you to `Pending`.
   - Run Flow2 once.
6. If you cannot 100% guarantee the allowlist constraint (e.g., filter limitations, uncertain field type/value, multiple flows enabled):
   - **Do not run**.
   - Mark **BLOCKED (business hours validation required)** and schedule the run for business hours.

## Validation (Level 1 first)

In SharePoint list (Level 1):

- The selected item transitions predictably:
  - `Pending → Sent` (and later `Completed` if you submit the card)
- No other recipients’ rows change.

In Teams:

- Exactly 1 card arrives for your user.

## Rollback (100% automated)

Rollback is a configuration revert:

1. Restore the previous filter / Top Count / Order By values (use a screenshot or exported definition as evidence).
2. Save Flow2.

## Evidence to attach (required)

- Screenshot (or exported flow definition snippet) of Flow2 queue query settings.
- Queue item before/after (`ID`, `RecipientEmail`, `QueueStatus`, `Created`, `Modified`).
- Teams screenshot showing only 1 card received.
- Note confirming **no other recipients** were eligible under the filter at runtime (e.g., screenshot of list filtered by recipient).

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence links/IDs.
