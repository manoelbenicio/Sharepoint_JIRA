# Power Automate Copilot - Step-by-Step Flow Creation

> **Strategy**: Use short, phased prompts. After each phase, verify Copilot created it correctly before proceeding.

---

## Prerequisites

- SharePoint Site: `https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA`
- Lists: `Ofertas_Pipeline`, `StatusReports_Queue`, `StatusReports_Historico`
- Function Key: REDACTED_FUNCTION_KEY`

---

# 🔵 FLOW 1: Queue Creator

## Phase 1: Create Trigger

**Go to**: https://make.powerautomate.com → Create → Describe to design

**Prompt 1:**
```
Create an automated flow that triggers when an item is created or modified 
in SharePoint list "Ofertas_Pipeline"
```

✅ **Verify**: SharePoint trigger appears with your site/list

---

## Phase 2: Initialize Variables

**Prompt 2:**
```
Add 3 variables at the start:
- varCurrentDate as String
- varUniqueKey as String  
- varRecipientEmail as String
```

✅ **Verify**: 3 Initialize Variable actions added

---

## Phase 3: Get Item Details

**Prompt 3:**
```
Get the SharePoint item that triggered the flow using its ID
```

✅ **Verify**: "Get item" action added with ID from trigger

---

## Phase 4: Add Main Condition

**Prompt 4:**
```
Add a condition to check if field "Status" equals "Em Acompanhamento"
```

✅ **Verify**: Condition block with Status = "Em Acompanhamento"

---

## Phase 5: Check Architect Assignment

**Prompt 5:**
```
Inside the Yes branch, add another condition to check if 
"Arquiteto Responsavel" is not empty
```

✅ **Verify**: Nested condition checking architect field

---

## Phase 6: Set Variables

**Prompt 6:**
```
In the inner Yes branch, set these variables:
- varCurrentDate to current UTC time formatted as yyyy-MM-dd
- varUniqueKey to concatenation of JiraKey and current date
- varRecipientEmail to the Arquiteto Responsavel email
```

✅ **Verify**: 3 Set Variable actions with correct expressions

---

## Phase 7: Create Queue Item

**Prompt 7:**
```
Create a new item in SharePoint list "StatusReports_Queue" with:
- Title: JiraKey from trigger
- JiraKey: JiraKey from trigger
- RecipientEmail: varRecipientEmail variable
- QueueStatus: "Pending"
- UniqueKey: varUniqueKey variable
- CreatedDateTime: current timestamp
```

✅ **Verify**: Create item action with all fields mapped

---

## Phase 8: Add Error Handling

**Prompt 8:**
```
Wrap the create item action in a Scope called "Try Create Queue Item" 
and add a parallel Scope called "Catch Error" that runs if the first fails
```

✅ **Verify**: Try/Catch pattern with Configure run after

---

## Phase 9: Save and Name

**Save the flow as:** `Flow1_QueueCreator_StatusReports`

---

# 🟢 FLOW 2: Worker (Response Handler)

## Phase 1: Create Trigger

**Go to**: https://make.powerautomate.com → Create → Describe to design

**Prompt 1:**
```
Create an automated flow triggered when an item is created 
in SharePoint list "StatusReports_Queue"
```

✅ **Verify**: SharePoint "When item is created" trigger

---

## Phase 2: Check Queue Status

**Prompt 2:**
```
Add a condition to check if field "QueueStatus" equals "Pending"
```

✅ **Verify**: Condition checking QueueStatus

---

## Phase 3: Update to Sent

**Prompt 3:**
```
In the Yes branch, update the SharePoint item to set QueueStatus to "Sent" 
and SentDateTime to current timestamp
```

✅ **Verify**: Update item action with QueueStatus = "Sent"

---

## Phase 4: Get Offer Details

**Prompt 4:**
```
Get the item from SharePoint list "Ofertas_Pipeline" where JiraKey 
matches the JiraKey from the queue item
```

✅ **Verify**: Get items action with filter by JiraKey

---

## Phase 5: Post Adaptive Card

**Prompt 5:**
```
Post an Adaptive Card to Teams user using the RecipientEmail field 
and wait for a response with timeout of 3 days
```

✅ **Verify**: "Post adaptive card and wait" action appears

**Then manually**: Paste the Adaptive Card JSON from `StatusReport_AdaptiveCard_v1.4.json`

---

## Phase 6: Handle Response

**Prompt 6:**
```
After the card response, update the queue item with:
- QueueStatus: "Completed"
- CompletedDateTime: current timestamp
- ResponseData: the response body from the card
```

✅ **Verify**: Update item action with response data

---

## Phase 7: Create History Record

**Prompt 7:**
```
Create a new item in SharePoint list "StatusReports_Historico" with:
- Title: JiraKey
- JiraKey: from queue item
- StatusSemanal: from card response
- Observacoes: from card response
- DataColeta: current date
- Arquiteto: RecipientEmail
```

✅ **Verify**: Create item in StatusReports_Historico

---

## Phase 8: Update Original Offer

**Prompt 8:**
```
Update the item in "Ofertas_Pipeline" list to set:
- UltimoStatus: the StatusSemanal from card response
- DataUltimoStatus: current date
```

✅ **Verify**: Update item action on Ofertas_Pipeline

---

## Phase 9: Add Validation

**Prompt 9:**
```
Before the update, add a condition: if StatusSemanal equals "Vermelho" 
AND Observacoes is empty, terminate the flow with status Failed 
and message "Red status requires observations"
```

✅ **Verify**: Validation condition with Terminate action

---

## Phase 10: Error Handling

**Prompt 10:**
```
Wrap all actions after the condition in a Scope called "Process Response"
Add a parallel Scope "Handle Error" that updates QueueStatus to "Error" if Process fails
```

✅ **Verify**: Try/Catch pattern

---

## Phase 11: Save and Name

**Save the flow as:** `Flow2_Worker_StatusReports`

---

# ✅ Post-Creation Checklist

| Step | Flow1 | Flow2 |
|------|-------|-------|
| Trigger configured | ☐ | ☐ |
| Variables initialized | ☐ | N/A |
| Conditions added | ☐ | ☐ |
| SharePoint actions work | ☐ | ☐ |
| Error handling added | ☐ | ☐ |
| Flow saved | ☐ | ☐ |
| Flow turned ON | ☐ | ☐ |

---

# 🧪 Quick Test

1. Modify an offer in `Ofertas_Pipeline` with Status = "Em Acompanhamento"
2. Check `StatusReports_Queue` for new item
3. Respond to Adaptive Card in Teams
4. Verify `StatusReports_Historico` has new record
