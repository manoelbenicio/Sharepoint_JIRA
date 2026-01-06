# Flow3: C-Level Weekly Flash Report Delivery

## Overview

**Purpose**: Automatically send consolidated weekly status reports to C-Level executives via Teams Adaptive Card every Monday morning.

**Trigger**: Scheduled (Recurrence) - Every Monday at 8:00 AM

**Dependencies**:
- `consolidar-v2` Azure Function endpoint
- `adaptive_card_clevel_flash_report.json` template
- C-Level Teams Channel or Group Chat

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLOW3: C-LEVEL WEEKLY REPORT                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  RECURRENCE  │───▶│ CALL AZURE   │───▶│ PARSE JSON   │      │
│  │  Mon 8:00 AM │    │ consolidar-v2│    │  Response    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                 │                │
│                                                 ▼                │
│                      ┌──────────────┐    ┌──────────────┐      │
│                      │ POST CARD TO │◀───│ BUILD CARD   │      │
│                      │ TEAMS CHANNEL│    │ WITH DATA    │      │
│                      └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Mapping

The Adaptive Card placeholders map to `consolidar-v2` response fields:

| Card Placeholder | consolidar-v2 Field | Description |
|-----------------|---------------------|-------------|
| `${semana}` | `semana_referencia` | Week reference (e.g., "Week 02/2026") |
| `${valor_pipeline_formatado}` | `pipeline.valor_total_formatado` | Pipeline value (e.g., "€2.5M") |
| `${total_ofertas}` | `pipeline.total_ofertas` | Total offers count |
| `${pipeline_ativo_quantidade}` | `pipeline.em_desenvolvimento` | Active offers in dev |
| `${resultados_7_dias_total}` | `resultados_7_dias.total` | Closed this week |
| `${win_rate_30d}` | `metricas.win_rate_30d` | Win rate percentage |
| `${win_rate_color}` | Dynamic | "Good" if ≥50%, "Warning" if ≥30%, "Attention" if <30% |
| `${margem_media}` | `metricas.margem_media` | Average margin % |
| `${won_7d_item1}` | `resultados_7_dias.won[0]` | First win this week |
| `${won_7d_item2}` | `resultados_7_dias.won[1]` | Second win this week |
| `${alert_item1}` | `alertas[0]` | First alert |
| `${alert_item2}` | `alertas[1]` | Second alert |
| `${deadline_item1}` | `deadlines[0]` | First deadline |
| `${deadline_item2}` | `deadlines[1]` | Second deadline |
| `${deadline_item3}` | `deadlines[2]` | Third deadline |
| `${top_arquiteto_1}` | `ranking_arquitetos[0]` | Top performer 1 |
| `${top_arquiteto_2}` | `ranking_arquitetos[1]` | Top performer 2 |
| `${top_arquiteto_3}` | `ranking_arquitetos[2]` | Top performer 3 |
| `${taxa_resposta}` | `metricas.taxa_resposta` | Response rate % |
| `${arquitetos_responderam}` | `metricas.arquitetos_responderam` | Count responded |
| `${total_arquitetos}` | `metricas.total_arquitetos` | Total architects |
| `${data_geracao}` | `metadata.timestamp` | Generation timestamp |
| `${powerbi_dashboard_url}` | Configuration | Power BI dashboard URL |

---

## Implementation Steps

### Step 1: Trigger Configuration
```json
{
  "type": "Recurrence",
  "recurrence": {
    "frequency": "Week",
    "interval": 1,
    "schedule": {
      "weekDays": ["Monday"],
      "hours": [8],
      "minutes": [0]
    },
    "timeZone": "E. South America Standard Time"
  }
}
```

### Step 2: Call Azure Function
```
HTTP Action:
  Method: GET
  URI: https://<function-app>.azurewebsites.net/api/consolidar-v2
  Headers:
    x-functions-key: @{variables('AzureFunctionKey')}
```

### Step 3: Parse JSON Response
Schema based on consolidar-v2 output structure.

### Step 4: Compose Adaptive Card
Use the `adaptive_card_clevel_flash_report.json` template with dynamic content substitution.

### Step 5: Post to Teams
```
Action: Post adaptive card in a chat or channel (Premium)
  - Recipient: C-Level Teams Channel/Group
  - Adaptive Card: @{outputs('Compose_Card')}
```

---

## Connector Requirements

| Connector | License | Required |
|-----------|---------|----------|
| Recurrence | Free | ✅ |
| HTTP | Premium | ✅ |
| Parse JSON | Free | ✅ |
| Compose | Free | ✅ |
| Microsoft Teams | Premium | ✅ |

> ⚠️ **Note**: This flow requires Premium connectors (HTTP + Teams Adaptive Card posting).

---

## Error Handling

1. **Azure Function Failure**: Configure retry policy (3 attempts, 5-minute intervals)
2. **Empty Response**: Check if `pipeline.total_ofertas > 0` before posting
3. **Teams Posting Failure**: Send email notification as fallback

---

## Testing Checklist

- [ ] Verify consolidar-v2 endpoint returns valid data
- [ ] Test card rendering in Teams Adaptive Card Designer
- [ ] Validate all placeholder substitutions
- [ ] Confirm C-Level channel permissions
- [ ] Run manual trigger test before enabling schedule

---

## File References

| File | Purpose |
|------|---------|
| `adaptive_card_clevel_flash_report.json` | Card template |
| `AZURE_FUNCTION_COMPLETE_MAP.md` | consolidar-v2 endpoint docs |
| `Project_Pending_Features_week1_2026.ini` | Template 5 specification |
