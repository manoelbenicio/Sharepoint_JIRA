<#
.SYNOPSIS
  PRE-QA reset: purge SharePoint lists via Azure Function admin endpoint, then upload a JIRA CSV to trigger Flow4.

.IMPORTANT
  PowerShell CLI tasks are Opus-only by project rule. Do not run unless you are Agent Opus 4.5 (or explicitly authorized).

.REQUIRES
  PnP.PowerShell

.EXAMPLE
  pwsh ops/scripts/powershell/preqa-reset-and-import.ps1 `
    -SiteUrl "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" `
    -CsvPath "HANDOFF_FIX_QA/JIRA PBI (JIRA Indra) 2025-12-30T03_17_34-0300.csv" `
    -LibraryRelativeUrl "Documentos compartilhados" `
    -FolderRelativeUrl "Documentos compartilhados/JIRA_Imports" `
    -FunctionBaseUrl "https://func-pipeline-consolidation.azurewebsites.net" `
    -FunctionKey "<FUNCTION_KEY>" `
    -AdminToken "<LAB_PURGE_ADMIN_TOKEN>" `
    -Confirmation "<LAB_PURGE_CONFIRMATION>" `
    -ListsToPurge @("Ofertas_Pipeline","StatusReports_Historico","Atualizacoes_Semanais") `
    -MaxItemsPerList 500 `
    -DryRun $true
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [Parameter(Mandatory = $true)]
  [string]$SiteUrl,

  [Parameter(Mandatory = $true)]
  [string]$CsvPath,

  # SharePoint upload target for Flow4 trigger
  [Parameter(Mandatory = $true)]
  [string]$FolderRelativeUrl,

  # Azure Function purge endpoint
  [Parameter(Mandatory = $true)]
  [string]$FunctionBaseUrl,

  [Parameter(Mandatory = $true)]
  [string]$FunctionKey,

  [Parameter(Mandatory = $true)]
  [string]$AdminToken,

  [Parameter(Mandatory = $true)]
  [string]$Confirmation,

  [Parameter(Mandatory = $true)]
  [string[]]$ListsToPurge,

  [Parameter(Mandatory = $false)]
  [int]$MaxItemsPerList = 500,

  [Parameter(Mandatory = $false)]
  [bool]$DryRun = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-PnP {
  if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    throw "PnP.PowerShell is not installed. Install-Module PnP.PowerShell -Scope CurrentUser"
  }
}

Ensure-PnP

if (-not (Test-Path -LiteralPath $CsvPath)) {
  throw "CSV not found: $CsvPath"
}

Write-Host "=== PRE-QA RESET ==="
Write-Host "DryRun: $DryRun"
Write-Host "SiteUrl: $SiteUrl"
Write-Host "FolderRelativeUrl: $FolderRelativeUrl"
Write-Host "ListsToPurge: $($ListsToPurge -join ', ')"

#
# Step 1: Purge lists (Azure Function)
#
$purgeUrl = ($FunctionBaseUrl.TrimEnd('/') + "/api/lab/purge-lists?code=" + [Uri]::EscapeDataString($FunctionKey))
$body = @{
  confirm            = $Confirmation
  dry_run            = $DryRun
  lists              = $ListsToPurge
  max_items_per_list = $MaxItemsPerList
} | ConvertTo-Json -Depth 6

Write-Host ""
Write-Host "Calling purge endpoint: $purgeUrl"
if ($PSCmdlet.ShouldProcess("AzureFunction", "Purge lists (dry_run=$DryRun)")) {
  $resp = Invoke-RestMethod -Method Post -Uri $purgeUrl -Headers @{ "x-admin-token" = $AdminToken } -Body $body -ContentType "application/json"
  $resp | ConvertTo-Json -Depth 10
}

if ($DryRun) {
  Write-Host ""
  Write-Host "DryRun=true: purge was not executed. Review output, then rerun with -DryRun $false."
}

#
# Step 2: Upload CSV to trigger Flow4
#
Write-Host ""
Write-Host "Connecting to SharePoint (interactive): $SiteUrl"
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

$csvFileName = Split-Path -Leaf $CsvPath
Write-Host "Uploading CSV to: $FolderRelativeUrl/$csvFileName"

if ($PSCmdlet.ShouldProcess("SharePoint", "Upload CSV to trigger Flow4")) {
  Add-PnPFile -Path $CsvPath -Folder $FolderRelativeUrl -NewFileName $csvFileName | Out-Null
  Write-Host "Upload done."
}

Write-Host ""
Write-Host "NEXT: wait a few minutes for Flow4 to run, then validate Level 1 in SharePoint lists."

