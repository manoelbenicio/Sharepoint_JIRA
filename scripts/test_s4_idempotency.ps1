# S4 Test: Retry Behavior (Idempotency)
# Verifies no duplicate rows in StatusReports_Historico
# 
# Usage:
#   Connect-PnPOnline -Url "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" -UseWebLogin
#   .\scripts\test_s4_idempotency.ps1

param(
    [string]$ListName = "StatusReports_Historico"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST S4: Retry behavior (idempotency)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking for duplicate rows in $ListName..." -ForegroundColor Yellow
Write-Host ""

# Get all items from StatusReports_Historico
$items = Get-PnPListItem -List $ListName -PageSize 500

if ($items.Count -eq 0) {
    Write-Host "[INFO] No items found in $ListName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "RESULT: S4 PASS - No data to check (0 items)" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($items.Count) items in $ListName" -ForegroundColor Gray
Write-Host ""

# Group by JiraKey + Semana + OfertaId + VersaoNumero
$groups = $items | Group-Object { 
    "$($_.FieldValues.Title)|$($_.FieldValues.Semana)|$($_.FieldValues.OfertaId)|$($_.FieldValues.VersaoNumero)" 
}

# Find duplicates (count > 1)
$duplicates = $groups | Where-Object { $_.Count -gt 1 }

if ($duplicates.Count -eq 0) {
    Write-Host "[OK] No duplicate combinations found" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "RESULT: S4 PASS - No duplicate history rows" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 0
}
else {
    Write-Host "[FAIL] Found $($duplicates.Count) duplicate combinations:" -ForegroundColor Red
    Write-Host ""
    
    foreach ($dup in $duplicates) {
        $parts = $dup.Name -split '\|'
        Write-Host "  JiraKey: $($parts[0])" -ForegroundColor Yellow
        Write-Host "  Semana: $($parts[1])" -ForegroundColor Yellow  
        Write-Host "  OfertaId: $($parts[2])" -ForegroundColor Yellow
        Write-Host "  VersaoNumero: $($parts[3])" -ForegroundColor Yellow
        Write-Host "  Count: $($dup.Count)" -ForegroundColor Red
        Write-Host "  IDs: $($dup.Group | ForEach-Object { $_.Id } | Join-String -Separator ', ')" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "RESULT: S4 FAIL - Duplicate history rows detected" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Cyan
    exit 1
}
