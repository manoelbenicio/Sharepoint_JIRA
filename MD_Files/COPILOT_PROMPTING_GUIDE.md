# Power Automate Copilot - Prompting Best Practices

## 🎯 Key Insight: Less is More

Copilot works better with **short, phased prompts** rather than long detailed plans. Here's why:

| Approach | Success Rate | Reason |
|----------|--------------|--------|
| ❌ Long detailed plan | Low | AI gets confused by too many steps |
| ✅ 2-3 phases | High | Clear, focused, iterative |

---

## 📋 Best Practices for Copilot Prompts

### 1. **Be Specific, Not Verbose**

❌ **Bad:**
```
Create a comprehensive automation that monitors SharePoint Ofertas_Pipeline list 
for changes, filters items where Status is "Em Acompanhamento" and assigns an 
architect, then creates queue items in StatusReports_Queue with unique keys, 
handles duplicates gracefully, and includes error handling...
```

✅ **Good (Phase 1):**
```
When an item is created or modified in SharePoint list "Ofertas_Pipeline", 
get the item details
```

✅ **Good (Phase 2):**
```
Add a condition: if Status equals "Em Acompanhamento"
```

---

### 2. **Use Action Verbs + Connectors**

Always mention the **connector name** explicitly:

```
When a new item is added to SharePoint list "Ofertas_Pipeline", 
post a message to Teams channel "General"
```

### 3. **Define Trigger → Action Pattern**

```
TRIGGER: When [event] in [connector/service]
ACTION: Do [specific action] in [target service]
```

### 4. **Iterate in Phases**

| Phase | Prompt Example |
|-------|---------------|
| 1 | "Create a flow triggered when SharePoint list item is modified" |
| 2 | "Add condition: Status equals 'Em Acompanhamento'" |
| 3 | "Add action: Create item in StatusReports_Queue list" |
| 4 | "Add error handling with Try/Catch scope" |

---

## 🔧 Copilot-Optimized Prompts for Your Flows

### Flow1: Queue Creator

**Phase 1:**
```
Create a flow that triggers when an item is created or modified 
in SharePoint list "Ofertas_Pipeline" at site 
"indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"
```

**Phase 2:**
```
Add a condition: Status equals "Em Acompanhamento" 
AND Arquiteto Responsavel is not empty
```

**Phase 3:**
```
In the Yes branch, create an item in SharePoint list "StatusReports_Queue"
with fields: JiraKey, RecipientEmail, Title
```

### Flow2: Worker

**Phase 1:**
```
Create a flow that triggers when an item is created in SharePoint list 
"StatusReports_Queue"
```

**Phase 2:**
```
Add condition: QueueStatus equals "Pending"
```

**Phase 3:**
```
Post an Adaptive Card to Teams user and wait for response
```

**Phase 4:**
```
When response received, update the SharePoint item with response data
```

---

## 📌 Quick Reference: Prompt Formula

```
[TRIGGER VERB] + [CONNECTOR] + [SPECIFIC RESOURCE]
  → [ACTION VERB] + [TARGET CONNECTOR] + [SPECIFIC TARGET]
```

## ⚠️ Common Mistakes

1. **Too much detail in one prompt** - Break into phases
2. **Vague language** - Use exact list/channel names
3. **Missing connector names** - Always specify SharePoint, Teams, Outlook
4. **Complex logic upfront** - Add conditions step by step

---

## 🔗 References

- [Microsoft Copilot Best Practices](https://learn.microsoft.com/en-us/power-automate/get-started-with-copilot)
- [Creating Flows with Copilot](https://learn.microsoft.com/en-us/power-automate/create-cloud-flow-copilot)
