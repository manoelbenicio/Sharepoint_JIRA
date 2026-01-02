# TD-009: Single source template (card/template)

## Ownership

- **Executed by**: Agent GPT-5.2 Codex
- **Peer reviewed by**: Agent Opus 4.5
- **PowerShell CLI required?**: No

## Goal

Eliminate “template drift” by defining one **canonical adaptive card template** and enforcing sync between Flow1 and Flow2.

## Strategy

1. Canonical template lives in repo (source of truth):
   - `adaptive_card_final_prodction.json`
2. Any change to the template must:
   - update the canonical file
   - regenerate any rendered artifacts (if applicable)
   - sync Flow2 `inputsAdaptiveCard` if Flow2 embeds the template
3. Add a preflight gate (offline) that fails CI/build if drift is detected (where feasible).

## Change plan (step-by-step)

1. Confirm canonical file keys and version:
   - `version: "1.4"`
   - Required `Action.Submit.data` keys present
2. Ensure Flow2 uses the canonical template:
   - If Flow2 stores `inputsAdaptiveCard`, sync it from the canonical file (script/tooling).
3. Ensure Flow1 uses either:
   - the canonical template directly (preferred), or
   - a minimal renderer that only injects data and preserves template structure.
4. Add/maintain tooling to validate:
   - template validity
   - required keys presence
   - no export-time split expressions

## Validation (offline + Level 1)

Offline:

- Render with sample data using `render_adaptive_card.py` (already in QA plan).

Level 1:

- Post one card and confirm `RespostaJSON` contains required keys.

## Rollback

- Revert to the last known-good canonical template + resync Flow2.

## Evidence to attach (required)

- Diff of template change
- Proof Flow2 inputs were synced (export snippet or screenshot)

## Execution log entry (append-only)

Append to `CHECKPOINT.md` → **Execution Log** with evidence.

