# TD-007: `VersaoReport` consistente

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Guarantee `VersaoReport` is always populated consistently (new queue items and new history rows), and decide how to handle legacy blanks.

## Background

- Some legacy queue items may have `VersaoReport` empty because the column was added later.
- New items must always set `VersaoReport` based on the target cycle (Tue=1, Fri=2).

## Change plan (step-by-step)

1. Flow1 queue creator:
   - Ensure new item includes `VersaoReport = varVersaoAlvo`.
2. Flow2 persistence:
   - Ensure history includes `VersaoNumero` (or equivalent) mapped from the card payload `versao_report`.
3. SharePoint list schema decision (legacy):
   - Option A (safe): keep column optional; backfill old blanks over time.
   - Option B (strict): set default value (e.g., `1`) and mark required after backfill.

## Validation (Level 1 first)

- Create 3 new queue items and confirm all have `VersaoReport` filled.
- Submit 3 cards and confirm `StatusReports_Historico` rows have `VersaoNumero` filled and correct.

## Rollback (100% automated)

- If any strict enforcement breaks writes, revert schema to optional and keep default only.

## Evidence to attach (required)

- Screenshots of 3 queue items showing `VersaoReport`.
- Screenshots of 3 history items showing `VersaoNumero`.

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

