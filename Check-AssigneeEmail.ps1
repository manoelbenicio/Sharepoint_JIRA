# Check-AssigneeEmail.ps1
# Verify if AssigneeEmail field exists and has data in Ofertas_Pipeline

$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"
$ListName = "Ofertas_Pipeline"

Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

Write-Host "`n=== Checking AssigneeEmail Field ===" -ForegroundColor Cyan

# Check if field exists
$field = Get-PnPField -List $ListName -Identity "AssigneeEmail" -ErrorAction SilentlyContinue
if ($field) {
    Write-Host "Field EXISTS:" -ForegroundColor Green
    Write-Host "  Title: $($field.Title)"
    Write-Host "  InternalName: $($field.InternalName)"
    Write-Host "  Id: $($field.Id)"
    Write-Host "  Type: $($field.TypeAsString)"
} else {
    Write-Host "Field AssigneeEmail does NOT exist in the list!" -ForegroundColor Red
    Disconnect-PnPOnline
    exit
}

Write-Host "`n=== Sample Data (first 15 items) ===" -ForegroundColor Cyan

$items = Get-PnPListItem -List $ListName -PageSize 100 | Select-Object -First 15

$hasData = 0
$noData = 0

foreach($item in $items) {
    $id = $item.Id
    $assigneeEmail = $item["AssigneeEmail"]
    $assignee = $item["Assignee"]
    
    if ($assigneeEmail -and $assigneeEmail -ne "") {
        $hasData++
        Write-Host "ID: $id | AssigneeEmail: $assigneeEmail" -ForegroundColor Green
    } else {
        $noData++
        Write-Host "ID: $id | AssigneeEmail: (empty) | Assignee: $assignee" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Items with AssigneeEmail: $hasData" -ForegroundColor Green
Write-Host "Items without AssigneeEmail: $noData" -ForegroundColor Yellow

Disconnect-PnPOnline
Write-Host "`nDone." -ForegroundColor Gray
