# QA Plan (Massive / Full-Scope) — Power Automate + SharePoint + Teams + Azure Functions

This plan is designed for **production-grade quality**:
- Default verification is **Level 1 (tables)**: validate state transitions directly in SharePoint lists.
- Level 2 (flows/run history) is only used when Level 1 evidence is insufficient.
- Every test run produces evidence (IDs, timestamps, screenshots/logs) and is structured to prevent flooding real users.

This repo can only provide the plan and offline artifact validation; tenant-side execution uses your available automation agents (browser/PowerShell/M365 MCP).

## Non-negotiable gating (do not mix implementation with QA)

- **QA execution must start only after all technical debts (TD-001..TD-011) are applied and peer-reviewed.**
- **Do not run QA while technical debt work is in progress** (avoids invalid results, false failures, and accidental flooding).
- **QA execution owner**: Agent Opus 4.5 (per agreement).
- **Implementation owners**: as defined in `CHECKPOINT.md` (each TD has an explicit agent owner).
- **Recipient safety (hard constraint)**: during QA, the only allowed Teams recipient is `mbenicios@minsait.com`.
  - If there is any possibility that another user can receive a card/message, **do not run the test**.
  - Mark the case as **BLOCKED (business hours validation required)** and schedule it for business hours.

## 0) Scope (what must be tested)

**Flows**
- Flow1: queue creator (`StatusReports_Queue` → `Pending`)
- Flow2: queue processor + Teams card + response persistence (queue → Teams → `StatusReports_Historico` + legacy writes)
- Flow3: consolidation + Teams post (optional for this QA cycle)
- Flow4: JIRA CSV import via Azure Function (data quality + Observacoes sanitization)

**Data stores**
- SharePoint lists: `ARQs_Teams`, `Ofertas_Pipeline`, `StatusReports_Queue`, `StatusReports_Historico`, `Atualizacoes_Semanais`

**UX surface**
- Teams Adaptive Card: every control (radio/choice/checkbox/date/text/toggles) and the submit button behavior.

## 1) Test governance (non-negotiables)

### A. Safety / flood control

- Only run mass tests with an **allowlist** (e.g., your recipient only) until exit criteria are met.
- In Flow2, set `Obter_itens_fila` to deterministic processing:
  - Filter Query: constrain to test recipient(s) or a single ID
  - `Order By: Created asc`
  - `Top Count: 1` initially (then raise gradually)
- Keep exactly one active Flow2 per `cardTypeId` to avoid trigger routing conflicts.

### B. Evidence requirements (per test case)

Capture and store:
- **Queue item**: `ID`, `JiraKey`, `OfertaId`, `Semana`, `VersaoReport`, `RecipientEmail`, `QueueStatus`, `Created`, `Modified` (+ `SentAt`, `CompletedAt`, `AttemptCount` if present)
- **History item**: `Title/JiraKey`, `OfertaId`, `Semana`, `VersaoNumero`, `ArquitetoEmail`, `DataPreenchimento`, `RespostaJSON`
- **Teams**: screenshot of the card and “resposta enviada” confirmation
- **Timestamps**: local time + UTC where possible

### C. Test case template (for the virtual agent)

- `TestId`:
- `StartTime`:
- `Environment`:
- `FlowsEnabled`:
- `Flow2Filter`:
- `InputData` (Queue IDs / JiraKeys):
- `Steps`:
- `Expected`:
- `Observed`:
- `Evidence` (IDs, screenshots, URLs):
- `Pass/Fail`:
- `Notes/Gaps`:

## 2) Automated preflight (offline / repo-local gates)

### A. Artifact build + validation (must pass)

- Build artifacts: `bash tools/build_deploy_artifacts.sh .env`
- Validate zips: `python tools/validate_flow_exports.py --zips dist_zips/*.zip`

Prevents:
- Split expressions exported as JSON arrays (import failure)
- Expression-like strings missing `@` (import failure)
- Unbalanced parentheses/quotes in expressions (import/runtime failure)

### B. Adaptive Card rendering sanity

- Render template with sample data (non-strict):\
  `python render_adaptive_card.py --template adaptive_card_final_prodction.json --data adaptive_card.data.json --non-strict --out /dev/null --no-teams-payload`

## 3) Level 1 verification standard (tables-first)

### A. Required SharePoint views (create once)

Create a view for `StatusReports_Queue` including at least:
- `ID`, `Created`, `Modified`, `QueueStatus`, `RecipientEmail`, `JiraKey`, `OfertaId`, `Semana`, `VersaoReport`, `UniqueKey`, `SentAt`, `CompletedAt`, `AttemptCount`

Create a view for `StatusReports_Historico` including at least:
- `Created`, `Title (JiraKey)`, `OfertaId`, `Semana`, `VersaoNumero`, `ArquitetoEmail`, `StatusProjeto`, `StatusAtual`, `Observacoes`, `RespostaJSON`

### B. How to “prove” each component works (Level 1)

- Flow1 worked if new rows appear in `StatusReports_Queue` with `QueueStatus=Pending` and correct keys.
- Flow2 “sent” worked if those rows transition `Pending → Sent` (and ideally `SentAt` is stamped).
- Flow2 “response” worked if `StatusReports_Historico` gets a new row after card submit.
- Data quality worked if `Observacoes` is plain text (no HTML tags) in `Ofertas_Pipeline` and downstream.

## 4) Test suite: Flow1 (Queue Creator)

### F1. Happy path (creates Pending)

- Preconditions: `ARQs_Teams` has your user active; `Ofertas_Pipeline` has open offers assigned to you.
- Action: run Flow1 manually once.
- Verify (queue): N new rows for your recipient with:
  - `QueueStatus=Pending`
  - `Semana` matches current `varSemanaRef`
  - `VersaoReport` matches current cycle

### F2. Dedupe correctness (no duplicate for Pending/Sent)

- Action: run Flow1 twice back-to-back.
- Verify (queue): for each `(OfertaId, Semana, RecipientEmail)` there is at most 1 row where `QueueStatus in (Pending, Sent)`.

### F3. Concurrency / race test

- Action: run Flow1 concurrently (or run two versions if ever enabled by mistake).
- Verify: duplicates must not be created; if duplicates appear, treat as a release blocker.

### F4. Field population robustness

Run with these data variants:
- Email is present only in `E_x002d_mail` (field_3 empty)
- Email is present only in `field_3` (E_x002d_mail empty)
- JiraKey missing/empty (should not create queue item or should create with safe defaults — define expected behavior and enforce it)

## 5) Test suite: Flow2 (Queue Wait + Card + Response)

### Configuration for safe testing (night mode)

In `Obter_itens_fila` use:
- Filter Query: `QueueStatus eq 'Pending' and (RecipientEmail eq '<your email>' or RecipientEmail eq '<your login>')`
- Order By: `Created asc`
- Top Count: `1`

**Hard constraint (current night safety)**:
- Replace the filter query with: `QueueStatus eq 'Pending' and RecipientEmail eq 'mbenicios@minsait.com'`
- If you cannot guarantee this constraint, mark the test as **BLOCKED (business hours validation required)**.

### S1. “Send card” (one item only)

- Setup: select a single queue row for you and set `QueueStatus=Pending`.
- Action: run Flow2 once.
- Verify (queue): selected row transitions to `Sent`.
- Verify (Teams): exactly one card arrives in “Chat with Flow bot”.

### S2. “Submit card” (happy path)

- Action: fill the card with valid values and click submit.
- Verify (history): a new `StatusReports_Historico` row is created for that `JiraKey` and `OfertaId`.

### S3. State machine correctness (no silent loss)

This is a release blocker if violated:
- If card post fails, queue item must not remain silently stuck in `Sent` with no evidence.
- If Flow2 marks `Sent` before posting, test must confirm it can retry safely (requires `AttemptCount` and/or an `Error` status).

### S4. Retry behavior (idempotency)

- Action: set same item back to `Pending` and rerun Flow2.
- Expected: either (a) Flow2 prevents duplicate card sends based on state, or (b) Flow2 increments attempt and sends again only if policy allows.
- Verify: no duplicate `StatusReports_Historico` rows for the same submit unless explicitly allowed.

## 6) Adaptive Card “Every Button” matrix (FULL SCOPE)

The virtual agent must exercise every control and each conditional path.

### A. Baseline: controls present & rendered

- Verify card header shows `JiraKey`, `Title`, `Semana`.
- Verify all expected controls are visible or conditionally visible as designed.

### B. ToggleVisibility sections

For each section (`Risks & Opportunities`, `Decision / Ask`):
- Test expand/collapse.
- Fill text (min length, max length).
- Submit with section collapsed and with section expanded.

### C. StatusProjeto radio group (3 paths)

Run 3 cases:
- `Verde` + Observacoes empty → submit allowed.
- `Amarelo` + Observacoes empty → submit allowed (unless business rule says otherwise).
- `Vermelho` + Observacoes empty → submit must be rejected by Flow2 with user feedback.
- `Vermelho` + Observacoes non-empty → submit allowed.

### D. TipoOportunidade (RFP/RFI/RFQ/Oferta)

Run cases:
- `Oferta` → `rfp_relacionada` optional.
- `RFI` with empty `rfp_relacionada` → reject with feedback.
- `RFQ` with empty `rfp_relacionada` → reject with feedback.
- `RFI/RFQ` with filled `rfp_relacionada` → allow.

### E. Checkbox-driven conditionals

For each checkbox:
- unchecked → submit
- checked → verify any dependent fields appear/are saved

Examples:
- `Houve reunião com cliente esta semana?`:
  - If checked: validate “Tipo de reunião” must be selectable and saved.
  - If unchecked: “Tipo de reunião” should not block submit.

### F. Data typing / validation

- Date: empty vs filled vs invalid (if UI allows).
- Numeric (`% Budget Consumido`): `0`, `100`, out-of-range, non-numeric (if UI allows).
- Long text: max length stress for `Observacoes`, `Risks`, `Decision`.

### G. Payload contract (must be present in `RespostaJSON`)

Confirm `RespostaJSON` includes the expected keys (at least):
- `jirakey`, `oferta_id`, `semana`, `arquiteto_email`, `cardTypeId`

## 7) Data quality: Observacoes sanitization (JIRA → SharePoint → Teams)

### DQ1. Azure Function setting is enabled

- Ensure deployed Azure Function has `IMPORT_STRIP_HTML_OBSERVACOES=true` (see `ZIP/Azure_Function/DEPLOY_CHECKLIST.md`).

### DQ2. Import with HTML samples

Use at least 10 real-world Observations samples that include:
- `<div class=...>`
- `<br>` and lists (`<li>`)
- HTML entities (`&gt;`, `&nbsp;`)

Verify:
- `Ofertas_Pipeline.Observacoes` is plain text (no tags).
- Card prefill for Observacoes is plain text.
- `StatusReports_Historico.Observacoes` does not store raw HTML.

## 8) Duplicates & trust protection (production readiness)

### DUP1. Queue duplicates detection

- Query `StatusReports_Queue` grouped by `(OfertaId, Semana, RecipientEmail)` and count > 1.
- If duplicates exist: do not proceed to broad rollout until:
  - uniqueness strategy is defined (UniqueKey enforced) and
  - cleanup procedure is executed.

### DUP2. Flood control test

- Create 20 pending items for your recipient only.
- Run Flow2 with `Top Count=1`, then `3`, then `10`.
- Verify exactly N cards are sent per run and no other recipients are touched.

## 9) Production deployment guardrails

### A. Change control

- Versioned release (`_vNN`).
- Disable older versions sharing `cardTypeId`.

### B. Post-deploy smoke (timeboxed but complete)

- Run Flow1 manually once (test recipient only).
- Run Flow2 once (Top Count=1).
- Submit one card and verify `StatusReports_Historico` row creation.

## 10) Exit criteria (no compromise)

Before enabling for all ARQs:
- 100% pass for Flow1 + Flow2 suites (F1–F4, S1–S4).
- 100% pass for Adaptive Card matrix (all branches and buttons).
- Observacoes sanitization passes with real HTML samples (DQ1–DQ2).
- No duplicates created during controlled reruns; known duplicates are remediated or blocked by uniqueness.
