# 🔧 Azure Function App Settings Configuration Guide
## Power BI Integration Setup

**Version:** 1.0  
**Date:** 2026-01-06  
**Gap:** G-006  
**Status:** ✅ **VERIFIED DEPLOYED** (2026-01-06 via Azure CLI)

---

## 🎯 Overview

The Azure Function (`function_app.py`) includes **14 fully implemented Power BI API endpoints**. 

> [!TIP]
> **All settings are already configured in Azure!** Verified via `az functionapp config appsettings list` on 2026-01-06.

> [!IMPORTANT]
> **Dual-Tenant Architecture:**
> - **SharePoint/Power BI**: Uses **Enterprise credentials** (VIVO tenant)
> - **Azure Function**: Hosted on **Personal Azure subscription** (different tenant)
> 
> The `PBI_*` settings point to the Enterprise tenant for API access.

---

## 📋 Required App Settings

### Power BI API Authentication (✅ VERIFIED CONFIGURED)

| Setting | Description | Status | Azure Value |
|---------|-------------|:------:|-------------|
| `PBI_TENANT_ID` | Azure AD Tenant ID (GUID) | ✅ | `edd5b6c2-...` |
| `PBI_CLIENT_ID` | App Registration Application (Client) ID | ✅ | `4a885196-...` |
| `PBI_CLIENT_SECRET` | App Registration Client Secret | ✅ | `[REDACTED]` |

### Other Azure Settings (✅ VERIFIED CONFIGURED)

| Setting | Value |
|---------|-------|
| `FUNCTIONS_WORKER_RUNTIME` | python |
| `FUNCTIONS_EXTENSION_VERSION` | ~4 |
| `AzureWebJobsStorage` | ✅ Configured |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | ✅ Configured |

---

## 🔐 Step 1: Create Azure AD App Registration

### 1.1 Navigate to Azure Portal

```
Azure Portal → Azure Active Directory → App registrations → New registration
```

### 1.2 Configure App Registration

| Field | Value |
|-------|-------|
| **Name** | `JIRA-SharePoint-PowerBI-Integration` |
| **Supported account types** | Accounts in this organizational directory only |
| **Redirect URI** | Leave blank (not needed for service principal) |

### 1.3 Note the Application IDs

After creation, note:
- **Application (client) ID** → `PBI_CLIENT_ID`
- **Directory (tenant) ID** → `PBI_TENANT_ID`

---

## 🔑 Step 2: Create Client Secret

### 2.1 Navigate to Certificates & secrets

```
App Registration → Certificates & secrets → New client secret
```

### 2.2 Configure Secret

| Field | Value |
|-------|-------|
| **Description** | `PowerBI API Access - Production` |
| **Expires** | 24 months (recommended) |

### 2.3 Copy Secret Value

> [!CAUTION]
> Copy the secret **Value** (not the Secret ID) immediately. It will not be shown again.

This value → `PBI_CLIENT_SECRET`

---

## 📊 Step 3: Configure Power BI API Permissions

### 3.1 Add API Permissions

```
App Registration → API permissions → Add a permission → Power BI Service
```

### 3.2 Required Permissions

| Permission | Type | Purpose |
|------------|------|---------|
| `Dataset.ReadWrite.All` | Application | List/refresh datasets |
| `Workspace.Read.All` | Application | List workspaces |
| `Report.Read.All` | Application | List reports |
| `Dataflow.ReadWrite.All` | Application | Manage dataflows (optional) |

### 3.3 Grant Admin Consent

```
API permissions → Grant admin consent for [Tenant Name]
```

> [!IMPORTANT]
> Admin consent is **required** for application permissions. This must be done by a Global Administrator or Application Administrator.

---

## 🏢 Step 4: Configure Power BI Service

### 4.1 Enable Service Principal Access

In the Power BI Admin Portal:

```
Power BI Admin Portal → Tenant settings → Developer settings
```

Enable:
- ✅ **Allow service principals to use Power BI APIs**
- ✅ Specify security group (optional) or enable for entire organization

### 4.2 Add Service Principal to Workspace

```
Power BI Service → Workspace → Access → Add → Enter App Name → Contributor or Admin role
```

---

## ⚙️ Step 5: Configure Azure Function App Settings

### 5.1 Navigate to Function App

```
Azure Portal → Function Apps → [Your Function App] → Configuration → Application settings
```

### 5.2 Add New Application Settings

| Name | Value |
|------|-------|
| `PBI_TENANT_ID` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `PBI_CLIENT_ID` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `PBI_CLIENT_SECRET` | `your-client-secret-value` |

### 5.3 Save and Restart

Click **Save** → Function App will automatically restart.

---

## 🧪 Step 6: Verify Configuration

### 6.1 Test Workspace Endpoint

```http
POST https://[your-function-app].azurewebsites.net/api/pbi-workspace
Content-Type: application/json
x-functions-key: [your-function-key]

{
  "workspace_name": "PBI_API_Access",
  "create_if_missing": false
}
```

### 6.2 Expected Response

```json
{
  "success": true,
  "workspace_name": "PBI_API_Access",
  "workspace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "created": false
}
```

### 6.3 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required env var: PBI_TENANT_ID` | App Setting not configured | Add the setting in Azure Portal |
| `Token request failed (401)` | Invalid credentials | Verify client ID and secret |
| `Forbidden` | No access to workspace | Add service principal to workspace |
| `Service principal not allowed` | Tenant setting disabled | Enable in Power BI Admin Portal |

---

## 📦 Available Power BI Endpoints

After configuration, these endpoints become available:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/pbi-workspace` | POST | Ensure workspace exists |
| `/pbi-datasets` | POST | List datasets in workspace |
| `/pbi-dataset-refresh` | POST | Trigger dataset refresh |
| `/pbi-dataset-refresh-history` | POST | Get refresh history |
| `/pbi-reports` | POST | List reports in workspace |
| `/pbi-report-clone` | POST | Clone report to workspace |
| `/pbi-dataflows` | POST | List dataflows |
| `/pbi-dataflow-refresh` | POST | Trigger dataflow refresh |
| `/pbi-capacities` | POST | List capacities |
| `/pbi-apps` | POST | List Power BI apps |
| `/pbi-dashboards` | POST | List dashboards |
| `/pbi-tiles` | POST | List dashboard tiles |
| `/pbi-gateways` | POST | List gateways |
| `/pbi-import` | POST | Import PBIX file |

---

## 🔄 Integration with Power Automate

### Trigger Refresh from Flow

In Power Automate, add an **HTTP** action:

```
Method: POST
URI: https://[function-app].azurewebsites.net/api/pbi-dataset-refresh
Headers:
  x-functions-key: [function-key]
  Content-Type: application/json
Body:
{
  "workspace_id": "[workspace-guid]",
  "dataset_id": "[dataset-guid]",
  "notify_option": "NoNotification"
}
```

---

## 📅 Recommended Refresh Schedule

| Use Case | Frequency | Trigger |
|----------|-----------|---------|
| After JIRA Import | Event-based | Flow1 completion |
| After Weekly Consolidation | Event-based | Flow3 completion |
| Fallback Scheduled | 3x daily | 08:00, 13:00, 18:00 BRT |

---

## ✅ Configuration Checklist

- [ ] Azure AD App Registration created
- [ ] Application (Client) ID noted
- [ ] Tenant ID noted
- [ ] Client secret created and copied
- [ ] Power BI API permissions added
- [ ] Admin consent granted
- [ ] Service principal enabled in Power BI tenant
- [ ] Service principal added to target workspace
- [ ] App Settings added to Azure Function:
  - [ ] `PBI_TENANT_ID`
  - [ ] `PBI_CLIENT_ID`
  - [ ] `PBI_CLIENT_SECRET`
- [ ] Function App restarted
- [ ] `/pbi-workspace` endpoint tested successfully

---

*Document: AZURE_FUNCTION_PBI_SETTINGS_GUIDE.md*  
*Gap: G-006 - Azure Function Environment Variables*
