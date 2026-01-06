# Premium Adaptive Cards - Data Mapping Guide

**Last Updated:** 2026-01-06  
**Status:** Ready for Integration

---

## 🎯 Overview

This document maps the Azure Function `consolidar-v2` output fields to the placeholders in each premium Adaptive Card template. Use this as a reference when integrating the cards into Power Automate Flow3.

---

## 📊 TEMPLATE_04: ARQ Performance

### Data Source: `consolidar-v2` Response

| Template Placeholder | Azure Function Field | Type | Example |
|---------------------|---------------------|------|---------|
| `${report_period}` | `semana` | string | "Week 02 • 2026" |
| `${total_arquitetos}` | `budget_metricas.total_arquitetos` | int | 12 |
| `${avg_utilization}` | `budget_metricas.taxa_utilizacao_global` | decimal | 78.5 |
| `${total_offers}` | `pipeline_ativo.quantidade` | int | 45 |

#### Top 5 ARQs by Utilization
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${util_1_name}` | `top_arquitetos_utilizacao[0].nome` | Sort by `taxa_utilizacao` DESC |
| `${util_1_pct}` | `top_arquitetos_utilizacao[0].taxa_utilizacao` | Format as % |
| `${util_1_hours}` | `top_arquitetos_utilizacao[0].horas_consumidas` / `horas_alocadas` | "150/200" format |

#### Top 5 ARQs by Offer Volume
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${vol_1_name}` | `top_mercados_volume[0].arquiteto` | Sort by count DESC |
| `${vol_1_count}` | `top_mercados_volume[0].quantidade` | Integer |
| `${vol_1_value}` | `top_mercados_volume[0].valor_formatado` | BRL format |

#### Top 5 ARQs by Pipeline Value
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${pipe_1_name}` | `top_arquitetos_valor[0].nome` | Sort by valor DESC |
| `${pipe_1_value}` | `top_arquitetos_valor[0].valor_formatado` | BRL format |
| `${pipe_1_count}` | `top_arquitetos_valor[0].quantidade` | Offer count |

#### Top 5 ARQs with 100MM+ Offers
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${big_1_name}` | Filter `ofertas` where `valor > 100000000` | Group by ARQ |
| `${big_1_count}` | Count of 100MM+ offers per ARQ | Integer |
| `${big_1_value}` | Sum of 100MM+ offers per ARQ | BRL format |

#### Top 5 ARQs by Wins (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${win_1_name}` | `resultados_30_dias.won` grouped by ARQ | Sort by count DESC |
| `${win_1_count}` | Won count per ARQ | Integer |
| `${win_1_value}` | Won value per ARQ | BRL format |

---

## 📈 TEMPLATE_05: Market Analysis

### Data Source: `consolidar-v2` Response

| Template Placeholder | Azure Function Field | Type |
|---------------------|---------------------|------|
| `${total_markets}` | Count distinct `mercado` | int |
| `${total_pipeline_value}` | `pipeline_ativo.valor_formatado` | string |
| `${total_won_value}` | `resultados_30_dias.won.valor_formatado` | string |

#### Top 5 Markets by Follow-up Status
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${followup_1_market}` | Filter status = "follow-up", group by `mercado` | Sort by count DESC |
| `${followup_1_count}` | Count per market | Integer |
| `${followup_1_value}` | Sum valor per market | BRL format |

#### Top 5 Markets by Wins (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${won_1_market}` | `top_mercados_won[0].mercado` | Exists in response |
| `${won_1_count}` | `top_mercados_won[0].quantidade` | Integer |
| `${won_1_value}` | `top_mercados_won[0].valor_formatado` | BRL format |

#### Top 5 Markets by Losses (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${lost_1_market}` | `top_mercados_lost[0].mercado` | Need to add to function |
| `${lost_1_count}` | `top_mercados_lost[0].quantidade` | Integer |
| `${lost_1_value}` | `top_mercados_lost[0].valor_formatado` | BRL format |

#### Top 5 Markets by Cancelled/Abandoned (90 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${cancelled_1_market}` | Filter status = "cancelado" AND last_update > 90 days | Group by market |
| `${cancelled_1_count}` | Count per market | Integer |

#### Top 5 Markets by Highest/Lowest Margin
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${high_margin_1_market}` | `top_mercados_margem[0].mercado` | Sort DESC |
| `${high_margin_1_value}` | `top_mercados_margem[0].margem_media` | % format |
| `${low_margin_1_market}` | `top_mercados_margem[-1].mercado` | Sort ASC |
| `${low_margin_1_value}` | `top_mercados_margem[-1].margem_media` | % format |

---

## 📉 TEMPLATE_06: Week-over-Week Trends

### Data Source: Requires Historical Data Storage

> ⚠️ **Note:** WoW comparisons require storing previous week's data. Recommend Azure Table Storage or Cosmos DB.

| Template Placeholder | Calculation | Type |
|---------------------|-------------|------|
| `${current_week_value}` | Current `pipeline_ativo.valor` | BRL |
| `${last_week_value}` | Previous week snapshot | BRL |
| `${delta_value}` | Current - Previous | BRL |
| `${delta_pct}` | ((Current - Previous) / Previous) * 100 | % |
| `${trend_icon}` | "📈" if positive, "📉" if negative | emoji |

#### KPI Trend Indicators
| Placeholder | Current Source | Target | Notes |
|-------------|----------------|--------|-------|
| `${winrate_current}` | `resultados_30_dias.win_rate` | 35% | Configurable |
| `${winrate_trend}` | Compare to last week | ↑/↓ | Direction |
| `${margin_current}` | `resultados_30_dias.won.margem_media` | 25% | Configurable |
| `${cycle_current}` | `ciclo_tempo_medio` | 15 days | Configurable |

#### Customer Concentration
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${client_1_name}` | Group by `cliente`, sort by valor DESC | Top 5 |
| `${client_1_value}` | Sum of pipeline per client | BRL |
| `${client_1_pct}` | (Client value / Total pipeline) * 100 | % |
| `${concentration_risk}` | If top 5 > 70% of pipeline | "HIGH" / "MEDIUM" / "LOW" |

---

## 🏢 TEMPLATE_07: Practice Analysis

### Data Source: `consolidar-v2` → `praticas_detalhadas`

| Template Placeholder | Azure Function Field | Type |
|---------------------|---------------------|------|
| `${total_practices}` | 6 (fixed: Data/IA, DS, SGE, DIC, GU, Cyber) | int |
| `${total_pipeline_value}` | `pipeline_ativo.valor_formatado` | string |
| `${avg_win_rate}` | Average of all practice win rates | % |

#### Practice Mapping
| Practice Code | Full Name | Function Field |
|--------------|-----------|----------------|
| `data_ia` | Dados/IA | `praticas_detalhadas.dados_ia` |
| `ds` | Digital Solutions | `praticas_detalhadas.ds` |
| `sge` | SGE | `praticas_detalhadas.sge` |
| `dic` | DIC | `praticas_detalhadas.dic` |
| `gu` | GU | Custom calculation needed |
| `cyber` | Cyber | `praticas_detalhadas.cyber` |

#### A) Follow-up by Practice (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${followup_1_practice}` | Filter status = "follow-up", group by `pratica` | Sort by count DESC |
| `${followup_1_count}` | Count per practice | Integer |
| `${followup_1_value}` | Sum valor per practice | BRL format |

#### B) Won by Practice (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${won_1_practice}` | `praticas_detalhadas.*.won` | Sort by valor DESC |
| `${won_1_count}` | `praticas_detalhadas.*.won.quantidade` | Integer |
| `${won_1_value}` | `praticas_detalhadas.*.won.valor_formatado` | BRL |

#### C) Lost by Practice (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${lost_1_practice}` | `praticas_detalhadas.*.lost` | Sort by valor DESC |
| `${lost_1_count}` | `praticas_detalhadas.*.lost.quantidade` | Integer |
| `${lost_1_value}` | `praticas_detalhadas.*.lost.valor_formatado` | BRL |

#### D) Cancelled/Abandoned by Practice (30 Days)
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${cancelled_1_practice}` | Filter cancelled, group by practice | Sort by count DESC |
| `${cancelled_1_count}` | Count per practice | Integer |
| `${cancelled_1_value}` | Sum valor per practice | BRL |

#### E) Highest Margin Practices
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${high_margin_1_practice}` | Sort practices by `margem_media_won` DESC | Top 5 |
| `${high_margin_1_value}` | `praticas_detalhadas.*.margem_media` | % |

#### F) Lowest Margin Practices
| Placeholder | Source | Notes |
|-------------|--------|-------|
| `${low_margin_1_practice}` | Sort practices by `margem_media_won` ASC | Bottom 5 |
| `${low_margin_1_value}` | `praticas_detalhadas.*.margem_media` | % |

#### Practice Comparison Matrix
| Placeholder | Source |
|-------------|--------|
| `${data_ia_won}` | `praticas_detalhadas.dados_ia.won.quantidade` |
| `${data_ia_lost}` | `praticas_detalhadas.dados_ia.lost.quantidade` |
| `${data_ia_winrate}` | Calculate from won / (won + lost) |

---

## 🔧 Azure Function Enhancements Required

To fully support all templates, the following additions to `consolidar-v2` are recommended:

### New Fields to Add

```python
# In the resultado dictionary, add:

# For TEMPLATE_05 - Market Analysis
"top_mercados_lost": [...],  # Top 5 markets by lost value
"top_mercados_cancelled": [...],  # Top 5 markets by cancellations

# For TEMPLATE_06 - WoW Trends  
"wow_comparison": {
    "current_week": {...},
    "previous_week": {...},  # Requires historical storage
    "deltas": {...}
},

# For TEMPLATE_07 - Practice Analysis
"praticas_30_dias": {
    "followup": [...],  # By practice
    "won": [...],       # By practice
    "lost": [...],      # By practice  
    "cancelled": [...]  # By practice
},
"praticas_margem_ranking": {
    "highest": [...],  # Top 5 by margin
    "lowest": [...]    # Bottom 5 by margin
}
```

---

## 📋 Integration Checklist

- [ ] Update `consolidar-v2` with new market/practice aggregations
- [ ] Implement historical data storage for WoW comparisons
- [ ] Create Power Automate expression mappings for each template
- [ ] Test card rendering with sample data
- [ ] Deploy to production Flow3

---

## 📞 Support

For questions about this mapping, contact the development team or refer to:
- `function_app.py` (lines 434-1311) for current implementation
- `POWER_BI_EXPORT_SPEC.md` for Power BI integration
