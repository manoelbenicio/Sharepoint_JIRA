# Flow5 - Ready-to-Paste Adaptive Cards

**Purpose**: Copy-paste ready compact JSONs for Power Automate Flow5 (Post Weekly Flash Report)  
**Templates**: `TEMPLATE_02_Weekly_Flash_Report.json` + `TEMPLATE_03_RAG_Matrix.json`  
**Created**: 2026-01-06  
**Status**: Ready for use

---

## ⚠️ IMPORTANT - Placeholder Replacement

These cards use `${placeholder}` syntax. In Power Automate:
1. **Paste** the JSON into the "Adaptive Card" field of the Teams action
2. **Replace** each `${placeholder}` with dynamic content from "Analisar JSON" output

---

## 📊 CARD 1: Weekly Flash Report (TEMPLATE_02)

**Paste into**: First "Post card in a chat or channel" action

```json
{"$schema":"http://adaptivecards.io/schemas/adaptive-card.json","type":"AdaptiveCard","version":"1.5","body":[{"type":"Container","style":"emphasis","bleed":true,"items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"⚡","size":"ExtraLarge"}],"verticalContentAlignment":"Center"},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"WEEKLY FLASH","weight":"Bolder","size":"Large","color":"Accent","spacing":"None"},{"type":"TextBlock","text":"30-Second Executive Brief • ${semana}","size":"Small","isSubtle":true,"spacing":"None"}]},{"type":"Column","width":"auto","items":[{"type":"Container","style":"good","items":[{"type":"TextBlock","text":" ON TRACK ","weight":"Bolder","size":"Small","horizontalAlignment":"Center"}]}],"verticalContentAlignment":"Center"}]}]},{"type":"Container","spacing":"Medium","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"1","style":"emphasis","items":[{"type":"TextBlock","text":"${valor_pipeline_formatado}","weight":"Bolder","size":"ExtraLarge","color":"Accent","horizontalAlignment":"Center"},{"type":"TextBlock","text":"PIPELINE","size":"Small","horizontalAlignment":"Center","spacing":"None","weight":"Bolder"},{"type":"TextBlock","text":"${total_ofertas} opportunities","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${ofertas_ativas}","weight":"Bolder","size":"ExtraLarge","color":"Good","horizontalAlignment":"Center"},{"type":"TextBlock","text":"ACTIVE","size":"Small","horizontalAlignment":"Center","spacing":"None","weight":"Bolder"},{"type":"TextBlock","text":"in development","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${ofertas_fechadas}","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center"},{"type":"TextBlock","text":"CLOSED","size":"Small","horizontalAlignment":"Center","spacing":"None","weight":"Bolder"},{"type":"TextBlock","text":"this week","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${win_rate}%","weight":"Bolder","size":"ExtraLarge","color":"Good","horizontalAlignment":"Center"},{"type":"TextBlock","text":"WIN RATE","size":"Small","horizontalAlignment":"Center","spacing":"None","weight":"Bolder"},{"type":"TextBlock","text":"YTD average","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${margem_media}%","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center"},{"type":"TextBlock","text":"MARGIN","size":"Small","horizontalAlignment":"Center","spacing":"None","weight":"Bolder"},{"type":"TextBlock","text":"avg gross","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","style":"good","items":[{"type":"TextBlock","text":"🏆 THIS WEEK'S WINS","weight":"Bolder","size":"Small"},{"type":"ColumnSet","spacing":"Small","columns":[{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"**${won_1_titulo}** • ${won_1_valor}","size":"Small"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"**${won_2_titulo}** • ${won_2_valor}","size":"Small"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","style":"warning","items":[{"type":"TextBlock","text":"⚠️ ATTENTION REQUIRED","weight":"Bolder","size":"Small"},{"type":"TextBlock","text":"• **${alert_1_titulo}** - ${alert_1_descricao}","size":"Small","wrap":true,"spacing":"Small"},{"type":"TextBlock","text":"• **${alert_2_titulo}** - ${alert_2_descricao}","size":"Small","wrap":true,"spacing":"None"}]},{"type":"Container","separator":true,"spacing":"Small","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"⚡ MINSAIT","size":"Small","weight":"Bolder","color":"Accent"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"Architecture & Solutions","size":"Small","isSubtle":true}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"${data_geracao}","size":"Small","isSubtle":true}]}]}]}],"msteams":{"width":"Full"}}
```

---

## 📊 CARD 2: RAG Matrix (TEMPLATE_03)

**Paste into**: Second "Post card in a chat or channel" action (with 2-second delay)

```json
{"$schema":"http://adaptivecards.io/schemas/adaptive-card.json","type":"AdaptiveCard","version":"1.5","body":[{"type":"Container","style":"emphasis","bleed":true,"items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"📊","size":"ExtraLarge"}],"verticalContentAlignment":"Center"},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"RAG MATRIX REPORT","weight":"Bolder","size":"Large","color":"Accent","spacing":"None"},{"type":"TextBlock","text":"Performance KPIs & Risk Assessment • ${semana}","size":"Small","isSubtle":true,"spacing":"None"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","items":[{"type":"TextBlock","text":"📈 KPI SCORECARD","weight":"Bolder","size":"Medium","color":"Accent"},{"type":"ColumnSet","columns":[{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"KPI","weight":"Bolder","size":"Small","isSubtle":true}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"Current","weight":"Bolder","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"Trend","weight":"Bolder","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"Delta","weight":"Bolder","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"Target","weight":"Bolder","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]}]},{"type":"ColumnSet","columns":[{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"Pipeline Value","size":"Small"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${valor_pipeline_formatado}","size":"Small","weight":"Bolder","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${pipeline_trend}","size":"Small","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${pipeline_delta}","size":"Small","color":"Good","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${pipeline_target}","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]}]},{"type":"ColumnSet","columns":[{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"Win Rate","size":"Small"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${win_rate}%","size":"Small","weight":"Bolder","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${win_rate_trend}","size":"Small","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${win_rate_delta}","size":"Small","color":"Good","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"35%","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]}]},{"type":"ColumnSet","columns":[{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"Average Margin","size":"Small"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${margem_media}%","size":"Small","weight":"Bolder","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${margin_trend}","size":"Small","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${margin_delta}","size":"Small","horizontalAlignment":"Center"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"28%","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","style":"attention","items":[{"type":"TextBlock","text":"🔴 OFFERS REQUIRING ATTENTION","weight":"Bolder","size":"Small"},{"type":"ColumnSet","spacing":"Small","columns":[{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"JIRA","weight":"Bolder","size":"Small","isSubtle":true}]},{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"OFFER","weight":"Bolder","size":"Small","isSubtle":true}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"VALUE","weight":"Bolder","size":"Small","isSubtle":true,"horizontalAlignment":"Right"}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"RAG","weight":"Bolder","size":"Small","isSubtle":true}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"ISSUE","weight":"Bolder","size":"Small","isSubtle":true}]}]},{"type":"ColumnSet","columns":[{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_1_jira}","size":"Small"}]},{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"${rag_1_titulo}","size":"Small","weight":"Bolder"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_1_valor}","size":"Small","horizontalAlignment":"Right"}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"🔴","size":"Small"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_1_issue}","size":"Small","color":"Attention"}]}]},{"type":"ColumnSet","columns":[{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_2_jira}","size":"Small"}]},{"type":"Column","width":"2","items":[{"type":"TextBlock","text":"${rag_2_titulo}","size":"Small","weight":"Bolder"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_2_valor}","size":"Small","horizontalAlignment":"Right"}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"🟡","size":"Small"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"${rag_2_issue}","size":"Small","color":"Warning"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","items":[{"type":"TextBlock","text":"📈 WEEK-OVER-WEEK DELTA","weight":"Bolder","size":"Small","color":"Accent"},{"type":"ColumnSet","spacing":"Small","columns":[{"type":"Column","width":"1","style":"good","items":[{"type":"TextBlock","text":"✅ WON","weight":"Bolder","size":"Small","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${won_count} offers","size":"Medium","weight":"Bolder","horizontalAlignment":"Center","spacing":"None"},{"type":"TextBlock","text":"${won_valor}","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","style":"attention","items":[{"type":"TextBlock","text":"❌ LOST","weight":"Bolder","size":"Small","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${lost_count} offers","size":"Medium","weight":"Bolder","horizontalAlignment":"Center","spacing":"None"},{"type":"TextBlock","text":"${lost_valor}","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","style":"accent","items":[{"type":"TextBlock","text":"🆕 NEW","weight":"Bolder","size":"Small","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${new_count} offers","size":"Medium","weight":"Bolder","horizontalAlignment":"Center","spacing":"None"},{"type":"TextBlock","text":"${new_valor}","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","style":"warning","items":[{"type":"TextBlock","text":"⏰ DUE <7d","weight":"Bolder","size":"Small","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${due_count} offers","size":"Medium","weight":"Bolder","horizontalAlignment":"Center","spacing":"None"},{"type":"TextBlock","text":"${due_valor} at risk","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]}]}]},{"type":"Container","separator":true,"spacing":"Small","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"⚡ MINSAIT","size":"Small","weight":"Bolder","color":"Accent"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"Legend: 📈 Improving • ➡️ Stable • 📉 Declining","size":"Small","isSubtle":true}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"${data_geracao}","size":"Small","isSubtle":true}]}]}]}],"msteams":{"width":"Full"}}
```

---

## 📋 Placeholder Reference Map

### Template 02 - Weekly Flash Report

| Placeholder | Dynamic Content Path |
|-------------|---------------------|
| `${semana}` | `body('Analisar_JSON')?['semana_referencia']` |
| `${valor_pipeline_formatado}` | `body('Analisar_JSON')?['pipeline']?['valor_total_formatado']` |
| `${total_ofertas}` | `body('Analisar_JSON')?['pipeline']?['total_ofertas']` |
| `${ofertas_ativas}` | `body('Analisar_JSON')?['pipeline']?['ofertas_ativas']` |
| `${ofertas_fechadas}` | `body('Analisar_JSON')?['resultados_7_dias']?['won']?['quantidade']` |
| `${win_rate}` | `body('Analisar_JSON')?['metricas']?['win_rate_30d']` |
| `${margem_media}` | `body('Analisar_JSON')?['metricas']?['margem_media']` |
| `${won_1_titulo}` | `body('Analisar_JSON')?['resultados_7_dias']?['won']?[0]?['titulo']` |
| `${won_1_valor}` | `body('Analisar_JSON')?['resultados_7_dias']?['won']?[0]?['valor_formatado']` |
| `${data_geracao}` | `body('Analisar_JSON')?['data_geracao']` |

### Template 03 - RAG Matrix

| Placeholder | Dynamic Content Path |
|-------------|---------------------|
| `${rag_1_jira}` | `body('Analisar_JSON')?['alertas']?[0]?['jira_key']` |
| `${rag_1_titulo}` | `body('Analisar_JSON')?['alertas']?[0]?['titulo']` |
| `${rag_1_valor}` | `body('Analisar_JSON')?['alertas']?[0]?['valor_formatado']` |
| `${rag_1_issue}` | `body('Analisar_JSON')?['alertas']?[0]?['issue']` |
| `${won_count}` | `body('Analisar_JSON')?['resultados_7_dias']?['won']?['quantidade']` |
| `${lost_count}` | `body('Analisar_JSON')?['resultados_7_dias']?['lost']?['quantidade']` |
| `${new_count}` | `body('Analisar_JSON')?['resultados_7_dias']?['new']?['quantidade']` |

---

## ✅ How to Use

1. **Copy** CARD 1 JSON → Paste into first Teams action
2. **Add 2-second delay** between cards
3. **Copy** CARD 2 JSON → Paste into second Teams action
4. **Replace** all `${placeholder}` with dynamic content
5. **Save** and test

---

## 📚 Related Documentation

- **Flow5 Channel**: `Ofertas_Status_Report_Semanal`
- **Azure Function**: `consolidar-v2`
