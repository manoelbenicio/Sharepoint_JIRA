# Flow6 - Premium Analytics: Complete Manual Setup Guide

**Document Version:** 1.0  
**Created:** 2026-01-06  
**Purpose:** Step-by-step manual configuration for Power Automate Flow6

---

## 🎯 Flow6 Overview

| Setting | Value |
|---------|-------|
| **Name** | `Flow6 - Premium Analytics Bi-Weekly` |
| **Type** | Scheduled cloud flow |
| **Channel** | `Ofertas_Analytics` (already created) |
| **Schedule** | Bi-weekly: Tuesday & Friday @ 9:00 AM BRT |
| **Cards** | 4 premium Adaptive Cards (Templates 04-07) |

---

## 📋 Step-by-Step Configuration

### STEP 1: Create the Flow

1. Go to **Power Automate** → **Create** → **Scheduled cloud flow**
2. Name: `Flow6 - Premium Analytics Bi-Weekly`
3. Click **Create**

---

### STEP 2: Configure Recurrence Trigger

**Action Type:** Recurrence

| Parameter | Value |
|-----------|-------|
| **Frequency** | Week |
| **Interval** | 1 |
| **Time zone** | (UTC-03:00) Brasilia |
| **Start time** | Leave empty or set to next Tuesday 09:00 |
| **On these days** | Tuesday, Friday |
| **At these hours** | 9 |
| **At these minutes** | 0 |

> ⚠️ **Initial Testing:** For testing, change to **Manual trigger** first. Switch to scheduled after validation.

---

### STEP 3: HTTP GET - Call Azure Function

**Action Type:** HTTP

| Parameter | Value |
|-----------|-------|
| **Method** | GET |
| **URI** | `https://func-pipeline-consolidation.azurewebsites.net/api/consolidar-v2` |
| **Headers** | See below |

**Headers Configuration:**
```
x-functions-key: <YOUR_FUNCTION_KEY>
Content-Type: application/json
```

> 📌 **Note:** Replace `<YOUR_FUNCTION_KEY>` with the actual Azure Function key from your deployment.

---

### STEP 4: Parse JSON Response

**Action Type:** Parse JSON

| Parameter | Value |
|-----------|-------|
| **Content** | `@{body('HTTP')}` (select dynamic content from HTTP action) |
| **Schema** | See JSON schema below |

**JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "semana": { "type": "string" },
    "data_geracao": { "type": "string" },
    "pipeline_ativo": {
      "type": "object",
      "properties": {
        "quantidade": { "type": "integer" },
        "valor": { "type": "number" },
        "valor_formatado": { "type": "string" }
      }
    },
    "resultados_30_dias": {
      "type": "object",
      "properties": {
        "won": {
          "type": "object",
          "properties": {
            "quantidade": { "type": "integer" },
            "valor_formatado": { "type": "string" },
            "margem_media_fmt": { "type": "string" }
          }
        },
        "lost": {
          "type": "object",
          "properties": {
            "quantidade": { "type": "integer" },
            "valor_formatado": { "type": "string" }
          }
        },
        "win_rate": { "type": "number" }
      }
    },
    "budget_metricas": {
      "type": "object",
      "properties": {
        "total_arquitetos": { "type": "integer" },
        "taxa_utilizacao_global": { "type": "number" }
      }
    },
    "top_mercados_volume": { "type": "array" },
    "top_mercados_valor": { "type": "array" },
    "top_mercados_margem": { "type": "array" },
    "praticas_detalhadas": { "type": "object" }
  }
}
```

---

### STEP 5: Compose Card 04 - ARQ Performance

**Action Type:** Compose  
**Action Name:** `Compose_Card_04_ARQ_Performance`

**Input:** Paste the complete JSON from:  
📁 `TEMPLATE_04_ARQ_Performance.json`

> ⚠️ **Important:** Replace all `${placeholder}` values with Power Automate expressions.

**Key Expression Mappings for Card 04:**

| Placeholder | Expression |
|-------------|------------|
| `${semana}` | `@{body('Parse_JSON')?['semana']}` |
| `${data_geracao}` | `@{body('Parse_JSON')?['data_geracao']}` |
| `${total_arquitetos}` | `@{body('Parse_JSON')?['budget_metricas']?['total_arquitetos']}` |
| `${utilizacao_media_pct}` | `@{body('Parse_JSON')?['budget_metricas']?['taxa_utilizacao_global']}` |
| `${total_ofertas_ativas}` | `@{body('Parse_JSON')?['pipeline_ativo']?['quantidade']}` |

---

### STEP 6: Post Card 04 to Teams

**Action Type:** Post adaptive card in a chat or channel (Microsoft Teams)

| Parameter | Value |
|-----------|-------|
| **Post as** | Flow bot |
| **Post in** | Channel |
| **Team** | Select your team containing `Ofertas_Analytics` |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | `@{outputs('Compose_Card_04_ARQ_Performance')}` |

---

### STEP 7: Delay 2 Seconds

**Action Type:** Delay

| Parameter | Value |
|-----------|-------|
| **Count** | 2 |
| **Unit** | Second |

> 📌 This prevents Teams throttling when posting multiple cards.

---

### STEP 8: Compose Card 05 - Market Analysis

**Action Type:** Compose  
**Action Name:** `Compose_Card_05_Market_Analysis`

**Input:** Paste the complete JSON from:  
📁 `TEMPLATE_05_Market_Analysis.json`

**Key Expression Mappings for Card 05:**

| Placeholder | Expression |
|-------------|------------|
| `${semana}` | `@{body('Parse_JSON')?['semana']}` |
| `${total_mercados}` | `@{length(body('Parse_JSON')?['top_mercados_volume'])}` |
| `${pipeline_total_30d_fmt}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${won_total_30d_fmt}` | `@{body('Parse_JSON')?['resultados_30_dias']?['won']?['valor_formatado']}` |

---

### STEP 9: Post Card 05 to Teams

**Action Type:** Post adaptive card in a chat or channel

| Parameter | Value |
|-----------|-------|
| **Post as** | Flow bot |
| **Post in** | Channel |
| **Team** | Same team |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | `@{outputs('Compose_Card_05_Market_Analysis')}` |

---

### STEP 10: Delay 2 Seconds

**Action Type:** Delay (same as Step 7)

---

### STEP 11: Compose Card 06 - WoW Trends

**Action Type:** Compose  
**Action Name:** `Compose_Card_06_WoW_Trends`

**Input:** Paste the complete JSON from:  
📁 `TEMPLATE_06_WoW_Trends.json`

**Key Expression Mappings for Card 06:**

| Placeholder | Expression |
|-------------|------------|
| `${semana}` | `@{body('Parse_JSON')?['semana']}` |
| `${pipeline_current_valor_fmt}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${pipeline_current_count}` | `@{body('Parse_JSON')?['pipeline_ativo']?['quantidade']}` |
| `${win_rate_current}` | `@{body('Parse_JSON')?['resultados_30_dias']?['win_rate']}` |

---

### STEP 12: Post Card 06 to Teams

**Action Type:** Post adaptive card in a chat or channel

| Parameter | Value |
|-----------|-------|
| **Post as** | Flow bot |
| **Post in** | Channel |
| **Team** | Same team |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | `@{outputs('Compose_Card_06_WoW_Trends')}` |

---

### STEP 13: Delay 2 Seconds

**Action Type:** Delay (same as Step 7)

---

### STEP 14: Compose Card 07 - Practice Analysis

**Action Type:** Compose  
**Action Name:** `Compose_Card_07_Practice_Analysis`

**Input:** Paste the complete JSON from:  
📁 `TEMPLATE_07_Practice_Analysis.json`

**Key Expression Mappings for Card 07:**

| Placeholder | Expression |
|-------------|------------|
| `${report_period}` | `@{body('Parse_JSON')?['semana']}` |
| `${total_practices}` | `6` (hardcoded) |
| `${total_pipeline_value}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${avg_win_rate}` | `@{body('Parse_JSON')?['resultados_30_dias']?['win_rate']}` |

---

### STEP 15: Post Card 07 to Teams (Final)

**Action Type:** Post adaptive card in a chat or channel

| Parameter | Value |
|-----------|-------|
| **Post as** | Flow bot |
| **Post in** | Channel |
| **Team** | Same team |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | `@{outputs('Compose_Card_07_Practice_Analysis')}` |

---

## 📊 Complete Flow Structure

```
┌──────────────────────────────────────────────────────────────────┐
│  1. Recurrence (Tue/Fri @ 9:00 AM BRT)                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. HTTP GET → consolidar-v2                                      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. Parse JSON                                                    │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ 4. Compose 04  │    │ 8. Compose 05  │    │ 11. Compose 06 │
│ ARQ Performance│    │ Market Analysis│    │ WoW Trends     │
└────────────────┘    └────────────────┘    └────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ 5. Post Teams  │    │ 9. Post Teams  │    │ 12. Post Teams │
└────────────────┘    └────────────────┘    └────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ 6. Delay 2s    │    │ 10. Delay 2s   │    │ 13. Delay 2s   │
└────────────────┘    └────────────────┘    └────────────────┘
                                                    │
                              ┌─────────────────────┘
                              ▼
                    ┌────────────────┐
                    │ 14. Compose 07 │
                    │Practice Analysis│
                    └────────────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │ 15. Post Teams │
                    │ (FINAL CARD)   │
                    └────────────────┘
```

---

## 📁 Template File Locations

All template JSON files are located in:
```
D:\VMs\Projetos\Sharepoint_JIRA\MD_Files\QA_FLOW\HANDOFF_FIX_QA\
```

| Template | File |
|----------|------|
| Card 04 - ARQ Performance | `TEMPLATE_04_ARQ_Performance.json` |
| Card 05 - Market Analysis | `TEMPLATE_05_Market_Analysis.json` |
| Card 06 - WoW Trends | `TEMPLATE_06_WoW_Trends.json` |
| Card 07 - Practice Analysis | `TEMPLATE_07_Practice_Analysis.json` |

---

## 🔑 Azure Function Details

| Setting | Value |
|---------|-------|
| **Function App** | `func-pipeline-consolidation` |
| **Endpoint** | `/api/consolidar-v2` |
| **Full URL** | `https://func-pipeline-consolidation.azurewebsites.net/api/consolidar-v2` |
| **Auth Method** | Function Key via `x-functions-key` header |

---

## 🔧 Teams Configuration

| Setting | Value |
|---------|-------|
| **Team** | (Your team name) |
| **Channel** | `Ofertas_Analytics` ✅ Already created |
| **Post as** | Flow bot |
| **Card Type** | Adaptive Card |

---

## ✅ Pre-Deployment Checklist

- [ ] Flow created with correct name
- [ ] Recurrence trigger configured (Tue/Fri @ 9:00 AM BRT)
- [ ] HTTP action has correct URL and Function Key
- [ ] Parse JSON has complete schema
- [ ] All 4 Compose actions have correct template JSON
- [ ] All 4 Post to Teams actions target `Ofertas_Analytics` channel
- [ ] 3 Delay actions (2 seconds each) between posts
- [ ] Manual test run completed successfully
- [ ] Cards render correctly in Teams
- [ ] Enable scheduled trigger for production

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `null` values breaking card | Use `coalesce()`: `@{coalesce(value, 'N/A')}` |
| Cards not appearing in Teams | Verify channel permissions and connection |
| HTTP 401 Unauthorized | Check Function Key is correct |
| Teams throttling | Increase delay between posts to 3-5 seconds |
| Card too large | Reduce content or split into smaller sections |

---

## 📞 Reference Documents

- `FLOW6_PREMIUM_ANALYTICS_SPEC.md` - Strategy document
- `FLOW6_EXPRESSIONS_REFERENCE.md` - Expression mappings
- `TEMPLATE_DATA_MAPPING.md` - Field reference
- `FLOW3_CLEVEL_WEEKLY_SPEC.md` - Similar flow for reference

---

**Document End**
