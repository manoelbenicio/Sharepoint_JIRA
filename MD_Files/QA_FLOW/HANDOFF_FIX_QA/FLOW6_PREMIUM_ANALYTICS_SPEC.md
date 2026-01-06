# Premium Cards Implementation Strategy

**Document Version:** 1.1  
**Created:** 2026-01-06  
**Last Updated:** 2026-01-06 07:04 BRT  
**Status:** ✅ APPROVED - Ready for Implementation

---

## 🎯 Executive Summary

This document outlines the **recommended best practices** for implementing the new premium Adaptive Cards (Templates 04-07) without impacting the existing production flows (Flow1, Flow2, Flow3).

### Key Decisions (User Approved)
- ✅ Channel Created: **Ofertas_Analytics**
- ✅ Schedule: **Bi-weekly (Tuesday & Friday)** or **Fridays only**
- ✅ Initial Mode: **Manual trigger** during testing period
- ✅ Approach: New Flow6 (isolated from production flows)

---

## 📋 Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION FLOWS                            │
├─────────────────────────────────────────────────────────────────────┤
│  Flow1: SharePoint → Queue Writer                                   │
│  Flow2: Queue → Individual Status Cards (TEMPLATE_01/02)            │
│  Flow3: Scheduled → C-Level Weekly Flash (Weekly Flash Card)        │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Azure Function: consolidar-v2                   │
│  • Pipeline metrics        • Market analysis                        │
│  • ARQ performance         • Practice metrics                       │
│  • Budget utilization      • Win/Loss tracking                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✅ APPROVED APPROACH: Create Flow6 (Premium Analytics)

### Why a New Flow?

| Benefit | Description |
|---------|-------------|
| **Zero Risk** | No impact on production Flow1/2/3 |
| **Independent Testing** | Test new cards without affecting weekly reports |
| **Gradual Rollout** | Enable by audience (managers first, then directors) |
| **Easy Rollback** | Disable Flow6 without touching other flows |
| **Bi-weekly Schedule** | Tuesday & Friday runs for fresh analytics |

---

## 🏗️ Approved Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION FLOWS (UNCHANGED)                     │
├─────────────────────────────────────────────────────────────────────┤
│  Flow1: SharePoint → Queue Writer              ✅ No changes        │
│  Flow2: Queue → Individual Status Cards        ✅ No changes        │
│  Flow3: C-Level Weekly Flash                   ✅ No changes        │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌──────────────────────────────┐  ┌──────────────────────────────────┐
│  Azure Function              │  │  Azure Function (FUTURE)         │
│  consolidar-v2               │  │  consolidar-v3-premium           │
│  (existing - used by Flow4)  │  │  (optional enhancement)          │
└──────────────────────────────┘  └──────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   NEW FLOW6 - PREMIUM ANALYTICS                     │
├─────────────────────────────────────────────────────────────────────┤
│  Trigger: Bi-weekly (Tuesday & Friday @ 9:00 AM BRT)                │
│  Channel: Ofertas_Analytics ✅ (Created 2026-01-06)                 │
│  Initial Mode: Manual trigger during testing                       │
│                                                                     │
│  Cards Delivered:                                                   │
│  • TEMPLATE_04: ARQ Performance                                     │
│  • TEMPLATE_05: Market Analysis                                     │
│  • TEMPLATE_06: WoW Trends                                          │
│  • TEMPLATE_07: Practice Analysis                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Implementation Steps

### Phase 1: Azure Function Enhancement (Optional)

> ⚠️ **Note:** You can skip this if current `consolidar-v2` provides enough data

```python
# Option A: Extend consolidar-v2 (adds new fields, backward compatible)
# Option B: Create consolidar-v3-premium (completely separate endpoint)
```

**Recommendation:** Start with **Option A** - just add new fields to existing endpoint

| New Field | Purpose |
|-----------|---------|
| `top_mercados_lost` | Market losses ranking |
| `top_mercados_cancelled` | Cancelled by market |
| `praticas_30_dias` | Practice-level 30-day metrics |
| `praticas_margem_ranking` | Margin by practice |
| `wow_comparison` | Week-over-week deltas |
| `customer_concentration` | Top clients by value |

---

### Phase 2: Create Teams Channel

1. **Create new channel:** `Ofertas_Premium_Analytics`
2. **Set permissions:** Directors + C-Level only
3. **Purpose:** Dedicated channel for deep-dive analytics

---

### Phase 3: Create Flow6 in Power Automate

#### Flow6 Configuration

| Setting | Value |
|---------|-------|
| **Name** | `Flow6 - Premium Analytics Bi-Weekly` |
| **Trigger Option A** | Recurrence: Tuesday & Friday @ 9:00 AM BRT |
| **Trigger Option B** | Recurrence: Fridays only @ 9:00 AM BRT |
| **Initial Mode** | ⚠️ **Manual trigger** during testing period |
| **HTTP Action** | GET `consolidar-v2` endpoint |
| **Parse JSON** | Same schema as Flow3 |
| **Post to Teams** | 4 cards in sequence to **Ofertas_Analytics** channel |

#### Flow6 Steps

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. TRIGGER: Recurrence (Monthly, 1st Monday, 9:00 AM BRT)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. HTTP GET: Azure Function consolidar-v2                       │
│    URL: https://<app>.azurewebsites.net/api/consolidar-v2       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PARSE JSON: Extract metrics                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 4a. Compose:    │ │ 4b. Compose:    │ │ 4c. Compose:    │
│ TEMPLATE_04     │ │ TEMPLATE_05     │ │ TEMPLATE_06     │
│ ARQ Performance │ │ Market Analysis │ │ WoW Trends      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              │   ┌───────────┴───────────────┤
              ▼   ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4d. Compose: TEMPLATE_07 Practice Analysis                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. POST TO TEAMS: Send all 4 cards to Premium_Analytics channel │
│    • Delay 2 seconds between cards to avoid throttling          │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 4: Testing Strategy

| Stage | Environment | Duration |
|-------|-------------|----------|
| **1. Dev Test** | Manual trigger, your user only | 1 day |
| **2. UAT** | Test channel with 3-5 stakeholders | 1 week |
| **3. Pilot** | Production channel, manual trigger | 2 weeks |
| **4. Production** | Enable scheduled trigger | Ongoing |

---

## 🔄 Alternative Approaches (Not Recommended)

### ❌ Option B: Add to Flow3

| Pros | Cons |
|------|------|
| Single flow to maintain | Risk breaking weekly report |
| Same schedule | Too many cards in one batch |
| | Longer execution time |
| | Harder to debug |

### ❌ Option C: Modify Existing Templates

| Pros | Cons |
|------|------|
| No new flows | Changes production immediately |
| | Can't A/B test |
| | Hard to rollback |

---

## 📅 Approved Schedule Matrix

| Flow | Frequency | Day(s) | Time | Cards | Status |
|------|-----------|--------|------|-------|--------|
| Flow2 | On-demand | Any | Immediate | Individual Status | ✅ Production |
| Flow3 | Weekly | Monday | 8:00 AM | Weekly Flash | ✅ Production |
| **Flow6** | **Bi-weekly** | **Tue & Fri** | **9:00 AM** | **Premium Analytics (4)** | 🆕 Testing |

### Alternative Schedule (If Preferred)

| Flow | Frequency | Day | Time | Cards |
|------|-----------|-----|------|-------|
| **Flow6** | **Weekly** | **Friday only** | **9:00 AM** | **Premium Analytics (4)** |

---

## 🧪 Validation Checklist

Before going to production:

- [ ] All 4 templates render correctly in Adaptive Card Designer
- [ ] Azure Function returns required fields
- [ ] Teams channel created with proper permissions
- [ ] Flow6 tested with manual trigger
- [ ] Stakeholders approve card content
- [ ] Scheduled trigger enabled

---

## 📊 Success Metrics

After 1 month of operation:

| Metric | Target |
|--------|--------|
| Card delivery success rate | > 99% |
| Executive feedback score | > 4/5 |
| Data accuracy | 100% |
| Flow execution time | < 30 seconds |

---

## 🚀 Quick Start Commands

### 1. Test Azure Function
```powershell
# Test current endpoint
Invoke-RestMethod -Uri "https://<app>.azurewebsites.net/api/consolidar-v2?code=<key>" -Method GET
```

### 2. Validate Templates
```powershell
# Open Adaptive Card Designer
Start-Process "https://adaptivecards.io/designer/"
# Paste template JSON and verify rendering
```

### 3. Create Flow6
1. Go to Power Automate → Create → Scheduled cloud flow
2. Name: `Flow6 - Premium Analytics Bi-Weekly`
3. Follow steps in Phase 3 above

---

## 📞 Support

| Issue | Contact |
|-------|---------|
| Azure Function | DevOps Team |
| Power Automate | Integration Team |
| Templates | This document |
| Business Logic | Data Analyst Team |

---

## 📎 Related Documents

- `TEMPLATE_04_ARQ_Performance.json`
- `TEMPLATE_05_Market_Analysis.json`
- `TEMPLATE_06_WoW_Trends.json`
- `TEMPLATE_07_Practice_Analysis.json`
- `TEMPLATE_DATA_MAPPING.md`
- `POWER_BI_EXPORT_SPEC.md`
- `FLOW3_CLEVEL_WEEKLY_SPEC.md`
