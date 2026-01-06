# 📊 SISTEMA DE LOGGING E CONTROLE DE INCONSISTÊNCIAS
## Azure Function - Monitoramento de Dados JIRA → SharePoint

**Versão:** 1.0  
**Data:** 2025-12-27  
**Tipo:** Documentação Técnica Detalhada

---

## 🎯 OBJETIVO DO SISTEMA

O sistema de logging foi desenvolvido para:

1. **Detectar mudanças no JIRA** → Novos campos, campos removidos, novos valores em Choice fields
2. **Rastrear qualidade dos dados** → Campos nulos, valores inválidos, inconsistências
3. **Gerar relatórios** → Estatísticas detalhadas por campo para auditoria
4. **Facilitar troubleshooting** → Logs contextualizados em cada etapa

---

## 📦 COMPONENTES DO SISTEMA

### 1. Logging de Execução (Python `logging`)
### 2. Relatório de Campos Choice (`choices_report`)
### 3. Contagem de Nulos (`null_counts`)
### 4. Detecção de Campos Ausentes (`campos_ausentes`)
### 5. Relatório de Normalização (`relatorio`)

---

## 📋 DETALHAMENTO: `/import-jira`

### Fluxo de Logging

```python
# ETAPA 1: Início
logging.info("Iniciando importação JIRA...")

# ETAPA 2: Recebimento de dados
logging.info("Recebido CSV bruto (%s caracteres)", len(csv_content))
# OU
logging.info("Recebido JSON array com %s ofertas", len(ofertas_jira))

# ETAPA 3: Parse do CSV
logging.info('Separador detectado: "%s"', sep)  # ";" ou ","
logging.info("CSV parseado: %s linhas, colunas: %s...", len(df), list(df.columns)[:5])

# ETAPA 4: Transformações (por campo)
logging.info("Campo %s: %s valores convertidos", campo, count)

# ETAPA 5: Validação de JiraKey
logging.error("JiraKey não encontrado ou todos vazios!")  # Se falhar
logging.error("Coluna JiraKey não existe no DataFrame!")  # Se falhar

# ETAPA 6: Estatísticas finais
logging.info("Estatísticas de campos null após limpeza: %s", null_counts_dict)
logging.info("Import JIRA concluído: %s ofertas processadas", total)

# ERRO: Qualquer exceção
logging.error("Erro no import JIRA: %s", str(e))
```

---

## 📊 ESTRUTURA DO `choices_report`

### O que é?
Relatório completo de todos os valores encontrados em campos Choice, permitindo detectar:
- Novos valores que o JIRA está enviando
- Valores com erros de digitação
- Distribuição de valores por campo

### Estrutura JSON

```json
{
  "choices_report": {
    "Status": {
      "total": 1954,
      "nulos": 12,
      "unicos": 9,
      "valores": [
        {"valor": "Under Study", "quantidade": 450},
        {"valor": "On Offer", "quantidade": 380},
        {"valor": "Won", "quantidade": 285},
        {"valor": "Lost", "quantidade": 120},
        {"valor": "FollowUp", "quantidade": 95},
        {"valor": "Presale", "quantidade": 82},
        {"valor": "Cancelled", "quantidade": 45},
        {"valor": "Rejected", "quantidade": 35},
        {"valor": "Abandoned", "quantidade": 12},
        {"valor": null, "quantidade": 12}
      ]
    },
    "Mercado": {
      "total": 1954,
      "nulos": 5,
      "unicos": 8,
      "valores": [
        {"valor": "FS", "quantidade": 520},
        {"valor": "Telco", "quantidade": 410},
        {"valor": "Energy", "quantidade": 380},
        {"valor": "Industry", "quantidade": 290},
        {"valor": "PA", "quantidade": 180},
        {"valor": "APyS", "quantidade": 95},
        {"valor": "TyM", "quantidade": 74},
        {"valor": null, "quantidade": 5}
      ]
    },
    "TipoServico": {...},
    "TipoOportunidade": {...},
    "PraticaUnificada": {...},
    "StatusBudgetAlocado": {...}
  }
}
```

### Código que Gera (Linhas 1724-1750)

```python
choices_report = {}
for field in [
    "Status",
    "Mercado",
    "TipoServico",
    "TipoOportunidade",
    "PraticaUnificada",
    "StatusBudgetAlocado",
]:
    if field in df_clean.columns:
        series = df_clean[field]
        counts = series.value_counts(dropna=False)
        valores = []
        for val, count in counts.items():
            if pd.isna(val):
                clean_val = None
            else:
                clean_val = val
            valores.append(
                {"valor": to_native(clean_val), "quantidade": int(count)}
            )
        choices_report[field] = {
            "total": int(series.shape[0]),      # Total de registros
            "nulos": int(series.isna().sum()),  # Quantos estão vazios
            "unicos": int(series.dropna().nunique()),  # Valores distintos
            "valores": valores,                 # Lista com cada valor e contagem
        }
```

### Como Interpretar

| Campo | Significado | Ação se Anormal |
|-------|-------------|-----------------|
| `total` | Total de ofertas processadas | Deve bater com o total geral |
| `nulos` | Ofertas sem valor neste campo | Verificar se JIRA está preenchido |
| `unicos` | Quantidade de valores distintos | Se aumentar, pode ter novos valores |
| `valores` | Lista de cada valor + contagem | Verificar se há valores novos/errados |

### Alertas Automáticos

| Condição | Alerta |
|----------|--------|
| `unicos` aumentou desde último import | 🔶 Novo valor detectado |
| `nulos` > 10% do total | 🔴 Campo com muitos vazios |
| Valor com quantidade 1 | 🔶 Possível erro de digitação |
| Valor não reconhecido | 🔴 Precisa adicionar ao mapeamento |

---

## 📊 ESTRUTURA DO `null_counts`

### O que é?
Contagem de campos nulos/vazios após todas as transformações, para **todos** os campos (não apenas Choice).

### Estrutura JSON

```json
{
  "null_counts": {
    "JiraKey": 0,
    "Status": 12,
    "Mercado": 5,
    "ValorEUR": 45,
    "ValorBRL": 890,
    "Margem": 1200,
    "PrazoProposta": 67,
    "Assignee": 23,
    "Cliente": 8,
    "TipoServico": 15,
    "TipoOportunidade": 1800,
    "JiraCreated": 0,
    "JiraUpdated": 0,
    "Observacoes": 1890,
    "Renewal": 1950
  }
}
```

### Código que Gera (Linhas 1720-1722)

```python
null_counts = df_clean.isna().sum()
null_counts_dict = {k: int(v) for k, v in null_counts.to_dict().items()}
logging.info("Estatísticas de campos null após limpeza: %s", null_counts_dict)
```

### Como Interpretar

| Campo com nulos | Nível | Ação |
|-----------------|-------|------|
| `JiraKey` = 0 | ✅ OK | Obrigatório, nunca pode ter nulo |
| `ValorBRL` alto | ⚠️ Normal | Muitas ofertas não têm valor BRL |
| `Margem` alto | ⚠️ Normal | Nem todas ofertas têm margem |
| `Status` > 0 | 🔴 Crítico | Verificar JIRA - status é obrigatório |
| `Mercado` > 0 | 🔶 Atenção | Verificar com KAMs |

---

## 📊 ESTRUTURA DO `campos_ausentes`

### O que é?
Lista de campos que estavam no mapeamento JIRA→SharePoint mas **não foram encontrados no CSV**.

### Estrutura JSON

```json
{
  "campos_ausentes": [
    "CodigoGEP",
    "TemporalScope",
    "DNManager"
  ]
}
```

### Código que Gera (Linhas 1763-1765)

```python
campos_ausentes = [
    col for col in column_mapping.values() if col not in df_clean.columns
]
```

### Como Interpretar

| Situação | Significado | Ação |
|----------|-------------|------|
| Lista vazia | ✅ Todos os campos esperados estão no CSV | - |
| Campo novo na lista | 🔶 JIRA removeu esse campo ou mudou o nome | Verificar export JIRA |
| Muitos campos | 🔴 Possível erro no export JIRA | Verificar filtro/colunas |

---

## 📋 DETALHAMENTO: `/normalizar-ofertas`

### O que é?
Endpoint que normaliza valores RAW aplicando mapeamento de-para.

### Relatório Gerado

```json
{
  "success": true,
  "unmapped_value": "UNMAPPED/OUTROS",
  "ofertas_normalizadas": [...],
  "relatorio": {
    "total_processado": 1954,
    "campos_choice": ["Status", "Mercado", "TipoServico", ...],
    "normalizacao": {
      "Status": {
        "total": 1954,
        "nulos": 12,
        "mapeados": 1890,
        "nao_mapeados": 52,
        "valores_nao_mapeados": [
          {"valor": "follow up", "quantidade": 25},
          {"valor": "under study", "quantidade": 15},
          {"valor": "follow-up", "quantidade": 12}
        ],
        "valores_mapeados": [
          {"valor": "Under Study", "quantidade": 450},
          {"valor": "On Offer", "quantidade": 380},
          {"valor": "FollowUp", "quantidade": 320}
        ]
      },
      "Mercado": {...}
    },
    "mapeamentos_nao_usados": {
      "Status": ["Aborted", "Draft"],
      "Mercado": ["Sanidad", "Defensa"]
    }
  }
}
```

### Campos do Relatório

| Campo | Descrição |
|-------|-----------|
| `total` | Total de registros processados |
| `nulos` | Registros com valor nulo (ignorados) |
| `mapeados` | Registros que foram normalizados com sucesso |
| `nao_mapeados` | Registros que não têm mapeamento (ficaram como `unmapped_value`) |
| `valores_nao_mapeados` | Lista de valores sem mapeamento + contagem |
| `valores_mapeados` | Lista de valores após normalização + contagem |
| `mapeamentos_nao_usados` | Mapeamentos configurados mas não utilizados (orphan) |

### Código que Gera (Linhas 1873-1950)

```python
# Inicializa contadores
relatorio = {}
for field in campos_choice:
    relatorio[field] = {
        "total": 0,
        "nulos": 0,
        "mapeados": 0,
        "nao_mapeados": 0,
        "valores_nao_mapeados": {},
        "valores_mapeados": {},
    }

# Para cada oferta, para cada campo
for rec in df_raw.to_dict("records"):
    for field in campos_choice:
        relatorio[field]["total"] += 1
        raw_val = rec.get(field)
        raw_key = normalize_value(raw_val)
        
        if raw_key is None:
            relatorio[field]["nulos"] += 1
        elif raw_key in mapping_by_field.get(field, {}):
            relatorio[field]["mapeados"] += 1
            # ... registra qual valor foi mapeado
        else:
            relatorio[field]["nao_mapeados"] += 1
            # ... registra valor sem mapeamento

# Detecta mapeamentos não usados
mapeamentos_nao_usados = {}
for field, mapping in mapping_by_field.items():
    unused = [k for k in mapping.keys() if k not in used_mapping_keys[field]]
    if unused:
        mapeamentos_nao_usados[field] = unused
```

### Como Interpretar

| Métrica | Nível | Ação |
|---------|-------|------|
| `nao_mapeados` = 0 | ✅ Perfeito | Todos valores foram normalizados |
| `nao_mapeados` < 5% | 🟡 OK | Alguns valores novos, adicionar ao mapeamento |
| `nao_mapeados` > 10% | 🔴 Crítico | JIRA mudou muitos valores, atualizar mapeamento urgente |
| `mapeamentos_nao_usados` tem itens | 🔶 Atenção | Mapeamentos órfãos, podem ser removidos |

---

## 📊 PAYLOAD COMPLETO DE RESPOSTA

### `/import-jira` - Exemplo Real

```json
{
  "success": true,
  "ofertas": [
    {
      "JiraKey": "OFBRA-1234",
      "Status": "Under Study",
      "Mercado": "FS",
      "ValorEUR": 125000.50,
      "ValorBRL": 750000.00,
      "Margem": 0.24,
      "...": "..."
    }
  ],
  "estatisticas": {
    "total_processado": 1954,
    "valor_eur_total": 45678900.50,
    "valor_brl_total": 285000000.00,
    "arquivo": "ofertas_2025-12-27.csv",
    "data_processamento": "2025-12-27T10:30:45.123456",
    
    "campos_ausentes": [],
    
    "null_counts": {
      "JiraKey": 0,
      "Status": 12,
      "Mercado": 5,
      "ValorEUR": 45,
      "...": "..."
    },
    
    "choices_report": {
      "Status": {
        "total": 1954,
        "nulos": 12,
        "unicos": 9,
        "valores": [
          {"valor": "Under Study", "quantidade": 450},
          {"valor": "On Offer", "quantidade": 380},
          "..."
        ]
      },
      "Mercado": {...},
      "TipoServico": {...}
    }
  }
}
```

---

## 🔔 INTEGRAÇÃO COM ALERTAS

### Power Automate - Detectar Anomalias

```
CONDIÇÃO 1: Novos valores em Choice
IF choices_report.Status.unicos > 9  // (valor esperado)
THEN Email de alerta "Novo valor detectado em Status"

CONDIÇÃO 2: Muitos nulos
IF null_counts.Status > (total * 0.05)
THEN Email de alerta "5%+ das ofertas sem Status"

CONDIÇÃO 3: Campos faltando
IF length(campos_ausentes) > 0
THEN Email de alerta "Campos removidos do JIRA: {campos_ausentes}"
```

### Exemplo de Flow de Alerta

```
┌────────────────────┐
│ Trigger: HTTP      │
│ (após /import-jira)│
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────┐
│ Parse JSON              │
│ estatisticas            │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ Condition:              │ SIM │ Send Email              │
│ campos_ausentes.length  ├────▶│ "Campos removidos!"     │
│       > 0               │     │ Lista: campos_ausentes  │
└─────────┬───────────────┘     └─────────────────────────┘
          │ NÃO
          ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ Condition:              │ SIM │ Send Email              │
│ choices_report.Status   ├────▶│ "Novos valores Status!" │
│   .unicos > ultimo_valor│     │ Lista: valores novos    │
└─────────┬───────────────┘     └─────────────────────────┘
          │ NÃO
          ▼
┌─────────────────────────┐
│ Continua normalmente    │
└─────────────────────────┘
```

---

## 📝 RESUMO DE AÇÕES POR ALERTA

| Situação | Log/Campo | Ação Recomendada |
|----------|-----------|------------------|
| Novo valor em Choice | `choices_report.*.valores` | Adicionar ao mapeamento ou verificar se é erro |
| Campo removido do CSV | `campos_ausentes` | Verificar export JIRA, atualizar mapeamento |
| Muitos nulos | `null_counts.*` alto | Verificar preenchimento no JIRA |
| Valor com 1 ocorrência | `valores.quantidade = 1` | Provavelmente erro de digitação |
| Mapeamento órfão | `mapeamentos_nao_usados` | JIRA parou de usar esse valor, considerar remover |
| JiraKey vazio | `logging.error` | CSV corrompido ou filtro errado |
| Parse CSV falhou | `logging.error` | Separador errado ou encoding |

---

## 🔧 CONFIGURAÇÃO DO LOGGING (host.json)

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    },
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Information",
      "Host.Aggregator": "Trace"
    }
  }
}
```

### Níveis de Log Usados

| Nível | Quando | Exemplo |
|-------|--------|---------|
| `INFO` | Operações normais | "Import JIRA concluído: 1954 ofertas" |
| `WARNING` | Algo inesperado mas tratável | "Texto truncado para 255 caracteres" |
| `ERROR` | Falha que impede operação | "JiraKey não encontrado!" |

---

## 📊 MONITORAMENTO NO AZURE

Os logs são enviados automaticamente para **Application Insights** (se configurado).

### Queries KQL Úteis

```kql
// Erros nos últimos 7 dias
traces
| where timestamp > ago(7d)
| where severityLevel == 3  // Error
| where message contains "import" or message contains "JIRA"
| project timestamp, message

// Quantidade de ofertas processadas por dia
traces
| where timestamp > ago(30d)
| where message contains "ofertas processadas"
| parse message with * ": " count:int " ofertas processadas"
| summarize sum(count) by bin(timestamp, 1d)

// Campos com muitos nulos
traces
| where message contains "Estatísticas de campos null"
| extend null_stats = parse_json(extract('\\{.*\\}', 0, message))
```

---

*Sistema de Logging e Controle de Inconsistências v1.0*  
*Azure Function - JIRA Teams PBI Integration*
