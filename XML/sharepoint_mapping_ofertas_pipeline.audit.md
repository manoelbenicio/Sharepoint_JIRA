# Audit: `sharepoint_mapping_ofertas_pipeline.xml`

Date: 2025-12-27

## What Was Checked

Cross-check between:

- SharePoint list schema in `ZIP/XML/sharepoint_mapping_ofertas_pipeline.xml`
- JIRA export sample `ZIP/JIRA PBI (JIRA Indra) 2025-12-26T05_53_47-0391.csv`
- Power Automate field usage (notably `_prod_ac_patch/flow4/.../definition.json`)

## OK (Schema vs Flows)

- List ID matches the flows’ target list: `{6DB5A12D-595D-4A1A-ACA1-035837613815}` (`Ofertas_Pipeline`)
- All fields written by Flow4 exist in the XML and have compatible types:
  - `Status`, `Mercado`, `TipoServico`, `TipoOportunidade`: `Choice` (Flow uses `item/<field>/Value`)
  - `Renewal`: `Boolean`
  - `ValorEUR`, `ValorBRL`: `Currency`
  - `Margem`, `TemporalScope`, `Est_x002e_BudgetInicio`: `Number`
  - `JiraCreated`, `JiraUpdated`, `PrazoProposta`: `DateTime`
  - `Title`, `JiraKey`, `Cliente`, `Assignee`, `CodigoGEP`, etc: `Text`

## NOT 100% (Choice Values vs CSV)

If the CSV values are imported “as-is” (PASSTHROUGH), the sample CSV contains **Choice** values that are not in the predefined choice lists.

Important nuance for the current project setup:

- In `Ofertas_Pipeline` the fields `Status`, `Mercado`, `TipoServico` are configured with `FillInChoice=TRUE`, so SharePoint should accept new/unlisted values (no import blocker; the main impact is reporting consistency).
- In `Ofertas_Pipeline_Normalizada` those same fields are `FillInChoice=FALSE`, so unlisted values would be rejected if/when you start writing into the normalized list.

### `Status` (CSV has 9 unique)

Missing in SharePoint choices:
- `Won-End`

### `Mercado` (CSV has 8 unique)

Missing in SharePoint choices:
- `Media`
- `No IT`

### `TipoServico` (CSV has 73 unique)

Missing in SharePoint choices (53 values):
- `BPO - BO`
- `BPO - FO`
- `BPO - Presale`
- `BPO BO`
- `BPO FO`
- `BPO FO&BO`
- `BPO Presales`
- `CNT - Estrategia`
- `CNT - Other`
- `CNT - Presale`
- `Cyber - Presale`
- `DIC - Arquitecture`
- `DIC - Network`
- `DIC - Other`
- `DIC - Presale`
- `DIC - Project`
- `DS - Automation & Low Code`
- `DS - Automation and RPA`
- `DS - Digital Channels`
- `DS - OneSite Platform`
- `DS - Portales Web`
- `DS - Presale`
- `DS - Testing`
- `Datos - Analytics`
- `Datos - DaM`
- `Datos - Data Modernization`
- `Datos - Data Strategy / Governance`
- `Datos - Presale`
- `GU - Field Service (FS)`
- `GU - Presale`
- `GU - Service Desk (SD)`
- `GU - Workplace (WP)`
- `OS GA`
- `OS GT`
- `OS GU`
- `OS TESTING`
- `P&A - Core TyM`
- `P&A - OSS (Sistema de suporte operativo)`
- `P&A – Media`
- `Phygital`
- `Phygital - Presale`
- `Project/Others`
- `SGE`
- `SGE - Contact Center`
- `SGE - Dynamics`
- `SGE - Presale`
- `SGE - SAP`
- `SGE - SAP Ariba`
- `SGE - SAP BTP`
- `SGE - SAP ECC`
- `SGE - SAP SuccesFactors`
- `SGE - Sales Force`
- `SGE - Soporte SAP`

## Recommended Action

Pick one approach (must match what `import-jira` outputs and where you write data):

1. **Keep PASSTHROUGH + FillInChoice=TRUE** (current): imports won’t be blocked, but reporting may fragment due to value variations.
2. **Activate normalization** (`/normalizar-ofertas`): convert to a curated set for consistent reporting (recommended for Power BI / leadership summaries).
3. **Expand choice options**: include all observed JIRA values (keeps raw fidelity, but grows choice lists and can still drift).

Note: if you keep `Won-End` as-is, Flow1’s status-color logic should treat `won-end` as “Good” (same as `won`).
