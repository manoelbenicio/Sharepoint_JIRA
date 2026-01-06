# 📊 Power BI Dashboard Specifications
## Executive Summary & Architect Allocation

**Version:** 1.0  
**Date:** 2026-01-06  
**Status:** Design Specification

---

## 🎯 Overview

Two Power BI dashboards to provide C-Level and operational visibility into the PreSales pipeline.

| Dashboard | Target Audience | Refresh |
|-----------|----------------|---------|
| Executive Summary | C-Level, Directors | Daily |
| Architect Allocation | Managers, Operations | Daily |

---

## 1. Executive Summary Dashboard

### 1.1 Purpose

Provide senior leadership with a single-page overview of pipeline health, win rates, and business performance.

### 1.2 Layout (1920x1080)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 📊 PIPELINE EXECUTIVE SUMMARY               [Date Filter] [Mercado▼]  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ PIPELINE    │  │ WON (30d)   │  │ WIN RATE    │  │ AVG CYCLE   │   │
│  │ ATIVO       │  │             │  │             │  │ TIME        │   │
│  │             │  │             │  │             │  │             │   │
│  │   R$ X.XM   │  │   R$ X.XM   │  │    XX%      │  │   XX dias   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌────────────────────────────────┐  ┌─────────────────────────────┐  │
│  │    PIPELINE BY STAGE           │  │   TOP 5 MERCADOS            │  │
│  │    (Funnel Chart)              │  │   (Bar Chart)               │  │
│  │                                │  │                             │  │
│  │    ▉▉▉▉▉▉▉▉▉▉ Qualificação    │  │   Financeiro    ████████    │  │
│  │    ▉▉▉▉▉▉▉▉ Proposta          │  │   Telecom       ██████      │  │
│  │    ▉▉▉▉▉▉ POC                 │  │   Varejo        █████       │  │
│  │    ▉▉▉▉ Negociação            │  │   Governo       ████        │  │
│  │    ▉▉ Fechamento              │  │   Saúde         ███         │  │
│  │                                │  │                             │  │
│  └────────────────────────────────┘  └─────────────────────────────┘  │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌────────────────────────────────┐  ┌─────────────────────────────┐  │
│  │   TOP 5 ARCHITECTS (Valor)     │  │   RESULTS 30 DAYS           │  │
│  │   (Table)                      │  │   (Donut Chart)             │  │
│  │                                │  │                             │  │
│  │   Architect A    R$ 2.5M      │  │        WON                  │  │
│  │   Architect B    R$ 1.8M      │  │       /    \                │  │
│  │   Architect C    R$ 1.2M      │  │    LOST    OPEN             │  │
│  │   Architect D    R$ 0.9M      │  │                             │  │
│  │   Architect E    R$ 0.7M      │  │                             │  │
│  │                                │  │                             │  │
│  └────────────────────────────────┘  └─────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Visual Specifications

#### 1.3.1 KPI Cards (Row 1)

| Card | Measure (DAX) | Format | Conditional Color |
|------|---------------|--------|-------------------|
| Pipeline Ativo | `CALCULATE(SUM([ValorTCV]), [Status] IN {"Em Qualificação", "Proposta", "POC", "Negociação"})` | Currency R$ | - |
| Won (30d) | `CALCULATE(SUM([ValorTCV]), [Status]="Won", [DataResultado] >= TODAY()-30)` | Currency R$ | Green if > R$500K |
| Win Rate | `DIVIDE([Won 30d Count], [Won 30d Count] + [Lost 30d Count])` | Percentage | Red < 30%, Yellow 30-50%, Green > 50% |
| Avg Cycle Time | `AVERAGE([DataResultado] - [DataEntrada])` | Number (dias) | - |

#### 1.3.2 Funnel Chart - Pipeline by Stage

```dax
Pipeline_Stage = 
SUMMARIZE(
    Ofertas_Pipeline,
    Ofertas_Pipeline[Status],
    "TCV", SUM(Ofertas_Pipeline[ValorTCV]),
    "Count", COUNT(Ofertas_Pipeline[JiraKey])
)
```

**Stage Order:**
1. Em Qualificação
2. Proposta Enviada
3. POC
4. Negociação
5. Fechamento

#### 1.3.3 Bar Chart - Top 5 Mercados

```dax
Top5_Mercados = 
TOPN(
    5,
    SUMMARIZE(
        Ofertas_Pipeline,
        Ofertas_Pipeline[Mercado],
        "TCV", SUM(Ofertas_Pipeline[ValorTCV])
    ),
    [TCV], DESC
)
```

#### 1.3.4 Table - Top 5 Architects

| Column | Field | Format |
|--------|-------|--------|
| Arquiteto | ArquitetoLead | Text |
| Valor Total | SUM(ValorTCV) | Currency |
| # Ofertas | COUNT(JiraKey) | Number |
| Win Rate | Calculated | Percentage |

#### 1.3.5 Donut Chart - Results 30 Days

```dax
Results_30d = 
CALCULATETABLE(
    SUMMARIZE(
        Ofertas_Pipeline,
        Ofertas_Pipeline[Status],
        "Count", COUNT(Ofertas_Pipeline[JiraKey])
    ),
    Ofertas_Pipeline[DataResultado] >= TODAY() - 30,
    Ofertas_Pipeline[Status] IN {"Won", "Lost"}
)
```

### 1.4 Filters & Slicers

| Filter | Type | Default |
|--------|------|---------|
| Date Range | Date Slicer | Last 90 days |
| Mercado | Dropdown | All |
| Prática | Dropdown | All |
| Status | Checkbox | Active Only |

---

## 2. Architect Allocation Dashboard

### 2.1 Purpose

Track architect workload, utilization, and budget consumption across the pipeline.

### 2.2 Layout (1920x1080)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 👥 ARCHITECT ALLOCATION DASHBOARD           [Date Filter] [Arquiteto▼]│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ ACTIVE      │  │ AVG OFFERS  │  │ TOTAL HOURS │  │ UTILIZATION │   │
│  │ ARCHITECTS  │  │ PER ARCH    │  │ BUDGET      │  │ RATE        │   │
│  │             │  │             │  │             │  │             │   │
│  │     XX      │  │    X.X      │  │   X,XXX h   │  │    XX%      │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                   ARCHITECT HEATMAP                             │   │
│  │                   (Matrix Visual)                               │   │
│  │                                                                 │   │
│  │   Arquiteto     │ Qualif │ Proposta │ POC │ Negoc │ Fecham │   │   │
│  │   ─────────────────────────────────────────────────────────    │   │
│  │   Architect A   │   3    │    2     │  1  │   -   │   -   │   │   │
│  │   Architect B   │   2    │    3     │  2  │   1   │   -   │   │   │
│  │   Architect C   │   1    │    1     │  -  │   2   │   1   │   │   │
│  │   Architect D   │   4    │    1     │  1  │   -   │   -   │   │   │
│  │   Architect E   │   2    │    2     │  2  │   1   │   -   │   │   │
│  │                                                                 │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────┐  ┌────────────────────────────┐  │
│  │   BUDGET HOURS CONSUMPTION      │  │   OFFERS BY ARCHITECT      │  │
│  │   (Stacked Bar)                 │  │   (Bar Chart)              │  │
│  │                                 │  │                            │  │
│  │   Arch A  ████████░░░░ 67%     │  │   Arch A  ██████████  10   │  │
│  │   Arch B  ██████████░░ 83%     │  │   Arch B  ████████    8    │  │
│  │   Arch C  ████████████ 100%    │  │   Arch C  ██████      6    │  │
│  │   Arch D  ██████░░░░░░ 50%     │  │   Arch D  ████████    8    │  │
│  │   Arch E  ████░░░░░░░░ 33%     │  │   Arch E  ████        4    │  │
│  │                                 │  │                            │  │
│  └─────────────────────────────────┘  └────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Visual Specifications

#### 2.3.1 KPI Cards (Row 1)

| Card | Measure (DAX) | Format |
|------|---------------|--------|
| Active Architects | `DISTINCTCOUNT([ArquitetoLead])` | Number |
| Avg Offers/Arch | `DIVIDE(COUNT([JiraKey]), DISTINCTCOUNT([ArquitetoLead]))` | Decimal 1 |
| Total Hours Budget | `SUM([HorasBudget])` | Number with comma |
| Utilization Rate | `DIVIDE(SUM([HorasConsumidas]), SUM([HorasBudget]))` | Percentage |

#### 2.3.2 Matrix - Architect Heatmap

```dax
ArchitectHeatmap = 
SUMMARIZE(
    Ofertas_Pipeline,
    Ofertas_Pipeline[ArquitetoLead],
    Ofertas_Pipeline[Status],
    "Count", COUNT(Ofertas_Pipeline[JiraKey])
)
```

**Conditional Formatting:**
| Count | Background Color |
|-------|------------------|
| 0 | White |
| 1-2 | Light Green |
| 3-4 | Yellow |
| 5+ | Red (overloaded) |

#### 2.3.3 Stacked Bar - Budget Hours Consumption

```dax
BudgetConsumption = 
SUMMARIZE(
    FILTER(Ofertas_Pipeline, [Status] <> "Won" && [Status] <> "Lost"),
    Ofertas_Pipeline[ArquitetoLead],
    "HorasUsadas", SUM(Ofertas_Pipeline[HorasConsumidas]),
    "HorasBudget", SUM(Ofertas_Pipeline[HorasBudget]),
    "Utilization", DIVIDE(SUM([HorasConsumidas]), SUM([HorasBudget]))
)
```

#### 2.3.4 Bar Chart - Offers by Architect

| Field | Axis |
|-------|------|
| ArquitetoLead | Y-Axis |
| COUNT(JiraKey) | X-Axis (Values) |
| Status | Legend (Stacked) |

### 2.4 Drillthrough Page

**Name:** Architect Detail

**Trigger:** Click on any architect name

| Visual | Data |
|--------|------|
| Profile Card | Name, Email, DN, Prática |
| Offer Table | All active offers for architect |
| Timeline | Offer wins/losses over time |
| Status Distribution | Pie chart of current offers by status |

---

## 3. Common DAX Measures

### 3.1 Time Intelligence

```dax
// Pipeline Value (Active)
Pipeline_Ativo = 
CALCULATE(
    SUM(Ofertas_Pipeline[ValorTCV]),
    Ofertas_Pipeline[Status] IN {"Em Qualificação", "Proposta Enviada", "POC", "Negociação", "Fechamento"}
)

// Won Value - Last 30 Days
Won_30d = 
CALCULATE(
    SUM(Ofertas_Pipeline[ValorTCV]),
    Ofertas_Pipeline[Status] = "Won",
    DATESINPERIOD(DateTable[Date], TODAY(), -30, DAY)
)

// Lost Value - Last 30 Days
Lost_30d = 
CALCULATE(
    SUM(Ofertas_Pipeline[ValorTCV]),
    Ofertas_Pipeline[Status] = "Lost",
    DATESINPERIOD(DateTable[Date], TODAY(), -30, DAY)
)

// Win Rate - Last 30 Days
WinRate_30d = 
VAR WonCount = CALCULATE(COUNTROWS(Ofertas_Pipeline), Ofertas_Pipeline[Status]="Won", Ofertas_Pipeline[DataResultado] >= TODAY()-30)
VAR LostCount = CALCULATE(COUNTROWS(Ofertas_Pipeline), Ofertas_Pipeline[Status]="Lost", Ofertas_Pipeline[DataResultado] >= TODAY()-30)
RETURN
DIVIDE(WonCount, WonCount + LostCount, 0)

// Average Cycle Time (Days)
AvgCycleTime = 
AVERAGEX(
    FILTER(Ofertas_Pipeline, Ofertas_Pipeline[Status] IN {"Won", "Lost"}),
    DATEDIFF(Ofertas_Pipeline[DataEntrada], Ofertas_Pipeline[DataResultado], DAY)
)
```

### 3.2 Ranking Measures

```dax
// Architect Rank by Value
Architect_Rank_Value = 
RANKX(
    ALL(Ofertas_Pipeline[ArquitetoLead]),
    CALCULATE(SUM(Ofertas_Pipeline[ValorTCV])),
    ,DESC,Dense
)

// Market Rank by Count
Market_Rank_Count = 
RANKX(
    ALL(Ofertas_Pipeline[Mercado]),
    CALCULATE(COUNTROWS(Ofertas_Pipeline)),
    ,DESC,Dense
)
```

---

## 4. Publishing & Sharing

### 4.1 Power BI Workspace

- **Workspace Name:** `PreSales Analytics`
- **License:** Pro (minimum)
- **Members:**
  - Directors: Viewer
  - Managers: Contributor
  - Admins: Admin

### 4.2 Teams Integration

1. Go to target Teams channel
2. Click **+** (Add a tab)
3. Select **Power BI**
4. Choose the dashboard
5. Save tab

### 4.3 Mobile App

Both dashboards optimized for Power BI Mobile:
- Responsive layout
- Simplified visuals for small screens
- Touch-enabled filters

---

## 5. Validation Checklist

- [ ] Dataset refreshes successfully
- [ ] All DAX measures calculate correctly
- [ ] Conditional formatting works
- [ ] Filters interact properly
- [ ] Mobile layout configured
- [ ] Published to workspace
- [ ] Teams tab created
- [ ] User permissions set

---

*Document: DASHBOARD_SPECIFICATIONS.md*  
*Project: JIRA → SharePoint → Teams/Power BI Integration*
