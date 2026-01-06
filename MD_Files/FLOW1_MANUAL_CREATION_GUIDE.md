# Flow1: Queue Creator - Manual Creation Guide

> **Trigger**: Recurrence (Tue/Fri 09:00 São Paulo)  
> **Purpose**: Creates queue items in `StatusReports_Queue` for actionable offers

---

## Prerequisites

1. ✅ Create list `StatusReports_Queue` with all columns (run PowerShell script)
2. ✅ Verify `UniqueKey` has **Enforce unique values = Yes**
3. ✅ Confirm `ARQs_Teams` list has active architects with emails

---

## Step-by-Step Creation

### 1. Create New Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **+ Create** → **Scheduled cloud flow**
3. Name: `Flow1_QueueCreator_StatusReports`
4. Configure schedule:
   - Start: Today 09:00
   - Repeat every: 1 week
   - On these days: **Tuesday, Friday**
   - Time zone: **(UTC-03:00) Brasilia**

---

### 2. Initialize Variables

#### Variable: SemanaRef (String)
```
Action: Initialize variable
Name: SemanaRef
Type: String
Value: formatDateTime(convertFromUtc(utcNow(), 'E. South America Standard Time'), 'WW/yyyy')
```

#### Variable: VersaoAlvo (Integer)
```
Action: Initialize variable
Name: VersaoAlvo
Type: Integer
Value: if(equals(dayOfWeek(convertFromUtc(utcNow(), 'E. South America Standard Time')), 2), 1, if(equals(dayOfWeek(convertFromUtc(utcNow(), 'E. South America Standard Time')), 5), 2, 0))
```

> **Note**: dayOfWeek returns 2=Tuesday, 5=Friday

---

### 3. Get ARQs_Teams List

```
Action: SharePoint - Get items
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: ARQs_Teams
Filter Query: Status eq 'Ativo'
Top Count: 500
```

---

### 4. Build Email Dictionary

```
Action: Data Operations - Select
From: outputs('Get_ARQs_Teams')?['body/value']
Map:
  - login: toLower(trim(item()?['Login']))
  - email: toLower(trim(coalesce(item()?['field_3'], item()?['E_x002d_mail'], item()?['Email'])))
```

---

### 5. Get Ofertas_Pipeline

```
Action: SharePoint - Get items
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: Ofertas_Pipeline
Top Count: 5000
```

---

### 6. Apply to Each Offer

```
Action: Apply to each
Select output: outputs('Get_Ofertas_Pipeline')?['body/value']
Concurrency Control: On, Degree of Parallelism: 1
```

**Inside the loop, add the following actions:**

---

### 6.1 Compose: NormalizedStatus

```
Action: Compose
Inputs: replace(toLower(trim(coalesce(items('Apply_to_each')?['Status']?['Value'], items('Apply_to_each')?['Status'], ''))), ' ', '-')
```

---

### 6.2 Condition: Is Status Actionable?

```
Action: Condition
Expression (Advanced mode):
not(or(equals(outputs('NormalizedStatus'), 'abandoned'), equals(outputs('NormalizedStatus'), 'lost'), equals(outputs('NormalizedStatus'), 'won'), equals(outputs('NormalizedStatus'), 'won-end'), equals(outputs('NormalizedStatus'), 'cancelled'), equals(outputs('NormalizedStatus'), 'canceled'), equals(outputs('NormalizedStatus'), 'cancelada'), equals(outputs('NormalizedStatus'), 'rejected')))
```

**If Yes → Continue. If No → Do nothing (empty branch).**

---

### 6.3 Filter Array: Find Architect

```
Action: Data Operations - Filter array
From: body('Build_Email_Dictionary')
Condition: item()?['login'] equals toLower(trim(coalesce(items('Apply_to_each')?['Assignee'], '')))
```

---

### 6.4 Condition: Architect Found with Email?

```
Action: Condition
Expression:
and(greater(length(body('Filter_Architect')), 0), not(empty(first(body('Filter_Architect'))?['email'])))
```

**If Yes → Continue. If No → Do nothing.**

---

### 6.5 Compose: CurrentSemanaReport

```
Action: Compose
Inputs: coalesce(items('Apply_to_each')?['SemanaReport'], '')
```

---

### 6.6 Compose: CurrentVersaoReport

```
Action: Compose
Inputs: int(coalesce(items('Apply_to_each')?['VersaoReport'], 0))
```

---

### 6.7 Condition: Needs Report?

```
Action: Condition
Expression:
or(not(equals(outputs('CurrentSemanaReport'), variables('SemanaRef'))), less(outputs('CurrentVersaoReport'), variables('VersaoAlvo')))
```

**If Yes → Create queue item. If No → Do nothing.**

---

### 6.8 Scope: Create Queue Item (with Error Handling)

```
Action: Scope
Name: Scope_CreateQueueItem
```

**Inside Scope:**

```
Action: SharePoint - Create item
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Queue

QueueStatus Value: Pending
RecipientEmail: first(body('Filter_Architect'))?['email']
JiraKey: items('Apply_to_each')?['JiraKey']
OfertaId: items('Apply_to_each')?['ID']
Semana: variables('SemanaRef')
VersaoReport: variables('VersaoAlvo')
UniqueKey: concat(items('Apply_to_each')?['JiraKey'], '|', variables('SemanaRef'), '|', string(variables('VersaoAlvo')))
AttemptCount: 0
```

---

### 6.9 Scope: Handle Duplicate Error

```
Action: Scope
Name: Scope_HandleError
Configure run after: Scope_CreateQueueItem has failed
```

**Inside Scope:**

```
Action: Compose
Name: ErrorDetails
Inputs: "Duplicate item skipped (UniqueKey already exists)"
```

> **Note**: This allows the flow to continue even if UniqueKey constraint rejects duplicate.

---

## Final Flow Structure

```
Recurrence (Tue/Fri 09:00)
├── Initialize: SemanaRef
├── Initialize: VersaoAlvo
├── Get ARQs_Teams (filter: Ativo)
├── Select: Build Email Dictionary
├── Get Ofertas_Pipeline
└── Apply to each (Offer)
    ├── Compose: NormalizedStatus
    └── Condition: Status Actionable?
        └── Yes:
            ├── Filter Array: Find Architect
            └── Condition: Architect Found?
                └── Yes:
                    ├── Compose: CurrentSemanaReport
                    ├── Compose: CurrentVersaoReport
                    └── Condition: Needs Report?
                        └── Yes:
                            ├── Scope: Create Queue Item
                            └── Scope: Handle Error (run after failed)
```

---

## Testing Checklist

- [ ] Run manually on a Tuesday → VersaoAlvo should be 1
- [ ] Run manually on a Friday → VersaoAlvo should be 2
- [ ] Check queue items have correct `UniqueKey` format
- [ ] Run again → No duplicates created
- [ ] Verify only active architect offers are queued
