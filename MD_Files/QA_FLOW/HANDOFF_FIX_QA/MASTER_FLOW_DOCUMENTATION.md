# Master Flow Documentation

**Last Updated**: 2026-01-06T12:42:00-03:00  
**Source of Truth**: Power Automate Screenshots (verified 2026-01-06)

---

## ✅ Verified Flow Structure (From Power Automate Screenshots)

| Flow | Name in PA | Purpose | Cards |
|------|------------|---------|-------|
| **Flow 1** | `Flow1_QueueCreator_PROD_v30` | Queue creation from SharePoint | N/A |
| **Flow 2** | `Flow2_Trigger_PROD_v30` | Card posting + response handling | 1 (production card) |
| **Flow 3** | `Flow3_PROD_v10` | Get Ofertas/Atualizacoes → HTTP → Post message | 1 message |
| **Flow 4** | `Flow4_Jinglet_Upload_PROD_v10` | JIRA CSV import trigger | 1 ("IMPORT JIRA CONCLUÍDO") |
| **Flow 5** | `Flow5_Post Weekly Flash Report` | Posts 3 premium cards | 3 (Executive, Flash, RAG) |
| **Flow 6** | `Flow6_Premium_Analytics_Bi_Weekly` | Premium analytics | 4 (ARQ, Market, WoW, Practice) |

---

## 📸 Evidence from Screenshots

### Flow 4 - Jinglet Upload (EXISTS!)
- **Trigger**: "Quando um arquivo é criado em uma pasta (prefixado)"
- **Actions**: Obter conteúdo de arquivo → Compor → HTTP → Analisar JSON → Aplicar a cada → Postar cartão
- **Channel**: `Ofertas_Status_Report_Semanal`
- **Card**: "IMPORT JIRA CONCLUÍDO"

### Flow 5 - Post Weekly Flash Report
- **Trigger**: Recurrence
- **Actions**: HTTP → Post Executive One-Pager → Post Weekly Flash Report → Post RAG Matrix
- **Channel**: `Ofertas_Status_Report_Semanal`
- **Cards**: 3 sequential posts

---

## 📋 Corrected Template Mapping

| Template | Full Name | Assigned To | Evidence |
|----------|-----------|-------------|----------|
| TEMPLATE_01 | `Executive_OnePager.json` | **Flow 5** | Screenshot shows "Post Executive One-Pager" action |
| TEMPLATE_02 | `Weekly_Flash_Report.json` | **Flow 5** | Screenshot shows "Post Weekly Flash Report" action |
| TEMPLATE_02_CLevel | `Weekly_Flash_Report_CLevel.json` | **Flow 3** | Used for C-Level message |
| TEMPLATE_03 | `RAG_Matrix.json` | **Flow 5** | Screenshot shows "Post RAG Matrix" action |
| TEMPLATE_04 | `ARQ_Performance.json` | **Flow 6** | Premium analytics |
| TEMPLATE_05 | `Market_Analysis.json` | **Flow 6** | Premium analytics |
| TEMPLATE_06 | `WoW_Trends.json` | **Flow 6** | Premium analytics |
| TEMPLATE_07 | `Practice_Analysis.json` | **Flow 6** | Premium analytics |
| JIRA Import Card | Custom | **Flow 4** | "IMPORT JIRA CONCLUÍDO" card |

---

## 📁 Ready-to-Paste Files Status

| Flow | File | Templates | Status |
|------|------|-----------|--------|
| Flow 3 | `FLOW3_READY_TO_PASTE_CARD.md` | TEMPLATE_02_CLevel only | ✅ |
| Flow 4 | `FLOW4_READY_TO_PASTE_CARD.md` | JIRA Import card | ❌ NEEDS CREATION |
| Flow 5 | `FLOW5_READY_TO_PASTE_CARDS.md` | Templates 01, 02, 03 | ⚠️ NEEDS UPDATE (add Template 01) |
| Flow 6 | `FLOW6_READY_TO_PASTE_CARDS.md` | Templates 04-07 | ✅ |

---

## 🔧 Pending Actions

1. [x] Update master documentation with correct flow structure
2. [ ] Create `FLOW4_READY_TO_PASTE_CARD.md` for JIRA Import card
3. [ ] Update `FLOW5_READY_TO_PASTE_CARDS.md` to include all 3 templates (01, 02, 03)
4. [ ] Update `FLOW3_READY_TO_PASTE_CARD.md` to only have Template 02_CLevel

---

## 📷 Screenshot Evidence Files

- `uploaded_image_0.png` - Flow1: QueueCreator
- `uploaded_image_1.png` - Flow2: Trigger  
- `uploaded_image_2.png` - Flow3: PROD_v10
- `uploaded_image_3.png` - Flow4: Jinglet_Upload
- `uploaded_image_4.png` - Flow5: Post Weekly Flash Report
