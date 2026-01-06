# Flow3 - Ready-to-Paste Adaptive Cards

**Purpose**: Copy-paste ready compact JSONs for Power Automate Flow3 (C-Level Weekly Flash Report)  
**Templates**: `TEMPLATE_01_Executive_OnePager.json` + `TEMPLATE_02_Weekly_Flash_Report_CLevel.json`  
**Created**: 2026-01-06  
**Status**: Ready for use - 2 Cards

---

## ⚠️ IMPORTANT - Placeholder Replacement

These cards use `${placeholder}` syntax. In Power Automate:
1. **Paste** the JSON into the "Adaptive Card" field of the Teams action
2. **Replace** each `${placeholder}` with dynamic content from "Analisar JSON" output

---

## 📊 CARD 1: Executive OnePager (TEMPLATE_01)

**Paste into**: First "Post card in a chat or channel" action

```json
{"$schema":"http://adaptivecards.io/schemas/adaptive-card.json","type":"AdaptiveCard","version":"1.5","body":[{"type":"Container","style":"emphasis","bleed":true,"minHeight":"50px","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"◆","size":"Large","color":"Accent","weight":"Bolder"}],"verticalContentAlignment":"Center"},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"EXECUTIVE PIPELINE BRIEFING","weight":"Bolder","size":"Large","color":"Accent","spacing":"None"},{"type":"TextBlock","text":"ARCHITECTURE & SOLUTIONS DIVISION","size":"Small","isSubtle":true,"spacing":"None","weight":"Lighter"}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"${semana_numero}","weight":"Bolder","size":"ExtraLarge","color":"Accent"},{"type":"TextBlock","text":"${ano}","size":"Small","isSubtle":true,"spacing":"None","horizontalAlignment":"Center"}],"verticalContentAlignment":"Center"}]}]},{"type":"Container","spacing":"Medium","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"1","style":"emphasis","items":[{"type":"TextBlock","text":"TOTAL PIPELINE","size":"Small","weight":"Bolder","color":"Accent","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${valor_pipeline_formatado}","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center","spacing":"Small"},{"type":"TextBlock","text":"${delta_pipeline} vs LW","size":"Small","color":"Good","horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"WIN RATE YTD","size":"Small","weight":"Bolder","horizontalAlignment":"Center","isSubtle":true},{"type":"TextBlock","text":"${win_rate}%","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center","color":"Good","spacing":"Small"},{"type":"TextBlock","text":"Target: 35%","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"OPPORTUNITIES","size":"Small","weight":"Bolder","horizontalAlignment":"Center","isSubtle":true},{"type":"TextBlock","text":"${total_ofertas}","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center","spacing":"Small"},{"type":"TextBlock","text":"+${novas_ofertas} new","size":"Small","color":"Good","horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"AVG MARGIN","size":"Small","weight":"Bolder","horizontalAlignment":"Center","isSubtle":true},{"type":"TextBlock","text":"${margem_media}%","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center","spacing":"Small"},{"type":"TextBlock","text":"Target: 28%","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]}]}]},{"type":"Container","separator":true,"spacing":"Medium","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"📊 PIPELINE BREAKDOWN","weight":"Bolder","size":"Small","color":"Accent"},{"type":"FactSet","spacing":"Small","facts":[{"title":"📝 Under Study","value":"${under_study_count} offers • ${under_study_valor}"},{"title":"📤 On Offer","value":"${on_offer_count} offers • ${on_offer_valor}"},{"title":"📋 Follow-up","value":"${followup_count} offers • ${followup_valor}"},{"title":"✅ Won","value":"${won_count} offers • ${won_valor}"},{"title":"❌ Lost","value":"${lost_count} offers • ${lost_valor}"}]}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"🔝 TOP 5 HIGH-VALUE DEALS","weight":"Bolder","size":"Small","color":"Accent"},{"type":"FactSet","spacing":"Small","facts":[{"title":"1","value":"${top1_titulo} • ${top1_valor}"},{"title":"2","value":"${top2_titulo} • ${top2_valor}"},{"title":"3","value":"${top3_titulo} • ${top3_valor}"},{"title":"4","value":"${top4_titulo} • ${top4_valor}"},{"title":"5","value":"${top5_titulo} • ${top5_valor}"}]}]}]}]},{"type":"Container","separator":true,"spacing":"Small","items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"⚡ MINSAIT","size":"Small","weight":"Bolder","color":"Accent"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"Architecture & Solutions Division","size":"Small","isSubtle":true}]},{"type":"Column","width":"auto","items":[{"type":"TextBlock","text":"${data_geracao}","size":"Small","isSubtle":true}]}]}]}],"msteams":{"width":"Full"}}
```

---

## 📊 CARD 2: C-Level Weekly Flash Report (TEMPLATE_02_CLevel)

**Paste into**: Second "Post card in a chat or channel" action (with 2-second delay)

```json
{"$schema":"http://adaptivecards.io/schemas/adaptive-card.json","type":"AdaptiveCard","version":"1.4","body":[{"type":"Container","style":"emphasis","bleed":true,"items":[{"type":"ColumnSet","columns":[{"type":"Column","width":"auto","verticalContentAlignment":"Center","items":[{"type":"TextBlock","text":"⚡","size":"ExtraLarge","weight":"Bolder"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":"WEEKLY FLASH REPORT","weight":"Bolder","size":"Large","wrap":true,"color":"Accent"},{"type":"TextBlock","text":"Architecture & Solutions | ${semana}","size":"Small","wrap":true,"isSubtle":true,"spacing":"None"}]},{"type":"Column","width":"auto","horizontalAlignment":"Right","items":[{"type":"TextBlock","text":"🏢 Minsait","size":"Small","isSubtle":true}],"verticalContentAlignment":"Center"}]}]},{"type":"TextBlock","text":"📊 NUMBERS AT A GLANCE","weight":"Bolder","size":"Medium","separator":true,"spacing":"Large"},{"type":"ColumnSet","columns":[{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"PIPELINE","size":"Small","isSubtle":true,"horizontalAlignment":"Center","weight":"Bolder"},{"type":"TextBlock","text":"${valor_pipeline_formatado}","weight":"Bolder","size":"ExtraLarge","color":"Accent","horizontalAlignment":"Center"},{"type":"TextBlock","text":"${total_ofertas} offers","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"ACTIVE","size":"Small","isSubtle":true,"horizontalAlignment":"Center","weight":"Bolder"},{"type":"TextBlock","text":"${ofertas_ativas}","weight":"Bolder","size":"ExtraLarge","color":"Good","horizontalAlignment":"Center"},{"type":"TextBlock","text":"in dev","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"CLOSED","size":"Small","isSubtle":true,"horizontalAlignment":"Center","weight":"Bolder"},{"type":"TextBlock","text":"${ofertas_fechadas}","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center"},{"type":"TextBlock","text":"this week","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"WIN RATE","size":"Small","isSubtle":true,"horizontalAlignment":"Center","weight":"Bolder"},{"type":"TextBlock","text":"${win_rate}%","weight":"Bolder","size":"ExtraLarge","color":"Good","horizontalAlignment":"Center"},{"type":"TextBlock","text":"30 days","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]},{"type":"Column","width":"1","items":[{"type":"TextBlock","text":"MARGIN","size":"Small","isSubtle":true,"horizontalAlignment":"Center","weight":"Bolder"},{"type":"TextBlock","text":"${margem_media}%","weight":"Bolder","size":"ExtraLarge","horizontalAlignment":"Center"},{"type":"TextBlock","text":"average","size":"Small","isSubtle":true,"horizontalAlignment":"Center","spacing":"None"}]}]},{"type":"Container","separator":true,"spacing":"Medium","style":"emphasis","items":[{"type":"TextBlock","text":"📈 ARCHITECT UTILIZATION","weight":"Bolder","size":"Small"},{"type":"TextBlock","text":"Responded: ${arqs_responderam} / ${total_arqs} architects (${taxa_resposta}%)","size":"Small","isSubtle":true,"spacing":"Small"}]},{"type":"Container","separator":true,"spacing":"Small","items":[{"type":"TextBlock","text":"Generated: ${data_geracao}","size":"Small","isSubtle":true,"horizontalAlignment":"Center"}]}],"msteams":{"width":"Full"}}
```

---

## 📋 Placeholder Reference Map

### Template 01 - Executive OnePager

| Placeholder | Dynamic Content Path |
|-------------|---------------------|
| `${semana_numero}` | `body('Analisar_JSON')?['semana_referencia']` |
| `${ano}` | `2026` or dynamic |
| `${valor_pipeline_formatado}` | `body('Analisar_JSON')?['pipeline']?['valor_total_formatado']` |
| `${delta_pipeline}` | `body('Analisar_JSON')?['pipeline']?['delta_semanal']` |
| `${win_rate}` | `body('Analisar_JSON')?['metricas']?['win_rate_30d']` |
| `${total_ofertas}` | `body('Analisar_JSON')?['pipeline']?['total_ofertas']` |
| `${margem_media}` | `body('Analisar_JSON')?['metricas']?['margem_media']` |
| `${top1_titulo}` | `body('Analisar_JSON')?['top_ofertas']?[0]?['titulo']` |
| `${data_geracao}` | `body('Analisar_JSON')?['data_geracao']` |

### Template 02 - C-Level Flash Report

| Placeholder | Dynamic Content Path |
|-------------|---------------------|
| `${semana}` | `body('Analisar_JSON')?['semana_referencia']` |
| `${valor_pipeline_formatado}` | `body('Analisar_JSON')?['pipeline']?['valor_total_formatado']` |
| `${total_ofertas}` | `body('Analisar_JSON')?['pipeline']?['total_ofertas']` |
| `${ofertas_ativas}` | `body('Analisar_JSON')?['pipeline']?['ofertas_ativas']` |
| `${ofertas_fechadas}` | `body('Analisar_JSON')?['resultados_30_dias']?['won']?['quantidade']` |
| `${win_rate}` | `body('Analisar_JSON')?['resultados_30_dias']?['win_rate']` |
| `${margem_media}` | `body('Analisar_JSON')?['resultados_30_dias']?['won']?['margem_media']` |
| `${arqs_responderam}` | `body('Analisar_JSON')?['arquitetos']?['responderam']` |
| `${total_arqs}` | `body('Analisar_JSON')?['arquitetos']?['total']` |
| `${taxa_resposta}` | `body('Analisar_JSON')?['arquitetos']?['taxa_resposta']` |
| `${data_geracao}` | `body('Analisar_JSON')?['data_geracao']` |

---

## ✅ How to Use

1. **Copy** CARD 1 JSON → Paste into first Teams action
2. **Add 2-second delay** between cards
3. **Copy** CARD 2 JSON → Paste into second Teams action
4. **Replace** all `${placeholder}` with dynamic content
5. **Save** and test

---

## 📚 Related Documentation

- **Flow3 Spec**: [FLOW3_CLEVEL_WEEKLY_SPEC.md](./FLOW3_CLEVEL_WEEKLY_SPEC.md)
- **Azure Function**: `consolidar-v2` endpoint
- **Channel**: `Ofertas_Status_Report_Semanal`
