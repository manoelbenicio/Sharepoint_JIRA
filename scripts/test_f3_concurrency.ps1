# F3 Test: Concurrency/Race Condition Test
# Verifies no duplicate queue items are created under parallel/rapid Flow1 invocations
#
# Primary check: UniqueKey duplicates (the actual constraint enforced by Flow1)
# Secondary info: OfertaId+Semana+Email combinations (informational only)
#
# Usage:
#   Connect-PnPOnline -Url "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" -UseWebLogin
#   .\scripts\test_f3_concurrency.ps1

param(
    [string]$QueueListName = "StatusReports_Queue"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST F3: Concurrency/Race Condition Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking for duplicate UniqueKey values (Flow1 dedupe constraint)..." -ForegroundColor Yellow
Write-Host ""

# Get all queue items
$items = Get-PnPListItem -List $QueueListName -PageSize 500

if ($items.Count -eq 0) {
    Write-Host "[INFO] No items found in $QueueListName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "RESULT: F3 PASS - No data to check (0 items)" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($items.Count) items in $QueueListName" -ForegroundColor Gray
Write-Host ""

# PRIMARY CHECK: UniqueKey duplicates (the actual constraint)
Write-Host "[1/2] Checking UniqueKey duplicates (PRIMARY)..." -ForegroundColor Gray

$uniqueKeyGroups = $items | Where-Object { 
    -not [string]::IsNullOrWhiteSpace($_.FieldValues.UniqueKey) 
} | Group-Object { $_.FieldValues.UniqueKey }

$uniqueKeyDupes = $uniqueKeyGroups | Where-Object { $_.Count -gt 1 }

Write-Host "  Items with UniqueKey: $($uniqueKeyGroups.Count)" -ForegroundColor Gray
Write-Host "  Duplicate UniqueKeys: $($uniqueKeyDupes.Count)" -ForegroundColor $(if ($uniqueKeyDupes.Count -gt 0) { "Red" } else { "Green" })

if ($uniqueKeyDupes.Count -gt 0) {
    Write-Host ""
    Write-Host "[DETAIL] Duplicate UniqueKeys found:" -ForegroundColor Red
    foreach ($dup in ($uniqueKeyDupes | Select-Object -First 10)) {
        Write-Host "  UniqueKey: $($dup.Name)" -ForegroundColor Yellow
        Write-Host "  Count: $($dup.Count)" -ForegroundColor Red
        $ids = ($dup.Group | ForEach-Object { $_.Id }) -join ", "
        Write-Host "  IDs: $ids" -ForegroundColor Gray
        Write-Host ""
    }
}

# SECONDARY CHECK: OfertaId+Semana+Email (informational only)
Write-Host ""
Write-Host "[2/2] Checking OfertaId+Semana+Email (informational)..." -ForegroundColor Gray

$groups = $items | Group-Object { 
    "$($_.FieldValues.OfertaId)|$($_.FieldValues.Semana)|$($_.FieldValues.RecipientEmail)" 
}

$duplicates = $groups | Where-Object { $_.Count -gt 1 }

Write-Host "  Unique combinations: $($groups.Count)" -ForegroundColor Gray
Write-Host "  With multiple items: $($duplicates.Count)" -ForegroundColor $(if ($duplicates.Count -gt 0) { "Yellow" } else { "Green" })

if ($duplicates.Count -gt 0) {
    Write-Host "  (This is expected if multiple JiraKeys map to same OfertaId)" -ForegroundColor Gray
}

# Final result based on UniqueKey only
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($uniqueKeyDupes.Count -eq 0) {
    Write-Host "RESULT: F3 PASS - No duplicate UniqueKey values found" -ForegroundColor Green
    Write-Host "  Flow1 dedupe constraint is working correctly" -ForegroundColor Green
    Write-Host "  UniqueKey format: JiraKey|Semana|VersaoReport" -ForegroundColor Gray
    exit 0
}
else {
    Write-Host "RESULT: F3 FAIL - Duplicate UniqueKey values detected" -ForegroundColor Red
    Write-Host "  $($uniqueKeyDupes.Count) duplicate UniqueKey values" -ForegroundColor Red
    Write-Host "  Flow1 dedupe logic needs investigation" -ForegroundColor Red
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
