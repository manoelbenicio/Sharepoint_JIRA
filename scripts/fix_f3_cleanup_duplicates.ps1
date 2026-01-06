# F3 Fix: Queue Duplicates Cleanup Script
# Removes duplicate queue items, keeping only the first item of each UniqueKey group
#
# Usage:
#   1. Connect to SharePoint first:
#      Connect-PnPOnline -Url "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" -UseWebLogin
#   2. Run in dry-run mode first to see what will be deleted:
#      .\scripts\fix_f3_cleanup_duplicates.ps1 -DryRun
#   3. Run for real:
#      .\scripts\fix_f3_cleanup_duplicates.ps1

param(
    [string]$QueueListName = "StatusReports_Queue",
    [switch]$DryRun = $false
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "F3 FIX: Queue Duplicates Cleanup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] - No items will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

# Get all queue items
Write-Host "[1/4] Fetching all queue items..." -ForegroundColor Gray
$items = Get-PnPListItem -List $QueueListName -PageSize 500

if ($items.Count -eq 0) {
    Write-Host "[INFO] No items found in $QueueListName" -ForegroundColor Gray
    exit 0
}

Write-Host "  Found $($items.Count) total items" -ForegroundColor Gray
Write-Host ""

# Group by UniqueKey
Write-Host "[2/4] Finding duplicate groups..." -ForegroundColor Gray
$groups = $items | Where-Object { 
    -not [string]::IsNullOrWhiteSpace($_.FieldValues.UniqueKey) 
} | Group-Object { $_.FieldValues.UniqueKey }

$duplicateGroups = $groups | Where-Object { $_.Count -gt 1 }

Write-Host "  Unique keys: $($groups.Count)" -ForegroundColor Gray
Write-Host "  Duplicate groups: $($duplicateGroups.Count)" -ForegroundColor $(if ($duplicateGroups.Count -gt 0) { "Yellow" } else { "Green" })

if ($duplicateGroups.Count -eq 0) {
    Write-Host ""
    Write-Host "No duplicates found. Nothing to clean up." -ForegroundColor Green
    exit 0
}

# Calculate items to delete
$itemsToDelete = @()
foreach ($group in $duplicateGroups) {
    # Keep the first item (oldest by ID), delete the rest
    $toDelete = $group.Group | Sort-Object Id | Select-Object -Skip 1
    $itemsToDelete += $toDelete
}

Write-Host "  Items to delete: $($itemsToDelete.Count)" -ForegroundColor Yellow
Write-Host ""

# Show sample of what will be deleted
Write-Host "[3/4] Sample of items to delete (first 10):" -ForegroundColor Gray
$sample = $itemsToDelete | Select-Object -First 10
foreach ($item in $sample) {
    $uk = $item.FieldValues.UniqueKey
    $status = $item.FieldValues.QueueStatus
    Write-Host "  ID: $($item.Id) | Status: $status | UniqueKey: $uk" -ForegroundColor Gray
}

if ($itemsToDelete.Count -gt 10) {
    Write-Host "  ... and $($itemsToDelete.Count - 10) more" -ForegroundColor Gray
}
Write-Host ""

# Delete or dry-run
Write-Host "[4/4] $(if ($DryRun) { 'Would delete' } else { 'Deleting' }) $($itemsToDelete.Count) duplicate items..." -ForegroundColor $(if ($DryRun) { "Yellow" } else { "Red" })

$deleted = 0
$errors = 0

if (-not $DryRun) {
    foreach ($item in $itemsToDelete) {
        try {
            Remove-PnPListItem -List $QueueListName -Identity $item.Id -Force
            $deleted++
            if ($deleted % 20 -eq 0) {
                Write-Host "  Deleted $deleted / $($itemsToDelete.Count)..." -ForegroundColor Gray
            }
        }
        catch {
            $errors++
            Write-Host "  ERROR deleting ID $($item.Id): $_" -ForegroundColor Red
        }
    }
}
else {
    $deleted = $itemsToDelete.Count
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN COMPLETE" -ForegroundColor Yellow
    Write-Host "  Would delete: $deleted items" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run without -DryRun to actually delete:" -ForegroundColor Cyan
    Write-Host "  .\scripts\fix_f3_cleanup_duplicates.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host "  Deleted: $deleted items" -ForegroundColor Green
    if ($errors -gt 0) {
        Write-Host "  Errors: $errors" -ForegroundColor Red
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
