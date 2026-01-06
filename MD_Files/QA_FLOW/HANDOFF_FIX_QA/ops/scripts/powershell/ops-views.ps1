<#
.SYNOPSIS
  Creates standard "Ops - Level 1" SharePoint views for queue/history lists.

.IMPORTANT
  PowerShell CLI tasks are Opus-only by project rule.
  Do not run this script unless you are Agent Opus 4.5 (or explicitly authorized by the user).

.REQUIRES
  PnP.PowerShell

.EXAMPLE
  pwsh ops/scripts/powershell/ops-views.ps1 -SiteUrl "https://.../sites/..." -QueueList "StatusReports_Queue" -HistoricoList "StatusReports_Historico"
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$SiteUrl,

  [Parameter(Mandatory = $true)]
  [string]$QueueList,

  [Parameter(Mandatory = $true)]
  [string]$HistoricoList
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-PnP {
  if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    throw "PnP.PowerShell is not installed. Install-Module PnP.PowerShell -Scope CurrentUser"
  }
}

function Ensure-View {
  param(
    [Parameter(Mandatory = $true)][string]$List,
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string[]]$Fields,
    [Parameter(Mandatory = $false)][string]$Query
  )

  $existing = Get-PnPView -List $List -ErrorAction SilentlyContinue | Where-Object { $_.Title -eq $Title }
  if ($null -eq $existing) {
    Write-Host "Creating view: $List :: $Title"
    Add-PnPView -List $List -Title $Title -Fields $Fields -Query $Query | Out-Null
    return
  }

  Write-Host "Updating view fields/query: $List :: $Title"
  Set-PnPView -List $List -Identity $existing.Id -Fields $Fields -Query $Query | Out-Null
}

Ensure-PnP
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

$queueFields = @(
  "ID",
  "Created",
  "Modified",
  "Title",
  "QueueStatus",
  "RecipientEmail",
  "JiraKey",
  "OfertaId",
  "Semana",
  "VersaoReport",
  "UniqueKey",
  "SentAt",
  "CompletedAt",
  "AttemptCount"
)

$histFields = @(
  "ID",
  "Created",
  "Title",
  "OfertaId",
  "Semana",
  "VersaoNumero",
  "ArquitetoEmail",
  "StatusProjeto",
  "StatusAtual",
  "Observacoes",
  "RespostaJSON"
)

Ensure-View -List $QueueList -Title "Ops - Queue (All)" -Fields $queueFields -Query ""
Ensure-View -List $QueueList -Title "Ops - Queue (Pending)" -Fields $queueFields -Query "<Where><Eq><FieldRef Name='QueueStatus'/><Value Type='Choice'>Pending</Value></Eq></Where>"
Ensure-View -List $QueueList -Title "Ops - Queue (Sent)" -Fields $queueFields -Query "<Where><Eq><FieldRef Name='QueueStatus'/><Value Type='Choice'>Sent</Value></Eq></Where>"
Ensure-View -List $QueueList -Title "Ops - Queue (Errors)" -Fields $queueFields -Query "<Where><Eq><FieldRef Name='QueueStatus'/><Value Type='Choice'>Error</Value></Eq></Where>"

# "Duplicates" view: this is a UI helper; real duplicate detection should be done via script/reporting (TD-006).
Ensure-View -List $QueueList -Title "Ops - Queue (Duplicates)" -Fields $queueFields -Query ""

Ensure-View -List $HistoricoList -Title "Ops - Historico (All)" -Fields $histFields -Query ""
Ensure-View -List $HistoricoList -Title "Ops - Historico (Last 24h)" -Fields $histFields -Query "<Where><Geq><FieldRef Name='Created'/><Value Type='DateTime'><Today OffsetDays='-1'/></Value></Geq></Where>"

Write-Host "Done."

