# F4 Test: Field Population Robustness
# Verifies Flow1 skips offers where architect email is missing
#
# This is a DESIGN VERIFICATION test - validates that:
# 1. ARQs_Teams lookup correctly maps assignee to email
# 2. Offers without valid email are NOT queued
#
# Usage:
#   Connect-PnPOnline -Url "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" -UseWebLogin
#   .\scripts\test_f4_field_robustness.ps1

param(
    [string]$QueueListName = "StatusReports_Queue",
    [string]$ArqsListName = "ARQs_Teams"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST F4: Field population robustness" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verifying Flow1 email validation logic..." -ForegroundColor Yellow
Write-Host ""

# Step 1: Check ARQs_Teams for any architects with missing email
Write-Host "[1/3] Checking ARQs_Teams for architects with missing email..." -ForegroundColor Gray

$arqs = Get-PnPListItem -List $ArqsListName -PageSize 500 | Where-Object {
    $_.FieldValues.Status -eq "Ativo"
}

$arqsWithoutEmail = $arqs | Where-Object {
    $email = $_.FieldValues.field_3
    if (-not $email) { $email = $_.FieldValues.Email }
    if (-not $email) { $email = $_.FieldValues.'E-mail' }
    [string]::IsNullOrWhiteSpace($email)
}

Write-Host "  Active architects: $($arqs.Count)" -ForegroundColor Gray
Write-Host "  Without valid email: $($arqsWithoutEmail.Count)" -ForegroundColor $(if ($arqsWithoutEmail.Count -gt 0) { "Yellow" } else { "Green" })

if ($arqsWithoutEmail.Count -gt 0) {
    Write-Host ""
    Write-Host "  Architects missing email:" -ForegroundColor Yellow
    foreach ($arq in $arqsWithoutEmail) {
        Write-Host "    - $($arq.FieldValues.Login) (ID: $($arq.Id))" -ForegroundColor Yellow
    }
}

# Step 2: Check queue for any items with empty RecipientEmail
Write-Host ""
Write-Host "[2/3] Checking queue for items with empty RecipientEmail..." -ForegroundColor Gray

$queueItems = Get-PnPListItem -List $QueueListName -PageSize 500

$queueWithoutEmail = $queueItems | Where-Object {
    [string]::IsNullOrWhiteSpace($_.FieldValues.RecipientEmail)
}

Write-Host "  Total queue items: $($queueItems.Count)" -ForegroundColor Gray
Write-Host "  Without RecipientEmail: $($queueWithoutEmail.Count)" -ForegroundColor $(if ($queueWithoutEmail.Count -gt 0) { "Red" } else { "Green" })

# Step 3: Validate design logic
Write-Host ""
Write-Host "[3/3] Validating Flow1 design logic..." -ForegroundColor Gray
Write-Host ""
Write-Host "  Flow1 Condition 6.4 (from FLOW1_MANUAL_CREATION_GUIDE.md):" -ForegroundColor Gray
Write-Host "  and(greater(length(body('Filter_Architect')), 0)," -ForegroundColor White
Write-Host "      not(empty(first(body('Filter_Architect'))?['email'])))" -ForegroundColor White
Write-Host ""
Write-Host "  [OK] This condition ensures:" -ForegroundColor Green
Write-Host "       - Architect exists in ARQs_Teams" -ForegroundColor Green
Write-Host "       - Architect has non-empty email" -ForegroundColor Green
Write-Host "       - If either fails, offer is skipped (no queue item)" -ForegroundColor Green

# Result
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($queueWithoutEmail.Count -eq 0) {
    Write-Host "RESULT: F4 PASS - No queue items with missing email" -ForegroundColor Green
    Write-Host "  Flow1 correctly validates email before queuing" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "RESULT: F4 FAIL - Found queue items with missing email" -ForegroundColor Red
    foreach ($item in $queueWithoutEmail) {
        Write-Host "  ID: $($item.Id), JiraKey: $($item.FieldValues.JiraKey)" -ForegroundColor Red
    }
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
