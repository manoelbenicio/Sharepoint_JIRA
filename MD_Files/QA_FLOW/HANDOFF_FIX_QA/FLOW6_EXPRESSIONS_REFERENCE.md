# Flow6 Power Automate Expressions Reference

**Document Version:** 1.0  
**Created:** 2026-01-06  
**Purpose:** Ready-to-use expressions for populating premium card templates

---

## 🎯 Overview

This document provides **copy-paste ready** Power Automate expressions for each template placeholder. Use these in your Compose actions to populate the Adaptive Cards.

---

## 📋 Prerequisites

After the HTTP GET action to `consolidar-v2`, add a **Parse JSON** action with this schema:

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

## 📊 TEMPLATE_04: ARQ Performance Expressions

### Header Section

| Placeholder | Power Automate Expression |
|------------|---------------------------|
| `${report_period}` | `@{body('Parse_JSON')?['semana']}` |
| `${total_arquitetos}` | `@{body('Parse_JSON')?['budget_metricas']?['total_arquitetos']}` |
| `${avg_utilization}` | `@{body('Parse_JSON')?['budget_metricas']?['taxa_utilizacao_global']}` |
| `${total_offers}` | `@{body('Parse_JSON')?['pipeline_ativo']?['quantidade']}` |

### Top 5 ARQs by Utilization

```
@{body('Parse_JSON')?['top_arquitetos_utilizacao']?[0]?['nome']}
@{body('Parse_JSON')?['top_arquitetos_utilizacao']?[0]?['taxa_utilizacao']}
@{body('Parse_JSON')?['top_arquitetos_utilizacao']?[1]?['nome']}
@{body('Parse_JSON')?['top_arquitetos_utilizacao']?[1]?['taxa_utilizacao']}
... (repeat for indices 2, 3, 4)
```

### Top 5 ARQs by Volume

```
@{body('Parse_JSON')?['top_arquitetos_volume']?[0]?['nome']}
@{body('Parse_JSON')?['top_arquitetos_volume']?[0]?['quantidade']}
@{body('Parse_JSON')?['top_arquitetos_volume']?[0]?['valor_formatado']}
```

### Top 5 ARQs by Pipeline Value

```
@{body('Parse_JSON')?['top_arquitetos_valor']?[0]?['nome']}
@{body('Parse_JSON')?['top_arquitetos_valor']?[0]?['valor_formatado']}
```

---

## 📈 TEMPLATE_05: Market Analysis Expressions

### Header Section

| Placeholder | Power Automate Expression |
|------------|---------------------------|
| `${total_markets}` | `@{length(body('Parse_JSON')?['top_mercados_volume'])}` |
| `${total_pipeline_value}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${total_won_value}` | `@{body('Parse_JSON')?['resultados_30_dias']?['won']?['valor_formatado']}` |

### Top 5 Markets by Won Offers

```
@{body('Parse_JSON')?['top_mercados_won']?[0]?['mercado']}
@{body('Parse_JSON')?['top_mercados_won']?[0]?['quantidade']}
@{body('Parse_JSON')?['top_mercados_won']?[0]?['valor_formatado']}
```

### Top 5 Markets by Margin

```
@{body('Parse_JSON')?['top_mercados_margem']?[0]?['mercado']}
@{body('Parse_JSON')?['top_mercados_margem']?[0]?['margem_media']}
```

---

## 📉 TEMPLATE_06: WoW Trends Expressions

### Pipeline Comparison

| Placeholder | Power Automate Expression |
|------------|---------------------------|
| `${current_week_value}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${current_week_count}` | `@{body('Parse_JSON')?['pipeline_ativo']?['quantidade']}` |
| `${last_week_value}` | `@{body('Parse_JSON')?['wow_comparison']?['previous_week']?['valor_formatado']}` |
| `${delta_pct}` | `@{body('Parse_JSON')?['wow_comparison']?['delta_pct']}` |

### KPI Indicators

```
@{body('Parse_JSON')?['resultados_30_dias']?['win_rate']}
@{body('Parse_JSON')?['resultados_30_dias']?['won']?['margem_media']}
@{body('Parse_JSON')?['ciclo_tempo_medio']}
```

### Trend Icons (Conditional)

```
@{if(greater(body('Parse_JSON')?['wow_comparison']?['delta_value'], 0), '📈', '📉')}
```

---

## 🏢 TEMPLATE_07: Practice Analysis Expressions

### Header Section

| Placeholder | Power Automate Expression |
|------------|---------------------------|
| `${total_practices}` | `6` |
| `${total_pipeline_value}` | `@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}` |
| `${avg_win_rate}` | `@{body('Parse_JSON')?['resultados_30_dias']?['win_rate']}` |

### Practice-Specific Data

#### Data/IA Practice
```
@{body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['won']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['lost']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['valor_formatado']}
```

#### DS Practice
```
@{body('Parse_JSON')?['praticas_detalhadas']?['ds']?['won']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['ds']?['lost']?['quantidade']}
```

#### SGE Practice
```
@{body('Parse_JSON')?['praticas_detalhadas']?['sge']?['won']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['sge']?['lost']?['quantidade']}
```

#### DIC Practice
```
@{body('Parse_JSON')?['praticas_detalhadas']?['dic']?['won']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['dic']?['lost']?['quantidade']}
```

#### Cyber Practice
```
@{body('Parse_JSON')?['praticas_detalhadas']?['cyber']?['won']?['quantidade']}
@{body('Parse_JSON')?['praticas_detalhadas']?['cyber']?['lost']?['quantidade']}
```

### Win Rate Calculation (Compose Expression)

```
@{div(
    mul(body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['won']?['quantidade'], 100),
    add(
        body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['won']?['quantidade'],
        body('Parse_JSON')?['praticas_detalhadas']?['dados_ia']?['lost']?['quantidade']
    )
)}
```

---

## 🔧 Complete Compose Action Example

### TEMPLATE_07 Compose Action

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "📊 PRACTICE PERFORMANCE REPORT",
      "weight": "Bolder",
      "size": "Large"
    },
    {
      "type": "TextBlock",
      "text": "Report Period: @{body('Parse_JSON')?['semana']}"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Total Pipeline",
          "value": "@{body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']}"
        },
        {
          "title": "Win Rate",
          "value": "@{body('Parse_JSON')?['resultados_30_dias']?['win_rate']}%"
        }
      ]
    }
  ]
}
```

---

## 📋 Flow6 Action Sequence

```
1. Trigger (Recurrence - Monthly)
        │
        ▼
2. HTTP GET (consolidar-v2)
        │
        ▼
3. Parse JSON (schema above)
        │
        ▼
4. Compose - Card 04 ARQ Performance
        │
        ▼
5. Post to Teams (Card 04)
        │
        ▼
6. Delay (2 seconds)
        │
        ▼
7. Compose - Card 05 Market Analysis
        │
        ▼
8. Post to Teams (Card 05)
        │
        ▼
9. Delay (2 seconds)
        │
        ▼
10. Compose - Card 06 WoW Trends
        │
        ▼
11. Post to Teams (Card 06)
        │
        ▼
12. Delay (2 seconds)
        │
        ▼
13. Compose - Card 07 Practice Analysis
        │
        ▼
14. Post to Teams (Card 07)
```

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `null` values in array | Use `coalesce()`: `@{coalesce(body('Parse_JSON')?['field'], 'N/A')}` |
| Division by zero | Use `if()`: `@{if(equals(denominator, 0), 0, div(numerator, denominator))}` |
| Missing array index | Check length first: `@{if(greater(length(array), 0), array[0], 'N/A')}` |
| Date formatting | Use `formatDateTime()`: `@{formatDateTime(utcNow(), 'yyyy-MM-dd')}` |

---

## ✅ Testing Checklist

- [ ] HTTP GET returns valid JSON
- [ ] Parse JSON succeeds without errors
- [ ] All Compose actions generate valid card JSON
- [ ] Cards render correctly in Teams
- [ ] No null/undefined values break the cards
- [ ] Delays prevent Teams throttling

---

## 📎 Related Documents

- `FLOW6_PREMIUM_ANALYTICS_SPEC.md` - Implementation strategy
- `TEMPLATE_DATA_MAPPING.md` - Field reference
- `TEMPLATE_04/05/06/07.json` - Card templates
