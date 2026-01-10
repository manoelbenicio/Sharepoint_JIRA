# Flow6 V2 Adaptive Cards - Ready to Paste

> **Use these V2 cards to replace the existing Flow6 actions in Power Automate**
> All cards validated ✅ | Under 28KB ✅ | Teams-compliant colors ✅

---

## Card 1: ARQ Performance (17KB)

**Action Name:** `Post Card 1 - ARQ Performance`

**Compose Action Expression:**
```
@{outputs('Parse_JSON')?['body']?['arq_performance_payload']}
```

**Adaptive Card JSON:**
```json
@{json(outputs('TEMPLATE_04_ARQ_Performance_V2'))}
```

📋 [View Full JSON](file:///d:/VMs/Projetos/Sharepoint_JIRA/MD_Files/QA_FLOW/HANDOFF_FIX_QA/TEMPLATE_04_ARQ_Performance_V2.json)

---

## Card 2: Market Analysis (19KB)

**Action Name:** `Post Card 2 - Market Analysis`

**Compose Action Expression:**
```
@{outputs('Parse_JSON')?['body']?['market_analysis_payload']}
```

📋 [View Full JSON](file:///d:/VMs/Projetos/Sharepoint_JIRA/MD_Files/QA_FLOW/HANDOFF_FIX_QA/TEMPLATE_05_Market_Analysis_V2.json)

---

## Card 3: WoW Trends (17KB)

**Action Name:** `Post Card 3 - WoW Trends`

**Compose Action Expression:**
```
@{outputs('Parse_JSON')?['body']?['wow_trends_payload']}
```

📋 [View Full JSON](file:///d:/VMs/Projetos/Sharepoint_JIRA/MD_Files/QA_FLOW/HANDOFF_FIX_QA/TEMPLATE_06_WoW_Trends_V2.json)

---

## Card 4: Practice Performance (20KB)

**Action Name:** `Post Card 4 - Practice Performance`

**Compose Action Expression:**
```
@{outputs('Parse_JSON')?['body']?['practice_analysis_payload']}
```

📋 [View Full JSON](file:///d:/VMs/Projetos/Sharepoint_JIRA/MD_Files/QA_FLOW/HANDOFF_FIX_QA/TEMPLATE_07_Practice_Analysis_V2.json)

---

## Deployment Steps

1. Open **Flow6 - Premium Analytics Bi-Weekly** in Power Automate
2. For each card action:
   - Click the existing Compose action
   - Replace the JSON with the V2 version from the links above
3. Add **Delay** action (2 seconds) between each Teams post
4. **Save** and **Test** the flow

---

## V2 Fixes Applied

| Issue | V2 Fix |
|-------|--------|
| Invisible text | Changed `Light` → `Accent`/`Good`/`Warning` |
| Dynamic styles | Removed all `${}` style variables |
| External images | Replaced with emojis |
| 28KB limit | All cards under 20KB |

---

*Generated: 2026-01-09 22:30 BRT*
