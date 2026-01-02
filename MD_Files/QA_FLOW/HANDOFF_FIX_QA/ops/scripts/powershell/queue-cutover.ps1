<#
.SYNOPSIS
  Blue/green cutover for queue list: create new list, migrate items, keep old list intact.

.IMPORTANT
  PowerShell CLI tasks are Opus-only by project rule.

.REQUIRES
  PnP.PowerShell

.NOTES
  This script handles SharePoint-side operations only. Flow cutover (Flow1/Flow2 pointing to new list)
  must be performed in Power Automate (or via your Power Platform automation tooling).

.EXAMPLE
  pwsh ops/scripts/powershell/queue-cutover.ps1 -SiteUrl "https://.../sites/..." -OldList "StatusReports_Queue_TEST" -NewList "StatusReports_Queue"
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [Parameter(Mandatory = $true)]
  [string]$SiteUrl,

  [Parameter(Mandatory = $true)]
  [string]$OldList,

  [Parameter(Mandatory = $true)]
  [string]$NewList,

  [Parameter(Mandatory = $false)]
  [string]$ReportDir = "tools/reports",

  [Parameter(Mandatory = $false)]
  [int]$PageSize = 500
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-PnP {
  if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    throw "PnP.PowerShell is not installed. Install-Module PnP.PowerShell -Scope CurrentUser"
  }
}

Ensure-PnP
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$schemaPath = Join-Path $ReportDir "queue_schema_backup_$ts.xml"
$itemsPath = Join-Path $ReportDir "queue_items_backup_$ts.csv"
$migratePath = Join-Path $ReportDir "queue_migration_report_$ts.csv"

Write-Host "Backing up schema for: $OldList"
$schemaFields = Get-PnPField -List $OldList | Select-Object InternalName, Title, TypeAsString, Required, SchemaXml
$schemaFields | ConvertTo-Json -Depth 4 | Out-File $schemaPath -Encoding UTF8
Write-Host "Wrote schema backup: $schemaPath"

Write-Host "Backing up items for: $OldList"
$oldItems = Get-PnPListItem -List $OldList -PageSize 5000 -Fields "*" 
$oldItems | ForEach-Object { $_.FieldValues } | ConvertTo-Json -Depth 6 | Out-File (Join-Path $ReportDir "queue_items_backup_$ts.json") -Encoding UTF8

# Create new list (minimal): use provisioning template extraction as a base is safer but requires editing template.
# Here we create a generic list and copy fields, keeping rollback simple (old list untouched).
if ($null -eq (Get-PnPList -Identity $NewList -ErrorAction SilentlyContinue)) {
  if (-not $WhatIfPreference) {
    Write-Host "Creating new list: $NewList"
    New-PnPList -Title $NewList -Template GenericList | Out-Null
  }
  else {
    Write-Host "WhatIf: Would create new list: $NewList"
  }
}
else {
  Write-Host "New list already exists: $NewList"
}

Write-Host "Copying fields from $OldList -> $NewList (best-effort)."
$oldFields = Get-PnPField -List $OldList | Where-Object { -not $_.Hidden -and -not $_.ReadOnlyField }
$newFieldNames = (Get-PnPField -List $NewList | Select-Object -ExpandProperty InternalName)

foreach ($f in $oldFields) {
  if ($newFieldNames -contains $f.InternalName) { continue }
  if (-not $WhatIfPreference) {
    try {
      Add-PnPFieldFromXml -List $NewList -FieldXml $f.SchemaXml | Out-Null
    }
    catch {
      Write-Warning "Failed to add field $($f.InternalName): $($_.Exception.Message)"
    }
  }
  else {
    Write-Host "WhatIf: Would add field $($f.InternalName) to $NewList"
  }
}

Write-Host "Migrating items (old list remains intact)."
$migrated = @()

foreach ($it in $oldItems) {
  $v = $it.FieldValues
  # Whitelist approach: only copy known business fields
  $businessFields = @("Title", "JiraKey", "Semana", "RecipientEmail", "UniqueKey", "QueueStatus", "AttemptCount", "SentAt", "CompletedAt", "OfertaId", "OfertaTitulo", "NomeGestor", "AssigneeEmail", "ManagerEmail", "ReportVersion", "ErrorMessage", "LastAttemptAt")
  $values = @{}
  foreach ($field in $businessFields) {
    if ($v.Keys -contains $field -and $null -ne $v[$field]) {
      $values[$field] = $v[$field]
    }
  }
  if (-not $WhatIfPreference) {
    try {
      $newItem = Add-PnPListItem -List $NewList -Values $values
      $migratedItem = New-Object PSObject -Property @{
        OldID          = $v.ID
        NewID          = $newItem.Id
        JiraKey        = $v["JiraKey"]
        Semana         = $v["Semana"]
        RecipientEmail = $v["RecipientEmail"]
        UniqueKey      = $v["UniqueKey"]
      }
      $migrated += $migratedItem
    }
    catch {
      Write-Warning "Failed to migrate item ID $($v.ID): $($_.Exception.Message)"
    }
  }
  else {
    Write-Host "WhatIf: Would migrate item ID $($v.ID)"
  }
}

$migrated | Export-Csv -NoTypeInformation -Path $migratePath
Write-Host "Wrote migration report: $migratePath"

Write-Host ""
Write-Host "NEXT STEP (outside this script): update Flow1/Flow2 to point to '$NewList' and run canary with recipient allowlist mbenicios@minsait.com."
Write-Host "Rollback remains immediate because '$OldList' was not modified."
