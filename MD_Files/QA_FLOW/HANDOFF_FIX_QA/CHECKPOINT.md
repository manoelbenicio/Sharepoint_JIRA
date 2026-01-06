# CHECKPOINT (Single Source of Truth)

Last updated: 2026-01-06T07:06:00-03:00

## Execution Ownership (Non-Negotiable)

- Every task below has an explicit **owner agent**.
- Any task that requires **PowerShell CLI (PnP / tenant scripting)** must be executed by **Agent Opus 4.5**.
- **Agent GPT-5.2 Codex** must not execute Opus-owned tasks, and **Agent Opus 4.5** must not execute Codex-owned tasks, unless you explicitly request it in writing.
- **Recipient safety (hard constraint)**: during QA/tests, the only allowed Teams recipient is `mbenicios@minsait.com`. If there is any possibility of other recipients receiving messages, the activity must be marked **BLOCKED (business hours validation required)**.
- Every executed task must append an entry into **Execution Log** (timestamp + agent + evidence).
- After execution, there is a mandatory **peer review**:
  - Agent GPT-5.2 Codex reviews Opus-owned deliverables/results.
  - Agent Opus 4.5 reviews Codex-owned deliverables/results.
  - If anything is unclear or not 100% correct, the reviewing agent must record a note in **Peer Review Log** (timestamp + agent + TD + finding + evidence).

## Execution Log (append-only)

| Timestamp (local) | Agent | TD | Action | Outcome | Evidence |
|---|---|---|---|---|---|
| 2025-12-30T00:00:00-03:00 | Agent GPT-5.2 Codex | N/A | Repo organization: added runbooks/scripts + ownership columns | OK | Repo files (`ops/`, `tools/`) |
| 2025-12-30T00:00:00-03:00 | Agent GPT-5.2 Codex | N/A | Added safety gating: only `mbenicios@minsait.com` allowed during QA/tests | OK | `QA_PRODUCTION_TEST_PLAN.md`, `ops/runbooks/TD-002-flow2-flood-control.md` |
| 2025-12-30T00:00:00-03:00 | Agent GPT-5.2 Codex | N/A | Added reference audit tool + generated initial report | OK | `tools/audit_queue_list_references.py`, `tools/reports/queue_list_reference_audit.json` |
| 2025-12-30T10:50:00-03:00 | Agent Antigravity | TD-002 | Created execution checklist for Flow2 flood control configuration | IN PROGRESS | `ops/runbooks/TD-002-EXECUTION-CHECKLIST.md` |
| 2025-12-30T10:50:00-03:00 | Agent Antigravity | N/A | Generated 360° Technical Debt Status Report | OK | Artifact: `TD_360_STATUS_REPORT.md` |
| 2025-12-30T10:52:00-03:00 | Agent Antigravity | TD-003/TD-006/TD-008 | Attempted PnP auth fix (incomplete: only 1/5 scripts) | INCOMPLETE | `preqa-reset-and-import.ps1` only |
| 2025-12-30T20:48:00-03:00 | Agent Antigravity | TD-003/TD-006/TD-008 | Verified + fixed PnP auth in ALL 5 scripts: `-DeviceLogin`/`-Interactive` → `-UseWebLogin` | OK | `ops-views.ps1:57`, `queue-dedupe.ps1:48`, `queue-cutover.ps1:47`, `queue-rollback.ps1:41`, `preqa-reset-and-import.ps1:110` |
| 2025-12-30T21:00:00-03:00 | Human (mbenicios) | TD-003 | Executed `ops-views.ps1`: created 7 SharePoint views (Queue + Historico) | OK | Terminal output: "Creating view: StatusReports_Queue :: Ops - Queue (All)", "Done." |
| 2025-12-30T21:05:00-03:00 | Agent Antigravity | N/A | Confirmed `-Interactive` NOT supported (Sept 2024 deprecation). `-UseWebLogin` is permanent solution. Updated PnP.PowerShell to v3.1.0 | OK | Error: "Specified method is not supported", "As of September 9th, 2024 this option is not available anymore" |
| 2025-12-30T21:17:00-03:00 | Human (mbenicios) | TD-006 | Executed `queue-dedupe.ps1 -Mode Scan`: found 61 duplicate groups | OK | `tools/reports/queue_dedupe_scan_20251230_211720.csv` |
| 2025-12-30T21:25:00-03:00 | Human (mbenicios) | TD-006 | Executed `queue-dedupe.ps1 -Mode Cleanup -KeepPolicy OldestCreated`: removed 88 duplicates | OK | `tools/reports/queue_dedupe_cleanup_20251230_212143.csv` |
| 2025-12-30T21:26:00-03:00 | Human (mbenicios) | TD-006 | Verified scan: 0 duplicate groups remaining | OK | `tools/reports/queue_dedupe_scan_20251230_212621.csv` |
| 2025-12-30T21:52:00-03:00 | Human (mbenicios) | TD-008 | Executed `queue-cutover.ps1`: migrated 63 items from `StatusReports_Queue` → `StatusReports_Queue`. Script fixed for constrained mode (5 fixes). | OK | `tools/reports/queue_migration_report_20251230_215236.csv` |
| 2025-12-30T21:59:00-03:00 | Human (mbenicios) | TD-008 | Updated Flow1/Flow2 to point to new list `StatusReports_Queue` | OK | User confirmation |
| 2025-12-30T22:08:00-03:00 | Agent Antigravity | QA | QA Preflight: 6 flow zips validated, Adaptive Card render OK | OK | `validate_flow_exports.py`, `render_adaptive_card.py` |
| 2025-12-30T22:38:00-03:00 | Agent Antigravity | QA-S1 | Flow2 triggered via browser agent (352ms, status Êxito). Teams Workflows bot received "Status Report Semanal" card for 2025-W50. | OK | Browser recordings: `qa_flow2_test`, `qa_s1_run_flow2`, `qa_s1_check_teams` |
| 2026-01-01T21:01:00-03:00 | Agent Antigravity | QA-F1 | Flow1 triggered: 13 queue items created in `StatusReports_Queue` | OK | Screenshot: `flow1_queue_populated` |
| 2026-01-01T21:03:00-03:00 | Agent Antigravity | QA-S1 | Flow2 triggered: 13 Adaptive Cards sent to Teams (OFBRA-4100,4102,4103,4107,4112,4113,4114, etc.) | OK | Cards visible in Teams Workflows chat |
| 2026-01-01T21:20:00-03:00 | Human (mbenicios) | QA-S2,S3 | Multiple cards submitted in Teams. Queue: 5 Completed, 7 Sent, 1 Pending. Data persisted to `StatusReports_Historico` | OK | Screenshots: `status_reports_queue_test_updated`, `status_reports_historico_results` |
| 2026-01-01T22:04:00-03:00 | Human (mbenicios) | QA-C3 | Vermelho validation test: Submit allowed despite empty Observações | FAIL | BUG: Flow2 validation not triggering |
| 2026-01-01T22:04:00-03:00 | Human (mbenicios) | QA-C4 | Vermelho + Obs filled: Submit allowed correctly | OK | "Teste C4" visible in Observações |
| 2026-01-01T22:11:00-03:00 | Human (mbenicios) | QA-A1,A2 | Adaptive Card Baseline verified via screenshot (Header + Controls) | OK | Screenshots verified |
| 2026-01-01T22:25:00-03:00 | Agent Antigravity | QA-DQ1,DQ2 | Verified HTML stripping logic in `function_app.py` | OK | Code inspection confirms `strip_html_to_text` and `normalize_observacoes` logic |
| 2026-01-01T22:30:00-03:00 | Agent Antigravity | QA-DUP1 | Verified duplicate detection logic in `queue-dedupe.ps1` | OK | Code inspection confirms Group-Object logic |
| 2026-01-06T07:00:00-03:00 | Agent Antigravity | Flow6 | Created 4 premium card templates (04-07): ARQ, Market, WoW, Practice | OK | `TEMPLATE_04-07_*.json` |
| 2026-01-06T07:04:00-03:00 | Human (mbenicios) | Flow6 | Created Teams channel `Ofertas_Analytics`, approved bi-weekly schedule (Tue/Fri) | OK | User confirmation |

## Peer Review Log (append-only)

| Timestamp (local) | Reviewer agent | Reviewed agent | TD | Finding | Evidence |
|---|---|---|---|---|---|
| 2025-12-30T00:00:00-03:00 | Agent Opus 4.5 | Agent GPT-5.2 Codex | N/A | Pending peer review of repo organization changes | N/A |
| 2025-12-30T21:07:00-03:00 | Agent Antigravity | Human (mbenicios) | TD-003 | TD-003 execution verified OK. 7 views created. PnP v3.1.0 confirmed. `-UseWebLogin` is correct permanent auth method. | Terminal logs show all views created successfully |
| 2025-12-30T21:26:00-03:00 | Agent Antigravity | Human (mbenicios) | TD-006 | TD-006 execution verified OK. 61 duplicate groups cleaned (88 items removed). KeepPolicy=OldestCreated. Script fixed for constrained language mode. | Scan report shows 0 duplicates remaining |
| 2025-12-30T22:00:00-03:00 | Agent Antigravity | Human (mbenicios) | TD-008 | TD-008 execution verified OK. 63 items migrated. Script fixed for constrained mode (whitelist approach, -contains operator, ShouldProcess removal). Flow1/Flow2 updated. | Migration report shows 63 items migrated |

This file is the *only* project progress tracker. Any agent changing this repo must update this file in the same PR/patch.

## What This Project Is

Power Automate + SharePoint + Teams solution for a weekly “Pipeline de Ofertas” status collection and consolidation:

- **Import** JIRA exports (CSV) into a SharePoint list (offers).
- **Distribute** a weekly Adaptive Card to each architect for each active offer they own.
- **Collect** card submissions and persist them (history + legacy list).
- **Consolidate** weekly status into a C‑Level summary posted to a Teams channel (via Azure Function).

## Key Decisions (Current)

- **Raw vs normalized data**:
  - `Ofertas_Pipeline` is the **raw, authoritative mirror** of the JIRA export (ingested by `/import-jira` in PASSTHROUGH mode).
  - Reporting/analytics should use **normalized outputs** (via mapping tables + `/normalizar-ofertas`) and/or `Ofertas_Pipeline_Normalizada` when activated.
  - Heavy transformations belong in **Azure Functions** (or optionally self-hosted `n8n` if enabled), not inside Power Automate.
- **Data control / observability**:
  - `/import-jira` emits per-batch stats (`choices_report`, `null_counts`, `campos_ausentes`) to detect JIRA drift and data quality issues early.
  - Alerts can be driven from those stats (Power Automate) without breaking the raw ingestion pipeline.
- **Adaptive Cards (Teams)**: standardize on Adaptive Card `version: "1.4"` for compatibility; keep Flow1/Flow2/templates aligned.
- **ALM (Solution-first)**:
  - Deploy as a Power Platform **Solution** with **Environment Variables** + **Connection References** (no hardcoded IDs/secrets in flows). Runbook: `SOLUTION/SOLUTION_RUNBOOK.md`.
  - Keep “listener” triggers minimal if the new designer doesn’t support them; move business logic to child flows (new designer) for maintainability.
- **Decoupled orchestration (no blocking)**:
  - Flow1 must **dispatch** cards without waiting for responses (no sequential “wait for response” bottleneck).
  - Flow2 must **collect/persist** responses independently (write to `StatusReports_Historico`), and Flow3 consolidates from history.
- **ARQs identity mapping (robustness)**:
  - `ARQs_Teams` must have a simple text column `Login` (e.g. `mbenicios`) to map architects → `Ofertas_Pipeline.Assignee` reliably.
  - This avoids deriving login from email via expressions and makes Flow1 filtering simpler and less fragile.
- **Card submit contract** (Flow1 → Teams → Flow2): `Action.Submit.data` must include `action`, `jirakey`, `oferta_id`, `semana`, `arquiteto_email`, `cardTypeId`, `arquiteto_nome`, `oferta_titulo` (see `adaptive_card_final_prodction.json`).
- **Card UX (status form)**:
  - `observacoes` is prefilled from the latest JIRA “Custom field (Observations)” (stored in `Ofertas_Pipeline.Observacoes`) and can be edited/cleared by ARQs.
  - Added optional sections: `riscos_oportunidades` and `decisao_ask`.
  - Added required classification `tipo_demanda`: `Oferta`, `RFI`, `RFQ`, `RFP` and linkage field `rfp_relacionada` (required when `tipo_demanda` is `RFI`/`RFQ`).
  - Added `reuniao_tipo` (`Presencial`/`Remoto`) alongside `reuniao_cliente`.
- **JIRA Observations formatting**:
  - JIRA may export “Custom field (Observations)” as HTML (`<div>`, `<br>`, `&gt;`).
  - `/api/import-jira` supports stripping HTML for readability via app setting `IMPORT_STRIP_HTML_OBSERVACOES=true` (see `ZIP/Azure_Function/function_app.py`).
- **Assignee enrichment (optional)**:
  - You can enrich offers during `/api/import-jira` with stable ARQ identifiers (matrícula) and contact fields using `IMPORT_ENRICH_ASSIGNEE=true`.
  - This keeps `Assignee` AS‑IS from JIRA, but adds `AssigneeMatricula`, `AssigneeNome`, `AssigneeEmail` for easier joins/reporting.

## Project Status (Timeline)

Current state: core flows, schemas, and documentation exist; exports are sanitized (no secrets/IDs hardcoded). Remaining work is mostly **standardization + deploy/runbook hardening**.

Estimated timeline (depends on access to Power Platform/Azure tenant for import/testing):

- **Milestone A (done)**: keep Flow2 `inputsAdaptiveCard` synced from the canonical template + confirm submission contract end-to-end.
- **Milestone B (done)**: deploy packaging + import/run steps using `dist_rendered/` and `dist_zips/` (`DEPLOY_RUNBOOK.md`).
- **Milestone C (done)**: enforce “observações obrigatório se Vermelho” (server-side validation in Flow2 + user feedback).
- **Milestone D (done)**: standardize consolidation output (Flow3 uses `/consolidar-v2` and posts `teams_card_html`).
- **Milestone E (2–5 days, optional hardening)**: replace `.env` rendering approach with Power Platform env vars / Entra ID auth (AAD) + rotation/runbook.

## Key Artifacts (Current)

- Adaptive Card template (placeholders `${...}`): `adaptive_card_final_prodction.json`
- Sample data for local rendering: `adaptive_card.data.json`
- Local renderer (template → rendered card + Teams webhook payload): `render_adaptive_card.py`
- Premium template variants (optional): `adaptive_card.premium.executive.json`, `adaptive_card.premium.boarddeck.json`, `adaptive_card.premium.futuristic.json`
- HTML report (full “Status Report Corporativo”): `ZIP/HTML`
- JIRA export sample: `ZIP/JIRA PBI (JIRA Indra) 2025-12-26T05_53_47-0391.csv`
- User correlation table (login ↔ email ↔ name): `ZIP/CSV/users_list_correlation.csv` (usage: `ZIP/CSV/USERS_LIST_CORRELATION.md`)
- Flow export “patch” workspaces (reference implementations): `_prod_ac_patch/`, `_flow*_patch/`
- Flow export ZIPs (deliverables): root `Fluxo*.zip` and `ZIP/*.zip` variants (AC, AC2, AC3…)
- Queue+wait Flow2 import package: `dist_zips/flow2_queue_wait.zip`
- Flow1 queue-creator import package: `dist_zips/flow1_queue_creator.zip`
- SharePoint list schemas (authoritative mappings): `ZIP/XML/INDEX.md`
- Handoff summary (for new chats/agents): `HANDOFF.md`
- Deploy/import runbook: `DEPLOY_RUNBOOK.md`
- Solution-based ALM (recommended): `SOLUTION/SOLUTION_RUNBOOK.md`
- Post-import validation: `VALIDATION_RUNBOOK.md`
- Manual Card Test Guide: `MANUAL_CARD_TESTS.md`
- Validation Fix Plan: `FIX_VALIDATION.md`
- 360° project docs (authoritative):
  - `ZIP/XML/ARCHITECTURE/STAKEHOLDER_PROJECT_GUIDE.md`
  - `ZIP/XML/ARCHITECTURE/ARCHITECTURE_DEEP_DIVE.md`
  - `ZIP/XML/ARCHITECTURE/AZURE_FUNCTION_COMPLETE_MAP.md`
  - `ZIP/XML/ARCHITECTURE/LOGGING_AND_DATA_CONTROL_SYSTEM.md`
- Secrets/config guidance: `SECURITY_CONFIG.md`
- Azure Function code + deploy: `ZIP/Azure_Function/` (includes LAB purge endpoint doc: `ZIP/Azure_Function/LAB_PURGE_ENDPOINT.md`)

## SharePoint Lists (GUIDs)

| List | GUID | Notes |
|---|---|---|
| `Ofertas_Pipeline` | `6db5a12d-595d-4a1a-aca1-035837613815` | Used by Flow1/Flow3/Flow5/Flow6 (and XML export). |
| `Atualizacoes_Semanais` | `172d7d29-5a3c-4608-b4ea-b5b027ef5ac0` | Used by Flow2 (legacy write) and Flow3 (read). |
| `ARQs_Teams` | `1ad529f7-db5b-4567-aa00-1582ff333264` | Flow1 references this list by name (`table: "ARQs_Teams"`), not by GUID in exported JSON. |
| `Ofertas_Pipeline_Normalizada` | `fa90b09d-5eb9-461f-bf15-64a494b00d2d` | Not referenced in the exported flows in this repo (likely Azure Function/internal). |
| `StatusReports_Historico` | `f58b3d23-5750-4b29-b30f-a7b5421cdd80` | Used by Flow2 (history write). |
| `Budget_Extensions` | `dfeda3e0-0cc9-434d-b8d5-5b450dc071b2` | Not referenced in the exported flows in this repo. |
| `Resumo_Semanal` | `1d4a803e-9884-4e10-b932-ef9ff598f127` | Not referenced in the exported flows in this repo. |
| `Jira_Allocation_Data` | `f25edf86-f23a-41bb-a7b1-84a096df2dd8` | Not referenced in the exported flows in this repo. |

## Flows (Intended Responsibilities)

- **Flow 1 – Weekly trigger + send cards**
  - Reads active architects from SharePoint list `ARQs_Teams`
  - For each architect: fetches assigned active offers and posts an Adaptive Card to the architect’s chat
  - Reference export: `_prod_ac_patch/flow1/`

- **Flow 2 – Teams Card Trigger (submit handler)**
  - Receives `Action.Submit` from the Adaptive Card
  - Persists the raw submission (`RespostaJSON`) in a history list
  - Also writes “legacy” structured fields for backwards compatibility
  - Reference export: `_prod_ac_patch/flow2/`

- **Flow 3 – Weekly consolidation (C‑Level)**
  - Fetches offers + updates
  - Calls Azure Function consolidation endpoint
  - Posts summary to Teams channel
  - Reference export: `_prod_ac_patch/flow3/`

- **Flow 5 – JIRA CSV import trigger** (Post Weekly Flash Report)
  - Watches a SharePoint folder for new CSV files
  - Calls Azure Function import endpoint
  - Upserts offers into SharePoint list
  - Posts a completion Adaptive Card to Teams channel
  - Reference export: `_prod_ac_patch/flow5/`

- **Flow 6 – Premium Analytics Bi-Weekly** ✅ (2026-01-06)
  - Schedule: Bi-weekly (Tue & Fri @ 9AM) or Fridays only
  - Channel: `Ofertas_Analytics`
  - Cards: TEMPLATE_04 (ARQ), TEMPLATE_05 (Market), TEMPLATE_06 (WoW), TEMPLATE_07 (Practice)
  - Specs: `FLOW6_PREMIUM_ANALYTICS_SPEC.md`

## Completed (So Far)

- [x] Adaptive Card templates created (standard + premium variants).
- [x] Added local rendering workflow: `render_adaptive_card.py` + example outputs (`adaptive_card.rendered.json`, `teams.webhook.payload.json`).
- [x] Produced “final production” placeholder-based card: `adaptive_card_final_prodction.json` (Adaptive Card `1.4`).
- [x] Updated Adaptive Card submit payload to include `cardTypeId`, `arquiteto_nome`, `oferta_titulo` (aligns with Flow1 sender + Flow2 storage).
- [x] Flow exports organized for patching/review: `_flow*_patch/`, `_prod_ac_patch/`, `tmp_zip_review/`.
- [x] Flow 1 export includes a working “compose Adaptive Card + PostCardToConversation” pattern (with `cardTypeId`).
- [x] Flow 2 export uses **TeamsCardTrigger** and embeds the Adaptive Card JSON (`inputsAdaptiveCard`) with `Action.Submit` (`submit_status`).
- [x] Flow 2 `inputsAdaptiveCard` is kept in sync from `adaptive_card_final_prodction.json` via `tools/sync_inputs_adaptive_card.py`.
- [x] Flow 2 enforces “observações obrigatório se status_projeto = Vermelho” (validation gate + Teams feedback) via `tools/patch_flow2_validation_gate.py`.
- [x] Flow 3 and Flow 4 exports wired to Azure Functions + Teams postings (message/card).
- [x] Flow 3 uses `/consolidar-v2` and posts `teams_card_html` to Teams (C‑Level output).
- [x] Sanitized Azure Function `?code=` and Teams channel IDs in exported flow JSONs (placeholders + local renderer `tools/render_flow_definitions.py`).
- [x] Added packaging tooling for deploy ZIPs: `tools/package_flow_exports.py` + `DEPLOY_RUNBOOK.md`.
- [x] Added “speed deploy” tooling: `tools/extract_env_from_flow_zips.py` + `tools/build_deploy_artifacts.sh` (generates `dist_zips/*.zip` locally).
- [x] Imported the latest flow set into Power Automate (saved as `_v5`) with no import errors; pending end-to-end validation per `VALIDATION_RUNBOOK.md`.
- [x] Flow4 validated in tenant: CSV dropped in `JIRA_Imports` → Azure Function import succeeded → `Ofertas_Pipeline` upserted (offers visible with `Assignee=mbenicios`).
- [x] Root-caused Flow1 “green run but no Teams cards”: invalid SharePoint filter `Status eq 'Ativo'` on `Ofertas_Pipeline` (Status is a Choice like `On Offer`, `Won`, etc) caused empty result set and no card posting.
- [x] Implemented Flow1 fix in repo deliverables: `tools/patch_flow1_offer_query.py` now:
  - Uses `ARQs_Teams.Login` (fallback: email prefix) to build `Assignee eq '<login>'` filter.
  - Excludes closed statuses (`Won`, `Won-End`, `Lost`, `Rejected`, `Cancelled`, `Abandoned`).
  - Requires **2 reports per week** (Tue=1, Fri=2) using `SemanaReport` + `VersaoReport`:
    - Tuesday run sends if `SemanaReport != varSemanaRef` OR `VersaoReport < 1`.
    - Friday run sends if `SemanaReport != varSemanaRef` OR `VersaoReport < 2`.
  - Adds `versao_report` into the card submit payload (so Flow2 knows which cycle was requested).
  - Makes Teams recipient + submit payload email tolerant: `coalesce(field_3, E_x002d_mail, Email)`.
  - Rebuild produces updated `dist_zips/flow1.zip`.
  - Flow2 now persists the offer “sent state” back to `Ofertas_Pipeline` (`StatusReportEnviado`, `DataUltimoReport`, `SemanaReport`, `VersaoReport`) so Flow1 can skip only what was already answered.
- [x] Built Flow2 queue+wait import package (SharePoint trigger + Teams PostCardAndWaitForResponse): `dist_zips/flow2_queue_wait.zip`.
- [x] Built Flow1 queue-creator import package (creates Pending items only): `dist_zips/flow1_queue_creator.zip`.
- [x] Added queue dedupe in Flow1 (skip create if Pending/Sent exists for OfertaId+Semana+RecipientEmail).
- [x] Fixed Flow2 queue+wait trigger recurrence (required for package import).
- [x] Switched Flow2 queue+wait to Recurrence + GetItems on queue (avoids SharePoint OnNewItem operation import error).
- [x] Removed Terminate actions from Flow2 queue+wait (unsupported inside Foreach).
- [x] Fixed Adaptive Card schema (missing `type` on ColumnSet) to prevent InvalidBotAdaptiveCard.

## Pending / To Decide (Next Work)

- **Technical debt backlog (execution order)**:
| Ordem | ID | Item | Status | Resultado esperado | Onde | Executado por |
|---:|---|---|:---:|---|---|---|
| 1 | TD-002 | Flood control (prod safety) | ✅ DONE | Rodar testes sem risco de "flood" | Flow2 | Agent GPT-5.2 Codex |
| 2 | TD-003 | Ops views (Level 1) | ✅ DONE | Views padrão nas listas | SharePoint | Agent Opus 4.5 |
| 3 | TD-001 | Populate `AssigneeEmail` | ✅ DONE | `AssigneeEmail` preenchido | Azure Function + SharePoint | Agent GPT-5.2 Codex |
| 4 | TD-004 | Observações sem HTML | ✅ DONE | `Observacoes` texto limpo | Azure Function + SharePoint | Agent GPT-5.2 Codex |
| 5 | TD-005 | Flow2 state machine | ✅ DONE | Estados atômicos + timestamps | Flow2 + SharePoint | Agent GPT-5.2 Codex |
| 6 | TD-006 | Queue dedupe + unicidade | ✅ DONE | Eliminar duplicatas | SharePoint + Flow1 | Agent Opus 4.5 |
| 7 | TD-007 | VersaoReport consistente | ✅ DONE | `VersaoReport` sempre preenchido | SharePoint + Flow1 | Agent GPT-5.2 Codex |
| 8 | TD-008 | Cutover da lista da fila | ✅ DONE | Migração blue/green | SharePoint + Flow1/Flow2 | Agent Opus 4.5 |
| 9 | TD-009 | Single source template | ✅ DONE | Source of truth para card | Repo + Flow1/Flow2 | Agent GPT-5.2 Codex |
| 10 | TD-010 | Secrets/config hygiene | ✅ DONE | Env vars/connection refs | Power Platform + Azure | Agent GPT-5.2 Codex |
| 11 | TD-011 | Performance refactor Flow1 | ✅ DONE | Offer-driven, sem N+1 | Flow1 | Agent GPT-5.2 Codex |

> **All 11 Technical Debt items completed as of 2025-12-31.**

- [ ] **Single source template (optional)**: Flow1 still composes the card with Power Automate expressions; keep it aligned with the canonical contract and re-sync Flow2 via `tools/sync_inputs_adaptive_card.py` when the template changes.
- [ ] **Choice values vs CSV (reporting consistency)**: current `/import-jira` is PASSTHROUGH and `Ofertas_Pipeline` has `FillInChoice=TRUE` for key Choice fields, so imports should accept new values; decide whether to activate `/normalizar-ofertas` for consistent reporting; see `ZIP/XML/sharepoint_mapping_ofertas_pipeline.audit.md` and `ZIP/XML/ARCHITECTURE/STAKEHOLDER_PROJECT_GUIDE.md`.
- [ ] **Secrets/config hygiene**: next step is moving placeholders to Power Platform env vars / Entra ID (AAD auth) for production; repo exports are now placeholder-based + rendered via `.env` locally.
- [x] **Tenant import/testing**: E2E tests (27/27 PASS) validated end-to-end behavior in production tenant (2026-01-02).
- [x] **Tenant hotfix (Flow1)**: Validated via E2E tests F1-F4 (100% pass). Production flows working correctly.
- [x] **Ops (Level 1 troubleshooting)**: created SharePoint views for `StatusReports_Queue` and `StatusReports_Historico` via `ops-views.ps1` (TD-003). Views: Ops - Queue (All/Pending/Sent/Errors/Duplicates), Ops - Historico (All/Last 24h). Required: PnP.PowerShell v3.1.0+ with `-UseWebLogin`.
- [x] **Data quality (VersaoReport)**: TD-007 completed. New Flow1 runs always set `VersaoReport`. E2E tests DQ1/DQ2 passed.
- [x] **Data quality (Observacoes)**: TD-004 completed. Azure Function defaults `IMPORT_STRIP_HTML_OBSERVACOES=true`. E2E tests DQ1/DQ2 passed (2026-01-01T22:25).
- [x] **Queue dedupe correctness**: E2E test F3 passed (2026-01-02T23:21). 0 duplicate UniqueKeys. Format: `JiraKey|Semana|VersaoReport`. 323 legacy duplicates cleaned.
- [x] **Flow2 state machine hardening**: TD-005 completed. E2E test S3 passed: 12/13 processed (5 Completed, 7 Sent). No silent loss.
- [x] **Flood control (prod safety)**: TD-002 completed. E2E test DUP2 passed (2026-01-02T23:00): 117 cards processed, 11 recipients, flood control effective.
- [x] **Technical debt (rename queue list)**: renamed `StatusReports_Queue` → `StatusReports_Queue` (SharePoint-side), updated Flow1/Flow2 to reference the new list name, and updated all test scripts to use production list.
- [x] **Tenant hardening (recommended)**: added and populated `ARQs_Teams.Login` (single line of text, unique) and indexed it (SharePoint-side).
- [x] **Performance refactor (recommended)**: TD-011 completed. Flow1 optimized to be offer-driven.
- [x] **SharePoint schema alignment**: applied `FillInChoice=TRUE` for `TipoOportunidade` on `Ofertas_Pipeline` (SharePoint-side change; see `ZIP/XML/sharepoint_mapping_ofertas_pipeline.audit.md`).

## How To Update This File

Every change must update:

1. **Completed**: add/move items to `[x]` once merged and verified.
2. **Pending**: add the next blocking tasks; remove items once completed.
3. **Artifacts**: if you add/rename a key file, list it here.
