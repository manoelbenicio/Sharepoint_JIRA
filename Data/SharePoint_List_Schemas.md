# SharePoint List Schema: Arquitetos_Expandida
# Import this via SharePoint > Site Settings > Create List from CSV

## Columns Configuration

| Column Name | Type | Required | Description |
|-------------|------|----------|-------------|
| Nome | Single line of text | Yes | Full name |
| Email | Single line of text | Yes | Corporate email |
| Cargo | Single line of text | No | Job title |
| Matricula | Single line of text | No | Employee ID |
| Tipo | Choice | Yes | Values: Arquiteto, DN, Trainee, Estagiario |
| Status | Choice | Yes | Values: Ativo, Inativo |
| UsernameJIRA | Single line of text | Yes | JIRA login for ETL mapping |
| ReportaA | Single line of text | No | Manager email |

## Import Steps

1. Go to SharePoint site: https://minsaborpfdev.sharepoint.com/sites/VivoDigitalSales
2. Click **New** > **List**
3. Select **From CSV**
4. Upload: `Equipe_Completa_SharePoint_Import.csv`
5. Configure column types as specified above
6. Rename list to: **Arquitetos_Expandida**

---

# SharePoint List Schema: Atualizacoes_Semanais
# For weekly status collection

## Columns Configuration

| Column Name | Type | Required | Description |
|-------------|------|----------|-------------|
| Arquiteto | Lookup (to Arquitetos_Expandida) | Yes | Reference to team member |
| Semana | Single line of text | Yes | Week reference (2026-W02) |
| StatusGeral | Choice | Yes | Values: 🟢 On Track, 🟡 At Risk, 🔴 Off Track |
| PrincipalConquista | Multiple lines of text | No | Main achievement |
| PrincipalDesafio | Multiple lines of text | No | Main challenge |
| PrecisaAjuda | Choice | No | Values: Não, Sim - urgente, Sim - pode esperar |
| DataResposta | Date and Time | Yes | Response timestamp |
| OfertasRelacionadas | Multiple lines of text | No | JIRA keys mentioned |

## Create Steps

1. Go to SharePoint site
2. Click **New** > **List** > **Blank list**
3. Name: **Atualizacoes_Semanais**
4. Add columns as specified above
5. Create views:
   - **Esta Semana**: Filter by Semana = current week
   - **Por Arquiteto**: Group by Arquiteto
   - **Pendentes Ação**: Filter by PrecisaAjuda = "Sim - urgente"
