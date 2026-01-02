# TD-011: Performance refactor Flow1 (offer-driven)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Eliminate the N+1 SharePoint query pattern in Flow1 by making it **offer-driven**:

- One query to get offers
- Group offers per assignee in-memory
- Then dispatch queue items/cards per assignee

## Why this matters

Current design loops ARQs and runs `Get items` per ARQ, which scales poorly and can cause long runs/timeouts.

## Target design (high level)

1. Query `ARQs_Teams` once (active ARQs).
2. Query `Ofertas_Pipeline` once (open offers for the week/cycle).
3. Build an in-memory map: `AssigneeLogin → [offers]`.
4. For each assignee:
   - resolve email
   - create queue items (Flow1 queue creator) or post cards (Flow1 trigger)

## Change plan (step-by-step)

1. Define filter for `Ofertas_Pipeline`:
   - exclude closed statuses
   - include only items requiring report this cycle (`SemanaReport`/`VersaoReport` rules)
2. Implement grouping:
   - Use `Select`/`Filter array`/`Compose` patterns or a child flow approach for maintainability.
3. Ensure dedupe remains correct:
   - queue dedupe: `(OfertaId, Semana, RecipientEmail)` or `UniqueKey`
4. Validate functional parity with current behavior:
   - no reduction in coverage
   - no change to recipient rules

## Validation (Level 1 first)

- Compare counts and recipients between old Flow1 and new Flow1 for the same dataset:
  - number of queue items created
  - number of cards posted (if applicable)
- Confirm runtime is reduced and API calls are reduced (flow analytics if available).

## Rollback

- Keep the previous Flow1 version and re-enable if any regression is detected.

## Evidence to attach (required)

- Before/after run durations
- Before/after number of SharePoint calls (if visible)
- Queue item counts matching expected results

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

