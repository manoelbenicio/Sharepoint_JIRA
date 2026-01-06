<#
.SYNOPSIS
  Scans and optionally cleans duplicates in the queue list based on UniqueKey strategy.

.IMPORTANT
  PowerShell CLI tasks are Opus-only by project rule.

.REQUIRES
  PnP.PowerShell

.EXAMPLE
  pwsh ops/scripts/powershell/queue-dedupe.ps1 -SiteUrl "https://.../sites/..." -QueueList "StatusReports_Queue" -Mode Scan

.EXAMPLE
  pwsh ops/scripts/powershell/queue-dedupe.ps1 -SiteUrl "https://.../sites/..." -QueueList "StatusReports_Queue" -Mode Cleanup -KeepPolicy OldestCreated -Confirm:$true
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [Parameter(Mandatory = $true)]
  [string]$SiteUrl,

  [Parameter(Mandatory = $true)]
  [string]$QueueList,

  [Parameter(Mandatory = $true)]
  [ValidateSet("Scan", "Cleanup")]
  [string]$Mode,

  [Parameter(Mandatory = $false)]
  [ValidateSet("OldestCreated", "NewestModified")]
  [string]$KeepPolicy = "OldestCreated",

  [Parameter(Mandatory = $false)]
  [string]$ReportDir = "tools/reports"
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
$scanPath = Join-Path $ReportDir "queue_dedupe_scan_$ts.csv"
$cleanupPath = Join-Path $ReportDir "queue_dedupe_cleanup_$ts.csv"

Write-Host "Reading queue items from: $QueueList"
$items = Get-PnPListItem -List $QueueList -PageSize 5000 -Fields "ID", "Created", "Modified", "UniqueKey", "OfertaId", "Semana", "RecipientEmail", "JiraKey", "QueueStatus"

$rows = @()
foreach ($it in $items) {
  $f = $it.FieldValues
  $obj = New-Object PSObject -Property @{
    ID             = $f.ID
    Created        = $f.Created
    Modified       = $f.Modified
    UniqueKey      = $f.UniqueKey
    OfertaId       = $f.OfertaId
    Semana         = $f.Semana
    RecipientEmail = $f.RecipientEmail
    JiraKey        = $f.JiraKey
    QueueStatus    = $f.QueueStatus
  }
  $rows += $obj
}

$dupesByUniqueKey = $rows | Group-Object -Property UniqueKey | Where-Object { $_.Count -gt 1 -and ($_.Name -ne $null) -and ($_.Name -ne "") }

$scanReport = @()
foreach ($g in $dupesByUniqueKey) {
  foreach ($r in $g.Group) {
    $scanReport += New-Object PSObject -Property @{
      GroupKey       = $g.Name
      GroupCount     = $g.Count
      ID             = $r.ID
      Created        = $r.Created
      Modified       = $r.Modified
      OfertaId       = $r.OfertaId
      Semana         = $r.Semana
      RecipientEmail = $r.RecipientEmail
      JiraKey        = $r.JiraKey
      QueueStatus    = $r.QueueStatus
    }
  }
}

$scanReport | Export-Csv -NoTypeInformation -Path $scanPath
Write-Host "Wrote scan report: $scanPath"
Write-Host ("Duplicate groups (UniqueKey): {0}" -f ($dupesByUniqueKey | Measure-Object).Count)

if ($Mode -eq "Scan") {
  exit 0
}

if (($dupesByUniqueKey | Measure-Object).Count -eq 0) {
  Write-Host "No duplicates found. Nothing to clean."
  exit 0
}

Write-Host "Cleanup mode requested. KeepPolicy: $KeepPolicy"

$cleanupActions = @()
foreach ($g in $dupesByUniqueKey) {
  $sorted = @()
  if ($KeepPolicy -eq "OldestCreated") {
    $sorted = @($g.Group | Sort-Object -Property Created, ID)
  }
  else {
    $sorted = @($g.Group | Sort-Object -Property Modified, ID -Descending)
  }

  $keep = $sorted | Select-Object -First 1
  $remove = $sorted | Select-Object -Skip 1

  foreach ($r in $remove) {
    $cleanupActions += New-Object PSObject -Property @{
      UniqueKey  = $g.Name
      KeptID     = $keep.ID
      RemovedID  = $r.ID
      KeepPolicy = $KeepPolicy
    }
  }
}

$cleanupActions | Export-Csv -NoTypeInformation -Path $cleanupPath
Write-Host "Wrote cleanup plan: $cleanupPath"

$removedCount = 0
foreach ($a in $cleanupActions) {
  Write-Host ("Removing duplicate: ID {0} (keeping ID {1})" -f $a.RemovedID, $a.KeptID)
  if (-not $WhatIfPreference) {
    Remove-PnPListItem -List $QueueList -Identity $a.RemovedID -Force
    $removedCount++
  }
}
Write-Host ("Removed {0} duplicate items." -f $removedCount)

Write-Host "Cleanup complete."

