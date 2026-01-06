# 📋 GUIA COMPLETO DO PROJETO
## JIRA → SharePoint → Teams/Power BI Integration

**Para:** Stakeholders, KAMs, Gerentes, DN  
**Versão:** 1.0  
**Data:** 2025-12-27

---

## 🎯 POR QUE ESTE PROJETO EXISTE?

### O Problema Anterior

```
┌──────────────────────────────────────────────────────────────────┐
│  ANTES: Processo Manual e Fragmentado                            │
├──────────────────────────────────────────────────────────────────┤
│  1. Dados no JIRA (sistema de ofertas)                           │
│  2. Export manual de CSV                                         │
│  3. Manipulação em Excel                                         │
│  4. Cópia manual para SharePoint                                 │
│  5. Report manual para liderança                                 │
│  6. Atualização de dashboards manual                             │
│                                                                  │
│  ⏱️ Tempo: 4-6 horas/semana                                      │
│  ❌ Erros: Alta taxa de inconsistências                          │
│  📉 Visibilidade: Dados desatualizados                           │
└──────────────────────────────────────────────────────────────────┘
```

### A Solução Implementada

```
┌──────────────────────────────────────────────────────────────────┐
│  AGORA: Pipeline Automatizado                                    │
├──────────────────────────────────────────────────────────────────┤
│  1. CSV JIRA → Azure Function (transformação automática)         │
│  2. Azure Function → SharePoint (upsert automático)              │
│  3. Power Automate → Azure Function (consolidação)               │
│  4. Azure Function → Teams (card executivo automático)           │
│  5. SharePoint → Power BI (refresh automático)                   │
│                                                                  │
│  ⏱️ Tempo: 5 minutos de supervisão                               │
│  ✅ Erros: Validação automática de tipos                         │
│  📈 Visibilidade: Dados em tempo real                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🏢 BENEFÍCIOS PARA CADA STAKEHOLDER

| Perfil | Benefício Principal |
|--------|---------------------|
| **C-Level/Diretoria** | Card semanal no Teams com métricas consolidadas (Win Rate, Pipeline, Budget) |
| **Gerentes de Mercado** | Visão de suas ofertas com status atualizado |
| **Arquitetos Presales** | Rastreamento de tempo de ciclo e carga de trabalho |
| **DN/Operações** | Controle de budget de horas e alertas de risco |
| **KAMs** | Status das ofertas por cliente |

---

## 📦 COMPONENTES DO SISTEMA

### 1. Azure Function (`function_app.py`)
**O que é:** Serviço na nuvem que processa dados automaticamente.  
**Por que existe:** Centralizar a lógica de transformação e cálculo de métricas.

| Endpoint | Função de Negócio |
|----------|------------------|
| `/import-jira` | Importa CSV do JIRA e prepara para SharePoint |
| `/normalizar-ofertas` | Padroniza valores para consistência dos reports |
| `/consolidar-v2` | Calcula métricas e gera card para Teams |
| `/pbi-*` | Integração com Power BI (refresh, datasets) |

### 2. SharePoint Lists
**O que é:** Banco de dados corporativo no Microsoft 365.  
**Por que existe:** Armazenar os dados de forma estruturada e acessível.

| Lista | Propósito |
|-------|-----------|
| `Ofertas_Pipeline` | Lista principal com todas as ofertas |
| `Atualizacoes_Semanais` | Respostas dos arquitetos via Forms |
| `Mapeamentos_Normalizacao` | Tabela de de-para para normalização |

### 3. Power Automate Flows
**O que é:** Automações que conectam os sistemas.  
**Por que existe:** Orquestrar o fluxo de dados entre componentes.

---

## 📊 AS DUAS ABORDAGENS DE DADOS

### Por que existem "dados normalizados" e "dados normais"?

O JIRA permite valores **livres** em campos que no SharePoint são **campos Choice** (listas suspensas). Isso cria um problema:

```
JIRA (Valor Livre)         SharePoint (Valor Esperado)
─────────────────         ──────────────────────────
"under study"       ≠     "Under Study"   (capitalização)
"follow up"         ≠     "FollowUp"      (espaço)
"followup"          ≠     "FollowUp"      (variação)
"On offer"          ≠     "On Offer"      (capitalização)
"UTILITIES"         ≠     "Utilities"     (maiúsculas)
"fs"                ≠     "FS"            (minúsculas)
```

### Duas Estratégias Possíveis

| Estratégia | Descrição | Prós | Contras |
|------------|-----------|------|---------|
| **A) FillInChoice=TRUE** | SharePoint aceita QUALQUER valor do JIRA | ✅ Simples, sem perda de dados | ❌ Valores inconsistentes nos reports |
| **B) Normalização** | Azure Function padroniza antes de enviar | ✅ Dados consistentes | ❌ Precisa manter tabela de-para |

### Decisão Atual do Projeto

> **Estamos usando a Estratégia A (FillInChoice=TRUE)** com os campos Choice configurados para aceitar valores livres.

Isso significa:
- Campos `Status`, `Mercado`, `TipoServico`, `TipoOportunidade`, `PraticaUnificada`, `StatusBudgetAlocado` aceitam qualquer valor
- O endpoint `/normalizar-ofertas` existe mas **não está sendo usado ativamente**
- Os reports podem ter variações de valores se o JIRA não for consistente

---

## 🔄 DETALHES DO ENDPOINT `/import-jira`

### Função de Negócio
Transforma o CSV exportado do JIRA em formato compatível com SharePoint.

### Fluxo de Dados

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ CSV do JIRA │────▶│ Azure Function   │────▶│ JSON formatado  │
│ (23 colunas)│     │ /import-jira     │     │ para SharePoint │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │ TRANSFORMAÇÕES   │
                    │ • Parse números  │
                    │ • Parse datas    │
                    │ • Parse boolean  │
                    │ • Limpar textos  │
                    │ • Validar JiraKey│
                    └──────────────────┘
```

### Mapeamento de Colunas JIRA → SharePoint

| Coluna no CSV JIRA | Campo no SharePoint | Transformação |
|-------------------|---------------------|---------------|
| `Issue key` | `JiraKey` | Maiúsculo + escape de apóstrofo |
| `Summary` | `Titulo` | Limite 255 caracteres |
| `Status` | `Status` | **PASSTHROUGH** (sem alteração) |
| `Custom field (Market)` | `Mercado` | **PASSTHROUGH** |
| `Custom field (Type of Service)` | `TipoServico` | **PASSTHROUGH** |
| `Custom field (Total Amount (euros))` | `ValorEUR` | Parse número pt-BR |
| `Custom field (Budg.Loc.Currency)` | `ValorBRL` | Parse número pt-BR |
| `Custom field (Margin)` | `Margem` | Parse % → decimal (24% → 0.24) |
| `Created` | `JiraCreated` | Parse data → YYYY-MM-DD |
| `Updated` | `JiraUpdated` | Parse data → YYYY-MM-DD |
| `Custom field (Proposal Due Date)` | `PrazoProposta` | Parse data |
| `Custom field (Renewal)` | `Renewal` | Parse boolean (Yes/No → true/false) |
| `Assignee` | `Assignee` | Limite 255 caracteres |
| `Component/s` | `Cliente` | Limite 255 caracteres |
| `Custom field (Observations)` | `Observacoes` | Limite 63.999 caracteres |

### Tratamento de Campos Choice (PASSTHROUGH)

O código atual **NÃO NORMALIZA** os campos Choice. Ele apenas:
1. Remove espaços extras
2. Remove valores null/nan
3. Passa o valor **exatamente como veio do JIRA**

```python
# Código atual (linhas 1610-1632 do function_app.py)
def normalize_choice_passthrough(val):
    """Passa valor JIRA diretamente, apenas limpando NaN e whitespace"""
    if is_null_value(val):
        return None
    val_str = str(val).strip()
    return val_str if val_str else None

for field in ["Status", "Mercado", "TipoServico", ...]:
    df_clean[field] = df_clean[field].apply(normalize_choice_passthrough)
```

---

## 🔧 OPÇÃO: ATIVAR NORMALIZAÇÃO COMPLETA

Se desejar padronizar os valores automaticamente, o sistema já tem o endpoint `/normalizar-ofertas` pronto.

### Como Funciona

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Ofertas RAW    │────▶│ Azure Function   │────▶│ Ofertas         │
│  do SharePoint  │     │/normalizar-ofertas│    │ Normalizadas    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  MAPEAMENTOS     │
                        │ (SharePoint List)│
                        │                  │
                        │ "follow up" → "FollowUp"
                        │ "under study" → "Under Study"
                        │ "fs" → "FS"
                        └──────────────────┘
```

### Tabela de Mapeamentos (Exemplo)

| Campo | ValorRaw | ValorNormalizado |
|-------|----------|------------------|
| Status | under study | Under Study |
| Status | follow up | FollowUp |
| Status | follow-up | FollowUp |
| Mercado | fs | FS |
| Mercado | utilities | Utilities |
| Mercado | TELECOMUNICAÇÕES | Telco |

### Relatório de Normalização

O endpoint retorna estatísticas de normalização:
- Quantos valores foram mapeados
- Quais valores NÃO têm mapeamento (precisam ser adicionados)
- Quais mapeamentos não foram usados

---

## 🔐 OPÇÃO: EXPANDIR CHOICES NO SHAREPOINT

Se preferir manter a abordagem sem normalização, configure os campos Choice do SharePoint para aceitar valores livres:

### Configuração Atual (FillInChoice=TRUE)

| Campo | FillInChoice | Valores Aceitos |
|-------|--------------|-----------------|
| `Status` | ✅ TRUE | Qualquer valor do JIRA |
| `Mercado` | ✅ TRUE | Qualquer valor do JIRA |
| `TipoServico` | ✅ TRUE | Qualquer valor do JIRA |
| `TipoOportunidade` | ❌ FALSE | Apenas Proposal, Presale |
| `PraticaUnificada` | ✅ TRUE | Qualquer valor do JIRA |
| `StatusBudgetAlocado` | ✅ TRUE | Qualquer valor do JIRA |

### Como Verificar/Alterar no SharePoint

1. Acesse a lista `Ofertas_Pipeline`
2. Clique na engrenagem → **Configurações da lista**
3. Clique no nome do campo (ex: `Status`)
4. Marque ✅ **"Permitir escolhas de 'Preenchimento'"**
5. Salvar

---

## 📈 MÉTRICAS GERADAS (consolidar-v2)

| Métrica | Fórmula | Uso |
|---------|---------|-----|
| **Win Rate** | Won / (Won + Lost) × 100 | Taxa de sucesso |
| **Pipeline Ativo** | Soma valor ofertas em desenvolvimento | Potencial de receita |
| **Tempo de Ciclo** | DataEntrega - DataRecebimento | Eficiência do time |
| **Taxa Utilização** | HorasConsumidas / HorasAlocadas × 100 | Gestão de capacidade |
| **Valor por Prática** | Valor × (% Prática) | Contribuição por área |

---

## 📝 RESUMO EXECUTIVO

| Componente | Status | Observação |
|------------|--------|------------|
| Azure Function | ✅ Ativo | 19 endpoints |
| Importação JIRA | ✅ Ativo | Via CSV + Power Automate |
| SharePoint List | ✅ Ativo | FillInChoice=TRUE |
| Normalização | ⚠️ Disponível (não ativo) | Pode ser ativado se necessário |
| Card Teams | ✅ Ativo | Gerado pelo consolidar-v2 |
| Power BI | ✅ Ativo | Refresh via API |

### Decisões Pendentes

1. **Ativar normalização?** Se os reports apresentarem inconsistências, podemos ativar a normalização via endpoint `/normalizar-ofertas`
2. **Manter lista de mapeamentos?** Requer manutenção quando novos valores surgirem no JIRA

---

*Documento criado para stakeholders do projeto JIRA Teams PBI Integration*
