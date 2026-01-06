# Power BI Export Specification

**Last Updated:** 2026-01-06  
**Status:** Ready for Implementation

---

## 🎯 Overview

This document defines the data export specification for connecting the Azure Function `consolidar-v2` to Power BI dashboards. The goal is to provide a structured JSON payload that can be consumed by Power BI via REST API or exported to Azure Blob/Data Lake for scheduled refresh.

---

## 📊 Export Endpoints

### Option 1: Direct REST API (Recommended for Real-Time)

```
GET https://<function-app>.azurewebsites.net/api/consolidar-v2-pbi?code=<function-key>
```

**Response Format:** JSON with flattened arrays for Power BI consumption

### Option 2: Azure Blob Storage (Recommended for Scheduled)

```
POST https://<function-app>.azurewebsites.net/api/export-pbi?code=<function-key>
```

**Output:** JSON file saved to Azure Blob Storage with timestamp

---

## 🗂️ Data Schema for Power BI

### 1. Executive Summary Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier (YYYY-WNN) |
| `data_geracao` | datetime | Report generation timestamp |
| `total_ofertas` | int | Total active offers |
| `pipeline_valor_total` | decimal | Total pipeline value (BRL) |
| `win_rate_7d` | decimal | Win rate last 7 days (%) |
| `win_rate_15d` | decimal | Win rate last 15 days (%) |
| `win_rate_30d` | decimal | Win rate last 30 days (%) |
| `margem_media_won` | decimal | Average margin on won deals (%) |
| `margem_media_lost` | decimal | Average margin on lost deals (%) |
| `taxa_resposta` | decimal | Architect response rate (%) |
| `total_arquitetos` | int | Total architects |
| `arquitetos_responderam` | int | Architects who responded |

### 2. Pipeline by Status Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `status` | string | Status category |
| `quantidade` | int | Number of offers |
| `valor` | decimal | Total value (BRL) |

### 3. Architect Performance Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `arquiteto` | string | Architect name |
| `ofertas_ativas` | int | Active offers count |
| `valor_pipeline` | decimal | Total value (BRL) |
| `horas_alocadas` | decimal | Budget hours allocated |
| `horas_consumidas` | decimal | Hours consumed |
| `taxa_utilizacao` | decimal | Utilization rate (%) |
| `media_ciclo_dias` | decimal | Average cycle time (days) |
| `won_30d` | int | Won offers last 30 days |
| `lost_30d` | int | Lost offers last 30 days |
| `ofertas_100mm` | int | Offers > 100MM BRL |

### 4. Market Analysis Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `mercado` | string | Market name |
| `ofertas_ativas` | int | Active offers |
| `valor_pipeline` | decimal | Pipeline value (BRL) |
| `won_30d_count` | int | Won count (30d) |
| `won_30d_valor` | decimal | Won value (30d) |
| `lost_30d_count` | int | Lost count (30d) |
| `lost_30d_valor` | decimal | Lost value (30d) |
| `followup_count` | int | Follow-up count |
| `followup_valor` | decimal | Follow-up value |
| `cancelled_90d` | int | Cancelled/Abandoned (90d) |
| `margem_media` | decimal | Average margin (%) |

### 5. Practice Mix Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `pratica` | string | Practice name |
| `valor_ponderado` | decimal | Weighted value (BRL) |
| `ofertas_count` | int | Number of offers |
| `pct_do_total` | decimal | Percentage of total |

### 6. Customer Concentration Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `cliente` | string | Client name |
| `valor_pipeline` | decimal | Pipeline value (BRL) |
| `ofertas_count` | int | Number of offers |
| `pct_concentracao` | decimal | Concentration percentage |

### 7. Week-over-Week Trends Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `metric` | string | Metric name |
| `current_value` | decimal | Current week value |
| `previous_value` | decimal | Previous week value |
| `delta_value` | decimal | Change value |
| `delta_pct` | decimal | Change percentage |
| `trend` | string | up/down/stable |

### 8. Practice Analysis Table

| Field | Type | Description |
|---|---|---|
| `semana` | string | Week identifier |
| `pratica` | string | Practice name (Data/IA, DS, SGE, DIC, GU, Cyber) |
| `ofertas_ativas` | int | Active offers |
| `valor_pipeline` | decimal | Pipeline value (BRL) |
| `followup_30d_count` | int | Follow-up count (30d) |
| `followup_30d_valor` | decimal | Follow-up value (30d) |
| `won_30d_count` | int | Won count (30d) |
| `won_30d_valor` | decimal | Won value (30d) |
| `lost_30d_count` | int | Lost count (30d) |
| `lost_30d_valor` | decimal | Lost value (30d) |
| `cancelled_30d` | int | Cancelled/Abandoned (30d) |
| `margem_media` | decimal | Average margin (%) |
| `win_rate` | decimal | Win rate (%) |

---

## 🔌 Power BI Connection Steps

1. **Create a new data source** in Power BI Desktop:
   - Data → Get Data → Web
   - Enter the API URL with function key

2. **Transform data** using Power Query:
   - Expand nested arrays (pipeline_por_fase, top_mercados, etc.)
   - Convert types (dates, numbers)
   - Create calculated columns for KPIs

3. **Schedule refresh** (Power BI Service):
   - Set up data gateway if needed
   - Configure refresh schedule (e.g., daily at 8 AM)

---

## 🧪 Sample API Response

```json
{
  "semana": "2026-W02",
  "data_geracao": "2026-01-06T09:00:00Z",
  "pbi_export": {
    "executive_summary": {...},
    "pipeline_by_status": [...],
    "architect_performance": [...],
    "market_analysis": [...],
    "practice_mix": [...],
    "customer_concentration": [...],
    "wow_trends": [...]
  }
}
```

---

## 📈 Recommended Power BI Dashboards

1. **Executive Dashboard** - Pipeline overview, win rates, margins
2. **Architect Performance** - Utilization, volume, cycle time
3. **Market Intelligence** - Won/lost by market, margins
4. **Trend Analysis** - WoW comparisons, forecasting
5. **Risk Monitoring** - Low margin, high concentration alerts

---

## ⚙️ Implementation Notes

- Function will need new endpoint `/consolidar-v2-pbi` with flattened structure
- Historical data storage recommended for trend analysis (Azure Table Storage or Cosmos DB)
- Consider caching layer (Redis) for high-frequency dashboard refreshes
