# 🔧 GUIA DE DISASTER RECOVERY
## Azure Function - Pipeline Consolidation

**Versão:** 1.0  
**Data:** 2025-12-27  
**Criticidade:** 🔴 Alta - Função em Produção

---

## 📍 LOCALIZAÇÃO DOS ARQUIVOS

### Código Fonte (Local)

```
D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction\
├── function_app.py        ← Código principal (2878 linhas, 19 endpoints)
├── requirements.txt       ← Dependências Python
├── host.json              ← Configuração Azure Functions
├── local.settings.json    ← Variáveis locais (NÃO vai para produção)
├── DEPLOY_GUIDE.md        ← Guia de deploy
├── DEPLOY_CHECKLIST.md    ← Checklist de deploy
└── README.md              ← Documentação
```

### Recursos Azure (Produção)

| Recurso | Nome | Região |
|---------|------|--------|
| **Resource Group** | `rg-pipeline-consolidation` | Brazil South |
| **Function App** | `func-pipeline-consolidation` | Brazil South |
| **Storage Account** | `stpipelineconsolidation` | Brazil South |
| **App Service Plan** | Consumption (Serverless) | Brazil South |

### URL de Produção

```
https://func-pipeline-consolidation.azurewebsites.net/api/
```

---

## 🔄 PASSO A PASSO: REIMPLANTAÇÃO COMPLETA

### Fase 1: Preparar Ambiente Local

```powershell
# 1.1 Verificar Azure CLI instalado
az --version
# Se não instalado: winget install Microsoft.AzureCLI

# 1.2 Verificar Azure Functions Core Tools
func --version
# Se não instalado: npm install -g azure-functions-core-tools@4

# 1.3 Login no Azure
az login
# Abrirá navegador para autenticação

# 1.4 Selecionar subscription correta
az account list --output table
az account set --subscription "<SUBSCRIPTION_NAME_OR_ID>"
```

### Fase 2: Recriar Recursos Azure (se necessário)

```powershell
# 2.1 Criar Resource Group
az group create `
  --name rg-pipeline-consolidation `
  --location brazilsouth

# 2.2 Criar Storage Account
az storage account create `
  --name stpipelineconsolidation `
  --location brazilsouth `
  --resource-group rg-pipeline-consolidation `
  --sku Standard_LRS

# 2.3 Criar Function App
az functionapp create `
  --resource-group rg-pipeline-consolidation `
  --consumption-plan-location brazilsouth `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  --name func-pipeline-consolidation `
  --storage-account stpipelineconsolidation `
  --os-type linux
```

### Fase 3: Deploy do Código

```powershell
# 3.1 Navegar para pasta do código
cd D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction

# 3.2 Verificar arquivos essenciais
dir function_app.py   # Deve existir (120KB)
dir requirements.txt  # Deve existir
dir host.json        # Deve existir

# 3.3 Publicar para Azure
func azure functionapp publish func-pipeline-consolidation

# Aguardar mensagem: "Deployment successful"
```

### Fase 4: Configurar Variáveis de Ambiente

```powershell
# 4.1 Configurar credenciais Power BI (obrigatório para /pbi-* endpoints)
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    PBI_TENANT_ID="<SEU_TENANT_ID>" `
    PBI_CLIENT_ID="<SEU_CLIENT_ID>" `
    PBI_CLIENT_SECRET="<SEU_CLIENT_SECRET>"

# 4.2 Verificar configurações
az functionapp config appsettings list `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --output table
```

### Fase 5: Obter Function Key

```powershell
# 5.1 Listar chaves disponíveis
az functionapp keys list `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation

# 5.2 Copiar o valor de "default" em "functionKeys"
# Exemplo de resposta:
# {
#   "functionKeys": {
#     "default": "AbCdEfGhIjKlMnOpQrStUvWxYz123456789=="
#   }
# }
```

### Fase 6: Validar Deploy

```powershell
# 6.1 Testar endpoint de health (sem chave)
$response = Invoke-RestMethod -Uri "https://func-pipeline-consolidation.azurewebsites.net/api/health"
$response  # Deve retornar {"status": "healthy"}

# 6.2 Testar endpoint com chave
$functionKey = "<SUA_FUNCTION_KEY>"
$uri = "https://func-pipeline-consolidation.azurewebsites.net/api/consolidar?code=$functionKey"
$body = @{
    ofertas = @()
    atualizacoes = @()
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json"
$response
```

---

## 🔗 QUEM CHAMA A FUNÇÃO?

### Power Automate Flows

| Flow | Endpoint Chamado | Trigger | Ação |
|------|------------------|---------|------|
| **Flow 3: Weekly Report** | `/api/consolidar-v2` | Recurrence (Semanal) | Gera card Teams |
| **Flow 4: JIRA Import** | `/api/import-jira` | Arquivo criado SharePoint | Importa CSV |
| **Flow B: Normalização** | `/api/normalizar-ofertas` | Manual/Agendado | Padroniza valores |

### Atualizar Function Key nos Flows

Se a Function Key mudou após o redeploy:

1. Abra **Power Automate** → make.powerautomate.com
2. Localize cada Flow que chama a Azure Function
3. Edite a ação **HTTP**
4. Atualize o parâmetro `code=` na URL

```
ANTES: https://func-...azurewebsites.net/api/consolidar-v2?code=CHAVE_ANTIGA
DEPOIS: https://func-...azurewebsites.net/api/consolidar-v2?code=CHAVE_NOVA
```

---

## 📦 DEPENDÊNCIAS

### Arquivos Críticos

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `function_app.py` | ~121KB | Código de todos os 19 endpoints |
| `requirements.txt` | 32 bytes | 3 bibliotecas Python |
| `host.json` | 356 bytes | Configuração runtime |

### Bibliotecas Python (requirements.txt)

```
azure-functions
pandas
numpy
```

### Variáveis de Ambiente (Produção)

| Variável | Obrigatório Para | Como Obter |
|----------|------------------|------------|
| `PBI_TENANT_ID` | /pbi-* endpoints | Azure AD → Propriedades |
| `PBI_CLIENT_ID` | /pbi-* endpoints | App Registration → Overview |
| `PBI_CLIENT_SECRET` | /pbi-* endpoints | App Registration → Certificates & secrets |

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Pós-Deploy

- [ ] `/api/health` retorna `{"status": "healthy"}`
- [ ] `/api/import-jira` com CSV de teste funciona
- [ ] `/api/consolidar-v2` com dados de teste funciona
- [ ] `/api/pbi-workspace` retorna workspaces (se PBI configurado)
- [ ] Power Automate Flows atualizados com nova Function Key
- [ ] Flow 3 executa com sucesso (teste manual)
- [ ] Flow 4 processa arquivo CSV

### Credenciais Verificadas

- [ ] Azure CLI logado na subscription correta
- [ ] Function Key copiada e atualizada nos Flows
- [ ] PBI_TENANT_ID, PBI_CLIENT_ID, PBI_CLIENT_SECRET configurados

---

## 🔐 CREDENCIAIS NECESSÁRIAS

### Azure

| Item | Onde Obter |
|------|------------|
| **Subscription** | Portal Azure → Subscriptions |
| **Resource Group** | `rg-pipeline-consolidation` (criar se não existir) |
| **Function Key** | `az functionapp keys list ...` |

### Power BI (App Registration)

| Item | Onde Obter |
|------|------------|
| **Tenant ID** | Azure AD → Properties → Tenant ID |
| **Client ID** | Azure AD → App registrations → [App] → Application ID |
| **Client Secret** | Azure AD → App registrations → [App] → Certificates & secrets |

### Power BI API Permissions

O App Registration deve ter as seguintes permissões:

```
API: Power BI Service
├── Dataset.ReadWrite.All
├── Workspace.Read.All
├── Report.Read.All
├── Dashboard.Read.All
└── Capacity.Read.All
```

---

## ⚠️ TROUBLESHOOTING

### Erro: "Function not found"

```powershell
# Verificar se deploy foi completo
az functionapp function list `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation
```

### Erro: "Unauthorized" (401)

- Verificar se Function Key está correta
- Verificar se o endpoint requer `auth_level=FUNCTION`

### Erro: "Internal Server Error" (500)

```powershell
# Ver logs em tempo real
func azure functionapp logstream func-pipeline-consolidation
```

### Erro nas credenciais PBI

```powershell
# Verificar se variáveis estão configuradas
az functionapp config appsettings list `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --query "[?name=='PBI_TENANT_ID' || name=='PBI_CLIENT_ID']"
```

---

## 📞 CONTATOS E SUPORTE

| Recurso | Responsável |
|---------|-------------|
| **Código Fonte** | Git local ou Azure DevOps |
| **Azure Subscription** | DN Technology Architecture |
| **Power BI App Registration** | Administrador Azure AD |
| **Power Automate Flows** | Arquiteto de Soluções |

---

## 🔄 BACKUP E VERSIONAMENTO

### Backup do Código

```powershell
# Fazer backup antes de alterações
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
Copy-Item -Path "D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction" `
  -Destination "D:\Backups\AzureFunction_$timestamp" -Recurse
```

### Git (se configurado)

```powershell
cd D:\VMs\Projetos\JIRA_Teams_PBI_Integration
git add .
git commit -m "Backup antes de redeploy DR"
git push origin main
```

---

*Guia de Disaster Recovery v1.0*  
*Azure Function - Pipeline Consolidation*
