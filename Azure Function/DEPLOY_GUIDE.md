# 🚀 Deploy Azure Function - Pipeline Consolidation

## Pré-requisitos

1. **Azure CLI** instalado: https://docs.microsoft.com/cli/azure/install-azure-cli
2. **Azure Functions Core Tools**: `npm install -g azure-functions-core-tools@4`
3. **Conta Azure** ativa

---

## Deploy Rápido

### 1. Login no Azure
```powershell
az login
```

### 2. Criar Resource Group
```powershell
az group create --name rg-pipeline-consolidation --location brazilsouth
```

### 3. Criar Storage Account
```powershell
az storage account create --name stpipelineconsolidation --location brazilsouth --resource-group rg-pipeline-consolidation --sku Standard_LRS
```

### 4. Criar Function App
```powershell
az functionapp create --resource-group rg-pipeline-consolidation --consumption-plan-location brazilsouth --runtime python --runtime-version 3.11 --functions-version 4 --name func-pipeline-consolidation --storage-account stpipelineconsolidation --os-type linux
```

### 5. Deploy do código
```powershell
cd d:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction
func azure functionapp publish func-pipeline-consolidation
```

---

## Testar

### Health Check
```
GET https://func-pipeline-consolidation.azurewebsites.net/api/health
```

### Consolidar Pipeline
```
POST https://func-pipeline-consolidation.azurewebsites.net/api/consolidar?code=<FUNCTION_KEY>
Content-Type: application/json

{
  "ofertas": [...],
  "atualizacoes": [...]
}
```

---

## Obter Function Key

```powershell
az functionapp keys list --name func-pipeline-consolidation --resource-group rg-pipeline-consolidation
```

Use esta chave no Power Automate para chamar a função.
