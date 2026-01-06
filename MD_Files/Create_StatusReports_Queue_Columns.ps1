# Create-StatusReports_Queue_Columns.ps1
# Creates all required columns for StatusReports_Queue list
# Compatible with SharePointPnPPowerShellOnline v3.29

param(
    [string]$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA",
    [string]$ListName = "StatusReports_Queue"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  StatusReports_Queue Setup Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Connect to SharePoint (will open browser for auth)
Write-Host "Connecting to SharePoint..." -ForegroundColor Yellow
Write-Host "Site: $SiteUrl" -ForegroundColor Gray
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

Write-Host "Connected successfully!" -ForegroundColor Green
Write-Host ""

# Check if list exists, if not create it
$list = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
if (-not $list) {
    Write-Host "Creating list: $ListName..." -ForegroundColor Yellow
    New-PnPList -Title $ListName -Template GenericList
    Write-Host "List created!" -ForegroundColor Green
}
else {
    Write-Host "List already exists: $ListName" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Creating columns..." -ForegroundColor Cyan
Write-Host ""

# Helper function to add field safely
function Add-FieldSafe {
    param($DisplayName, $InternalName, $Type, $Choices, $DefaultValue, $Indexed, $EnforceUnique)
    
    $existing = Get-PnPField -List $ListName -Identity $InternalName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  [SKIP] $DisplayName already exists" -ForegroundColor Gray
        return
    }
    
    try {
        switch ($Type) {
            "Choice" {
                $choiceXml = "<Field Type='Choice' DisplayName='$DisplayName' Name='$InternalName' Format='Dropdown'>"
                $choiceXml += "<Default>$DefaultValue</Default><CHOICES>"
                foreach ($c in $Choices) {
                    $choiceXml += "<CHOICE>$c</CHOICE>"
                }
                $choiceXml += "</CHOICES></Field>"
                Add-PnPFieldFromXml -List $ListName -FieldXml $choiceXml
            }
            "Text" {
                Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Text -AddToDefaultView
            }
            "Number" {
                Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Number -AddToDefaultView
            }
            "Note" {
                Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Note
            }
            "DateTime" {
                Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type DateTime -AddToDefaultView
            }
        }
        
        # Set indexed and unique if needed
        if ($Indexed -or $EnforceUnique) {
            $field = Get-PnPField -List $ListName -Identity $InternalName
            if ($Indexed) {
                $field.Indexed = $true
            }
            if ($EnforceUnique) {
                $field.EnforceUniqueValues = $true
                $field.Indexed = $true  # Required for unique
            }
            $field.Update()
            $field.Context.ExecuteQuery()
        }
        
        Write-Host "  [OK] $DisplayName" -ForegroundColor Green
    }
    catch {
        Write-Host "  [ERROR] $DisplayName - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create all columns
Add-FieldSafe -DisplayName "QueueStatus" -InternalName "QueueStatus" -Type "Choice" -Choices @("Pending", "Sent", "Completed", "Error") -DefaultValue "Pending" -Indexed $true
Add-FieldSafe -DisplayName "RecipientEmail" -InternalName "RecipientEmail" -Type "Text" -Indexed $true
Add-FieldSafe -DisplayName "JiraKey" -InternalName "JiraKey" -Type "Text" -Indexed $true
Add-FieldSafe -DisplayName "OfertaId" -InternalName "OfertaId" -Type "Number"
Add-FieldSafe -DisplayName "Semana" -InternalName "Semana" -Type "Text" -Indexed $true
Add-FieldSafe -DisplayName "VersaoReport" -InternalName "VersaoReport" -Type "Number"
Add-FieldSafe -DisplayName "UniqueKey" -InternalName "UniqueKey" -Type "Text" -Indexed $true -EnforceUnique $true
Add-FieldSafe -DisplayName "ResponseJson" -InternalName "ResponseJson" -Type "Note"
Add-FieldSafe -DisplayName "SentAt" -InternalName "SentAt" -Type "DateTime"
Add-FieldSafe -DisplayName "CompletedAt" -InternalName "CompletedAt" -Type "DateTime"
Add-FieldSafe -DisplayName "AttemptCount" -InternalName "AttemptCount" -Type "Number"
Add-FieldSafe -DisplayName "LastError" -InternalName "LastError" -Type "Note"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Verify UniqueKey has 'Enforce unique values' = Yes" -ForegroundColor Yellow
Write-Host "Check at: $SiteUrl/Lists/$ListName/AllItems.aspx" -ForegroundColor Gray
Write-Host ""

Disconnect-PnPOnline
