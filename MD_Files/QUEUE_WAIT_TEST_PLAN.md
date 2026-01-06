# Queue + Wait Architecture - Test Plan

> **Scope**: Minimal test with 1 queue item and 1 recipient  
> **Estimated time**: 10-15 minutes

---

## Pre-Test Setup

### 1. Verify SharePoint Lists

| List | Check |
|------|-------|
| `StatusReports_Queue` | ✅ All columns created, UniqueKey is UNIQUE |
| `ARQs_Teams` | ✅ Your user exists with `Status=Ativo` and valid email |
| `Ofertas_Pipeline` | ✅ Test offer exists (see below) |
| `StatusReports_Historico` | ✅ List exists with correct columns |

### 2. Create Test Offer

In `Ofertas_Pipeline`, create or identify an item:

```
JiraKey: TEST-QW-001
Status: Under Study (or any non-closed status)
Assignee: [your login from ARQs_Teams]
SemanaReport: (leave empty or set to old value like "01/2024")
VersaoReport: 0
Est_x002e_BudgetInicio: 100 (required field!)
```

---

## Test Execution

### Test A: Flow1 - Queue Creation

1. **Run Flow1 manually** (or wait for schedule)

2. **Check `StatusReports_Queue`**:
   - [ ] New item created
   - [ ] `QueueStatus` = `Pending`
   - [ ] `RecipientEmail` = your email
   - [ ] `JiraKey` = `TEST-QW-001`
   - [ ] `UniqueKey` = `TEST-QW-001|WW/2025|1` (or 2)
   - [ ] `AttemptCount` = 0

3. **Run Flow1 again**:
   - [ ] NO duplicate created (UniqueKey blocks it)
   - [ ] Flow completes without errors

---

### Test B: Flow2 - Worker Response

1. **Flow2 auto-triggers** when queue item is created

2. **Check queue item** (after ~30 seconds):
   - [ ] `QueueStatus` changed to `Sent`
   - [ ] `SentAt` populated
   - [ ] `AttemptCount` = 1

3. **Check Teams**:
   - [ ] Adaptive Card received in 1:1 chat with Flow bot
   - [ ] Card displays offer info correctly

4. **Fill and Submit Card**:
   - Status Atual: `em_desenvolvimento`
   - Status Projeto: `Verde`
   - Reunião Cliente: Yes
   - Probabilidade: 75%
   - Observações: "Test submission"
   - Click **Enviar Status Report**

5. **Check queue item**:
   - [ ] `QueueStatus` = `Completed`
   - [ ] `CompletedAt` populated
   - [ ] `ResponseJson` contains JSON with your responses

6. **Check `StatusReports_Historico`**:
   - [ ] New item created
   - [ ] All fields mapped correctly
   - [ ] `RespostaJSON` populated

7. **Check `Ofertas_Pipeline` (TEST-QW-001)**:
   - [ ] `SemanaReport` = current week
   - [ ] `VersaoReport` = 1 or 2
   - [ ] `DataUltimoReport` = today
   - [ ] `StatusReportEnviado` = Yes

---

### Test C: Validation - Red Status

1. **Create new queue item** manually:
   ```
   QueueStatus: Pending
   RecipientEmail: your email
   JiraKey: TEST-QW-002
   OfertaId: [any valid ID]
   Semana: 52/2025
   VersaoReport: 1
   UniqueKey: TEST-QW-002|52/2025|1
   ```

2. **Wait for Flow2 to trigger**

3. **Submit card** with:
   - Status Projeto: `Vermelho`
   - Observações: (leave EMPTY)

4. **Check queue item**:
   - [ ] `QueueStatus` = `Error`
   - [ ] `LastError` contains "Vermelho requer observações"

---

## Success Criteria

| Criterion | Status |
|-----------|--------|
| Flow1 creates queue items only for actionable offers | ⬜ |
| Duplicate UniqueKey is rejected gracefully | ⬜ |
| Flow2 transitions: Pending → Sent → Completed | ⬜ |
| Adaptive Card received in Teams 1:1 chat | ⬜ |
| Response captured in `ResponseJson` | ⬜ |
| `StatusReports_Historico` item created | ⬜ |
| `Ofertas_Pipeline` updated correctly | ⬜ |
| Red status validation works | ⬜ |

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Queue item not created | Flow1 run history, ARQs_Teams has active architect |
| Card not received | Teams app permissions, recipient email correct |
| Status code 100 | Bot not installed for recipient |
| Status code 300 | User was in active conversation |
| Historico not created | Field mapping errors in Flow2 |
| Ofertas_Pipeline error | Missing required field `Est_x002e_BudgetInicio` |
