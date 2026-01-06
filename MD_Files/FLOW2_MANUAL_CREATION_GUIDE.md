# Flow2: Worker - Manual Creation Guide

> **Trigger**: SharePoint "When an item is created" on `StatusReports_Queue`  
> **Purpose**: Sends adaptive card, waits for response, persists to SharePoint

---

## Prerequisites

1. ✅ Flow1 is creating queue items correctly
2. ✅ `StatusReport_AdaptiveCard_v1.4.json` file ready
3. ✅ `StatusReports_Historico` list exists

---

## Step-by-Step Creation

### 1. Create New Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **+ Create** → **Automated cloud flow**
3. Name: `Flow2_Worker_StatusReports`
4. Trigger: **When an item is created (SharePoint)**

---

### 2. Configure Trigger

```
Trigger: When an item is created
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Queue
```

---

### 3. Condition: Only Process Pending Items

```
Action: Condition
Condition: triggerOutputs()?['body/QueueStatus/Value'] is equal to Pending
```

**If No → Terminate (success)**

---

### 4. Update Queue: Mark as Sent

```
Action: SharePoint - Update item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Queue
Id: triggerOutputs()?['body/ID']

Fields:
- QueueStatus Value: Sent
- SentAt: utcNow()
- AttemptCount: add(int(coalesce(triggerOutputs()?['body/AttemptCount'], 0)), 1)
```

---

### 5. Compose: Adaptive Card JSON

```
Action: Compose
Name: AdaptiveCardJson
Inputs: [Paste entire JSON from StatusReport_AdaptiveCard_v1.4.json]
```

**Replace template variables:**
```json
// In the Inputs, replace:
"${jirakey}" → "@{triggerOutputs()?['body/JiraKey']}"
"${oferta_id}" → "@{triggerOutputs()?['body/OfertaId']}"
"${semana}" → "@{triggerOutputs()?['body/Semana']}"
"${versao_report}" → "@{triggerOutputs()?['body/VersaoReport']}"
"${arquiteto_email}" → "@{triggerOutputs()?['body/RecipientEmail']}"
```

---

### 6. Post Adaptive Card and Wait for Response

```
Action: Microsoft Teams - Post adaptive card and wait for a response

Post as: Flow bot
Post in: Chat with Flow bot
Recipient: triggerOutputs()?['body/RecipientEmail']
Adaptive Card: outputs('AdaptiveCardJson')
Update message: ✅ Resposta recebida! Obrigado pelo status report.
Should update card: Yes

Advanced options:
- If chat is active: Send
- If bot not installed: Succeed with status code
```

---

### 7. Compose: Response Data

```
Action: Compose
Name: ResponseData
Inputs: outputs('Post_adaptive_card_and_wait')?['body/data']
```

---

### 8. Compose: Status Code Check

```
Action: Compose
Name: StatusCode
Inputs: coalesce(outputs('Post_adaptive_card_and_wait')?['statusCode'], 200)
```

---

### 9. Condition: Response Successful?

```
Action: Condition
Condition: outputs('StatusCode') is equal to 200
```

**If No → Update queue as Error and terminate:**

```
Action: SharePoint - Update item (in No branch)
Id: triggerOutputs()?['body/ID']
QueueStatus Value: Error
LastError: concat('Status code: ', string(outputs('StatusCode')), ' - Bot not installed or user busy')
```

---

### 10. Validation: Red Status Requires Observacoes

```
Action: Condition
Expression:
or(
  not(equals(outputs('ResponseData')?['status_projeto'], 'Vermelho')),
  not(empty(outputs('ResponseData')?['observacoes']))
)
```

**If No (Red without observacoes) → Update Error:**

```
Action: SharePoint - Update item
QueueStatus Value: Error
LastError: Status Vermelho requer observações preenchidas
```

---

### 11. Update Queue: Mark as Completed

```
Action: SharePoint - Update item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Queue
Id: triggerOutputs()?['body/ID']

Fields:
- QueueStatus Value: Completed
- CompletedAt: utcNow()
- ResponseJson: string(outputs('Post_adaptive_card_and_wait')?['body'])
```

---

### 12. Create Item in StatusReports_Historico

```
Action: SharePoint - Create item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Historico

Fields:
- Title: triggerOutputs()?['body/JiraKey']
- OfertaId: triggerOutputs()?['body/OfertaId']
- Semana: triggerOutputs()?['body/Semana']
- VersaoNumero: triggerOutputs()?['body/VersaoReport']
- DataPreenchimento: utcNow()
- ArquitetoEmail: triggerOutputs()?['body/RecipientEmail']
- StatusAtual: outputs('ResponseData')?['status_atual']
- StatusProjeto: outputs('ResponseData')?['status_projeto']
- ReuniaoCliente: if(equals(outputs('ResponseData')?['reuniao_cliente'], 'true'), true, false)
- PropostaAtualizada: if(equals(outputs('ResponseData')?['proposta_atualizada'], 'true'), true, false)
- BloqueioExistente: if(equals(outputs('ResponseData')?['bloqueio_existente'], 'true'), true, false)
- PrevisaoFechamento: outputs('ResponseData')?['previsao_fechamento']
- ProbabilidadeGanho: outputs('ResponseData')?['probabilidade_ganho']
- BudgetConsumido: int(coalesce(outputs('ResponseData')?['budget_consumido'], 0))
- Observacoes: outputs('ResponseData')?['observacoes']
- RespostaJSON: string(outputs('Post_adaptive_card_and_wait')?['body'])
```

---

### 13. Get Oferta from Ofertas_Pipeline

> **CRITICAL**: Required to get existing values for required fields

```
Action: SharePoint - Get item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: Ofertas_Pipeline
Id: triggerOutputs()?['body/OfertaId']
```

---

### 14. Update Ofertas_Pipeline

```
Action: SharePoint - Update item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: Ofertas_Pipeline
Id: triggerOutputs()?['body/OfertaId']

Fields:
- SemanaReport: triggerOutputs()?['body/Semana']
- VersaoReport: triggerOutputs()?['body/VersaoReport']
- DataUltimoReport: utcNow()
- StatusReportEnviado: Yes

# REQUIRED FIELD - pass existing value:
- Est_x002e_BudgetInicio: outputs('Get_Oferta')?['body/Est_x002e_BudgetInicio']
```

---

## Final Flow Structure

```
When item is created (Queue)
├── Condition: QueueStatus = Pending?
│   └── No: Terminate
├── Update Queue: Sent + SentAt
├── Compose: AdaptiveCardJson
├── Post adaptive card and wait
├── Compose: ResponseData
├── Compose: StatusCode
├── Condition: StatusCode = 200?
│   └── No: Update Error + Terminate
├── Condition: Red validation passed?
│   └── No: Update Error + Terminate
├── Update Queue: Completed
├── Create Historico item
├── Get Oferta (for required fields)
└── Update Ofertas_Pipeline
```

---

## Testing Checklist

- [ ] Create test queue item manually with `QueueStatus = Pending`
- [ ] Verify card arrives in Teams 1:1 chat
- [ ] Submit response → Check `Completed` status
- [ ] Verify `ResponseJson` populated
- [ ] Check `StatusReports_Historico` has new item
- [ ] Check `Ofertas_Pipeline` fields updated
- [ ] Test Red status without observacoes → Should get Error
