# Deploy / Import Runbook (Power Automate Exports)

This repo keeps **sanitized** flow exports (no Teams IDs and no Azure Function keys). To import into an environment you must render placeholders and package ZIPs locally.

> For **professional ALM** (recommended), deploy via **Power Platform Solution**: `SOLUTION/SOLUTION_RUNBOOK.md`.

## AS-IS → TO-BE (What changed)

- **AS-IS**: exports contained hardcoded Teams IDs and Azure Function `?code=` keys.
- **TO-BE**: exports use placeholders + local render step (`.env` → `dist_rendered/`) + packaging (`dist_zips/`).
- **Flow2**: now enforces “`observacoes` obrigatório se status_projeto = Vermelho” (server-side gate).
- **Flow2**: `inputsAdaptiveCard` is kept in sync from `adaptive_card_final_prodction.json` via script.
- **Flow1**: offer lookup filter fixed (no invalid `Status eq 'Ativo'` on `Ofertas_Pipeline`; filter by `Assignee` only) to ensure Teams cards are actually sent.

## Prereqs

- Python 3.10+ recommended
- A `.env` file created from `.env.example` (never commit `.env`)

Fastest option: auto-fill `.env` from the latest PROD export ZIPs already in this repo:

```bash
python tools/extract_env_from_flow_zips.py --env .env --force
```

Fill at least:

- `TEAMS_GROUP_ID`, `TEAMS_CHANNEL_ID`
- `AZURE_FUNCTION_CODE_IMPORT_JIRA`
- `AZURE_FUNCTION_CODE_CONSOLIDAR_V2`

## Fast Path (one command)

```bash
bash tools/build_deploy_artifacts.sh .env
```

After import, validate using: `VALIDATION_RUNBOOK.md`

## 1) Sync the canonical Adaptive Card into Flow2

```bash
python tools/sync_inputs_adaptive_card.py
```

## 2) Ensure Flow2 has the validation gate (idempotent)

```bash
python tools/patch_flow2_validation_gate.py
python tools/patch_flow2_rfp_link_gate.py
```

## 3) Render placeholders (secrets/IDs) into deployable files

```bash
python tools/render_flow_definitions.py --env .env --out dist_rendered
```

Output: `dist_rendered/_prod_ac_patch/flow*/.../definition.json`

## 4) Package ZIPs ready to import

```bash
python tools/package_flow_exports.py --src-root dist_rendered/_prod_ac_patch --out dist_zips
```

Output: `dist_zips/flow1.zip`, `dist_zips/flow2.zip`, `dist_zips/flow3.zip`, `dist_zips/flow4.zip`

## 4.5) Validate ZIPs (import preflight)

The build script `tools/build_deploy_artifacts.sh` runs this automatically. To run it manually:

```bash
python tools/validate_flow_exports.py --zips dist_zips/*.zip
```

## 5) Import into Power Automate

- Power Automate → **My flows** → **Import** → select the zip(s) from `dist_zips/`
- During import, review/confirm connections for SharePoint + Teams.
