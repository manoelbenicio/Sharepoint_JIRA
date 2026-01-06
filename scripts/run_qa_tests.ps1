# QA Test Runner Script
# Run with Windows PowerShell 5.1:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_qa_tests.ps1

# Import the legacy module (works in PS 5.1)
Import-Module SharePointPnPPowerShellOnline -Force

$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  QA TEST RUNNER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
Write-Host "  URL: $SiteUrl" -ForegroundColor Gray
Write-Host ""

# Connect using UseWebLogin (browser-based)
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

Write-Host "Connected successfully!" -ForegroundColor Green
Write-Host ""

# Run F3 Concurrency Test
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  RUNNING TEST F3: Concurrency" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
& ".\scripts\test_f3_concurrency.ps1"

Write-Host ""

# Run DUP2 Flood Control Test
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  RUNNING TEST DUP2: Flood Control" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
& ".\scripts\test_dup2_flood_control.ps1"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ALL TESTS COMPLETED" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# Disconnect
Disconnect-PnPOnline
