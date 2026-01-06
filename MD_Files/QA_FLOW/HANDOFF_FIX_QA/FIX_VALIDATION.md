# Fix Plan: Adaptive Card Validation Logic

**Objective:** Correctly enforce "Vermelho requires Observações" and "RFI/RFQ requires RFP ID" in Flow2.

## 1. Current Bug (C3)
**Issue:** `Status=Vermelho` with empty `Observações` is accepted.
**Cause:** The condition expression likely checks for `null` but not empty string `""` or whitespace, OR the failure branch isn't terminating.

### Fix
Update the "Condition - Validate Status" expression in Flow2:

```excel
@and(
    equals(triggerBody()?['data']?['status_projeto'], 'Vermelho'),
    empty(trim(coalesce(triggerBody()?['data']?['observacoes'], '')))
)
```
*If True → Post failure card + Terminate.*

## 2. Missing Validation (D1-D4)
**Issue:** No validation for "Tipo de Oportunidade" (RFI/RFQ needs RFP Id).

### Fix
Add a new Condition block "Condition - Validate Tipo":

```excel
@and(
    or(
        equals(triggerBody()?['data']?['tipo_demanda'], 'RFI'),
        equals(triggerBody()?['data']?['tipo_demanda'], 'RFQ')
    ),
    empty(trim(coalesce(triggerBody()?['data']?['rfp_relacionada'], '')))
)
```
*If True → Post failure card (generic error or specific "RFP Required") + Terminate.*

## 3. Implementation Steps
1. Open Flow2 (Worker) in Edit mode.
2. Locate the "Switch - Handle Response" or main Sequence.
3. Insert these Conditions **before** the "Update Item" / "Create History" actions.
4. **True Branch (Error):**
   - Action: `Post card in a chat or channel` (same card but with Error message variable set).
   - Action: `Terminate` (Succeeded/Cancelled) to stop processing.
5. **False Branch (Success):** Continue to existing logic.

## 4. Retest
- Run Test C3 (Vermelho + Empty) → Should Fail
- Run Test D2 (RFI + Empty) → Should Fail
- Run Test D4 (RFI + Filled) → Should Pass
