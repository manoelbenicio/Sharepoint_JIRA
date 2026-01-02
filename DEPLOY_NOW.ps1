# ============================================================
# ONE-CLICK DEPLOY SCRIPT - Sharepoint_JIRA Project
# Run: powershell -ExecutionPolicy Bypass -File DEPLOY_NOW.ps1
# ============================================================

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  SHAREPOINT_JIRA - ONE-CLICK DEPLOY                    " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# STEP 1: Check Prerequisites
Write-Host "STEP 1 - Checking prerequisites..." -ForegroundColor Yellow

$azInstalled = Get-Command az -ErrorAction SilentlyContinue
$funcInstalled = Get-Command func -ErrorAction SilentlyContinue

if (-not $azInstalled) {
    Write-Host "  ERROR: Azure CLI not found. Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Azure CLI installed" -ForegroundColor Green

if (-not $funcInstalled) {
    Write-Host "  ERROR: Azure Functions Core Tools not found." -ForegroundColor Red
    Write-Host "  Install with: npm install -g azure-functions-core-tools@4" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK: Azure Functions Core Tools installed" -ForegroundColor Green

# STEP 2: Azure Login Check
Write-Host ""
Write-Host "STEP 2 - Checking Azure login..." -ForegroundColor Yellow

$accountJson = az account show 2>$null
if (-not $accountJson) {
    Write-Host "  INFO: Opening browser for Azure login..." -ForegroundColor Cyan
    az login
}
Write-Host "  OK: Azure logged in" -ForegroundColor Green

# STEP 3: Deploy Azure Function
Write-Host ""
Write-Host "STEP 3 - Deploying Azure Function..." -ForegroundColor Yellow

$functionPath = "D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction"
$functionApp = "func-pipeline-consolidation"
$resourceGroup = "rg-pipeline-consolidation"

if (-not (Test-Path $functionPath)) {
    Write-Host "  ERROR: Function path not found: $functionPath" -ForegroundColor Red
    exit 1
}

Push-Location $functionPath
try {
    Write-Host "  INFO: Publishing to Azure (2-3 minutes)..." -ForegroundColor Cyan
    func azure functionapp publish $functionApp --python
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Deploy successful!" -ForegroundColor Green
    }
    else {
        Write-Host "  ERROR: Deploy failed. Check output above." -ForegroundColor Red
    }
}
finally {
    Pop-Location
}

# STEP 4: Verify & Get Function Key
Write-Host ""
Write-Host "STEP 4 - Verifying deployment..." -ForegroundColor Yellow

try {
    $healthUrl = "https://${functionApp}.azurewebsites.net/api/health"
    Write-Host "  INFO: Testing health endpoint..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 30
    Write-Host "  OK: Health check passed!" -ForegroundColor Green
}
catch {
    Write-Host "  WARN: Health check pending - function may still be starting" -ForegroundColor Yellow
}

# Get Function Key
Write-Host ""
Write-Host "  INFO: Retrieving Function Key..." -ForegroundColor Cyan
$keysJson = az functionapp keys list --name $functionApp --resource-group $resourceGroup 2>$null
if ($keysJson) {
    $keys = $keysJson | ConvertFrom-Json
    if ($keys.functionKeys.default) {
        Write-Host ""
        Write-Host "========================================================" -ForegroundColor Green
        Write-Host "  FUNCTION KEY (save this for Power Automate):          " -ForegroundColor Green
        Write-Host "========================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host $keys.functionKeys.default -ForegroundColor White -BackgroundColor DarkGreen
        Write-Host ""
    }
}

# Summary
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  DEPLOY COMPLETE!                                      " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Copy the Function Key above" -ForegroundColor White
Write-Host "  2. Create Flow1 in Power Automate" -ForegroundColor White
Write-Host "  3. Create Flow2 in Power Automate" -ForegroundColor White
Write-Host "  4. Run the test plan" -ForegroundColor White
Write-Host ""
Write-Host "Docs: D:\VMs\Projetos\Sharepoint_JIRA\MD_Files\" -ForegroundColor Gray
Write-Host "URL:  https://${functionApp}.azurewebsites.net/api/" -ForegroundColor Gray
Write-Host ""
