# Adaptive Card Manual Test Guide

**Suite 3 Tests for Manual Execution**

---

## A1-A2: Baseline Tests

Open Teams → Workflows chat → Find any recent card

### A1: Header Verification
✅ **PASS if** card shows:
- JiraKey (e.g., "OFBRA-4100")
- Title (project name)
- Semana (e.g., "Week 1/2026", "01/01/2026 21:09")

### A2: Controls Verification
✅ **PASS if** all visible:
- [ ] Status do Projeto radio buttons (Verde, Amarelo, Vermelho)
- [ ] Status Atual da Oferta dropdown
- [ ] Probabilidade de Ganho dropdown
- [ ] Observações text area
- [ ] Risks & Opportunities section (Abrir/Editar)
- [ ] Decision/Ask section (Abrir/Editar)
- [ ] "Enviar Status Report" button

---

## C1-C4: StatusProjeto Validation

### C1: Verde + Obs Empty → ✅ Should ALLOW

1. Select: 🟢 Verde - Sem problemas
2. Leave Observações EMPTY
3. Fill required dropdowns
4. Click "Enviar Status Report"
5. **Expected:** Submission accepted

### C2: Amarelo + Obs Empty → ✅ Should ALLOW

1. Select: 🟡 Amarelo - Atenção necessária
2. Leave Observações EMPTY
3. Fill required dropdowns
4. Click "Enviar Status Report"
5. **Expected:** Submission accepted

### C3: Vermelho + Obs Empty → ❌ Should REJECT

1. Select: 🔴 Vermelho - Crítico
2. Leave Observações EMPTY
3. Fill required dropdowns
4. Click "Enviar Status Report"
5. **Expected:** Error/warning message requiring observation

### C4: Vermelho + Obs Filled → ✅ Should ALLOW

1. Select: 🔴 Vermelho - Crítico
2. Type in Observações: "Teste validação vermelho"
3. Fill required dropdowns
4. Click "Enviar Status Report"
5. **Expected:** Submission accepted

---

## D1-D4: TipoOportunidade Validation

### D1: Tipo=Oferta + RFP Empty → ✅ Should ALLOW

1. Select Status Atual: anything NOT RFI/RFQ
2. Leave RFP field empty
3. Click Submit
4. **Expected:** Allowed

### D2: Tipo=RFI + RFP Empty → ❌ Should REJECT

1. Select Status Atual: RFI
2. Leave RFP field EMPTY
3. Click Submit
4. **Expected:** Error requiring RFP

### D3: Tipo=RFQ + RFP Empty → ❌ Should REJECT

1. Select Status Atual: RFQ
2. Leave RFP field EMPTY
3. Click Submit
4. **Expected:** Error requiring RFP

### D4: Tipo=RFI/RFQ + RFP Filled → ✅ Should ALLOW

1. Select Status Atual: RFI or RFQ
2. Fill RFP field with any text
3. Click Submit
4. **Expected:** Allowed

---

## Recording Results

After each test, mark in E2E_TEST_EXECUTION_TRACKER.md:
- ✅ Pass / ❌ Fail
- Timestamp
- Notes/Evidence
