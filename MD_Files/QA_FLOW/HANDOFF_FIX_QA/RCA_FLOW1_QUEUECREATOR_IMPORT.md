# RCA — Flow1 Queue Creator ZIP Import Failure (Template Expression Parse Errors)

## Summary

Power Automate import of `Flow1_QueueCreator_PROD` failed with template language parsing errors referencing `item/UniqueKey` (e.g., “expected token `Identifier` / `EndOfData` …”).

## Customer Impact

- Deployment blocked at import time (no runtime fallback).
- Risk of production deployment delays and repeated incident churn if the same artifact is reused.

## What Happened (Symptoms)

- Import UI error: exported Logic App template invalid.
- Error pointed to an expression for the queue item `UniqueKey` field.

## Root Cause

1) **Invalid export representation for `item/UniqueKey`**
- In `dist_zips/flow1_queue_creator_broken_20251229.zip`, `item/UniqueKey` was stored as a **JSON array of string fragments** instead of a **single string** expression.
- Power Automate expects a single template language string (e.g., `\"@concat(...)\"`). A list-of-strings cannot be parsed as one expression, so import fails.

2) **No automated preflight validation**
- The repository had packaging scripts but no gating step to validate importability of the produced ZIPs (split expressions, missing `@`, unbalanced parentheses/quotes).
- This allowed an import-breaking artifact to be treated as “ready”.

## Contributing Factors

- Long expressions are prone to copy/paste, line-splitting, or accidental structural edits during patching/review.
- No “CI-like” guardrail to fail fast before sharing artifacts with a production-bound process.

## Corrective Action (Implemented)

- Fixed `Flow1_QueueCreator_PROD` export by ensuring `item/UniqueKey` is a **single, balanced** `@concat(...)` expression string.
  - Updated artifact: `dist_zips/flow1_queue_creator.zip`
  - Backup kept: `dist_zips/flow1_queue_creator_broken_20251229.zip`

## Preventive Actions (Implemented)

- Added automated ZIP validation: `tools/validate_flow_exports.py`
  - Detects split expressions (list-of-strings), expression-like strings missing leading `@`, and unbalanced parentheses/quotes.
- Wired validation into `tools/build_deploy_artifacts.sh` so builds fail before shipping artifacts.
- Updated docs to recommend running validation prior to import:
  - `DEPLOY_RUNBOOK.md`
  - `FLOWS_FINAL/FLOW1_MANUAL_CREATION_GUIDE.md`
  - `FLOWS_FINAL/FLOW1_COPILOT_STUDIO_PROMPT.md`

## Verification / How To Validate

- Run: `python tools/validate_flow_exports.py --zips dist_zips/flow1_queue_creator.zip`
- Import: Power Automate → My flows → Import → `dist_zips/flow1_queue_creator.zip`

