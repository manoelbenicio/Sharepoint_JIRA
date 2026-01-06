# F3 Fix: Flow1 Dedupe Enhancement

## Problem
Flow1 creates duplicate queue items because it doesn't check if an item with the same UniqueKey already exists before creating a new one.

**Evidence:** F3 test found 58 duplicate (OfertaId+Semana+Email) combinations.

---

## Fix: Add "Check Existing" Before Create

### Step-by-Step Instructions

1. **Open Flow1** in Power Automate edit mode

2. **Find the "Create Item" action** that creates the queue item

3. **Add a new action BEFORE "Create Item":**
   - Action: **Get Items** (SharePoint)
   - Site Address: `https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA`
   - List Name: `StatusReports_Queue`
   - Filter Query:
     ```
     UniqueKey eq '@{variables('UniqueKey')}'
     ```
   - Top Count: `1`

4. **Add a Condition after "Get Items":**
   - Condition: `length(outputs('Get_Items')?['body/value'])` **is equal to** `0`
   - If yes → Create Item (existing action)
   - If no → Skip (do nothing)

### Visual Flow

```
┌─────────────────────┐
│  Build UniqueKey    │
│  (existing logic)   │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Get Items          │  ← NEW
│  Filter: UniqueKey  │
│  Top Count: 1       │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Condition          │  ← NEW
│  length() = 0 ?     │
├─────────┬───────────┤
│  Yes    │    No     │
└────┬────┴────┬──────┘
     ▼         ▼
┌─────────┐ ┌─────────┐
│ Create  │ │ (Skip)  │
│ Item    │ │         │
└─────────┘ └─────────┘
```

---

## Alternative: SharePoint Indexed Column

If you want to enforce uniqueness at the SharePoint level:

1. Go to SharePoint List Settings → Indexed Columns
2. Create index on `UniqueKey` column
3. Note: SharePoint doesn't enforce uniqueness, only indexing for performance

---

## Verification After Fix

1. Clean up existing duplicates:
   ```powershell
   .\scripts\fix_f3_cleanup_duplicates.ps1
   ```

2. Run Flow1 multiple times on the same week

3. Re-run F3 test:
   ```powershell
   .\scripts\test_f3_concurrency.ps1
   ```

Expected result: `F3 PASS - No duplicate queue items found`
