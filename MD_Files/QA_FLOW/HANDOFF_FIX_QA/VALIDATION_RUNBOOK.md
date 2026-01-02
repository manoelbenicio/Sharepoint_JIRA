# Validation Runbook (After Import)

Goal: validate end-to-end behavior in the target Power Platform environment after importing `dist_zips/*.zip`.

## Optional: Reset Data For Testing (Recommended)

If you want a clean test run (15–30 records), purge the lists **in the TEST site/environment only**:

- `Ofertas_Pipeline` (offers)
- `Atualizacoes_Semanais` (legacy weekly updates)
- `StatusReports_Historico` (raw submissions history)

Fastest manual approach (small volumes):
- Open each list in SharePoint → select all items in the view → Delete.

If you want a **repeatable automated purge**, we can add an **admin-only** Azure Function endpoint (guarded by env flags + confirmation token), but the Azure Function source code (`function_app.py`) is not in this repo.
Update: Azure Function code is available in `ZIP/Azure_Function/function_app.py` and now includes `/api/lab/purge-lists` (see `ZIP/Azure_Function/LAB_PURGE_ENDPOINT.md`).

## Pre-checks (before running anything)

- Confirm connections are **Connected** for SharePoint + Teams in all imported flows.
- Confirm the SharePoint site URL used in the flows is correct (dataset parameter).
- Confirm lists exist (GUIDs in `CHECKPOINT.md`) and the service account has permission:
  - `Ofertas_Pipeline`
  - `Atualizacoes_Semanais`
  - `StatusReports_Historico`
  - `ARQs_Teams`

## Flow4 (Import JIRA CSV → Ofertas_Pipeline)

1) Upload the latest CSV into the SharePoint folder `JIRA_Imports`.
2) Verify Flow4 run succeeds and posts the “IMPORT JIRA CONCLUÍDO” card in the configured Teams channel.
3) Verify `Ofertas_Pipeline` received new/updated items and key fields are not null unexpectedly.
4) If import fails: check the HTTP action response body (Azure Function error) and confirm the `?code=` used is valid.

## Flow1 (Send weekly cards)

Designer note: if you see `AxiosError` / `Request failed with status code 400` when clicking **Save**, force the classic designer:
- Turn **Novo designer** OFF, then refresh; or
- Edit URL adding `?v3=false` (or `&v3=false`) and reload.
This is a Power Automate UI issue and does not affect end users.

If Save fails with `InvalidVariableOperation` mentioning `varVersaoAlvo must be initialized before it can be used`, you imported an older Flow1 package. Import the latest `dist_zips/flow1.zip` (it initializes `varVersaoAlvo` in its own step before `Obter_itens_1`).

1) Ensure `ARQs_Teams` has at least one active architect (`Status = Ativo`) with a valid email.
2) Ensure `Ofertas_Pipeline` has at least one active offer assigned to that architect.
3) Trigger Flow1 manually (“Run”) to avoid waiting for recurrence.
4) Verify the architect receives an Adaptive Card and can submit it.

Troubleshooting (common): if Flow1 run is green but no cards arrive:
- Check Flow1 action `Obter itens 1` filter query. It must NOT use `Status eq 'Ativo'` (Ofertas_Pipeline.Status values are `Under Study`, `On Offer`, `Won`, etc).
- In LAB/testing, filter only by `Assignee eq '<login>'` to guarantee cards are sent (no gates).
- Fix options:
  - **Fastest (LAB)**: edit the flow → action `Obter itens 1` → Filter Query → set to only:
    - `concat('Assignee eq ''', toLower(trim(items('Aplicar_a_cada')?['Login'])), '''')`
  - **Cleanest (recommended)**: import the updated `dist_zips/flow1.zip` as `Fluxo1_Trigger_PROD_v6` (disable `_v5`), then run `_v6`.

Flow1 `_v6` default gating (to keep volume low and performance stable):
- Only sends for offers where `Assignee == ARQs_Teams.Login`.
- Skips closed statuses: `Won`, `Won-End`, `Lost`, `Rejected`, `Cancelled`, `Abandoned`.
- Requires **2 submissions per week** (Tue + Fri) using `SemanaReport` + `VersaoReport`:
  - Tuesday cycle (`varVersaoAlvo = 1`) sends if `SemanaReport != varSemanaRef` OR `VersaoReport < 1`.
  - Friday cycle (`varVersaoAlvo = 2`) sends if `SemanaReport != varSemanaRef` OR `VersaoReport < 2`.
  - When the ARQ submits, Flow2 updates `Ofertas_Pipeline` (`StatusReportEnviado=true`, `DataUltimoReport`, `SemanaReport`, `VersaoReport`).

## Flow2 (Card submit handler + validation)

Designer note: Flow2 uses the Teams trigger “When someone responds to an adaptive card”, which is currently **not supported by the Novo designer**. This warning is expected and is only shown to makers while editing; it does not impact runtime/production behavior. Keep **Novo designer** OFF for Flow2 (use `?v3=false`).

Runtime note (important): for Flow2 to fire, the Adaptive Card must be posted by **Flow bot** in a **1:1 chat** (the Flow bot conversation). If you post the card to a Teams **channel**, Teams often shows “Não é possível acessar o aplicativo” on submit and Flow2 will not trigger.

Runtime note (important #2): `CardTypeId` must be **unique per environment**. If you have multiple Flow2 versions enabled (ex: `_v5` and `_v6`) using the same `CardTypeId` (`status_report_v1`), Teams may show “Não é possível acessar o aplicativo” and no Flow2 run will appear. Keep only ONE Flow2 enabled per `CardTypeId`.
Current packages use `CardTypeId = status_report_v2`. If the tenant has any old Flow2 still registered with `status_report_v1`, disable/delete it to avoid routing conflicts.

Note: If Flow2 import/save fails with `OpenApiOperationParameterValidationFailed` mentioning missing required property `item/Est_x002e_BudgetInicio`, you must use the latest `dist_zips/flow2.zip` (it patches the offer using the existing `Est_x002e_BudgetInicio` value).

### Test A (happy path)
1) Submit card with `status_projeto = Verde`, `tipo_demanda = Oferta` (or RFP), and any observations.
2) Verify:
   - One new item in `StatusReports_Historico` with `RespostaJSON`.
   - One new item in `Atualizacoes_Semanais` (legacy fields).

### Test A2 (rule: RFI/RFQ requires rfp_relacionada)
1) Submit card with `tipo_demanda = RFI` or `RFQ` and leave `rfp_relacionada` empty.
2) Verify:
   - Flow2 sends a Teams message asking to re-submit with `RFP relacionada`.
   - No new items are created in `StatusReports_Historico` or `Atualizacoes_Semanais` for this submission.

### Test B (rule: Vermelho requires observacoes)
1) Submit card with `status_projeto = Vermelho` and leave `observacoes` empty.
2) Verify:
   - Flow2 sends a Teams message asking to re-submit with observations.
   - No new items are created in `StatusReports_Historico` or `Atualizacoes_Semanais` for this submission.

## Note: JIRA Observacoes may contain HTML

If the `Observações` field is prefilled with HTML (e.g. `<div class="ExternalClass...">`, `&gt;`), enable sanitization in Azure Function `/api/import-jira` using app setting `IMPORT_STRIP_HTML_OBSERVACOES=true` and re-run Flow4 import so SharePoint `Ofertas_Pipeline.Observacoes` is updated with clean text.

## Note: Collapsible sections in Teams

The card uses `Action.ToggleVisibility` to keep `Risks & Opportunities` and `Decision / Ask` collapsed by default. If your Teams client does not render the toggle, the fallback is to keep those inputs always visible (we can switch if needed).

## Flow3 (Consolidation C‑Level)

1) Trigger Flow3 manually (“Run”).
2) Verify it calls Azure Function `/consolidar-v2` and posts the returned `teams_card_html` in the Teams channel.
3) If consolidation output is blank/broken: validate the function response contains `teams_card_html`.

## Common Failures (Fast Triage)

- **401/403 from Azure Function**: wrong function key (`?code=`). Update `.env`, rebuild `dist_zips/`, re-import (or edit the HTTP action in the flow).
- **Card submits but Flow2 not triggered**: wrong Teams trigger registration / cardTypeId mismatch. Re-import Flow2 and ensure `inputsAdaptiveCard` matches `adaptive_card_final_prodction.json`.
- **SharePoint “not found”**: wrong list GUID or site URL in the dataset parameter.

## Performance Notes (If Flow1 feels slow)

Power Automate connectors are latency-bound. The biggest slowdown is usually **many sequential SharePoint calls** + **many Teams posts**.

Quick wins (no redesign):
- Ensure `Ofertas_Pipeline.Assignee` is **indexed** (List settings → Indexed columns). Optional: index `ARQs_Teams.Status` and `ARQs_Teams.Login`.
- In Flow1, enable **Concurrency control** on the outer `Aplicar a cada` (ARQs loop) and set a small degree (e.g. `5`). Keep Teams posting sequential if you hit throttling.
- In `Get items`, use **Limit columns by view** (create a view with only needed columns) to reduce payload/latency.

Scalable redesign (optional):
- Avoid N+1 SharePoint queries: do **one** `Get items` to fetch all offers (300 is fine) and use `Filter array` per login inside the ARQs loop.

Even more scalable (recommended if Flow1 hangs):
- Drive Flow1 by **offers** instead of **ARQs**:
  - `Get items` once for `Ofertas_Pipeline` (only actionable statuses)
  - Resolve recipient using `ARQs_Teams` (Login → Email) in-memory
  - Post cards without any “wait for response” action (responses handled by Flow2)
