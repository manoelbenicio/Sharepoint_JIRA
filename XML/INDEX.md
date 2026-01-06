# SharePoint Schema Mapping Index

> ✅ **Validated via PnP PowerShell:** 2025-12-28

This folder contains XML schema exports for SharePoint lists used in this project.

## SharePoint Lists GUIDs

| List Name | GUID | Mapping File | Usage Notes |
|---|---|---|---|
| `Ofertas_Pipeline` | `6db5a12d-595d-4a1a-aca1-035837613815` | `sharepoint_mapping_ofertas_pipeline.xml` | ✅ Flow1, Flow3, Flow4; also `ZIP/XML/sharepoint_mapping_ofertas_pipeline.audit.md` for CSV-vs-Choice analysis. |
| `Atualizacoes_Semanais` | `172d7d29-5a3c-4608-b4ea-b5b027ef5ac0` | `ZIP/XML/sharepoint_mapping_atualizacoes_semanais.xml` | Used by Flow2 (legacy write) and Flow3 (read). |
| `ARQs_Teams` | `1ad529f7-db5b-4567-aa00-1582ff333264` | `ZIP/XML/sharepoint_mapping_arqs_teams.xml` | Used by Flow1 (read); flow export references list by name (`ARQs_Teams`). |
| `Ofertas_Pipeline_Normalizada` | `fa90b09d-5eb9-461f-bf15-64a494b00d2d` | `ZIP/XML/sharepoint_mapping_ofertas_pipeline_normalizada.xml` | Not referenced in exported flows in this repo (likely Azure Function/internal). |
| `StatusReports_Historico` | `f58b3d23-5750-4b29-b30f-a7b5421cdd80` | *(no mapping yet)* | ✅ Flow2 history |
| `StatusReports_Queue` | `12197c6e-b5d4-4bcd-96d4-c8aafc426d0a` | *(no mapping yet)* | 🆕 Flow1/Flow2 queue |
| `Budget_Extensions` | `dfeda3e0-0cc9-434d-b8d5-5b450dc071b2` | *(no mapping yet)* | ✅ Not in flows |
| `Resumo_Semanal` | `1d4a803e-9884-4e10-b932-ef9ff598f127` | `ZIP/XML/sharepoint_mapping_Resumo_Semanal.xml` | Not referenced in exported flows in this repo. |
| `Jira_Allocation_Data` | `f25edf86-f23a-41bb-a7b1-84a096df2dd8` | *(no mapping yet)* | ✅ Not in flows |

## Architecture Docs (Reference)

Deep-dive documentation lives in `ZIP/XML/ARCHITECTURE/`:

- `ZIP/XML/ARCHITECTURE/STAKEHOLDER_PROJECT_GUIDE.md`
- `ZIP/XML/ARCHITECTURE/ARCHITECTURE_DEEP_DIVE.md`
- `ZIP/XML/ARCHITECTURE/AZURE_FUNCTION_COMPLETE_MAP.md`
- `ZIP/XML/ARCHITECTURE/LOGGING_AND_DATA_CONTROL_SYSTEM.md`
