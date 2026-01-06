# Azure Function Deployment Checklist

> **Última atualização:** 2025-12-25T18:00:00-03:00  
> **Function App:** `func-pipeline-consolidation` (ÚNICA)

---

## ✅ Decisão de Arquitetura

| Item | Decisão |
|------|---------|
| **Function App** | `func-pipeline-consolidation` (única) |
| **Resource Group** | `rg-pipeline-consolidation` |
| **Codebase** | `D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction\` |
| **Arquivo principal** | `function_app.py` (contém TODOS os 18 endpoints) |

---

## 📁 Estrutura Oficial de Deploy

```
D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction\  ← DEPLOY DAQUI
├── function_app.py      ✅ 18 endpoints (~60KB)
├── requirements.txt     ✅ pandas, numpy, azure-functions
├── host.json           ✅ v2.0, extensionBundle 4.x
├── local.settings.json ✅ Config local
├── FUNCTIONS_AS_IS.md  📄 Documentação AS-IS
├── DEPLOY_CHECKLIST.md 📄 Este arquivo
└── README.md           📄 Guia geral
```

---

## 📋 Endpoints no `function_app.py` (18 total)

### Core (4 endpoints)
| # | Endpoint | Status |
|---|----------|--------|
| 1 | `/api/health` | ✅ Pronto |
| 2 | `/api/consolidar` | ✅ Pronto |
| 3 | `/api/import-jira` | ✅ Pronto |
| 4 | `/api/normalizar-ofertas` | ✅ Pronto |
| + | `/api/lab/purge-lists` | ✅ Pronto (LAB/admin-only) |

### Power BI API (14 endpoints)
| # | Endpoint | Status |
|---|----------|--------|
| 5-18 | `/api/pbi-*` (workspace, datasets, reports, dashboards, etc.) | ✅ Pronto |

---

## 🚀 Comandos de Deploy

### Pré-requisitos
```powershell
# Verificar Azure CLI
az --version

# Verificar Azure Functions Core Tools
func --version

# Login no Azure (se necessário)
az login
```

### Deploy Step-by-Step

```powershell
# 1. Navegar para a pasta do Function App
cd D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction

# 2. Verificar se host.json existe
dir host.json

# 3. Publicar para o Azure
func azure functionapp publish func-pipeline-consolidation

# 4. Verificar se deploy funcionou
az functionapp show --name func-pipeline-consolidation --resource-group rg-pipeline-consolidation --query "state"
```

### Configurar Variáveis de Ambiente (para pbi-workspace)

```powershell
# Apenas se for usar o endpoint /pbi-workspace
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    PBI_TENANT_ID="<seu-tenant-id>" `
    PBI_CLIENT_ID="<client-id>" `
    PBI_CLIENT_SECRET="<secret>"
```

### Configurar Variáveis de Ambiente (qualidade de dados / import-jira)

`Custom field (Observations)` do JIRA pode vir com HTML (ex.: `<div class=...>`, `&gt;`). Para o texto ficar legível em Teams/Power BI, o `/api/import-jira` pode remover HTML antes de gravar em `Ofertas_Pipeline.Observacoes`:

```powershell
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    IMPORT_STRIP_HTML_OBSERVACOES="true"
```

### Configurar Variáveis de Ambiente (enriquecimento de Assignee / Matrícula)

Se você quiser que o `/api/import-jira` **enriqueça** cada oferta com dados do ARQ (a partir da lista `ARQs_Teams`), habilite:

- `IMPORT_ENRICH_ASSIGNEE=true`

Isso adiciona no payload retornado os campos:
- `AssigneeMatricula` (usa `ARQs_Teams.Title`)
- `AssigneeNome` (usa `ARQs_Teams.field_1`)
- `AssigneeEmail` (usa `ARQs_Teams.field_3` / `E_x002d_mail`)

Requisitos:
- Service Principal com permissão Graph para ler itens do site/lista (mesmo conjunto de `SP_TENANT_ID`, `SP_CLIENT_ID`, `SP_CLIENT_SECRET`).
- `SP_SITE_URL` (ou `SP_SITE_ID`) configurado.
- Opcional: `ARQS_TEAMS_LIST_ID` (default: `1ad529f7-db5b-4567-aa00-1582ff333264`).

```powershell
az functionapp config appsettings set `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation `
  --settings `
    IMPORT_ENRICH_ASSIGNEE="true" `
    SP_SITE_URL="https://<tenant>.sharepoint.com/sites/<site>" `
    ARQS_TEAMS_LIST_ID="1ad529f7-db5b-4567-aa00-1582ff333264"
```

### Obter Function Key

```powershell
az functionapp keys list `
  --name func-pipeline-consolidation `
  --resource-group rg-pipeline-consolidation
```

---

## ✅ Checklist Completo

### Fase 1: Preparação
- [x] Código consolidado em único `function_app.py`
- [x] Todos os 5 endpoints implementados
- [x] `requirements.txt` atualizado (pandas, numpy)
- [x] `host.json` configurado (v2.0)
- [x] Documentação `FUNCTIONS_AS_IS.md` atualizada

### Fase 2: Deploy (por você)
- [ ] Navegar para pasta `AzureFunction/`
- [ ] Executar `func azure functionapp publish func-pipeline-consolidation`
- [ ] Verificar logs de deploy
- [ ] Testar `/api/health` no browser

### Fase 3: Validação
- [ ] Testar `/api/health` → deve retornar `{"status": "healthy"}`
- [ ] Testar `/api/import-jira` com CSV de exemplo
- [ ] Testar `/api/consolidar` com dados de amostra
- [ ] (Opcional) Configurar variáveis PBI e testar `/api/pbi-workspace`

### Fase 4: Power Automate
- [ ] Atualizar Flow 4 com nova Function Key (se mudou)
- [ ] Verificar Flow 4 funcionando com `/api/import-jira`
- [ ] Agendar Flow B para usar `/api/normalizar-ofertas`

### Fase 5 (LAB opcional): Purge de dados para testes
- [ ] Ler `LAB_PURGE_ENDPOINT.md`
- [ ] Configurar App Settings (Graph + flags de segurança)
- [ ] Testar com `dry_run=true` antes de usar `dry_run=false`

---

## ⚠️ Atenção

1. **NÃO usar** a pasta `AzureFunction_Normalizada/` - ela foi criada como backup mas não será usada
2. **Única Function App**: `func-pipeline-consolidation`
3. **Único codebase**: `D:\VMs\Projetos\JIRA_Teams_PBI_Integration\AzureFunction\`

---

*Documento gerado automaticamente em 2025-12-24*
