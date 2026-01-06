# TD-002 Execution Checklist

**Status:** 🟡 IN PROGRESS  
**Executed by:** AI Agent (Antigravity) + Human (Portal)  
**Started:** 2025-12-30T10:50:00-03:00  

## Required Flow2 Configuration

Apply these settings to Flow2's SharePoint `Obter_itens_fila` (Get items) action:

### Filter Query
```
QueueStatus eq 'Pending' and RecipientEmail eq 'mbenicios@minsait.com'
```

### Order By
```
Created asc
```

### Top Count
```
1
```

## Execution Steps

- [ ] 1. Open Flow2 in Power Automate edit mode
- [ ] 2. Locate SharePoint action `Obter_itens_fila` / `Get items`
- [ ] 3. Set Filter Query as above
- [ ] 4. Set Order By: `Created asc`
- [ ] 5. Set Top Count: `1`
- [ ] 6. Save Flow2
- [ ] 7. Create 1 test queue item with `QueueStatus=Pending` for `mbenicios@minsait.com`
- [ ] 8. Run Flow2 once (canary test)
- [ ] 9. Verify: exactly 1 card received in Teams
- [ ] 10. Verify: queue item transitions `Pending → Sent`

## Evidence Required

- [ ] Screenshot of Flow2 queue query settings
- [ ] Queue item before/after (ID, RecipientEmail, QueueStatus, Created, Modified)
- [ ] Teams screenshot showing only 1 card received

## Validation

- [ ] Selected item transitions predictably: `Pending → Sent`
- [ ] No other recipients' rows changed
- [ ] Exactly 1 card arrives for `mbenicios@minsait.com`

## Notes

> [!IMPORTANT]
> If you cannot 100% guarantee the allowlist constraint, **DO NOT RUN**.
> Mark as **BLOCKED (business hours validation required)**.
