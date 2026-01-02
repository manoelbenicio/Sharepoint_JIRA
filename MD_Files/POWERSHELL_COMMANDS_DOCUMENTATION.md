# 📋 PowerShell Commands & Connections Documentation

> **Project:** JIRA → SharePoint → Teams/Power BI Integration  
> **Last Updated:** 2025-12-30  
> **Purpose:** Complete reference of all PowerShell commands, connections, and configurations used in this project

---

## 📑 Table of Contents

1. [Environment Overview](#1-environment-overview)
2. [PowerShell Version & Modules](#2-powershell-version--modules)
3. [Connection Details](#3-connection-details)
4. [SharePoint Lists & GUIDs](#4-sharepoint-lists--guids)
5. [PowerShell Scripts Reference](#5-powershell-scripts-reference)
6. [Azure CLI Commands](#6-azure-cli-commands)
7. [PnP PowerShell Commands](#7-pnp-powershell-commands)
8. [Credential & Authentication Reference](#8-credential--authentication-reference)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Environment Overview

### Target Tenant & Site

| Property | Value |
|----------|-------|
| **Tenant** | `indra365.sharepoint.com` |
| **Site URL** | `https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA` |
| **Environment** | SharePoint Online (Microsoft 365) |
| **Azure Subscription** | (Azure Function hosting) |
| **Resource Group** | `rg-pipeline-consolidation` |
| **Function App** | `func-pipeline-consolidation` |

### Azure Function Details

| Property | Value |
|----------|-------|
| **URL Base** | `https://func-pipeline-consolidation.azurewebsites.net/api/` |
| **Runtime** | Python 3.11 |
| **Function Key** | REDACTED_FUNCTION_KEY |
| **Total Endpoints** | 18 (4 core + 14 Power BI API) |

---

## 2. PowerShell Version & Modules

### Required PowerShell Version

```powershell
# Check PowerShell version
$PSVersionTable.PSVersion

# Recommended: PowerShell 5.1+ or PowerShell 7+
```

### Required Modules

| Module | Version | Purpose |
|--------|---------|---------|
| **SharePointPnPPowerShellOnline** | v3.29 | SharePoint Online management |
| **Azure CLI** | Latest | Azure resource management |
| **Azure Functions Core Tools** | v4.x | Function deployment |

### Module Installation Commands

```powershell
# Install PnP PowerShell module (Legacy - used in this project)
Install-Module SharePointPnPPowerShellOnline -Scope CurrentUser

# Alternative: Modern PnP.PowerShell module
Install-Module PnP.PowerShell -Scope CurrentUser

# Verify installation
Get-Module SharePointPnPPowerShellOnline -ListAvailable

# Install Azure CLI (Windows)
winget install Microsoft.AzureCLI

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Verify Azure CLI
az --version

# Verify Azure Functions Core Tools
func --version
```

---

## 3. Connection Details

### SharePoint Connection

```powershell
# Connection method used in this project
$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"

# Connect using web login (browser-based authentication)
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

# Verify connection
Get-PnPConnection

# Disconnect when finished
Disconnect-PnPOnline
```

> **Authentication Method:** `-UseWebLogin` opens a browser window for interactive login using your Microsoft 365 credentials. This is the recommended method for development/admin tasks.

### Azure CLI Connection

```powershell
# Login to Azure (opens browser)
az login

# Verify current account
az account show

# Set specific subscription (if needed)
az account set --subscription "SUBSCRIPTION_NAME_OR_ID"
```

---

## 4. SharePoint Lists & GUIDs

> ✅ **Validated via PnP PowerShell:** 2025-12-28

### Lists Used in This Project

| List Name | GUID | Usage | Mapping File |
|-----------|------|-------|--------------|
| `Ofertas_Pipeline` | `6db5a12d-595d-4a1a-aca1-035837613815` | Flow1, Flow3, Flow4 | `sharepoint_mapping_ofertas_pipeline.xml` |
| `Atualizacoes_Semanais` | `172d7d29-5a3c-4608-b4ea-b5b027ef5ac0` | Flow2



, Flow3 | `sharepoint_mapping_atualizacoes_semanais.xml` |
| `ARQs_Teams` | `1ad529f7-db5b-4567-aa00-1582ff333264` | Flow1 | `sharepoint_mapping_arqs_teams.xml` |
| `Ofertas_Pipeline_Normalizada` | `fa90b09d-5eb9-461f-bf15-64a494b00d2d` | Azure Function | `sharepoint_mapping_ofertas_pipeline_normalizada.xml` |
| `StatusReports_Historico` | `f58b3d23-5750-4b29-b30f-a7b5421cdd80` | Flow2 history | `share2point_mapping_statusreports_historico.xml` |
| `StatusReports_Queue_TEST` | `12197c6e-b5d4-4bcd-96d4-c8aafc426d0a` | 🆕 Flow1/Flow2 queue | Created via PowerShell |
| `Budget_Extensions` | `dfeda3e0-0cc9-434d-b8d5-5b450dc071b2` | Not in flows | `sharepoint_mapping_budget_extensions.xml` |
| `Jira_Allocation_Data` | `f25edf86-f23a-41bb-a7b1-84a096df2dd8` | Not in flows | `sharepoint_jira_Allocation_Data.xml` |
| `Resumo_Semanal` | `1d4a803e-9884-4e10-b932-ef9ff598f127` | Not in flows | `sharepoint_mapping_Resumo_Semanal.xml` |

### Commands to Get List GUIDs

```powershell
# Connect to SharePoint
$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

# Get all lists with GUIDs
Get-PnPList | Select-Object Title, Id | Format-Table -AutoSize

# Get specific list details
Get-PnPList -Identity "Ofertas_Pipeline" | Select-Object Title, Id, ItemCount

# Disconnect
Disconnect-PnPOnline
```

---

## 5. PowerShell Scripts Reference

### Script 1: DEPLOY_NOW.ps1

**Location:** `D:\VMs\Projetos\Sharepoint_JIRA\DEPLOY_NOW.ps1`  
**Purpose:** One-click deploy script for Azure Function

```powershell
# Run command:
powershell -ExecutionPolicy Bypass -File DEPLOY_NOW.ps1
```

**What it does:**
1. Checks prerequisites (Azure CLI, Azure Functions Core Tools)
2. Verifies Azure login (opens browser if needed)
3. Deploys Azure Function to `func-pipeline-consolidation`
4. Verifies deployment with health check
5. Retrieves and displays Function Key

**Key Variables:**
- `$functionPath` = `D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction`
- `$functionApp` = `func-pipeline-consolidation`
- `$resourceGroup` = `rg-pipeline-consolidation`

---

### Script 2: Create_StatusReports_Queue_Columns.ps1

**Location:** `D:\VMs\Projetos\Sharepoint_JIRA\MD_Files\Create_StatusReports_Queue_Columns.ps1`  
**Purpose:** Creates SharePoint list `StatusReports_Queue_TEST` with all required columns  
**PnP Module Version:** SharePointPnPPowerShellOnline v3.29

```powershell
# Run command:
.\Create_StatusReports_Queue_Columns.ps1 `
    -SiteUrl "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA" `
    -ListName "StatusReports_Queue_TEST"
```

**Columns Created:**

| Column Name | Type | Properties |
|-------------|------|------------|
| `QueueStatus` | Choice | Options: Pending, Sent, Completed, Error (Default: Pending) |
| `RecipientEmail` | Text | Indexed |
| `JiraKey` | Text | Indexed |
| `OfertaId` | Number | - |
| `Semana` | Text | Indexed |
| `VersaoReport` | Number | - |
| `UniqueKey` | Text | Indexed + Enforce Unique |
| `ResponseJson` | Note (Multi-line) | - |
| `SentAt` | DateTime | - |
| `CompletedAt` | DateTime | - |
| `AttemptCount` | Number | - |
| `LastError` | Note (Multi-line) | - |

**PnP Commands Used:**

```powershell
# Connection
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

# Check if list exists
Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue

# Create list if not exists
New-PnPList -Title $ListName -Template GenericList

# Check if field exists
Get-PnPField -List $ListName -Identity $InternalName -ErrorAction SilentlyContinue

# Create Choice field from XML
Add-PnPFieldFromXml -List $ListName -FieldXml $choiceXml

# Create Text field
Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Text -AddToDefaultView

# Create Number field
Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Number -AddToDefaultView

# Create Note (multi-line) field
Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type Note

# Create DateTime field
Add-PnPField -List $ListName -DisplayName $DisplayName -InternalName $InternalName -Type DateTime -AddToDefaultView

# Get field for modification
$field = Get-PnPField -List $ListName -Identity $InternalName

# Set indexed and unique properties
$field.Indexed = $true
$field.EnforceUniqueValues = $true
$field.Update()
$field.Context.ExecuteQuery()

# Disconnect
Disconnect-PnPOnline
```

---

## 6. Azure CLI Commands

### Azure Function Management

```powershell
# Check Azure CLI version
az --version

# Login to Azure
az login

# Verify current account
az account show

# Navigate to function folder and deploy
cd D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction
func azure functionapp publish func-pipeline-consolidation --python

# Check function app status
az functionapp show --name func-pipeline-consolidation --resource-group rg-pipeline-consolidation --query "state"

# List function keys
az functionapp keys list --name func-pipeline-consolidation --resource-group rg-pipeline-consolidation
```

### Configure App Settings

```powershell
# Power BI Settings (Optional)
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    PBI_TENANT_ID="<tenant-id>" `
    PBI_CLIENT_ID="<client-id>" `
    PBI_CLIENT_SECRET="<secret>"

# SharePoint Settings
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    SP_TENANT_ID="" `
    SP_CLIENT_ID="" `
    SP_CLIENT_SECRET="" `
    SP_SITE_URL="https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"

# Import settings
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    IMPORT_STRIP_HTML_OBSERVACOES="true" `
    IMPORT_ENRICH_ASSIGNEE="true" `
    ARQS_TEAMS_LIST_ID="1ad529f7-db5b-4567-aa00-1582ff333264"
```

---

## 7. PnP PowerShell Commands

### Common Operations Reference

```powershell
# ============================================
# CONNECTION
# ============================================
$SiteUrl = "https://indra365.sharepoint.com/sites/Grp_T_DN_Arquitetura_Solucoes_Multi_Praticas_QA"
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

# ============================================
# LIST OPERATIONS
# ============================================
# Get all lists
Get-PnPList | Select-Object Title, Id

# Get specific list
Get-PnPList -Identity "Ofertas_Pipeline"

# Create new list
New-PnPList -Title "NewListName" -Template GenericList

# ============================================
# FIELD OPERATIONS
# ============================================
# Get all fields in a list
Get-PnPField -List "ListName"

# Get specific field
Get-PnPField -List "ListName" -Identity "FieldInternalName"

# Create text field
Add-PnPField -List "ListName" -DisplayName "Field Display" -InternalName "FieldInternal" -Type Text

# Create choice field from XML
$xml = @"
<Field Type='Choice' DisplayName='Status' Name='Status' Format='Dropdown'>
  <Default>Pending</Default>
  <CHOICES>
    <CHOICE>Pending</CHOICE>
    <CHOICE>Completed</CHOICE>
    <CHOICE>Error</CHOICE>
  </CHOICES>
</Field>
"@
Add-PnPFieldFromXml -List "ListName" -FieldXml $xml

# Update field properties
$field = Get-PnPField -List "ListName" -Identity "FieldName"
$field.Indexed = $true
$field.Update()
$field.Context.ExecuteQuery()

# ============================================
# ITEM OPERATIONS
# ============================================
# Get all items
Get-PnPListItem -List "ListName"

# Get items with filter
Get-PnPListItem -List "ListName" -Query "<View><Query><Where><Eq><FieldRef Name='JiraKey'/><Value Type='Text'>PROJ-123</Value></Eq></Where></Query></View>"

# Create item
Add-PnPListItem -List "ListName" -Values @{"Title"="New Item"; "Status"="Pending"}

# Update item
Set-PnPListItem -List "ListName" -Identity 1 -Values @{"Status"="Completed"}

# ============================================
# EXPORT SCHEMA (used to generate XML files)
# ============================================
# Export list schema
Get-PnPList -Identity "ListName" -Includes Fields, Views | 
    ConvertTo-Xml -Depth 10 | 
    Out-File "list_schema.xml"

# ============================================
# DISCONNECT
# ============================================
Disconnect-PnPOnline
```

---

## 8. Credential & Authentication Reference

### Authentication Methods Used

| Component | Method | Details |
|-----------|--------|---------|
| **PnP PowerShell** | `-UseWebLogin` | Browser-based interactive login |
| **Azure CLI** | `az login` | Browser-based interactive login |
| **Azure Function** | Function Key | HTTP header `x-functions-key` |
| **Power Automate → SharePoint** | OAuth 2.0 | M365 connector |
| **Power Automate → Azure Function** | Function Key | HTTP header |
| **Azure Function → Power BI** | Service Principal | OAuth 2.0 client_credentials |

### Azure Function Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FUNCTIONS_WORKER_RUNTIME` | `python` | Yes |
| `ENVIRONMENT` | `LAB` or `PRODUCTION` | Yes |
| `SP_TENANT_ID` | SharePoint tenant ID | For Graph API |
| `SP_CLIENT_ID` | SharePoint app client ID | For Graph API |
| `SP_CLIENT_SECRET` | SharePoint app secret | For Graph API |
| `SP_SITE_URL` | SharePoint site URL | For Graph API |
| `PBI_TENANT_ID` | Power BI tenant ID | For PBI endpoints |
| `PBI_CLIENT_ID` | Power BI app client ID | For PBI endpoints |
| `PBI_CLIENT_SECRET` | Power BI app secret | For PBI endpoints |
| `IMPORT_STRIP_HTML_OBSERVACOES` | Strip HTML from notes | Optional |
| `IMPORT_ENRICH_ASSIGNEE` | Enrich with ARQ data | Optional |
| `ARQS_TEAMS_LIST_ID` | ARQs_Teams list GUID | Optional |

---

## 9. Troubleshooting

### Common Issues & Solutions

#### Issue: PnP module not found
```powershell
# Install the module
Install-Module SharePointPnPPowerShellOnline -Scope CurrentUser -Force

# Or use modern PnP.PowerShell
Install-Module PnP.PowerShell -Scope CurrentUser
```

#### Issue: Connection timeout
```powershell
# Use legacy authentication if web login fails
Connect-PnPOnline -Url $SiteUrl -Credentials (Get-Credential)
```

#### Issue: Access denied to list
- Verify you have Site Collection Administrator permissions
- Check if the list requires specific permissions

#### Issue: Azure Function deploy fails
```powershell
# Verify you're logged in
az account show

# Check function app exists
az functionapp show --name func-pipeline-consolidation --resource-group rg-pipeline-consolidation

# Check host.json exists
Test-Path .\host.json
```

#### Issue: Field already exists
```powershell
# The script handles this - check console output for [SKIP] messages
# Fields are only created if they don't exist
```

---

## 📚 Related Documentation

| Document | Path | Description |
|----------|------|-------------|
| Architecture Deep Dive | `XML/ARCHITECTURE/ARCHITECTURE_DEEP_DIVE.md` | Complete system architecture |
| Deploy Checklist | `Azure Function/DEPLOY_CHECKLIST.md` | Step-by-step deployment guide |
| SharePoint Schema Index | `XML/INDEX.md` | List GUIDs and mapping files |
| Flow1 Guide | `MD_Files/FLOW1_MANUAL_CREATION_GUIDE.md` | Queue Creator flow setup |
| Flow2 Guide | `MD_Files/FLOW2_MANUAL_CREATION_GUIDE.md` | Worker flow setup |
| Checkpoint | `CHECKPOINT.json` | Project status and credentials |

---

*Document generated: 2025-12-30*  
*Project: JIRA → SharePoint → Teams/Power BI Integration*
