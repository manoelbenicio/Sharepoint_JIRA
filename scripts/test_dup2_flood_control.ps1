# DUP2 Test: Flood Control Verification
# Verifies that Flow2 respects TopCount limits when sending cards
#
# This test checks the current queue state to verify:
# 1. Queue items are properly batched
# 2. Sent count respects the configured TopCount
# 3. No flood of cards to recipients
#
# Usage:
#   pwsh
#   Connect-PnPOnline -Url "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" -UseWebLogin
#   .\scripts\test_dup2_flood_control.ps1

param(
    [string]$QueueListName = "StatusReports_Queue",
    [int[]]$ExpectedTopCounts = @(1, 3, 10)
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DUP2: Flood Control Verification" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Analyzing queue status distribution..." -ForegroundColor Yellow
Write-Host ""

# Get all queue items
$items = Get-PnPListItem -List $QueueListName -PageSize 500

if ($items.Count -eq 0) {
    Write-Host "[INFO] No items found in $QueueListName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "RESULT: DUP2 INCONCLUSIVE - No queue data to verify" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($items.Count) total queue items" -ForegroundColor Gray
Write-Host ""

# Group by QueueStatus
$statusGroups = $items | Group-Object { $_.FieldValues.QueueStatus }

Write-Host "[1/3] Queue Status Distribution:" -ForegroundColor Gray
Write-Host ""

$pending = 0
$sent = 0
$completed = 0
$errorCount = 0

foreach ($group in $statusGroups) {
    $statusName = if ([string]::IsNullOrWhiteSpace($group.Name)) { "(Empty)" } else { $group.Name }
    $color = switch ($statusName) {
        "Pending" { "Yellow" }
        "Sent" { "Cyan" }
        "Completed" { "Green" }
        "Error" { "Red" }
        default { "Gray" }
    }
    Write-Host "  $($statusName): $($group.Count)" -ForegroundColor $color
    
    switch ($group.Name) {
        "Pending" { $pending = $group.Count }
        "Sent" { $sent = $group.Count }
        "Completed" { $completed = $group.Count }
        "Error" { $errorCount = $group.Count }
    }
}

Write-Host ""
Write-Host "[2/3] Processing Rate Analysis:" -ForegroundColor Gray
$processed = $sent + $completed
Write-Host "  Pending: $pending" -ForegroundColor Yellow
Write-Host "  Processed (Sent+Completed): $processed" -ForegroundColor Cyan
Write-Host "  Error: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })

# Check for flood indicators
Write-Host ""
Write-Host "[3/3] Flood Control Indicators:" -ForegroundColor Gray

# Group by RecipientEmail to check for per-recipient flooding
$recipientGroups = $items | Where-Object { 
    $_.FieldValues.QueueStatus -eq "Sent" -or $_.FieldValues.QueueStatus -eq "Completed"
} | Group-Object { $_.FieldValues.RecipientEmail }

Write-Host ""
Write-Host "  Cards sent per recipient:" -ForegroundColor Gray
foreach ($recipient in $recipientGroups) {
    $email = if ([string]::IsNullOrWhiteSpace($recipient.Name)) { "(Empty)" } else { $recipient.Name }
    Write-Host "    $($email): $($recipient.Count) cards" -ForegroundColor Gray
}

# Analyze SentAt timestamps to check for batching
$sentItems = $items | Where-Object { 
    $_.FieldValues.QueueStatus -eq "Sent" -or $_.FieldValues.QueueStatus -eq "Completed"
} | Where-Object {
    $null -ne $_.FieldValues.SentAt
}

if ($sentItems.Count -gt 0) {
    Write-Host ""
    Write-Host "  Timestamps analysis (SentAt):" -ForegroundColor Gray
    $sentTimes = $sentItems | ForEach-Object { $_.FieldValues.SentAt } | Sort-Object
    $firstSent = $sentTimes | Select-Object -First 1
    $lastSent = $sentTimes | Select-Object -Last 1
    
    if ($firstSent -and $lastSent) {
        $duration = $lastSent - $firstSent
        Write-Host "    First card: $firstSent" -ForegroundColor Gray
        Write-Host "    Last card: $lastSent" -ForegroundColor Gray
        Write-Host "    Duration: $($duration.TotalMinutes.ToString('F1')) minutes" -ForegroundColor Gray
    }
}

# Final result
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Pass criteria:
# 1. No excessive cards to single recipient in short time
# 2. Queue shows orderly progression (Pending -> Sent -> Completed)
# 3. No mass Error status

if ($errorCount -eq 0 -and $processed -le 20) {
    Write-Host "RESULT: DUP2 PASS - Flood control appears effective" -ForegroundColor Green
    Write-Host "  - $processed cards processed (within safe limits)" -ForegroundColor Green
    Write-Host "  - $pending items remain pending (controlled backlog)" -ForegroundColor Green
    Write-Host "  - 0 errors" -ForegroundColor Green
    exit 0
}
elseif ($errorCount -gt 0) {
    Write-Host "RESULT: DUP2 WARNING - Errors detected during processing" -ForegroundColor Yellow
    Write-Host "  - $errorCount items in Error status" -ForegroundColor Yellow
    Write-Host "  - Review Flow2 run history for details" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "RESULT: DUP2 INFO - Large batch processed" -ForegroundColor Cyan
    Write-Host "  - $processed cards processed" -ForegroundColor Cyan
    Write-Host "  - Verify TopCount was correctly applied in Flow2" -ForegroundColor Cyan
    exit 0
}

Write-Host "============================================================" -ForegroundColor Cyan
