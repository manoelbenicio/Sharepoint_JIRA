# Flow6 - Tutorial Passo a Passo Completo

**Objetivo:** Criar o Flow6 - Premium Analytics do zero no Power Automate  
**Tempo Estimado:** 30-45 minutos  
**Pré-requisitos:** Conta com licença Premium do Power Automate

---

## 📍 PARTE 1: Criar o Fluxo

### Passo 1.1 - Acessar o Power Automate
1. Abra o navegador
2. Acesse: **https://make.powerautomate.com**
3. Faça login com sua conta corporativa

### Passo 1.2 - Criar Novo Fluxo
1. No menu lateral esquerdo, clique em **"Criar"** (ou "Create")
2. Na tela de opções, clique em **"Fluxo de nuvem agendado"** (Scheduled cloud flow)
3. Aparecerá uma caixa de diálogo:
   - **Nome do fluxo:** Digite `Flow6 - Premium Analytics Bi-Weekly`
   - **Executar este fluxo:** Selecione "Semana" (Week)
   - Clique no botão **"Criar"** (azul)

---

## 📍 PARTE 2: Configurar o Trigger de Recorrência

### Passo 2.1 - Configurar Recurrence
1. O trigger "Recurrence" aparecerá automaticamente na tela
2. Clique nele para expandir
3. Configure os campos:

| Campo | Valor |
|-------|-------|
| **Interval** | `1` |
| **Frequency** | `Week` |
| **Time zone** | `(UTC-03:00) Brasilia` |
| **Start time** | Deixe vazio ou coloque `2026-01-07T09:00:00Z` |
| **On these days** | Clique e marque: ☑️ Tuesday, ☑️ Friday |
| **At these hours** | `9` |
| **At these minutes** | `0` |

4. Clique fora do card para confirmar

---

## 📍 PARTE 3: Adicionar Ação HTTP GET

### Passo 3.1 - Adicionar Nova Ação
1. Clique no botão **"+ Novo passo"** (ou "+ New step") abaixo do Recurrence
2. Na caixa de pesquisa, digite: `HTTP`
3. Nos resultados, clique em **"HTTP"** (ícone azul)

### Passo 3.2 - Configurar HTTP
1. Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Method** | Selecione `GET` no dropdown |
| **URI** | `https://func-pipeline-consolidation.azurewebsites.net/api/consolidar-v2` |

2. Clique em **"Mostrar opções avançadas"** (Show advanced options)
3. Em **Headers**, clique em **"+ Adicionar novo item"**:
   - **Chave:** `x-functions-key`
   - **Valor:** `[SUA_FUNCTION_KEY_AQUI]`
4. Adicione outro header:
   - **Chave:** `Content-Type`
   - **Valor:** `application/json`

---

## 📍 PARTE 4: Parse JSON

### Passo 4.1 - Adicionar Parse JSON
1. Clique no botão **"+ Novo passo"**
2. Na caixa de pesquisa, digite: `Parse JSON`
3. Clique na ação **"Parse JSON"** (Data Operations)

### Passo 4.2 - Configurar Parse JSON
1. No campo **Content**:
   - Clique na caixa de texto
   - No painel de conteúdo dinâmico que aparece à direita, clique em **"Body"** (do HTTP)
   
2. No campo **Schema**, clique na caixa de texto e cole:

```json
{
  "type": "object",
  "properties": {
    "semana": { "type": "string" },
    "data_geracao": { "type": "string" },
    "pipeline_ativo": {
      "type": "object",
      "properties": {
        "quantidade": { "type": "integer" },
        "valor": { "type": "number" },
        "valor_formatado": { "type": "string" }
      }
    },
    "resultados_30_dias": {
      "type": "object",
      "properties": {
        "won": {
          "type": "object",
          "properties": {
            "quantidade": { "type": "integer" },
            "valor_formatado": { "type": "string" },
            "margem_media_fmt": { "type": "string" }
          }
        },
        "lost": {
          "type": "object",
          "properties": {
            "quantidade": { "type": "integer" },
            "valor_formatado": { "type": "string" }
          }
        },
        "win_rate": { "type": "number" }
      }
    },
    "budget_metricas": {
      "type": "object",
      "properties": {
        "total_arquitetos": { "type": "integer" },
        "taxa_utilizacao_global": { "type": "number" }
      }
    },
    "top_mercados_volume": { "type": "array" },
    "top_mercados_valor": { "type": "array" },
    "top_mercados_margem": { "type": "array" },
    "praticas_detalhadas": { "type": "object" }
  }
}
```

---

## 📍 PARTE 5: Compose Card 04 (ARQ Performance)

### Passo 5.1 - Adicionar Compose
1. Clique em **"+ Novo passo"**
2. Digite na pesquisa: `Compose`
3. Clique em **"Compose"** (Data Operations)

### Passo 5.2 - Renomear a Ação
1. Clique nos **três pontinhos (...)** no canto superior direito do card
2. Clique em **"Renomear"**
3. Digite: `Compose_Card_04_ARQ_Performance`
4. Pressione Enter

### Passo 5.3 - Colar o Template
1. No campo **Inputs**:
   - Abra o arquivo `TEMPLATE_04_ARQ_Performance.json`
   - Copie TODO o conteúdo JSON
   - Cole no campo Inputs

> ⚠️ **IMPORTANTE:** Você precisará substituir os placeholders `${...}` por expressões do Power Automate. Veja a seção "Substituição de Placeholders" no final.

---

## 📍 PARTE 6: Post Card 04 no Teams

### Passo 6.1 - Adicionar Ação Teams
1. Clique em **"+ Novo passo"**
2. Digite na pesquisa: `Post adaptive card`
3. Clique em **"Post adaptive card in a chat or channel"** (Microsoft Teams)

### Passo 6.2 - Configurar Conexão (se necessário)
1. Se aparecer "Criar conexão", clique em **"Entrar"**
2. Autentique com sua conta corporativa
3. Clique em **"Permitir"**

### Passo 6.3 - Configurar Post
Configure os campos na seguinte ordem:

| Campo | Valor |
|-------|-------|
| **Post as** | Selecione `Flow bot` |
| **Post in** | Selecione `Channel` |
| **Team** | Clique no dropdown e selecione seu time |
| **Channel** | Selecione `Ofertas_Analytics` |
| **Adaptive Card** | Clique na caixa, depois no painel dinâmico selecione **Outputs** do `Compose_Card_04_ARQ_Performance` |

---

## 📍 PARTE 7: Delay (2 segundos)

### Passo 7.1 - Adicionar Delay
1. Clique em **"+ Novo passo"**
2. Digite na pesquisa: `Delay`
3. Clique em **"Delay"** (Schedule)

### Passo 7.2 - Configurar Delay
| Campo | Valor |
|-------|-------|
| **Count** | `2` |
| **Unit** | `Second` |

---

## 📍 PARTE 8: Compose Card 05 (Market Analysis)

### Passo 8.1 - Adicionar Compose
1. Clique em **"+ Novo passo"**
2. Digite: `Compose`
3. Clique em **"Compose"**

### Passo 8.2 - Renomear
1. Clique nos **três pontinhos (...)**
2. Clique em **"Renomear"**
3. Digite: `Compose_Card_05_Market_Analysis`

### Passo 8.3 - Colar Template
1. Abra o arquivo `TEMPLATE_05_Market_Analysis.json`
2. Copie TODO o conteúdo
3. Cole no campo **Inputs**

---

## 📍 PARTE 9: Post Card 05 no Teams

### Passo 9.1 - Adicionar Post
1. Clique em **"+ Novo passo"**
2. Digite: `Post adaptive card`
3. Selecione **"Post adaptive card in a chat or channel"**

### Passo 9.2 - Configurar
| Campo | Valor |
|-------|-------|
| **Post as** | `Flow bot` |
| **Post in** | `Channel` |
| **Team** | (mesmo time) |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | Selecione **Outputs** do `Compose_Card_05_Market_Analysis` |

---

## 📍 PARTE 10: Delay (2 segundos)

Repita os passos 7.1 e 7.2.

---

## 📍 PARTE 11: Compose Card 06 (WoW Trends)

### Passo 11.1 - Adicionar Compose
1. Clique em **"+ Novo passo"**
2. Digite: `Compose`
3. Clique em **"Compose"**

### Passo 11.2 - Renomear
1. Renomeie para: `Compose_Card_06_WoW_Trends`

### Passo 11.3 - Colar Template
1. Abra `TEMPLATE_06_WoW_Trends.json`
2. Cole o conteúdo no campo **Inputs**

---

## 📍 PARTE 12: Post Card 06 no Teams

| Campo | Valor |
|-------|-------|
| **Post as** | `Flow bot` |
| **Post in** | `Channel` |
| **Team** | (mesmo time) |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | Selecione **Outputs** do `Compose_Card_06_WoW_Trends` |

---

## 📍 PARTE 13: Delay (2 segundos)

Repita os passos 7.1 e 7.2.

---

## 📍 PARTE 14: Compose Card 07 (Practice Analysis)

### Passo 14.1 - Adicionar Compose
1. Clique em **"+ Novo passo"**
2. Digite: `Compose`
3. Clique em **"Compose"**

### Passo 14.2 - Renomear
1. Renomeie para: `Compose_Card_07_Practice_Analysis`

### Passo 14.3 - Colar Template
1. Abra `TEMPLATE_07_Practice_Analysis.json`
2. Cole o conteúdo no campo **Inputs**

---

## 📍 PARTE 15: Post Card 07 no Teams (FINAL)

| Campo | Valor |
|-------|-------|
| **Post as** | `Flow bot` |
| **Post in** | `Channel` |
| **Team** | (mesmo time) |
| **Channel** | `Ofertas_Analytics` |
| **Adaptive Card** | Selecione **Outputs** do `Compose_Card_07_Practice_Analysis` |

---

## 📍 PARTE 16: Salvar e Testar

### Passo 16.1 - Salvar o Fluxo
1. No canto superior direito, clique no botão **"Salvar"** (Save)
2. Aguarde a mensagem "Seu fluxo está pronto"

### Passo 16.2 - Testar Manualmente
1. No canto superior direito, clique em **"Testar"** (Test)
2. Selecione **"Manualmente"**
3. Clique em **"Testar"**
4. Clique em **"Executar fluxo"** (Run flow)
5. Acompanhe a execução - cada ação ficará verde ✅ se bem-sucedida

### Passo 16.3 - Verificar no Teams
1. Abra o Microsoft Teams
2. Navegue até o canal **Ofertas_Analytics**
3. Verifique se os 4 cards apareceram

---

## 🔄 Substituição de Placeholders

Nos templates, você precisa substituir `${placeholder}` por expressões dinâmicas.

### Como Fazer:
1. No campo **Inputs** do Compose, localize o placeholder (ex: `${semana}`)
2. Delete o placeholder
3. Clique no local onde estava
4. No painel de **Conteúdo dinâmico** à direita, clique em **"Expressão"**
5. Digite a expressão e clique em **OK**

### Tabela de Expressões:

| Placeholder | Expressão Power Automate |
|-------------|--------------------------|
| `${semana}` | `body('Parse_JSON')?['semana']` |
| `${data_geracao}` | `body('Parse_JSON')?['data_geracao']` |
| `${total_arquitetos}` | `body('Parse_JSON')?['budget_metricas']?['total_arquitetos']` |
| `${utilizacao_media_pct}` | `body('Parse_JSON')?['budget_metricas']?['taxa_utilizacao_global']` |
| `${total_ofertas_ativas}` | `body('Parse_JSON')?['pipeline_ativo']?['quantidade']` |
| `${pipeline_valor_fmt}` | `body('Parse_JSON')?['pipeline_ativo']?['valor_formatado']` |
| `${won_valor_fmt}` | `body('Parse_JSON')?['resultados_30_dias']?['won']?['valor_formatado']` |
| `${win_rate}` | `body('Parse_JSON')?['resultados_30_dias']?['win_rate']` |

---

## 📋 Checklist Final

- [ ] Fluxo criado com nome correto
- [ ] Recurrence configurado para Ter/Sex 9h BRT
- [ ] HTTP GET com URL e Function Key corretos
- [ ] Parse JSON com schema completo
- [ ] 4 ações Compose com templates corretos
- [ ] 4 ações Post to Teams apontando para Ofertas_Analytics
- [ ] 3 ações Delay de 2 segundos entre posts
- [ ] Teste manual executado com sucesso
- [ ] Cards aparecem no Teams

---

## ❓ Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Connection not found" | Reconfigure a conexão do Teams |
| HTTP retorna 401 | Verifique a Function Key |
| Card não renderiza | Valide o JSON no Adaptive Card Designer |
| Fluxo falha em Parse JSON | Verifique se o schema está correto |

---

**FIM DO TUTORIAL**
