<#
.SYNOPSIS
  Rollback helper for queue list cutover (SharePoint-side only).

.IMPORTANT
  PowerShell CLI tasks are Opus-only by project rule.

.REQUIRES
  PnP.PowerShell

.NOTES
  The primary rollback for TD-008 is disabling the new Flow1/Flow2 versions and enabling the previous ones that still
  point to StatusReports_Queue_TEST. This script does not toggle flows; it keeps SharePoint-side rollback safe and auditable.

.EXAMPLE
  pwsh ops/scripts/powershell/queue-rollback.ps1 -SiteUrl "https://.../sites/..." -OldList "StatusReports_Queue_TEST" -NewList "StatusReports_Queue"
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [Parameter(Mandatory = $true)]
  [string]$SiteUrl,

  [Parameter(Mandatory = $true)]
  [string]$OldList,

  [Parameter(Mandatory = $true)]
  [string]$NewList
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

Write-Host "Rollback guidance (SharePoint-side):"
Write-Host "- Do NOT delete '$NewList' during rollback. Keep for postmortem."
Write-Host "- Confirm '$OldList' still exists and is intact."

$old = Get-PnPList -Identity $OldList -ErrorAction SilentlyContinue
if ($null -eq $old) { throw "Old list not found: $OldList" }
$new = Get-PnPList -Identity $NewList -ErrorAction SilentlyContinue
if ($null -eq $new) { Write-Warning "New list not found (nothing to rollback SharePoint-side): $NewList" }

Write-Host ""
Write-Host "NEXT STEP (Power Automate):"
Write-Host "1) Disable the new Flow1/Flow2 versions that point to '$NewList'."
Write-Host "2) Enable the previous Flow1/Flow2 versions that point to '$OldList'."
Write-Host "3) Confirm Flow2 flood control still restricts recipient to mbenicios@minsait.com before any runs."

