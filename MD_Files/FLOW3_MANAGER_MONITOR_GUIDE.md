# Flow3: Manager Monitor (Optional)

> **Trigger**: Recurrence (every 30 minutes, weekdays only)  
> **Purpose**: Posts queue status summary to Teams channel

---

## Step-by-Step Creation

### 1. Create New Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **+ Create** → **Scheduled cloud flow**
3. Name: `Flow3_ManagerMonitor_Queue`
4. Configure schedule:
   - Repeat every: 30 minutes
   - Start: Now

---

### 2. Get Queue Items

```
Action: SharePoint - Get items
Site Address: https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA
List Name: StatusReports_Queue_TEST
Top Count: 5000
```

---

### 3. Filter: Pending Items

```
Action: Data Operations - Filter array
From: outputs('Get_Queue_Items')?['body/value']
Condition: item()?['QueueStatus/Value'] equals 'Pending'
```

---

### 4. Filter: Sent Items

```
Action: Data Operations - Filter array
From: outputs('Get_Queue_Items')?['body/value']
Condition: item()?['QueueStatus/Value'] equals 'Sent'
```

---

### 5. Filter: Completed Items

```
Action: Data Operations - Filter array
From: outputs('Get_Queue_Items')?['body/value']
Condition: item()?['QueueStatus/Value'] equals 'Completed'
```

---

### 6. Filter: Error Items

```
Action: Data Operations - Filter array
From: outputs('Get_Queue_Items')?['body/value']
Condition: item()?['QueueStatus/Value'] equals 'Error'
```

---

### 7. Compose: Summary Message

```
Action: Compose
Name: SummaryMessage
Inputs:
📊 **Queue Status Report**
━━━━━━━━━━━━━━━━━━━━━━
✅ Completed: @{length(body('Filter_Completed'))}
⏳ Pending: @{length(body('Filter_Pending'))}
📤 Sent (awaiting): @{length(body('Filter_Sent'))}
❌ Error: @{length(body('Filter_Error'))}
━━━━━━━━━━━━━━━━━━━━━━
🕐 Updated: @{formatDateTime(utcNow(), 'dd/MM/yyyy HH:mm')} UTC
```

---

### 8. Condition: Any Pending or Errors?

```
Action: Condition
Expression:
or(greater(length(body('Filter_Pending')), 0), greater(length(body('Filter_Error')), 0))
```

**If Yes → Post to Teams. If No → Skip (nothing to report).**

---

### 9. Post to Teams Channel

```
Action: Microsoft Teams - Post message in a chat or channel

Post as: Flow bot
Post in: Channel
Team: [Select your team]
Channel: [Select monitoring channel]
Message: outputs('SummaryMessage')
```

---

### 10. Optional: List Pending Recipients

If you want to include pending recipients:

```
Action: Data Operations - Select
From: body('Filter_Pending')
Map:
  email: item()?['RecipientEmail']
  jirakey: item()?['JiraKey']
```

Then append to message:
```
📋 **Pending Recipients:**
@{join(body('Select_Pending'), char(10))}
```

---

## Final Flow Structure

```
Recurrence (30 min)
├── Get Queue Items
├── Filter: Pending
├── Filter: Sent
├── Filter: Completed
├── Filter: Error
├── Compose: SummaryMessage
├── Condition: Any pending/errors?
│   └── Yes: Post to Teams Channel
│   └── No: (skip)
```

---

## Sample Output

```
📊 Queue Status Report
━━━━━━━━━━━━━━━━━━━━━━
✅ Completed: 85
⏳ Pending: 12
📤 Sent (awaiting): 3
❌ Error: 2
━━━━━━━━━━━━━━━━━━━━━━
🕐 Updated: 28/12/2025 18:00 UTC

📋 Pending Recipients:
- architect1@indra.es (DNSM-1234)
- architect2@indra.es (DNSM-5678)
```
