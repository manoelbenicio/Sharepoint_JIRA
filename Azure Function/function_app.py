import azure.functions as func
import pandas as pd
import numpy as np
import json
import logging
import re
import os
import html
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, date

app = func.FunctionApp()

NULL_LIKE = {"nan", "none", "null", "n/a", "na", "#n/a", "", " ", "-", "--", "undefined"}


def is_null_like(val):
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    if isinstance(val, str) and val.strip().lower() in NULL_LIKE:
        return True
    return False


def parse_number(val, default=0.0):
    if is_null_like(val):
        return default
    if isinstance(val, (int, float, np.integer, np.floating)) and not pd.isna(val):
        return float(val)

    s = str(val).strip()
    if not s:
        return default

    s = s.replace("R$", "").replace("€", "").replace("$", "")
    s = s.replace("\u00a0", " ").replace(" ", "")

    has_dot = "." in s
    has_comma = "," in s
    if has_dot and has_comma:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_comma and not has_dot:
        s = s.replace(",", ".")

    s = re.sub(r"[^0-9.\-]", "", s)
    if s in ("", "-", ".", "-."):
        return default
    try:
        return float(s)
    except ValueError:
        return default


def to_native(val):
    if val is None:
        return None
    if isinstance(val, float) and pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.floating, np.bool_)):
        return val.item()
    if isinstance(val, np.str_):
        return str(val)
    if isinstance(val, (pd.Timestamp, datetime, date)):
        return val.isoformat()
    return val


def to_native_obj(obj):
    if isinstance(obj, dict):
        return {k: to_native_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_native_obj(v) for v in obj]
    return to_native(obj)


def extract_choice_value(val):
    if is_null_like(val):
        return None
    if isinstance(val, dict):
        for key in ("Value", "value", "Title", "Name", "DisplayName", "label", "Label"):
            if key in val and not is_null_like(val[key]):
                return extract_choice_value(val[key])
        return json.dumps(val, ensure_ascii=False, sort_keys=True)
    if isinstance(val, list):
        if not val:
            return None
        extracted = []
        for item in val:
            cleaned = extract_choice_value(item)
            if not is_null_like(cleaned):
                extracted.append(str(cleaned))
        return ", ".join(extracted) if extracted else None
    if isinstance(val, str):
        cleaned = val.strip()
        return cleaned if cleaned else None
    return val


def normalize_frame(df):
    if df is None or df.empty:
        return df
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(extract_choice_value)
    return df


@app.route(route="consolidar", auth_level=func.AuthLevel.FUNCTION)
def consolidar_pipeline(req: func.HttpRequest) -> func.HttpResponse:
    """
    Recebe dados do SharePoint e retorna métricas agregadas para o report C-Level.
    TOLERANTE: Funciona mesmo com ofertas ou atualizações vazias.
    IDEMPOTENTE: Pode rodar múltiplas vezes no dia sem problemas.
    """
    logging.info("Iniciando consolidação do pipeline...")

    try:
        # Recebe dados do Power Automate
        req_body = req.get_json()
        ofertas = req_body.get("ofertas", [])
        atualizacoes = req_body.get("atualizacoes", [])

        # Converte para DataFrame
        df_ofertas = pd.DataFrame(ofertas) if ofertas else pd.DataFrame()
        df_atualizacoes = pd.DataFrame(atualizacoes) if atualizacoes else pd.DataFrame()
        df_ofertas = normalize_frame(df_ofertas)
        df_atualizacoes = normalize_frame(df_atualizacoes)

        # Semana atual
        semana = datetime.now().strftime("%Y-W%V")
        data_geracao = datetime.now().isoformat()

        # ===== CASO 1: Nenhum dado recebido =====
        if df_ofertas.empty and df_atualizacoes.empty:
            resultado = {
                "semana": semana,
                "status": "sem_dados",
                "mensagem": "Nenhum dado recebido (ofertas e atualizações vazias)",
                "total_ofertas": 0,
                "total_atualizacoes": 0,
                "valor_total": 0.0,
                "taxa_resposta": 0.0,
                "total_arquitetos": 0,
                "arquitetos_responderam": 0,
                "pipeline_por_fase": [],
                "top_mercados": [],
                "top_arquitetos": [],
                "data_geracao": data_geracao,
            }
            logging.info("Consolidação: Nenhum dado recebido")
            resultado = to_native_obj(resultado)
            return func.HttpResponse(
                json.dumps(resultado, ensure_ascii=False),
                status_code=200,
                mimetype="application/json",
            )

        # ===== CASO 2: Apenas atualizações (sem ofertas) =====
        if df_ofertas.empty:
            # Gerar métricas baseadas apenas nas atualizações
            arq_col = next(
                (
                    c
                    for c in df_atualizacoes.columns
                    if "arquiteto" in c.lower() or "nome" in c.lower()
                ),
                None,
            )
            if arq_col:
                df_atualizacoes[arq_col] = df_atualizacoes[arq_col].apply(extract_choice_value)
                total_arqs = df_atualizacoes[arq_col].nunique()
            else:
                total_arqs = 0

            # Contar RAG status
            rag_col = next(
                (
                    c
                    for c in df_atualizacoes.columns
                    if "rag" in c.lower() or "status" in c.lower()
                ),
                None,
            )
            rag_stats = []
            if rag_col:
                df_atualizacoes[rag_col] = df_atualizacoes[rag_col].apply(extract_choice_value)
                rag_counts = df_atualizacoes[rag_col].value_counts()
                rag_stats = [
                    {"status": str(k), "quantidade": int(v)}
                    for k, v in rag_counts.items()
                ]

            resultado = {
                "semana": semana,
                "status": "apenas_atualizacoes",
                "mensagem": (
                    f"Processado com {len(df_atualizacoes)} atualizações "
                    "(sem dados de ofertas do pipeline)"
                ),
                "total_ofertas": 0,
                "total_atualizacoes": len(df_atualizacoes),
                "valor_total": 0.0,
                "taxa_resposta": 100.0,  # Todos que têm atualização "responderam"
                "total_arquitetos": int(total_arqs),
                "arquitetos_responderam": int(total_arqs),
                "pipeline_por_fase": [],
                "rag_distribution": rag_stats,
                "top_mercados": [],
                "top_arquitetos": [],
                "data_geracao": data_geracao,
            }
            logging.info(
                "Consolidação (apenas atualizações): %s registros",
                len(df_atualizacoes),
            )
            resultado = to_native_obj(resultado)
            return func.HttpResponse(
                json.dumps(resultado, ensure_ascii=False),
                status_code=200,
                mimetype="application/json",
            )

        # ===== CASO 3: Processamento completo (com ofertas) =====

        # Total geral
        total_ofertas = len(df_ofertas)

        # Valor total (se existir coluna de valor)
        valor_col = None
        if "ValorEUR" in df_ofertas.columns:
            valor_col = "ValorEUR"
        elif "ValorBRL" in df_ofertas.columns:
            valor_col = "ValorBRL"
        else:
            valor_col = next(
                (c for c in df_ofertas.columns if "amount" in c.lower() or "valor" in c.lower()),
                None,
            )
        if valor_col and valor_col in df_ofertas.columns:
            df_ofertas[valor_col] = df_ofertas[valor_col].apply(parse_number)
            valor_total = float(df_ofertas[valor_col].sum())
        else:
            valor_total = 0.0

        # Pipeline por fase (Status)
        status_col = (
            "Status"
            if "Status" in df_ofertas.columns
            else (df_ofertas.columns[3] if len(df_ofertas.columns) > 3 else df_ofertas.columns[0])
        )
        if status_col in df_ofertas.columns:
            df_ofertas[status_col] = df_ofertas[status_col].apply(extract_choice_value)

        # Agregar por status - contagem e valor
        if valor_col and valor_col in df_ofertas.columns:
            pipeline_por_fase = (
                df_ofertas.groupby(status_col)
                .agg(quantidade=(status_col, "count"), valor=(valor_col, "sum"))
                .reset_index()
            )
            pipeline_por_fase = pipeline_por_fase.rename(columns={status_col: "fase"})
        else:
            pipeline_por_fase = (
                df_ofertas.groupby(status_col).size().reset_index(name="quantidade")
            )
            pipeline_por_fase = pipeline_por_fase.rename(columns={status_col: "fase"})
            pipeline_por_fase["valor"] = 0

        # Top 5 Mercados
        market_col = next(
            (c for c in df_ofertas.columns if "market" in c.lower() or "mercado" in c.lower()),
            None,
        )
        top_mercados = []
        if market_col:
            df_ofertas[market_col] = df_ofertas[market_col].apply(extract_choice_value)
            if valor_col:
                top_mercados = (
                    df_ofertas.groupby(market_col)[valor_col]
                    .sum()
                    .nlargest(5)
                    .reset_index()
                )
                top_mercados.columns = ["mercado", "valor"]
            else:
                top_mercados = df_ofertas[market_col].value_counts().head(5).reset_index()
                top_mercados.columns = ["mercado", "quantidade"]
            top_mercados = top_mercados.to_dict("records")

        # Top 5 Arquitetos
        assignee_col = next((c for c in df_ofertas.columns if "assignee" in c.lower()), None)
        top_arquitetos = []
        if assignee_col:
            df_ofertas[assignee_col] = df_ofertas[assignee_col].apply(extract_choice_value)
            top_arquitetos = df_ofertas[assignee_col].value_counts().head(5).reset_index()
            top_arquitetos.columns = ["arquiteto", "projetos"]
            top_arquitetos = top_arquitetos.to_dict("records")

        # Taxa de resposta (se tiver atualizações)
        taxa_resposta = 0.0
        total_arquitetos = 0
        arquitetos_responderam = 0
        if not df_atualizacoes.empty and assignee_col:
            total_arquitetos = df_ofertas[assignee_col].nunique()
            arq_col_upd = next(
                (
                    c
                    for c in df_atualizacoes.columns
                    if "arquiteto" in c.lower() or "nome" in c.lower()
                ),
                None,
            )
            if arq_col_upd:
                df_atualizacoes[arq_col_upd] = df_atualizacoes[arq_col_upd].apply(
                    extract_choice_value
                )
                arquitetos_responderam = df_atualizacoes[arq_col_upd].nunique()
                taxa_resposta = (
                    round((arquitetos_responderam / total_arquitetos) * 100, 1)
                    if total_arquitetos > 0
                    else 0.0
                )

        # ===== RESULTADO COMPLETO =====
        resultado = {
            "semana": semana,
            "status": "sucesso",
            "mensagem": (
                f"Consolidação completa: {total_ofertas} ofertas, "
                f"{len(df_atualizacoes)} atualizações"
            ),
            "total_ofertas": int(total_ofertas),
            "total_atualizacoes": len(df_atualizacoes),
            "valor_total": float(valor_total),
            "taxa_resposta": float(taxa_resposta),
            "total_arquitetos": int(total_arquitetos),
            "arquitetos_responderam": int(arquitetos_responderam),
            "pipeline_por_fase": pipeline_por_fase.to_dict("records"),
            "top_mercados": top_mercados,
            "top_arquitetos": top_arquitetos,
            "data_geracao": data_geracao,
        }

        logging.info(
            "Consolidação concluída: %s ofertas, %s atualizações",
            total_ofertas,
            len(df_atualizacoes),
        )

        resultado = to_native_obj(resultado)
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Erro na consolidação: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "erro"}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    resultado = {"status": "healthy", "timestamp": datetime.now().isoformat()}
    resultado = to_native_obj(resultado)
    return func.HttpResponse(
        json.dumps(resultado, ensure_ascii=False),
        status_code=200,
        mimetype="application/json",
    )


# =============================================================================
# CONSOLIDAÇÃO V2 - CARD C-LEVEL PROFISSIONAL
# =============================================================================

def format_brl(value):
    """Formata valor em Real brasileiro: R$ 1.234.567,89"""
    if value is None or pd.isna(value):
        return "R$ 0,00"
    try:
        num = float(value)
        # Formatar com separador de milhares e vírgula decimal
        formatted = f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ 0,00"


def parse_date_safe(val):
    """Parse seguro de data, retorna None se inválido"""
    if is_null_like(val):
        return None
    try:
        if isinstance(val, (datetime, date)):
            return val if isinstance(val, datetime) else datetime.combine(val, datetime.min.time())
        dt = pd.to_datetime(val, errors="coerce", dayfirst=True)
        return dt.to_pydatetime() if pd.notna(dt) else None
    except Exception:
        return None


# Status categories for business logic (atualizado 2025-12-25 per business requirements)
# 1. Em Desenvolvimento = Arquiteto trabalhando na proposta
STATUS_EM_DESENVOLVIMENTO = {"Under Study", "On Offer", "Proposal", "Presale", 
                             "under study", "on offer", "proposal", "presale"}

# 2. Entregue (KAM/Clientes) = Proposta enviada, aguardando resposta
STATUS_ENTREGUE = {"Follow-up", "FollowUp", "Delivered", 
                   "follow-up", "followup", "delivered"}

# 3. Ganhas = Cliente aceitou a proposta
STATUS_WON = {"Won", "Won-End", "won", "won-end"}

# 4. Perdidas = Cliente rejeitou ou perdemos para concorrente
STATUS_LOST = {"Lost", "Rejected", "lost", "rejected"}

# 5. Canceladas = Cliente abandonou, sem resposta por 60-90 dias, ou cancelada por KAM/DN
STATUS_CANCELADAS = {"Cancelled", "Abandoned", "cancelled", "abandoned"}


@app.route(route="consolidar-v2", auth_level=func.AuthLevel.FUNCTION)
def consolidar_pipeline_v2(req: func.HttpRequest) -> func.HttpResponse:
    """
    Consolidação V2 - Card C-Level Profissional
    
    Retorna métricas detalhadas com visão temporal:
    - Pipeline ativo (em desenvolvimento)
    - Entregas da semana (últimos 7 dias) com range de datas
    - Agenda próxima semana (próximos 7 dias) com range de datas
    - Resultados 7 e 30 dias (Won/Lost) com margens
    - Top 5 mercados e arquitetos (por valor e quantidade)
    - Top 5 ofertas com maiores/menores margens
    - Lista de arquitetos pendentes
    - Card HTML formatado para Teams
    """
    logging.info("Iniciando consolidação V2 C-Level...")
    
    try:
        from datetime import timedelta
        
        req_body = req.get_json()
        ofertas = req_body.get("ofertas", [])
        atualizacoes = req_body.get("atualizacoes", [])
        
        df_ofertas = pd.DataFrame(ofertas) if ofertas else pd.DataFrame()
        df_atualizacoes = pd.DataFrame(atualizacoes) if atualizacoes else pd.DataFrame()
        df_ofertas = normalize_frame(df_ofertas)
        df_atualizacoes = normalize_frame(df_atualizacoes)
        
        # Datas de referência
        hoje = datetime.now()
        semana = hoje.strftime("%Y-W%V")
        data_geracao = hoje.strftime("%d/%b/%Y às %H:%M")
        
        ha_7_dias = hoje - timedelta(days=7)
        ha_15_dias = hoje - timedelta(days=15)
        ha_30_dias = hoje - timedelta(days=30)
        em_7_dias = hoje + timedelta(days=7)
        
        # Formatar ranges de data para os títulos
        range_7_dias = f"{ha_7_dias.strftime('%d/%m')} a {hoje.strftime('%d/%m/%Y')}"
        range_15_dias = f"{ha_15_dias.strftime('%d/%m')} a {hoje.strftime('%d/%m/%Y')}"
        range_30_dias = f"{ha_30_dias.strftime('%d/%m')} a {hoje.strftime('%d/%m/%Y')}"
        range_semana_atual = range_7_dias
        range_proxima_semana = f"{hoje.strftime('%d/%m')} a {em_7_dias.strftime('%d/%m/%Y')}"
        
        # Resultado base para caso sem dados
        resultado_base = {
            "semana": semana,
            "data_geracao": data_geracao,
            "status": "sem_dados",
            "total_ofertas_recebidas": 0,
        }
        
        if df_ofertas.empty:
            resultado_base["mensagem"] = "Nenhuma oferta recebida"
            return func.HttpResponse(
                json.dumps(to_native_obj(resultado_base), ensure_ascii=False),
                status_code=200,
                mimetype="application/json",
            )
        
        # Identificar colunas
        status_col = "Status" if "Status" in df_ofertas.columns else None
        valor_col = next((c for c in ["ValorBRL", "ValorEUR", "Amount", "ValorTotal_Potencial"] if c in df_ofertas.columns), None)
        prazo_col = next((c for c in ["PrazoProposta", "Prazo", "DueDate", "DataPrazoEntrega"] if c in df_ofertas.columns), None)
        updated_col = next((c for c in ["JiraUpdated", "Updated", "ModifiedDate"] if c in df_ofertas.columns), None)
        assignee_col = next((c for c in ["Assignee", "Arquiteto", "Owner", "ArquitetoPresales"] if c in df_ofertas.columns), None)
        mercado_col = next((c for c in ["Mercado", "Market", "Sector"] if c in df_ofertas.columns), None)
        jirakey_col = next((c for c in ["JiraKey", "Key", "Title"] if c in df_ofertas.columns), None)
        margem_col = next((c for c in ["Margem", "Margin", "GrossMargin", "MargemBrutaPct"] if c in df_ofertas.columns), None)
        
        # Colunas para tempo de ciclo
        data_recebimento_col = next((c for c in ["DataRecebimentoRFP", "Created", "CreatedDate"] if c in df_ofertas.columns), None)
        data_entrega_col = next((c for c in ["DataEntregaKAM", "DeliveredDate"] if c in df_ofertas.columns), None)
        
        # Colunas para Budget de Horas
        budget_col = next((c for c in ["Est.BudgetInicio", "BudgetHoras", "HorasAlocadas", "EstBudgetInicio"] if c in df_ofertas.columns), None)
        horas_consumidas_col = next((c for c in ["HorasConsumidas", "HorasUsadas", "HorasTrabalhadas"] if c in df_ofertas.columns), None)
        
        # Colunas para Práticas (percentuais)
        pct_ds_col = next((c for c in ["%DS", "PctDS", "PercentDS"] if c in df_ofertas.columns), None)
        pct_dic_col = next((c for c in ["%DIC", "PctDIC", "PercentDIC"] if c in df_ofertas.columns), None)
        pct_dados_col = next((c for c in ["%Dados/IA", "PctDados", "PercentDadosIA", "%DadosIA"] if c in df_ofertas.columns), None)
        pct_cyber_col = next((c for c in ["%Cyber", "PctCyber", "PercentCyber"] if c in df_ofertas.columns), None)
        pct_sge_col = next((c for c in ["%SGE", "PctSGE", "PercentSGE"] if c in df_ofertas.columns), None)
        pct_outros_col = next((c for c in ["%Outros", "PctOutros", "PercentOutros"] if c in df_ofertas.columns), None)
        pratica_col = next((c for c in ["PraticaUnificada", "Pratica", "Practice"] if c in df_ofertas.columns), None)
        
        # Parse de valores e datas
        if valor_col:
            df_ofertas["_valor"] = df_ofertas[valor_col].apply(parse_number)
        else:
            df_ofertas["_valor"] = 0.0
            
        if prazo_col:
            df_ofertas["_prazo"] = df_ofertas[prazo_col].apply(parse_date_safe)
        else:
            df_ofertas["_prazo"] = None
            
        if updated_col:
            df_ofertas["_updated"] = df_ofertas[updated_col].apply(parse_date_safe)
        else:
            df_ofertas["_updated"] = None
        
        # Parse margem - já vem como percentual (0-100)
        if margem_col:
            df_ofertas["_margem"] = df_ofertas[margem_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_margem"] = 0.0
        
        # Parse datas para tempo de ciclo
        if data_recebimento_col:
            df_ofertas["_data_recebimento"] = df_ofertas[data_recebimento_col].apply(parse_date_safe)
        else:
            df_ofertas["_data_recebimento"] = None
            
        if data_entrega_col:
            df_ofertas["_data_entrega"] = df_ofertas[data_entrega_col].apply(parse_date_safe)
        else:
            df_ofertas["_data_entrega"] = None
        
        # Parse Budget de Horas
        if budget_col:
            df_ofertas["_budget_horas"] = df_ofertas[budget_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_budget_horas"] = 0.0
            
        if horas_consumidas_col:
            df_ofertas["_horas_consumidas"] = df_ofertas[horas_consumidas_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_horas_consumidas"] = 0.0
        
        # Parse percentuais de Práticas
        if pct_ds_col:
            df_ofertas["_pct_ds"] = df_ofertas[pct_ds_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_ds"] = 0.0
            
        if pct_dic_col:
            df_ofertas["_pct_dic"] = df_ofertas[pct_dic_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_dic"] = 0.0
            
        if pct_dados_col:
            df_ofertas["_pct_dados"] = df_ofertas[pct_dados_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_dados"] = 0.0
            
        if pct_cyber_col:
            df_ofertas["_pct_cyber"] = df_ofertas[pct_cyber_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_cyber"] = 0.0
            
        if pct_sge_col:
            df_ofertas["_pct_sge"] = df_ofertas[pct_sge_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_sge"] = 0.0
            
        if pct_outros_col:
            df_ofertas["_pct_outros"] = df_ofertas[pct_outros_col].apply(lambda x: parse_number(x, default=0.0))
        else:
            df_ofertas["_pct_outros"] = 0.0
        
        # Calcular dias de ciclo (data_entrega - data_recebimento)
        def calc_dias_ciclo(row):
            if row["_data_recebimento"] and row["_data_entrega"]:
                try:
                    delta = row["_data_entrega"] - row["_data_recebimento"]
                    return max(0, delta.days)
                except:
                    pass
            return None
        
        df_ofertas["_dias_ciclo"] = df_ofertas.apply(calc_dias_ciclo, axis=1)
        
        # Normalizar status para categorização
        if status_col:
            df_ofertas["_status_clean"] = df_ofertas[status_col].apply(
                lambda x: str(x).strip() if not is_null_like(x) else ""
            )
        else:
            df_ofertas["_status_clean"] = ""
        
        # ===== CATEGORIZAR OFERTAS =====
        def categorize(status):
            s = str(status).strip().lower() if status else ""
            if any(st.lower() == s for st in STATUS_EM_DESENVOLVIMENTO):
                return "desenvolvimento"
            elif any(st.lower() == s for st in STATUS_ENTREGUE):
                return "entregue"
            elif any(st.lower() == s for st in STATUS_WON):
                return "won"
            elif any(st.lower() == s for st in STATUS_LOST):
                return "lost"
            elif any(st.lower() == s for st in STATUS_CANCELADAS):
                return "canceladas"
            return "outro"
        
        df_ofertas["_categoria"] = df_ofertas["_status_clean"].apply(categorize)
        
        # ===== 1. PIPELINE ATIVO (Em Desenvolvimento) =====
        df_dev = df_ofertas[df_ofertas["_categoria"] == "desenvolvimento"]
        pipeline_ativo = {
            "quantidade": len(df_dev),
            "valor": float(df_dev["_valor"].sum()),
            "valor_formatado": format_brl(df_dev["_valor"].sum()),
            "status_incluidos": list(STATUS_EM_DESENVOLVIMENTO)[:2]
        }
        
        # ===== 2. ENTREGAS DESTA SEMANA (últimos 7 dias) =====
        df_entregue = df_ofertas[df_ofertas["_categoria"] == "entregue"]
        if updated_col:
            df_entregue_semana = df_entregue[
                df_entregue["_updated"].apply(lambda x: x is not None and x >= ha_7_dias)
            ]
        else:
            df_entregue_semana = pd.DataFrame()
        
        entregas_semana = {
            "quantidade": len(df_entregue_semana),
            "valor": float(df_entregue_semana["_valor"].sum()) if len(df_entregue_semana) > 0 else 0.0,
            "valor_formatado": format_brl(df_entregue_semana["_valor"].sum() if len(df_entregue_semana) > 0 else 0),
            "periodo": "últimos 7 dias",
            "range_datas": range_semana_atual
        }
        
        # ===== 3. AGENDA PRÓXIMA SEMANA (próximos 7 dias) =====
        if prazo_col:
            df_proxima = df_ofertas[
                (df_ofertas["_categoria"] == "desenvolvimento") &
                (df_ofertas["_prazo"].apply(lambda x: x is not None and hoje <= x <= em_7_dias))
            ]
            em_2_dias = hoje + timedelta(days=2)
            df_urgentes = df_ofertas[
                (df_ofertas["_categoria"] == "desenvolvimento") &
                (df_ofertas["_prazo"].apply(lambda x: x is not None and hoje <= x <= em_2_dias))
            ]
            lista_urgentes = df_urgentes[jirakey_col].tolist()[:5] if jirakey_col and len(df_urgentes) > 0 else []
        else:
            df_proxima = pd.DataFrame()
            df_urgentes = pd.DataFrame()
            lista_urgentes = []
        
        # Criar lista detalhada das ofertas da próxima semana
        lista_ofertas_proxima = []
        if len(df_proxima) > 0 and jirakey_col:
            for _, row in df_proxima.iterrows():
                oferta_info = {
                    "jira_key": str(row[jirakey_col]) if jirakey_col else "N/A",
                    "arquiteto": str(row[assignee_col]) if assignee_col and assignee_col in row else "N/A",
                    "prazo": row["_prazo"].strftime("%d/%m") if row["_prazo"] else "N/A",
                    "valor": float(row["_valor"]) if row["_valor"] else 0.0,
                    "valor_formatado": format_brl(row["_valor"])
                }
                lista_ofertas_proxima.append(oferta_info)
        
        agenda_proxima_semana = {
            "quantidade": len(df_proxima),
            "valor": float(df_proxima["_valor"].sum()) if len(df_proxima) > 0 else 0.0,
            "valor_formatado": format_brl(df_proxima["_valor"].sum() if len(df_proxima) > 0 else 0),
            "urgentes": len(df_urgentes),
            "lista_urgentes": lista_urgentes,
            "range_datas": range_proxima_semana,
            "lista_ofertas": lista_ofertas_proxima[:20]  # Limitar a 20 ofertas
        }
        
        # ===== 4. RESULTADOS 7 DIAS =====
        df_won_7d = df_ofertas[
            (df_ofertas["_categoria"] == "won") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_7_dias))
        ] if updated_col else pd.DataFrame()
        
        df_lost_7d = df_ofertas[
            (df_ofertas["_categoria"] == "lost") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_7_dias))
        ] if updated_col else pd.DataFrame()
        
        resultados_7_dias = {
            "won": {
                "quantidade": len(df_won_7d),
                "valor": float(df_won_7d["_valor"].sum()) if len(df_won_7d) > 0 else 0.0,
                "valor_formatado": format_brl(df_won_7d["_valor"].sum() if len(df_won_7d) > 0 else 0)
            },
            "lost": {
                "quantidade": len(df_lost_7d),
                "valor": float(df_lost_7d["_valor"].sum()) if len(df_lost_7d) > 0 else 0.0,
                "valor_formatado": format_brl(df_lost_7d["_valor"].sum() if len(df_lost_7d) > 0 else 0)
            },
            "periodo": "últimos 7 dias",
            "range_datas": range_7_dias
        }
        
        # ===== 4B. RESULTADOS 15 DIAS =====
        df_won_15d = df_ofertas[
            (df_ofertas["_categoria"] == "won") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_15_dias))
        ] if updated_col else pd.DataFrame()
        
        df_lost_15d = df_ofertas[
            (df_ofertas["_categoria"] == "lost") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_15_dias))
        ] if updated_col else pd.DataFrame()
        
        # Win Rate 15 dias usando JiraKey único para evitar duplicatas
        if jirakey_col:
            won_unique_15d = df_won_15d[jirakey_col].nunique() if len(df_won_15d) > 0 else 0
            lost_unique_15d = df_lost_15d[jirakey_col].nunique() if len(df_lost_15d) > 0 else 0
        else:
            won_unique_15d = len(df_won_15d)
            lost_unique_15d = len(df_lost_15d)
        
        total_fechadas_15d = won_unique_15d + lost_unique_15d
        win_rate_15d = round((won_unique_15d / total_fechadas_15d) * 100, 1) if total_fechadas_15d > 0 else 0.0
        
        resultados_15_dias = {
            "won": {
                "quantidade": won_unique_15d,
                "valor": float(df_won_15d["_valor"].sum()) if len(df_won_15d) > 0 else 0.0,
                "valor_formatado": format_brl(df_won_15d["_valor"].sum() if len(df_won_15d) > 0 else 0)
            },
            "lost": {
                "quantidade": lost_unique_15d,
                "valor": float(df_lost_15d["_valor"].sum()) if len(df_lost_15d) > 0 else 0.0,
                "valor_formatado": format_brl(df_lost_15d["_valor"].sum() if len(df_lost_15d) > 0 else 0)
            },
            "win_rate": win_rate_15d,
            "win_rate_fmt": f"{win_rate_15d}%",
            "periodo": "últimos 15 dias",
            "range_datas": range_15_dias
        }
        
        # ===== 5. RESULTADOS 30 DIAS COM MARGENS =====
        df_won_30d = df_ofertas[
            (df_ofertas["_categoria"] == "won") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_30_dias))
        ] if updated_col else df_ofertas[df_ofertas["_categoria"] == "won"]
        
        df_lost_30d = df_ofertas[
            (df_ofertas["_categoria"] == "lost") &
            (df_ofertas["_updated"].apply(lambda x: x is not None and x >= ha_30_dias))
        ] if updated_col else df_ofertas[df_ofertas["_categoria"] == "lost"]
        
        # Win Rate 30 dias usando JiraKey único para evitar duplicatas
        if jirakey_col:
            won_unique_30d = df_won_30d[jirakey_col].nunique() if len(df_won_30d) > 0 else 0
            lost_unique_30d = df_lost_30d[jirakey_col].nunique() if len(df_lost_30d) > 0 else 0
        else:
            won_unique_30d = len(df_won_30d)
            lost_unique_30d = len(df_lost_30d)
        
        total_fechadas_30d = won_unique_30d + lost_unique_30d
        win_rate_30d = round((won_unique_30d / total_fechadas_30d) * 100, 1) if total_fechadas_30d > 0 else 0.0
        
        # Calcular margens médias (margem já vem como percentual 0-100)
        margem_media_won = round(df_won_30d["_margem"].mean(), 1) if len(df_won_30d) > 0 and margem_col else 0.0
        margem_media_lost = round(df_lost_30d["_margem"].mean(), 1) if len(df_lost_30d) > 0 and margem_col else 0.0
        
        resultados_30_dias = {
            "won": {
                "quantidade": len(df_won_30d),
                "valor": float(df_won_30d["_valor"].sum()) if len(df_won_30d) > 0 else 0.0,
                "valor_formatado": format_brl(df_won_30d["_valor"].sum() if len(df_won_30d) > 0 else 0),
                "margem_media": margem_media_won,
                "margem_media_fmt": f"{margem_media_won}%"
            },
            "lost": {
                "quantidade": lost_unique_30d,
                "valor": float(df_lost_30d["_valor"].sum()) if len(df_lost_30d) > 0 else 0.0,
                "valor_formatado": format_brl(df_lost_30d["_valor"].sum() if len(df_lost_30d) > 0 else 0),
                "margem_media": margem_media_lost,
                "margem_media_fmt": f"{margem_media_lost}%"
            },
            "win_rate": win_rate_30d,
            "win_rate_fmt": f"{win_rate_30d}%",
            "periodo": "últimos 30 dias",
            "range_datas": range_30_dias
        }
        
        # ===== 5B. TOP 5 OFERTAS COM MAIORES/MENORES MARGENS =====
        top_margens_altas = []
        top_margens_baixas = []
        if margem_col and jirakey_col:
            df_com_margem = df_ofertas[df_ofertas["_margem"] > 0].copy()
            if len(df_com_margem) > 0:
                # Top 5 maiores margens
                df_top_alta = df_com_margem.nlargest(5, "_margem")
                top_margens_altas = [
                    {
                        "oferta": str(row[jirakey_col]) if jirakey_col else "N/A",
                        "margem": round(row["_margem"] * 100, 1),
                        "margem_fmt": f"{round(row['_margem'] * 100, 1)}%",
                        "valor": float(row["_valor"]),
                        "valor_formatado": format_brl(row["_valor"])
                    }
                    for _, row in df_top_alta.iterrows()
                ]
                
                # Top 5 menores margens (que ainda são positivas)
                df_top_baixa = df_com_margem.nsmallest(5, "_margem")
                top_margens_baixas = [
                    {
                        "oferta": str(row[jirakey_col]) if jirakey_col else "N/A",
                        "margem": round(row["_margem"] * 100, 1),
                        "margem_fmt": f"{round(row['_margem'] * 100, 1)}%",
                        "valor": float(row["_valor"]),
                        "valor_formatado": format_brl(row["_valor"])
                    }
                    for _, row in df_top_baixa.iterrows()
                ]
        
        # ===== 6. TOP 5 MERCADOS =====
        top_mercados = []
        if mercado_col:
            mercado_agg = df_ofertas.groupby(mercado_col).agg(
                quantidade=("_valor", "count"),
                valor=("_valor", "sum")
            ).reset_index().sort_values("valor", ascending=False).head(5)
            
            top_mercados = [
                {
                    "mercado": str(row[mercado_col]),
                    "quantidade": int(row["quantidade"]),
                    "valor": float(row["valor"]),
                    "valor_formatado": format_brl(row["valor"])
                }
                for _, row in mercado_agg.iterrows()
            ]
        
        # ===== 7. TOP 5 ARQUITETOS POR VALOR =====
        top_arquitetos_valor = []
        if assignee_col:
            arq_valor_agg = df_ofertas.groupby(assignee_col).agg(
                quantidade=("_valor", "count"),
                valor=("_valor", "sum")
            ).reset_index().sort_values("valor", ascending=False).head(5)
            
            top_arquitetos_valor = [
                {
                    "arquiteto": str(row[assignee_col]),
                    "quantidade": int(row["quantidade"]),
                    "valor": float(row["valor"]),
                    "valor_formatado": format_brl(row["valor"])
                }
                for _, row in arq_valor_agg.iterrows()
            ]
        
        # ===== 8. TOP 5 ARQUITETOS POR QUANTIDADE (carga de trabalho) =====
        top_arquitetos_quantidade = []
        if assignee_col:
            df_ativas = df_ofertas[df_ofertas["_categoria"].isin(["desenvolvimento", "entregue"])]
            arq_qtd_agg = df_ativas.groupby(assignee_col).agg(
                ofertas_ativas=("_valor", "count"),
                valor_total=("_valor", "sum")
            ).reset_index().sort_values("ofertas_ativas", ascending=False).head(5)
            
            top_arquitetos_quantidade = [
                {
                    "arquiteto": str(row[assignee_col]),
                    "ofertas_ativas": int(row["ofertas_ativas"]),
                    "valor_total": float(row["valor_total"]),
                    "valor_formatado": format_brl(row["valor_total"])
                }
                for _, row in arq_qtd_agg.iterrows()
            ]
        
        # ===== 8B. TEMPO MÉDIO POR ARQUITETO (dias de ciclo) =====
        tempo_arquitetos = []
        top_arquitetos_rapidos = []
        top_arquitetos_lentos = []
        media_geral_ciclo = 0.0
        
        if assignee_col and data_recebimento_col and data_entrega_col:
            # Filtrar ofertas com dados de ciclo válidos
            df_com_ciclo = df_ofertas[df_ofertas["_dias_ciclo"].notna()].copy()
            
            if len(df_com_ciclo) > 0:
                # Média geral
                media_geral_ciclo = round(df_com_ciclo["_dias_ciclo"].mean(), 1)
                
                # Agrupar por arquiteto
                arq_tempo_agg = df_com_ciclo.groupby(assignee_col).agg(
                    quantidade_ofertas=("_dias_ciclo", "count"),
                    media_dias=("_dias_ciclo", "mean"),
                    min_dias=("_dias_ciclo", "min"),
                    max_dias=("_dias_ciclo", "max")
                ).reset_index()
                
                arq_tempo_agg["media_dias"] = arq_tempo_agg["media_dias"].round(1)
                
                # Top 5 mais rápidos (menor média)
                df_rapidos = arq_tempo_agg.nsmallest(5, "media_dias")
                top_arquitetos_rapidos = [
                    {
                        "arquiteto": str(row[assignee_col]),
                        "media_dias": float(row["media_dias"]),
                        "ofertas_analisadas": int(row["quantidade_ofertas"]),
                        "min_dias": int(row["min_dias"]),
                        "max_dias": int(row["max_dias"])
                    }
                    for _, row in df_rapidos.iterrows()
                ]
                
                # Top 5 mais lentos (maior média)
                df_lentos = arq_tempo_agg.nlargest(5, "media_dias")
                top_arquitetos_lentos = [
                    {
                        "arquiteto": str(row[assignee_col]),
                        "media_dias": float(row["media_dias"]),
                        "ofertas_analisadas": int(row["quantidade_ofertas"]),
                        "min_dias": int(row["min_dias"]),
                        "max_dias": int(row["max_dias"])
                    }
                    for _, row in df_lentos.iterrows()
                ]
        
        tempo_ciclo_metricas = {
            "media_geral_dias": media_geral_ciclo,
            "media_geral_fmt": f"{media_geral_ciclo} dias",
            "top_5_rapidos": top_arquitetos_rapidos,
            "top_5_lentos": top_arquitetos_lentos
        }
        
        total_arquitetos = df_ofertas[assignee_col].nunique() if assignee_col else 0
        arquitetos_responderam = 0
        arquitetos_pendentes = []
        
        if not df_atualizacoes.empty and assignee_col:
            arq_col_upd = next(
                (c for c in df_atualizacoes.columns if "arquiteto" in c.lower() or "nome" in c.lower()),
                None
            )
            if arq_col_upd:
                set_responderam = set(df_atualizacoes[arq_col_upd].dropna().unique())
                set_total = set(df_ofertas[assignee_col].dropna().unique())
                arquitetos_responderam = len(set_responderam & set_total)
                arquitetos_pendentes = list(set_total - set_responderam)[:20]
        
        taxa_resposta = round((arquitetos_responderam / total_arquitetos) * 100, 1) if total_arquitetos > 0 else 0.0
        
        status_report = {
            "taxa_resposta": taxa_resposta,
            "taxa_resposta_fmt": f"{taxa_resposta}%",
            "responderam": arquitetos_responderam,
            "total": total_arquitetos,
            "pendentes_count": len(arquitetos_pendentes),
            "pendentes": arquitetos_pendentes
        }
        
        # ===== 10. MÉTRICAS DE BUDGET (HORAS) =====
        total_horas_alocadas = float(df_ofertas["_budget_horas"].sum())
        total_horas_consumidas = float(df_ofertas["_horas_consumidas"].sum())
        horas_disponiveis = total_horas_alocadas - total_horas_consumidas
        taxa_utilizacao = round((total_horas_consumidas / total_horas_alocadas) * 100, 1) if total_horas_alocadas > 0 else 0.0
        
        # Ofertas em risco (>80% de utilização)
        ofertas_em_risco = []
        if budget_col and horas_consumidas_col:
            df_ofertas["_taxa_utilizacao"] = df_ofertas.apply(
                lambda row: (row["_horas_consumidas"] / row["_budget_horas"] * 100) if row["_budget_horas"] > 0 else 0,
                axis=1
            )
            df_risco = df_ofertas[df_ofertas["_taxa_utilizacao"] > 80].nlargest(10, "_taxa_utilizacao")
            ofertas_em_risco = [
                {
                    "oferta": str(row[jirakey_col]) if jirakey_col else "N/A",
                    "arquiteto": str(row[assignee_col]) if assignee_col else "N/A",
                    "horas_alocadas": float(row["_budget_horas"]),
                    "horas_consumidas": float(row["_horas_consumidas"]),
                    "taxa": round(row["_taxa_utilizacao"], 1),
                    "taxa_fmt": f"{round(row['_taxa_utilizacao'], 1)}%"
                }
                for _, row in df_risco.iterrows()
            ]
        
        budget_metricas = {
            "total_horas_alocadas": total_horas_alocadas,
            "total_horas_alocadas_fmt": f"{total_horas_alocadas:,.0f}h".replace(",", "."),
            "total_horas_consumidas": total_horas_consumidas,
            "total_horas_consumidas_fmt": f"{total_horas_consumidas:,.0f}h".replace(",", "."),
            "horas_disponiveis": horas_disponiveis,
            "horas_disponiveis_fmt": f"{horas_disponiveis:,.0f}h".replace(",", "."),
            "taxa_utilizacao": taxa_utilizacao,
            "taxa_utilizacao_fmt": f"{taxa_utilizacao}%",
            "alerta_budget": taxa_utilizacao > 80,
            "ofertas_em_risco": ofertas_em_risco
        }
        
        # ===== 11. MÉTRICAS DE PRÁTICAS (TOP 5 POR VALOR) =====
        # Calcular valor ponderado por prática: Valor * (% / 100)
        praticas_valores = {
            "DS": float((df_ofertas["_valor"] * df_ofertas["_pct_ds"] / 100).sum()),
            "DIC": float((df_ofertas["_valor"] * df_ofertas["_pct_dic"] / 100).sum()),
            "Dados_IA": float((df_ofertas["_valor"] * df_ofertas["_pct_dados"] / 100).sum()),
            "Cyber": float((df_ofertas["_valor"] * df_ofertas["_pct_cyber"] / 100).sum()),
            "SGE": float((df_ofertas["_valor"] * df_ofertas["_pct_sge"] / 100).sum()),
            "Outros": float((df_ofertas["_valor"] * df_ofertas["_pct_outros"] / 100).sum())
        }
        
        # Contar ofertas por prática (onde % > 0)
        praticas_ofertas = {
            "DS": int((df_ofertas["_pct_ds"] > 0).sum()),
            "DIC": int((df_ofertas["_pct_dic"] > 0).sum()),
            "Dados_IA": int((df_ofertas["_pct_dados"] > 0).sum()),
            "Cyber": int((df_ofertas["_pct_cyber"] > 0).sum()),
            "SGE": int((df_ofertas["_pct_sge"] > 0).sum()),
            "Outros": int((df_ofertas["_pct_outros"] > 0).sum())
        }
        
        # Ordenar e pegar Top 5
        praticas_ranking = sorted(
            [
                {
                    "pratica": nome,
                    "valor": valor,
                    "valor_fmt": format_brl(valor),
                    "ofertas": praticas_ofertas.get(nome, 0)
                }
                for nome, valor in praticas_valores.items()
            ],
            key=lambda x: x["valor"],
            reverse=True
        )[:5]
        
        praticas_metricas = {
            "ranking": praticas_ranking,
            "total_valor_praticas": float(sum(praticas_valores.values())),
            "total_valor_praticas_fmt": format_brl(sum(praticas_valores.values()))
        }
        
        # ===== 12. GERAR CARD HTML PARA TEAMS =====
        pendentes_str = ", ".join(arquitetos_pendentes[:10])
        if len(arquitetos_pendentes) > 10:
            pendentes_str += f" (+{len(arquitetos_pendentes) - 10} mais)"
        
        # Formatar top arquitetos por quantidade para HTML
        top_arq_qtd_html = ""
        for i, arq in enumerate(top_arquitetos_quantidade[:5], 1):
            top_arq_qtd_html += f"<tr><td style='padding: 6px 10px;'>{i}. {arq['arquiteto']}</td><td style='text-align: right; font-weight: 600;'>{arq['ofertas_ativas']} ofertas</td></tr>"
        
        # Formatar top margens para HTML
        top_margens_html = ""
        for arq in top_margens_altas[:3]:
            top_margens_html += f"<tr style='background: linear-gradient(90deg, #e8f5e9 0%, #fff 100%);'><td style='padding: 6px 10px;'>{arq['oferta']}</td><td style='text-align: right; color: #2e7d32; font-weight: 600;'>{arq['margem_fmt']}</td></tr>"
        for arq in top_margens_baixas[:2]:
            top_margens_html += f"<tr style='background: linear-gradient(90deg, #fff3e0 0%, #fff 100%);'><td style='padding: 6px 10px;'>{arq['oferta']}</td><td style='text-align: right; color: #e65100; font-weight: 600;'>{arq['margem_fmt']}</td></tr>"
        
        # Formatar práticas ranking para HTML
        praticas_html = ""
        for i, p in enumerate(praticas_metricas['ranking'][:5], 1):
            bar_color = "#0078d4" if i <= 2 else "#5c2d91" if i <= 4 else "#8764b8"
            praticas_html += f"<tr><td style='padding: 6px 10px;'><span style='display: inline-block; width: 8px; height: 8px; background: {bar_color}; border-radius: 50%; margin-right: 8px;'></span>{p['pratica']}</td><td style='text-align: right; font-weight: 600;'>{p['valor_fmt']}</td><td style='text-align: right; opacity: 0.7;'>{p['ofertas']} ofertas</td></tr>"
        
        # Formatar ofertas em risco para HTML
        risco_html = ""
        for oferta in budget_metricas['ofertas_em_risco'][:5]:
            color = "#d32f2f" if oferta['taxa'] > 90 else "#e65100"
            risco_html += f"<tr><td style='padding: 6px 10px;'>{oferta['oferta']}</td><td style='text-align: center;'>{oferta['arquiteto']}</td><td style='text-align: right; color: {color}; font-weight: 600;'>{oferta['taxa_fmt']}</td></tr>"
        
        # Cor do alerta de budget
        budget_color = "#d32f2f" if budget_metricas['taxa_utilizacao'] > 90 else "#e65100" if budget_metricas['taxa_utilizacao'] > 80 else "#2e7d32"
        budget_icon = "🔴" if budget_metricas['taxa_utilizacao'] > 90 else "🟠" if budget_metricas['taxa_utilizacao'] > 80 else "🟢"
        
        teams_card_html = f"""
<div style="font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; max-width: 700px; margin: 0 auto; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.12);">
    
    <!-- HEADER PREMIUM - CORES MINSAIT -->
    <div style="background: linear-gradient(135deg, #0d1f17 0%, #163829 50%, #0f261c 100%); color: white; padding: 28px 24px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 28px; margin-right: 12px;">📊</span>
            <div>
                <h1 style="margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">STATUS REPORT CORPORATIVO</h1>
                <p style="margin: 4px 0 0 0; opacity: 0.85; font-size: 13px; font-weight: 400;">Pipeline de Ofertas • Consolidação Semanal</p>
            </div>
        </div>
        <div style="display: flex; gap: 20px; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.15);">
            <div style="flex: 1; text-align: center; padding: 12px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                <p style="margin: 0; font-size: 28px; font-weight: 700;">{len(df_ofertas)}</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8; text-transform: uppercase;">Ofertas Ativas</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 12px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                <p style="margin: 0; font-size: 28px; font-weight: 700;">{pipeline_ativo['valor_formatado']}</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8; text-transform: uppercase;">Valor Pipeline</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 12px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                <p style="margin: 0; font-size: 28px; font-weight: 700;">{resultados_30_dias['win_rate']}%</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; opacity: 0.8; text-transform: uppercase;">Win Rate 30d</p>
            </div>
        </div>
        <p style="margin: 16px 0 0 0; font-size: 11px; opacity: 0.6; text-align: right;">📅 Semana {semana} • {data_geracao}</p>
    </div>
    
    <!-- SEÇÃO: PIPELINE & ENTREGAS -->
    <div style="padding: 20px 24px; background: #ffffff;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #0078d4; border-radius: 2px; margin-right: 10px;"></span>
            PIPELINE & ENTREGAS
        </h2>
        <div style="display: flex; gap: 16px;">
            <div style="flex: 1; padding: 16px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 12px;">
                <p style="margin: 0; font-size: 11px; color: #1565c0; text-transform: uppercase; font-weight: 600;">Em Desenvolvimento</p>
                <p style="margin: 8px 0 0 0; font-size: 24px; font-weight: 700; color: #0d47a1;">{pipeline_ativo['quantidade']}</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #1565c0;">{pipeline_ativo['valor_formatado']}</p>
            </div>
            <div style="flex: 1; padding: 16px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 12px;">
                <p style="margin: 0; font-size: 11px; color: #2e7d32; text-transform: uppercase; font-weight: 600;">Entregas Semana</p>
                <p style="margin: 8px 0 0 0; font-size: 24px; font-weight: 700; color: #1b5e20;">{entregas_semana['quantidade']}</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #2e7d32;">{entregas_semana['valor_formatado']}</p>
            </div>
            <div style="flex: 1; padding: 16px; background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-radius: 12px;">
                <p style="margin: 0; font-size: 11px; color: #e65100; text-transform: uppercase; font-weight: 600;">Próxima Semana</p>
                <p style="margin: 8px 0 0 0; font-size: 24px; font-weight: 700; color: #bf360c;">{agenda_proxima_semana['quantidade']}</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #e65100;">{agenda_proxima_semana['valor_formatado']}</p>
            </div>
        </div>
    </div>
    
    <!-- SEÇÃO: RESULTADOS WON/LOST -->
    <div style="padding: 20px 24px; background: #f8f9fa;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #5c2d91; border-radius: 2px; margin-right: 10px;"></span>
            RESULTADOS (30 DIAS)
        </h2>
        <div style="display: flex; gap: 16px;">
            <div style="flex: 1; padding: 16px; background: #fff; border-radius: 12px; border-left: 5px solid #2e7d32;">
                <p style="margin: 0 0 12px 0; font-size: 12px; color: #2e7d32; font-weight: 600;">✅ WON</p>
                <p style="margin: 0; font-size: 22px; font-weight: 700; color: #1b5e20;">{resultados_30_dias['won']['quantidade']} ofertas</p>
                <p style="margin: 4px 0 0 0; font-size: 15px; color: #2e7d32;">{resultados_30_dias['won']['valor_formatado']}</p>
                <p style="margin: 8px 0 0 0; font-size: 11px; color: #666;">Margem média: <strong>{resultados_30_dias['won']['margem_media_fmt']}</strong></p>
            </div>
            <div style="flex: 1; padding: 16px; background: #fff; border-radius: 12px; border-left: 5px solid #c62828;">
                <p style="margin: 0 0 12px 0; font-size: 12px; color: #c62828; font-weight: 600;">❌ LOST</p>
                <p style="margin: 0; font-size: 22px; font-weight: 700; color: #b71c1c;">{resultados_30_dias['lost']['quantidade']} ofertas</p>
                <p style="margin: 4px 0 0 0; font-size: 15px; color: #c62828;">{resultados_30_dias['lost']['valor_formatado']}</p>
                <p style="margin: 8px 0 0 0; font-size: 11px; color: #666;">Margem média: <strong>{resultados_30_dias['lost']['margem_media_fmt']}</strong></p>
            </div>
        </div>
    </div>
    
    <!-- SEÇÃO: BUDGET DE HORAS -->
    <div style="padding: 20px 24px; background: #ffffff;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #00695c; border-radius: 2px; margin-right: 10px;"></span>
            ⏱️ BUDGET DE HORAS
        </h2>
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
            <div style="flex: 1; padding: 14px; background: #e0f2f1; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #00695c; font-weight: 600;">ALOCADAS</p>
                <p style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #004d40;">{budget_metricas['total_horas_alocadas_fmt']}</p>
            </div>
            <div style="flex: 1; padding: 14px; background: #fce4ec; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #c2185b; font-weight: 600;">CONSUMIDAS</p>
                <p style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #880e4f;">{budget_metricas['total_horas_consumidas_fmt']}</p>
            </div>
            <div style="flex: 1; padding: 14px; background: #e8f5e9; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #2e7d32; font-weight: 600;">DISPONÍVEIS</p>
                <p style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #1b5e20;">{budget_metricas['horas_disponiveis_fmt']}</p>
            </div>
        </div>
        <div style="padding: 14px; background: linear-gradient(90deg, #f5f5f5 0%, #eeeeee 100%); border-radius: 10px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 13px; color: #424242;">Taxa de Utilização:</span>
            <span style="font-size: 18px; font-weight: 700; color: {budget_color};">{budget_icon} {budget_metricas['taxa_utilizacao_fmt']}</span>
        </div>
        {f'''<div style="margin-top: 16px; padding: 14px; background: #ffebee; border-radius: 10px; border-left: 4px solid #d32f2f;">
            <p style="margin: 0 0 8px 0; font-size: 12px; color: #c62828; font-weight: 600;">🚨 OFERTAS EM RISCO (>{">"}80% budget)</p>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">{risco_html}</table>
        </div>''' if risco_html else ''}
    </div>
    
    <!-- SEÇÃO: TOP 5 PRÁTICAS -->
    <div style="padding: 20px 24px; background: #f8f9fa;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #7b1fa2; border-radius: 2px; margin-right: 10px;"></span>
            🏆 TOP 5 PRÁTICAS (POR VALOR)
        </h2>
        <table style="width: 100%; font-size: 13px; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden;">
            <thead><tr style="background: #ede7f6;"><th style="padding: 10px 12px; text-align: left; font-weight: 600; color: #4a148c;">Prática</th><th style="padding: 10px 12px; text-align: right; font-weight: 600; color: #4a148c;">Valor</th><th style="padding: 10px 12px; text-align: right; font-weight: 600; color: #4a148c;">Ofertas</th></tr></thead>
            <tbody>{praticas_html}</tbody>
        </table>
        <p style="margin: 12px 0 0 0; font-size: 12px; color: #666; text-align: right;">Total valor práticas: <strong>{praticas_metricas['total_valor_praticas_fmt']}</strong></p>
    </div>
    
    <!-- SEÇÃO: TOP ARQUITETOS -->
    {f'''<div style="padding: 20px 24px; background: #ffffff;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #1565c0; border-radius: 2px; margin-right: 10px;"></span>
            👨‍💼 TOP 5 ARQUITETOS (VOLUME)
        </h2>
        <table style="width: 100%; font-size: 13px; border-collapse: collapse; background: #f8f9fa; border-radius: 10px; overflow: hidden;">{top_arq_qtd_html}</table>
    </div>''' if top_arq_qtd_html else ''}
    
    <!-- SEÇÃO: TEMPO DE CICLO -->
    <div style="padding: 20px 24px; background: #f8f9fa;">
        <h2 style="margin: 0 0 16px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: #00796b; border-radius: 2px; margin-right: 10px;"></span>
            ⚡ TEMPO DE CICLO
        </h2>
        <div style="display: flex; gap: 16px;">
            <div style="flex: 1; padding: 14px; background: #fff; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #00796b; font-weight: 600;">MÉDIA GERAL</p>
                <p style="margin: 6px 0 0 0; font-size: 24px; font-weight: 700; color: #004d40;">{tempo_ciclo_metricas['media_geral_fmt']}</p>
            </div>
            <div style="flex: 2; padding: 14px; background: #e8f5e9; border-radius: 10px;">
                <p style="margin: 0 0 8px 0; font-size: 11px; color: #2e7d32; font-weight: 600;">🏃 MAIS RÁPIDOS</p>
                {' • '.join([f"<strong>{a['arquiteto']}</strong> ({a['media_dias']}d)" for a in tempo_ciclo_metricas['top_5_rapidos'][:3]]) if tempo_ciclo_metricas['top_5_rapidos'] else 'N/A'}
            </div>
        </div>
    </div>
    
    <!-- SEÇÃO: STATUS REPORT -->
    <div style="padding: 20px 24px; background: {'#ffebee' if status_report['taxa_resposta'] < 80 else '#e8f5e9'};">
        <h2 style="margin: 0 0 12px 0; font-size: 14px; color: #1a1a2e; font-weight: 600; display: flex; align-items: center;">
            <span style="display: inline-block; width: 4px; height: 16px; background: {'#c62828' if status_report['taxa_resposta'] < 80 else '#2e7d32'}; border-radius: 2px; margin-right: 10px;"></span>
            {'⚠️' if status_report['taxa_resposta'] < 80 else '✅'} TAXA DE RESPOSTA SEMANAL
        </h2>
        <p style="margin: 0; font-size: 15px;"><strong>{status_report['taxa_resposta_fmt']}</strong> ({status_report['responderam']} de {status_report['total']} arquitetos)</p>
        {f'<p style="margin: 10px 0 0 0; font-size: 12px; color: #c62828;">🔴 Pendentes: {pendentes_str}</p>' if arquitetos_pendentes else '<p style="margin: 8px 0 0 0; font-size: 12px; color: #2e7d32;">✅ Todos responderam!</p>'}
    </div>
    
    <!-- FOOTER -->
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 16px 24px; text-align: center;">
        <p style="margin: 0; font-size: 11px; opacity: 0.7;">🤖 Gerado automaticamente por <strong>Azure Function</strong> | Pipeline Consolidation v2.1</p>
        <p style="margin: 6px 0 0 0; font-size: 10px; opacity: 0.5;">Minsait • DN Technology Architecture</p>
    </div>
</div>
"""
        
        # ===== RESULTADO FINAL =====
        resultado = {
            "semana": semana,
            "data_geracao": data_geracao,
            "status": "sucesso",
            "total_ofertas_recebidas": len(df_ofertas),
            
            "pipeline_ativo": pipeline_ativo,
            "entregas_semana": entregas_semana,
            "agenda_proxima_semana": agenda_proxima_semana,
            
            "resultados_7_dias": resultados_7_dias,
            "resultados_15_dias": resultados_15_dias,
            "resultados_30_dias": resultados_30_dias,
            
            "top_mercados": top_mercados,
            "top_arquitetos_valor": top_arquitetos_valor,
            "top_arquitetos_quantidade": top_arquitetos_quantidade,
            "tempo_ciclo_metricas": tempo_ciclo_metricas,
            
            "top_margens_altas": top_margens_altas,
            "top_margens_baixas": top_margens_baixas,
            
            "budget_metricas": budget_metricas,
            "praticas_metricas": praticas_metricas,
            
            "status_report": status_report,
            
            "teams_card_html": teams_card_html
        }
        
        logging.info("Consolidação V2 concluída: %s ofertas processadas", len(df_ofertas))
        
        return func.HttpResponse(
            json.dumps(to_native_obj(resultado), ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
        
    except Exception as e:
        logging.error("Erro na consolidação V2: %s", str(e))
        import traceback
        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "status": "erro",
                "traceback": traceback.format_exc()
            }, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )




























































@app.route(route="import-jira", auth_level=func.AuthLevel.FUNCTION)
def import_jira(req: func.HttpRequest) -> func.HttpResponse:
    """
    Transforma dados JIRA (CSV) para formato SharePoint.
    Recebe: csv_content (CSV bruto) OU ofertas (JSON array)
    Retorna: Lista formatada para UPSERT no SharePoint
    """
    logging.info("Iniciando importação JIRA...")

    try:
        req_body = req.get_json()
        csv_content = req_body.get("csv_content", None)
        ofertas_jira = req_body.get("ofertas", [])
        arquivo_nome = req_body.get("arquivo", "unknown.csv")

        # OPÇÃO 1: Recebeu CSV bruto (vindo do Power Automate)
        if csv_content:
            import io

            logging.info("Recebido CSV bruto (%s caracteres)", len(csv_content))
            try:
                # Autodetect separador (vírgula ou ponto-e-vírgula)
                first_line = (
                    csv_content.split("\n")[0]
                    if "\n" in csv_content
                    else csv_content.split("\r")[0]
                )
                sep = ";" if first_line.count(";") > first_line.count(",") else ","
                logging.info('Separador detectado: "%s"', sep)

                df = pd.read_csv(io.StringIO(csv_content), sep=sep)
                logging.info(
                    "CSV parseado: %s linhas, colunas: %s...",
                    len(df),
                    list(df.columns)[:5],
                )
            except Exception as csv_error:
                logging.error("Erro parsing CSV: %s", str(csv_error))
                return func.HttpResponse(
                    json.dumps(
                        {"error": f"Erro ao parsear CSV: {str(csv_error)}", "success": False}
                    ),
                    status_code=400,
                    mimetype="application/json",
                )
        # OPÇÃO 2: Recebeu JSON array (ofertas já parseadas)
        elif ofertas_jira:
            logging.info("Recebido JSON array com %s ofertas", len(ofertas_jira))
            df = pd.DataFrame(ofertas_jira)
        else:
            # Nenhum dado recebido
            return func.HttpResponse(
                json.dumps({"error": "Nenhuma oferta recebida", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        # Neste ponto, df já contém os dados (seja de CSV ou JSON)

        # Normaliza coluna de valor quando apenas o weighted estiver presente
        if (
            "Custom field (Total Amount (euros))" not in df.columns
            and "Custom field (Total amount (€) weighted)" in df.columns
        ):
            df = df.rename(
                columns={
                    "Custom field (Total amount (€) weighted)": "Custom field (Total Amount (euros))"
                }
            )

        # Mapeamento de colunas JIRA -> SharePoint
        column_mapping = {
            "Issue key": "JiraKey",
            "Issue id": "JiraId",
            "Assignee": "Assignee",
            "Status": "Status",
            "Summary": "Titulo",
            "Component/s": "Cliente",
            "Custom field (Market)": "Mercado",
            "Custom field (Type of Service)": "TipoServico",
            "Custom field (Total Amount (euros))": "ValorEUR",
            "Custom field (Budg.Loc.Currency)": "ValorBRL",
            "Custom field (Margin)": "Margem",
            "Custom field (Country)": "Country",
            "Custom field (DN Manager)": "DNManager",
            "Custom field (Market Manager)": "MarketManager",
            "Custom field (Operations Manager)": "OperationsManager",
            "Created": "JiraCreated",
            "Updated": "JiraUpdated",
            "Custom field (Proposal Due Date)": "PrazoProposta",
            "Custom field (Observations)": "Observacoes",
            "Custom field (Type Business Opportunity)": "TipoOportunidade",
            "Custom field (Renewal)": "Renewal",
            "Custom field (Temporal Scope)": "TemporalScope",
            "Custom field (Código GEP)": "CodigoGEP",
        }

        # Renomear colunas existentes
        rename_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # Selecionar apenas colunas mapeadas
        available_cols = [v for v in column_mapping.values() if v in df.columns]
        df_clean = df[available_cols].copy()

        # ============================================================
        # BLINDAGEM COMPLETA - CONVERSÃO DE TIPOS PARA SHAREPOINT
        # ============================================================

        # Lista de valores que devem ser tratados como NULL
        NULL_VALUES = ["nan", "none", "null", "n/a", "na", "#n/a", "", " ", "-", "--", "undefined"]

        def is_null_value(val):
            """Verifica se o valor deve ser tratado como NULL"""
            if pd.isna(val) or val is None:
                return True
            if isinstance(val, str) and str(val).strip().lower() in NULL_VALUES:
                return True
            return False

        # -------------------------------------------------------------
        # 1. CAMPOS NUMÉRICOS - Parse robusto (pt-BR, %, moeda)
        # Trata: "1.234,56" (pt-BR), "24%", "€1000", "R$500", etc.
        # -------------------------------------------------------------
        def parse_number(val, *, default=0, allow_null=False, percent=False):
            """Parse robusto de número: trata pt-BR, porcentagem, moeda"""
            if is_null_value(val):
                return None if allow_null else default

            # Se já é número, usa direto
            if isinstance(val, (int, float)) and not pd.isna(val):
                num = float(val)
            else:
                s = str(val).strip()

                # Remover símbolos de moeda e espaços
                s = s.replace("R$", "").replace("€", "").replace("$", "")
                s = s.replace("\u00a0", " ")  # nbsp
                s = s.replace(" ", "")

                # Tratar porcentagem
                has_percent = "%" in s
                s = s.replace("%", "")

                # Detectar formato pt-BR: "1.234,56" (ponto milhar, vírgula decimal)
                # vs formato US: "1,234.56" (vírgula milhar, ponto decimal)
                if "." in s and "," in s:
                    # Se vírgula vem depois do ponto: pt-BR (1.234,56)
                    if s.rfind(",") > s.rfind("."):
                        s = s.replace(".", "").replace(",", ".")
                    # Se ponto vem depois da vírgula: US (1,234.56)
                    else:
                        s = s.replace(",", "")
                else:
                    # Só tem um tipo de separador - assumir vírgula como decimal
                    s = s.replace(",", ".")

                # Remover caracteres não-numéricos restantes
                s = re.sub(r"[^0-9.\-]", "", s)

                if s in ("", "-", ".", "-."):
                    return None if allow_null else default

                try:
                    num = float(s)
                except ValueError:
                    return None if allow_null else default

                # Se tinha % e percent=False, ainda assim converter
                if has_percent and not percent:
                    num = num / 100

            # Se é campo de porcentagem e valor > 1, converter
            if percent and num > 1:
                num = num / 100

            # Retornar int se for inteiro
            return int(num) if num == int(num) else num

        # Aplicar nos campos numéricos
        for col in ["ValorEUR", "ValorBRL"]:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(lambda x: parse_number(x, default=0))

        if "Margem" in df_clean.columns:
            df_clean["Margem"] = df_clean["Margem"].apply(
                lambda x: parse_number(x, default=0, percent=True)
            )

        if "TemporalScope" in df_clean.columns:
            df_clean["TemporalScope"] = df_clean["TemporalScope"].apply(
                lambda x: parse_number(x, allow_null=True)
            )

        # -------------------------------------------------------------
        # 2. CAMPOS DATETIME
        # JiraCreated, JiraUpdated = date-only (YYYY-MM-DD)
        # PrazoProposta = date-only
        # -------------------------------------------------------------
        def parse_date(val):
            """Converte para date-only (YYYY-MM-DD)"""
            if is_null_value(val):
                return None
            try:
                dt = pd.to_datetime(val, errors="coerce", dayfirst=True)
                return dt.date().isoformat() if pd.notna(dt) else None
            except Exception:
                return None

        # JiraCreated e JiraUpdated são date-only
        for col in ["JiraCreated", "JiraUpdated"]:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(parse_date)

        # PrazoProposta é date-only
        if "PrazoProposta" in df_clean.columns:
            df_clean["PrazoProposta"] = df_clean["PrazoProposta"].apply(parse_date)

        # -------------------------------------------------------------
        # 3. CAMPO BOOLEAN (Renewal)
        # Aceita: Yes/No, True/False, 1/0, Sim/Não, Y/N
        # -------------------------------------------------------------
        if "Renewal" in df_clean.columns:

            def convert_boolean(val):
                if is_null_value(val):
                    return False  # Default para Boolean
                if isinstance(val, bool):
                    return val
                val_str = str(val).strip().lower()
                return val_str in ["yes", "true", "1", "sim", "y", "s"]

            df_clean["Renewal"] = df_clean["Renewal"].apply(convert_boolean)

        # -------------------------------------------------------------
        # 4. CAMPOS CHOICE - PASSAR VALORES JIRA SEM TRANSFORMAÇÃO
        # IMPORTANTE: SharePoint deve ter FillInChoice=TRUE nos campos Choice
        # -------------------------------------------------------------

        def normalize_choice_passthrough(val):
            """Passa valor JIRA diretamente, apenas limpando NaN e whitespace"""
            if is_null_value(val):
                return None
            val_str = str(val).strip()
            return val_str if val_str else None

        for field in [
            "Status",
            "Mercado",
            "TipoServico",
            "TipoOportunidade",
            "PraticaUnificada",
            "StatusBudgetAlocado",
        ]:
            if field in df_clean.columns:
                df_clean[field] = df_clean[field].apply(normalize_choice_passthrough)
                unique_vals = df_clean[field].dropna().unique()
                logging.info(
                    'Choice "%s": %s valores únicos passados do JIRA',
                    field,
                    len(unique_vals),
                )

        # -------------------------------------------------------------
        # 5. CAMPOS DE TEXTO
        # Limpa NaN-like, normaliza espaços, limita tamanho
        # -------------------------------------------------------------
        TEXT_FIELD_LIMITS = {
            "Titulo": 255,
            "Cliente": 255,
            "DNManager": 255,
            "MarketManager": 255,
            "OperationsManager": 255,
            "Assignee": 255,
            "CodigoGEP": 50,
            "Observacoes": 63999,  # Note field limit
            # Optional enrichment (set by IMPORT_ENRICH_ASSIGNEE=true)
            "AssigneeMatricula": 50,
            "AssigneeEmail": 255,
            "AssigneeNome": 255,
        }

        def normalize_text(val, max_length=255):
            """Normaliza campo de texto: limpa NaN, normaliza espaços, limita tamanho"""
            if is_null_value(val):
                return None

            val_str = str(val).strip()

            # Normalizar espaços múltiplos
            val_str = re.sub(r"\s+", " ", val_str)

            # Normalizar quebras de linha (CRLF -> LF)
            val_str = val_str.replace("\r\n", "\n").replace("\r", "\n")

            # Limitar tamanho
            if len(val_str) > max_length:
                val_str = val_str[: max_length - 3] + "..."
                logging.warning("Texto truncado para %s caracteres", max_length)

            return val_str if val_str else None

        def strip_html_to_text(val_str: str) -> str:
            """Converte HTML simples (JIRA/Outlook) para texto preservando quebras de linha."""
            s = html.unescape(val_str)
            s = s.replace("\r\n", "\n").replace("\r", "\n")

            # Quebras de linha comuns em HTML
            s = re.sub(r"(?i)<br\s*/?>", "\n", s)
            s = re.sub(r"(?i)</(div|p|tr|h\d)>", "\n", s)
            s = re.sub(r"(?i)<li[^>]*>", "- ", s)
            s = re.sub(r"(?i)</li>", "\n", s)

            # Remover tags remanescentes
            s = re.sub(r"<[^>]+>", "", s)

            # Normalizar espaços preservando \n
            s = re.sub(r"[ \\t]+", " ", s)
            s = "\n".join(line.strip() for line in s.split("\n"))
            s = re.sub(r"\n{3,}", "\n\n", s)
            return s.strip()

        STRIP_HTML_OBSERVACOES = os.getenv("IMPORT_STRIP_HTML_OBSERVACOES", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "sim",
            "s",
        }

        def normalize_observacoes(val, max_length=63999):
            """Normaliza Observacoes: remove HTML (opcional), preserva quebras de linha, limita tamanho."""
            if is_null_value(val):
                return None

            s = str(val).strip()
            if STRIP_HTML_OBSERVACOES and ("<" in s or "&lt;" in s or "&gt;" in s or "&amp;" in s):
                s = strip_html_to_text(s)
            else:
                s = html.unescape(s).replace("\r\n", "\n").replace("\r", "\n").strip()

            if not s:
                return None

            if len(s) > max_length:
                s = s[: max_length - 3] + "..."
                logging.warning("Observacoes truncado para %s caracteres", max_length)

            return s

        for field, limit in TEXT_FIELD_LIMITS.items():
            if field in df_clean.columns:
                if field == "Observacoes":
                    df_clean[field] = df_clean[field].apply(
                        lambda x, l=limit: normalize_observacoes(x, l)
                    )
                else:
                    df_clean[field] = df_clean[field].apply(
                        lambda x, l=limit: normalize_text(x, l)
                    )

        # -------------------------------------------------------------
        # 5b. ENRIQUECIMENTO OPCIONAL DO ASSIGNEE (LOGIN -> MATRÍCULA/NOME/EMAIL)
        #
        # Objetivo: manter `Assignee` AS-IS (login do JIRA), mas também popular colunas
        # derivadas úteis para relatórios e troubleshooting em SharePoint.
        #
        # Requer permissões Graph para ler a lista ARQs_Teams (SP_* env vars).
        # -------------------------------------------------------------
        ENRICH_ASSIGNEE = os.getenv("IMPORT_ENRICH_ASSIGNEE", "false").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "sim",
            "s",
        }

        if ENRICH_ASSIGNEE and "Assignee" in df_clean.columns:
            try:
                token = get_graph_token()
                site_id = os.environ.get("SP_SITE_ID")
                if not site_id:
                    site_url = get_required_env("SP_SITE_URL")
                    site_id = resolve_sharepoint_site_id(site_url, token)

                arqs_list_id = os.getenv(
                    "ARQS_TEAMS_LIST_ID", "1ad529f7-db5b-4567-aa00-1582ff333264"
                )

                # Fetch ARQs_Teams items (once) and build mapping by Login (lowercase).
                mapping = {}
                next_link = f"/sites/{site_id}/lists/{arqs_list_id}/items?$top=999&$expand=fields($select=Title,Login,field_1,field_3,E_x002d_mail,Status)"
                while next_link:
                    _, resp_body = graph_request("GET", next_link, token)
                    payload = json.loads(resp_body or "{}")
                    for item in payload.get("value", []):
                        fields = item.get("fields") or {}
                        login = (fields.get("Login") or "").strip().lower()
                        if not login:
                            continue
                        mapping[login] = {
                            "matricula": (fields.get("Title") or "").strip(),
                            "nome": (fields.get("field_1") or "").strip(),
                            "email": (fields.get("field_3") or fields.get("E_x002d_mail") or "").strip().lower(),
                        }
                    next_link = payload.get("@odata.nextLink")

                def enrich_login(val):
                    if is_null_value(val):
                        return None
                    key = str(val).strip().lower()
                    return mapping.get(key)

                enriched = df_clean["Assignee"].apply(enrich_login)
                df_clean["AssigneeMatricula"] = enriched.apply(lambda x: x.get("matricula") if x else None)
                df_clean["AssigneeNome"] = enriched.apply(lambda x: x.get("nome") if x else None)
                df_clean["AssigneeEmail"] = enriched.apply(lambda x: x.get("email") if x else None)

                missing = int(df_clean["AssigneeMatricula"].isna().sum())
                logging.info(
                    "Enriquecimento Assignee: %s ofertas, %s sem match em ARQs_Teams",
                    int(df_clean.shape[0]),
                    missing,
                )
            except Exception as exc:
                logging.warning("Falha no enriquecimento Assignee (continuando sem enrich): %s", str(exc))

        # -------------------------------------------------------------
        # 6. JIRAKEY - Campo crítico para UPSERT
        # Escape de apóstrofo para OData filter + validação obrigatória
        # -------------------------------------------------------------
        if "JiraKey" in df_clean.columns:

            def normalize_jirakey(val):
                if is_null_value(val):
                    return None
                val_str = str(val).strip().upper()  # JiraKey sempre maiúsculo
                # Escape de apóstrofo para OData
                val_str = val_str.replace("'", "''")
                return val_str

            df_clean["JiraKey"] = df_clean["JiraKey"].apply(normalize_jirakey)

            # Validar que JiraKey existe
            if df_clean["JiraKey"].isna().all():
                logging.error("JiraKey não encontrado ou todos vazios!")
                return func.HttpResponse(
                    json.dumps(
                        {"error": "JiraKey é obrigatório mas não foi encontrado", "success": False}
                    ),
                    status_code=400,
                    mimetype="application/json",
                )
        else:
            logging.error("Coluna JiraKey não existe no DataFrame!")
            return func.HttpResponse(
                json.dumps({"error": "Coluna JiraKey não encontrada no CSV", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        # -------------------------------------------------------------
        # 7. REMOVER COLUNAS QUE NÃO VÃO PARA SHAREPOINT
        # -------------------------------------------------------------
        cols_to_remove = ["JiraId", "Country"]
        for col in cols_to_remove:
            if col in df_clean.columns:
                df_clean = df_clean.drop(columns=[col])

        # -------------------------------------------------------------
        # 8. LOG E RELATORIO DE ESTATISTICAS
        # -------------------------------------------------------------
        null_counts = df_clean.isna().sum()
        null_counts_dict = {k: int(v) for k, v in null_counts.to_dict().items()}
        logging.info("Estatísticas de campos null após limpeza: %s", null_counts_dict)

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
                    "total": int(series.shape[0]),
                    "nulos": int(series.isna().sum()),
                    "unicos": int(series.dropna().nunique()),
                    "valores": valores,
                }

        # Converter para lista de dicionários
        ofertas_formatadas = df_clean.to_dict("records")
        ofertas_formatadas = [
            {k: to_native(v) for k, v in rec.items()} for rec in ofertas_formatadas
        ]

        # Estatísticas
        total = len(ofertas_formatadas)
        valor_eur_total = df_clean["ValorEUR"].sum() if "ValorEUR" in df_clean.columns else 0
        valor_brl_total = df_clean["ValorBRL"].sum() if "ValorBRL" in df_clean.columns else 0

        campos_ausentes = [
            col for col in column_mapping.values() if col not in df_clean.columns
        ]

        resultado = {
            "success": True,
            "ofertas": ofertas_formatadas,
            "estatisticas": {
                "total_processado": total,
                "valor_eur_total": float(valor_eur_total),
                "valor_brl_total": float(valor_brl_total),
                "arquivo": arquivo_nome,
                "data_processamento": datetime.now().isoformat(),
                "campos_ausentes": campos_ausentes,
                "null_counts": null_counts_dict,
                "choices_report": choices_report,
            },
        }

        logging.info("Import JIRA concluído: %s ofertas processadas", total)

        resultado = to_native_obj(resultado)
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Erro no import JIRA: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="normalizar-ofertas", auth_level=func.AuthLevel.FUNCTION)
def normalizar_ofertas(req: func.HttpRequest) -> func.HttpResponse:
    """
    Normaliza dados RAW do SharePoint usando regras pre-aprovadas.
    Recebe: ofertas_raw (array), mapeamentos (array)
    Retorna: ofertas_normalizadas + relatorio de discrepancias
    """
    logging.info("Iniciando normalizacao de ofertas...")

    try:
        req_body = req.get_json()
        ofertas_raw = req_body.get("ofertas_raw", [])
        mapeamentos = req_body.get("mapeamentos", [])
        unmapped_value = req_body.get("unmapped_value", "UNMAPPED/OUTROS")
        campos_choice = req_body.get(
            "campos_choice",
            [
                "Status",
                "Mercado",
                "TipoServico",
                "TipoOportunidade",
                "PraticaUnificada",
                "StatusBudgetAlocado",
            ],
        )

        if not ofertas_raw:
            return func.HttpResponse(
                json.dumps({"error": "Nenhuma oferta RAW recebida", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        df_raw = pd.DataFrame(ofertas_raw)

        NULL_VALUES = ["nan", "none", "null", "n/a", "na", "#n/a", "", " ", "-", "--", "undefined"]

        def is_null_value(val):
            if pd.isna(val) or val is None:
                return True
            if isinstance(val, str) and str(val).strip().lower() in NULL_VALUES:
                return True
            return False

        def normalize_value(val):
            if is_null_value(val):
                return None
            val_str = str(val).strip()
            return val_str if val_str else None

        # Monta mapeamento por campo
        mapping_by_field = {field: {} for field in campos_choice}
        used_mapping_keys = {field: set() for field in campos_choice}

        for item in mapeamentos:
            field = item.get("Campo") or item.get("campo") or item.get("Field") or item.get("field")
            raw_val = item.get("ValorRaw") or item.get("valor_raw") or item.get("Raw") or item.get("raw")
            norm_val = (
                item.get("ValorNormalizado")
                or item.get("valor_normalizado")
                or item.get("Normalizado")
                or item.get("normalizado")
            )
            ativo = item.get("Ativo")
            if ativo is None:
                ativo = True
            if field not in mapping_by_field or not ativo:
                continue
            raw_key = normalize_value(raw_val)
            if raw_key is None:
                continue
            mapping_by_field[field][raw_key] = normalize_value(norm_val)

        # Relatorio de normalizacao
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

        ofertas_normalizadas = []
        for rec in df_raw.to_dict("records"):
            rec_norm = dict(rec)
            for field in campos_choice:
                if field not in rec:
                    continue
                relatorio[field]["total"] += 1
                raw_val = rec.get(field)
                raw_key = normalize_value(raw_val)
                if raw_key is None:
                    relatorio[field]["nulos"] += 1
                    rec_norm[field] = None
                    continue
                if raw_key in mapping_by_field.get(field, {}):
                    mapped_val = mapping_by_field[field][raw_key]
                    used_mapping_keys[field].add(raw_key)
                    relatorio[field]["mapeados"] += 1
                    mapped_key = mapped_val if mapped_val is not None else None
                    relatorio[field]["valores_mapeados"][mapped_key] = (
                        relatorio[field]["valores_mapeados"].get(mapped_key, 0) + 1
                    )
                    rec_norm[field] = mapped_val
                else:
                    relatorio[field]["nao_mapeados"] += 1
                    relatorio[field]["valores_nao_mapeados"][raw_key] = (
                        relatorio[field]["valores_nao_mapeados"].get(raw_key, 0) + 1
                    )
                    rec_norm[field] = unmapped_value
            ofertas_normalizadas.append(rec_norm)

        # Mapeamentos nao utilizados
        mapeamentos_nao_usados = {}
        for field, mapping in mapping_by_field.items():
            unused = [k for k in mapping.keys() if k not in used_mapping_keys[field]]
            if unused:
                mapeamentos_nao_usados[field] = unused

        # Formata relatorio
        relatorio_formatado = {}
        for field, stats in relatorio.items():
            relatorio_formatado[field] = {
                "total": stats["total"],
                "nulos": stats["nulos"],
                "mapeados": stats["mapeados"],
                "nao_mapeados": stats["nao_mapeados"],
                "valores_nao_mapeados": [
                    {"valor": k, "quantidade": v}
                    for k, v in stats["valores_nao_mapeados"].items()
                ],
                "valores_mapeados": [
                    {"valor": k, "quantidade": v}
                    for k, v in stats["valores_mapeados"].items()
                ],
            }

        resultado = {
            "success": True,
            "unmapped_value": unmapped_value,
            "ofertas_normalizadas": [
                {k: to_native(v) for k, v in rec.items()} for rec in ofertas_normalizadas
            ],
            "relatorio": {
                "total_processado": len(ofertas_normalizadas),
                "campos_choice": campos_choice,
                "normalizacao": relatorio_formatado,
                "mapeamentos_nao_usados": mapeamentos_nao_usados,
            },
        }

        resultado = to_native_obj(resultado)
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Erro na normalizacao: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


def get_required_env(name):
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def get_graph_token():
    tenant_id = get_required_env("SP_TENANT_ID")
    client_id = get_required_env("SP_CLIENT_ID")
    client_secret = get_required_env("SP_CLIENT_SECRET")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    data = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
    ).encode("utf-8")

    req = Request(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"Token request failed ({exc.code}): {body}") from exc

    access_token = payload.get("access_token")
    if not access_token:
        raise RuntimeError("Token response missing access_token")
    return access_token


def graph_request(method, path_or_url, token, body=None, extra_headers=None):
    if path_or_url.startswith("https://"):
        url = path_or_url
    else:
        url = f"https://graph.microsoft.com/v1.0{path_or_url}"

    headers = {"Authorization": f"Bearer {token}"}
    if extra_headers:
        headers.update(extra_headers)

    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, resp_body
    except HTTPError as exc:
        resp_body = exc.read().decode("utf-8")
        raise RuntimeError(f"Graph API error ({exc.code}): {resp_body}") from exc


def resolve_sharepoint_site_id(site_url, token):
    parsed = urlparse(site_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or not parsed.path:
        raise ValueError("Invalid SP_SITE_URL (expected https://<tenant>.sharepoint.com/sites/<site>)")

    # Graph expects: /sites/{hostname}:{server-relative-path}
    path = parsed.path.rstrip("/")
    status, body = graph_request("GET", f"/sites/{parsed.netloc}:{path}", token)
    payload = json.loads(body or "{}")
    site_id = payload.get("id")
    if not site_id:
        raise RuntimeError("Graph response missing site id")
    return site_id


def get_env_bool(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "y", "on")


def parse_csv_env_set(name):
    raw = os.environ.get(name, "")
    items = []
    for part in raw.split(","):
        cleaned = part.strip().strip("{}").lower()
        if cleaned:
            items.append(cleaned)
    return set(items)


@app.route(route="lab/purge-lists", auth_level=func.AuthLevel.FUNCTION)
def lab_purge_lists(req: func.HttpRequest) -> func.HttpResponse:
    """
    LAB-only admin endpoint to purge SharePoint list items (for testing).

    Safety controls (all required):
    - ENVIRONMENT must NOT be 'prod'/'production'
    - LAB_PURGE_ENABLED=true
    - LAB_PURGE_ADMIN_TOKEN must match header x-admin-token
    - LAB_PURGE_CONFIRMATION must match body.confirm
    - Lists must be in allowlist (LAB_PURGE_ALLOWED_LIST_IDS) OR in the built-in default allowlist

    Body:
    {
      "confirm": "....",
      "dry_run": true,
      "lists": ["<list-guid>", "Ofertas_Pipeline", ...],
      "max_items_per_list": 200
    }
    """

    try:
        env_name = os.environ.get("ENVIRONMENT", "").strip().lower()
        if env_name in ("prod", "production"):
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Disabled in PROD environment"}, ensure_ascii=False),
                status_code=403,
                mimetype="application/json",
            )

        if not get_env_bool("LAB_PURGE_ENABLED", False):
            return func.HttpResponse(
                json.dumps({"success": False, "error": "LAB purge is disabled (LAB_PURGE_ENABLED=false)"}),
                status_code=403,
                mimetype="application/json",
            )

        admin_token_expected = get_required_env("LAB_PURGE_ADMIN_TOKEN")
        admin_token = req.headers.get("x-admin-token") or req.headers.get("X-Admin-Token") or ""
        if not admin_token or admin_token != admin_token_expected:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Unauthorized (missing/invalid x-admin-token)"}),
                status_code=401,
                mimetype="application/json",
            )

        try:
            body = req.get_json()
        except ValueError:
            body = {}

        confirmation_expected = get_required_env("LAB_PURGE_CONFIRMATION")
        confirm = (body.get("confirm") or "").strip()
        if not confirm or confirm != confirmation_expected:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Missing/invalid confirm value"}),
                status_code=400,
                mimetype="application/json",
            )

        requested_lists = body.get("lists") or []
        if not isinstance(requested_lists, list) or not requested_lists:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Body.lists must be a non-empty array"}),
                status_code=400,
                mimetype="application/json",
            )

        dry_run = body.get("dry_run", True)
        max_items = int(body.get("max_items_per_list", os.environ.get("LAB_PURGE_MAX_ITEMS_PER_LIST", "500")))
        if max_items <= 0:
            max_items = 500

        # Default allowlist (known lists used by the flows). Prefer configuring env allowlist in each environment.
        default_allowed = {
            "6db5a12d-595d-4a1a-aca1-035837613815",  # Ofertas_Pipeline
            "172d7d29-5a3c-4608-b4ea-b5b027ef5ac0",  # Atualizacoes_Semanais
            "f58b3d23-5750-4b29-b30f-a7b5421cdd80",  # StatusReports_Historico
        }
        allowed_env = parse_csv_env_set("LAB_PURGE_ALLOWED_LIST_IDS")
        allowed = allowed_env if allowed_env else default_allowed

        name_to_id = {
            "ofertas_pipeline": "6db5a12d-595d-4a1a-aca1-035837613815",
            "atualizacoes_semanais": "172d7d29-5a3c-4608-b4ea-b5b027ef5ac0",
            "statusreports_historico": "f58b3d23-5750-4b29-b30f-a7b5421cdd80",
        }

        list_ids = []
        for raw in requested_lists:
            if not isinstance(raw, str):
                continue
            cleaned = raw.strip().strip("{}")
            key = cleaned.lower()
            list_id = name_to_id.get(key) or cleaned
            list_id_norm = list_id.lower()
            if list_id_norm not in allowed:
                return func.HttpResponse(
                    json.dumps(
                        {
                            "success": False,
                            "error": f"List not allowed: {raw}",
                            "hint": "Configure LAB_PURGE_ALLOWED_LIST_IDS or request only known list names/ids",
                        },
                        ensure_ascii=False,
                    ),
                    status_code=403,
                    mimetype="application/json",
                )
            list_ids.append(list_id_norm)

        token = get_graph_token()
        site_id = os.environ.get("SP_SITE_ID")
        if not site_id:
            site_url = get_required_env("SP_SITE_URL")
            site_id = resolve_sharepoint_site_id(site_url, token)

        report = {"success": True, "dry_run": bool(dry_run), "site_id": site_id, "lists": []}

        for list_id in list_ids:
            # Enumerate up to max_items + 1 so we can stop safely.
            item_ids = []
            next_link = f"/sites/{site_id}/lists/{list_id}/items?$top=999"
            while next_link:
                _, resp_body = graph_request("GET", next_link, token)
                payload = json.loads(resp_body or "{}")
                for item in payload.get("value", []):
                    item_id = item.get("id")
                    if item_id:
                        item_ids.append(item_id)
                        if len(item_ids) > max_items:
                            break
                if len(item_ids) > max_items:
                    break
                next_link = payload.get("@odata.nextLink")

            if len(item_ids) > max_items:
                report["lists"].append(
                    {
                        "list_id": list_id,
                        "success": False,
                        "error": f"List exceeds max_items_per_list ({max_items}). Refusing to purge.",
                        "items_seen": len(item_ids),
                    }
                )
                continue

            deleted = 0
            errors = 0
            if not dry_run:
                for item_id in item_ids:
                    try:
                        graph_request("DELETE", f"/sites/{site_id}/lists/{list_id}/items/{item_id}", token)
                        deleted += 1
                    except Exception as exc:
                        errors += 1
                        logging.error("Purge delete failed list=%s item=%s: %s", list_id, item_id, str(exc))

            report["lists"].append(
                {
                    "list_id": list_id,
                    "items_found": len(item_ids),
                    "deleted": deleted,
                    "errors": errors,
                    "success": errors == 0 and (deleted == len(item_ids) if not dry_run else True),
                }
            )

        return func.HttpResponse(
            json.dumps(report, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Erro no purge-lists: %s", str(e))
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )


def get_pbi_token():
    tenant_id = get_required_env("PBI_TENANT_ID")
    client_id = get_required_env("PBI_CLIENT_ID")
    client_secret = get_required_env("PBI_CLIENT_SECRET")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    data = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
    ).encode("utf-8")

    req = Request(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"Token request failed ({exc.code}): {body}") from exc

    access_token = payload.get("access_token")
    if not access_token:
        raise RuntimeError("Token response missing access_token")
    return access_token


def pbi_request(method, path, token, body=None):
    base_url = "https://api.powerbi.com/v1.0/myorg"
    url = f"{base_url}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, resp_body
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"PBI API error ({exc.code}): {body}") from exc


@app.route(route="pbi-workspace", auth_level=func.AuthLevel.FUNCTION)
def pbi_workspace(req: func.HttpRequest) -> func.HttpResponse:
    """
    Ensures a Power BI workspace exists and returns its id.
    Input: workspace_name (default PBI_API_Access), create_if_missing (default True)
    """
    logging.info("Power BI workspace ensure iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_name = req_body.get("workspace_name", "PBI_API_Access")
        create_if_missing = req_body.get("create_if_missing", True)

        token = get_pbi_token()
        _, body = pbi_request("GET", "/groups", token)
        groups = json.loads(body or "{}").get("value", [])

        workspace = None
        for group in groups:
            if group.get("name", "").strip().lower() == workspace_name.strip().lower():
                workspace = group
                break

        created = False
        if workspace is None and create_if_missing:
            _, body = pbi_request("POST", "/groups", token, {"name": workspace_name})
            workspace = json.loads(body or "{}")
            created = True

        if workspace is None:
            return func.HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "error": f"Workspace '{workspace_name}' not found",
                    }
                ),
                status_code=404,
                mimetype="application/json",
            )

        resultado = {
            "success": True,
            "workspace_name": workspace.get("name"),
            "workspace_id": workspace.get("id"),
            "created": created,
        }
        resultado = to_native_obj(resultado)
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI workspace: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


# =============================================================================
# POWER BI API - DATASETS
# =============================================================================


@app.route(route="pbi-datasets", auth_level=func.AuthLevel.FUNCTION)
def pbi_datasets(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista datasets de um workspace.
    Input: workspace_id (required)
    """
    logging.info("Power BI list datasets iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        if not workspace_id:
            return func.HttpResponse(
                json.dumps({"error": "workspace_id is required", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request("GET", f"/groups/{workspace_id}/datasets", token)
        datasets = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "datasets": [
                {
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "configuredBy": ds.get("configuredBy"),
                    "isRefreshable": ds.get("isRefreshable"),
                    "isOnPremGatewayRequired": ds.get("isOnPremGatewayRequired"),
                }
                for ds in datasets
            ],
            "count": len(datasets),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI datasets: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-dataset-refresh", auth_level=func.AuthLevel.FUNCTION)
def pbi_dataset_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    Dispara refresh de um dataset.
    Input: workspace_id, dataset_id, notify_option (optional: NoNotification, MailOnFailure, MailOnCompletion)
    """
    logging.info("Power BI dataset refresh iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        dataset_id = req_body.get("dataset_id")
        notify_option = req_body.get("notify_option", "NoNotification")

        if not workspace_id or not dataset_id:
            return func.HttpResponse(
                json.dumps(
                    {"error": "workspace_id and dataset_id are required", "success": False}
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        refresh_body = {"notifyOption": notify_option}
        
        try:
            pbi_request(
                "POST",
                f"/groups/{workspace_id}/datasets/{dataset_id}/refreshes",
                token,
                refresh_body,
            )
        except RuntimeError as e:
            # 202 Accepted is expected for async refresh
            if "202" not in str(e):
                raise

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
            "message": "Refresh triggered successfully",
            "notify_option": notify_option,
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=202,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI dataset refresh: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-dataset-refresh-history", auth_level=func.AuthLevel.FUNCTION)
def pbi_dataset_refresh_history(req: func.HttpRequest) -> func.HttpResponse:
    """
    Obtém histórico de refresh de um dataset.
    Input: workspace_id, dataset_id, top (optional, default 5)
    """
    logging.info("Power BI dataset refresh history iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        dataset_id = req_body.get("dataset_id")
        top = req_body.get("top", 5)

        if not workspace_id or not dataset_id:
            return func.HttpResponse(
                json.dumps(
                    {"error": "workspace_id and dataset_id are required", "success": False}
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request(
            "GET",
            f"/groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top}",
            token,
        )
        refreshes = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
            "refreshes": [
                {
                    "requestId": r.get("requestId"),
                    "status": r.get("status"),
                    "startTime": r.get("startTime"),
                    "endTime": r.get("endTime"),
                    "refreshType": r.get("refreshType"),
                }
                for r in refreshes
            ],
            "count": len(refreshes),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI refresh history: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


# =============================================================================
# POWER BI API - REPORTS
# =============================================================================


@app.route(route="pbi-reports", auth_level=func.AuthLevel.FUNCTION)
def pbi_reports(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista reports de um workspace.
    Input: workspace_id (required)
    """
    logging.info("Power BI list reports iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        if not workspace_id:
            return func.HttpResponse(
                json.dumps({"error": "workspace_id is required", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request("GET", f"/groups/{workspace_id}/reports", token)
        reports = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "reports": [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "datasetId": r.get("datasetId"),
                    "webUrl": r.get("webUrl"),
                    "embedUrl": r.get("embedUrl"),
                }
                for r in reports
            ],
            "count": len(reports),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI reports: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-report-clone", auth_level=func.AuthLevel.FUNCTION)
def pbi_report_clone(req: func.HttpRequest) -> func.HttpResponse:
    """
    Clona um report para outro workspace.
    Input: workspace_id, report_id, target_workspace_id, new_name
    """
    logging.info("Power BI clone report iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        report_id = req_body.get("report_id")
        target_workspace_id = req_body.get("target_workspace_id")
        new_name = req_body.get("new_name")

        if not all([workspace_id, report_id, new_name]):
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "workspace_id, report_id, and new_name are required",
                        "success": False,
                    }
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        clone_body = {"name": new_name}
        if target_workspace_id:
            clone_body["targetWorkspaceId"] = target_workspace_id

        _, body = pbi_request(
            "POST",
            f"/groups/{workspace_id}/reports/{report_id}/Clone",
            token,
            clone_body,
        )
        cloned_report = json.loads(body or "{}")

        resultado = {
            "success": True,
            "cloned_report": {
                "id": cloned_report.get("id"),
                "name": cloned_report.get("name"),
                "webUrl": cloned_report.get("webUrl"),
            },
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI clone report: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


# =============================================================================
# POWER BI API - DASHBOARDS
# =============================================================================


@app.route(route="pbi-dashboards", auth_level=func.AuthLevel.FUNCTION)
def pbi_dashboards(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista dashboards de um workspace.
    Input: workspace_id (required)
    """
    logging.info("Power BI list dashboards iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        if not workspace_id:
            return func.HttpResponse(
                json.dumps({"error": "workspace_id is required", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request("GET", f"/groups/{workspace_id}/dashboards", token)
        dashboards = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dashboards": [
                {
                    "id": d.get("id"),
                    "displayName": d.get("displayName"),
                    "webUrl": d.get("webUrl"),
                    "embedUrl": d.get("embedUrl"),
                    "isReadOnly": d.get("isReadOnly"),
                }
                for d in dashboards
            ],
            "count": len(dashboards),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI dashboards: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-dashboard-tiles", auth_level=func.AuthLevel.FUNCTION)
def pbi_dashboard_tiles(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista tiles de um dashboard.
    Input: workspace_id, dashboard_id
    """
    logging.info("Power BI list dashboard tiles iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        dashboard_id = req_body.get("dashboard_id")

        if not workspace_id or not dashboard_id:
            return func.HttpResponse(
                json.dumps(
                    {"error": "workspace_id and dashboard_id are required", "success": False}
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request(
            "GET", f"/groups/{workspace_id}/dashboards/{dashboard_id}/tiles", token
        )
        tiles = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dashboard_id": dashboard_id,
            "tiles": [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "reportId": t.get("reportId"),
                    "datasetId": t.get("datasetId"),
                    "embedUrl": t.get("embedUrl"),
                }
                for t in tiles
            ],
            "count": len(tiles),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI dashboard tiles: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


# =============================================================================
# POWER BI API - DATASOURCES & GATEWAYS
# =============================================================================


@app.route(route="pbi-datasources", auth_level=func.AuthLevel.FUNCTION)
def pbi_datasources(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista datasources de um dataset.
    Input: workspace_id, dataset_id
    """
    logging.info("Power BI list datasources iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        dataset_id = req_body.get("dataset_id")

        if not workspace_id or not dataset_id:
            return func.HttpResponse(
                json.dumps(
                    {"error": "workspace_id and dataset_id are required", "success": False}
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request(
            "GET", f"/groups/{workspace_id}/datasets/{dataset_id}/datasources", token
        )
        datasources = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
            "datasources": [
                {
                    "datasourceId": ds.get("datasourceId"),
                    "datasourceType": ds.get("datasourceType"),
                    "gatewayId": ds.get("gatewayId"),
                    "connectionDetails": ds.get("connectionDetails"),
                }
                for ds in datasources
            ],
            "count": len(datasources),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI datasources: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-gateways", auth_level=func.AuthLevel.FUNCTION)
def pbi_gateways(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista gateways disponíveis.
    """
    logging.info("Power BI list gateways iniciado...")

    try:
        token = get_pbi_token()
        _, body = pbi_request("GET", "/gateways", token)
        gateways = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "gateways": [
                {
                    "id": g.get("id"),
                    "name": g.get("name"),
                    "type": g.get("type"),
                    "publicKey": g.get("publicKey"),
                }
                for g in gateways
            ],
            "count": len(gateways),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI gateways: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-dataset-bind-gateway", auth_level=func.AuthLevel.FUNCTION)
def pbi_dataset_bind_gateway(req: func.HttpRequest) -> func.HttpResponse:
    """
    Vincula um dataset a um gateway.
    Input: workspace_id, dataset_id, gateway_id
    """
    logging.info("Power BI bind dataset to gateway iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        dataset_id = req_body.get("dataset_id")
        gateway_id = req_body.get("gateway_id")

        if not all([workspace_id, dataset_id, gateway_id]):
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "workspace_id, dataset_id, and gateway_id are required",
                        "success": False,
                    }
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        bind_body = {"gatewayObjectId": gateway_id}
        pbi_request(
            "POST",
            f"/groups/{workspace_id}/datasets/{dataset_id}/Default.BindToGateway",
            token,
            bind_body,
        )

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
            "gateway_id": gateway_id,
            "message": "Dataset bound to gateway successfully",
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI bind gateway: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


# =============================================================================
# POWER BI API - IMPORT & CAPACITY
# =============================================================================


@app.route(route="pbi-import-status", auth_level=func.AuthLevel.FUNCTION)
def pbi_import_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Verifica status de uma importação.
    Input: workspace_id, import_id
    """
    logging.info("Power BI import status iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        import_id = req_body.get("import_id")

        if not workspace_id or not import_id:
            return func.HttpResponse(
                json.dumps(
                    {"error": "workspace_id and import_id are required", "success": False}
                ),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()
        _, body = pbi_request("GET", f"/groups/{workspace_id}/imports/{import_id}", token)
        import_info = json.loads(body or "{}")

        resultado = {
            "success": True,
            "workspace_id": workspace_id,
            "import_id": import_id,
            "name": import_info.get("name"),
            "importState": import_info.get("importState"),
            "datasets": import_info.get("datasets", []),
            "reports": import_info.get("reports", []),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI import status: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-capacities", auth_level=func.AuthLevel.FUNCTION)
def pbi_capacities(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista capacidades disponíveis.
    """
    logging.info("Power BI list capacities iniciado...")

    try:
        token = get_pbi_token()
        _, body = pbi_request("GET", "/capacities", token)
        capacities = json.loads(body or "{}").get("value", [])

        resultado = {
            "success": True,
            "capacities": [
                {
                    "id": c.get("id"),
                    "displayName": c.get("displayName"),
                    "sku": c.get("sku"),
                    "state": c.get("state"),
                    "region": c.get("region"),
                }
                for c in capacities
            ],
            "count": len(capacities),
        }
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI capacities: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="pbi-workspace-users", auth_level=func.AuthLevel.FUNCTION)
def pbi_workspace_users(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista ou adiciona usuários a um workspace.
    Input: workspace_id, action (list/add), user_email (for add), access_right (for add: Admin, Member, Contributor, Viewer)
    """
    logging.info("Power BI workspace users iniciado...")

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}

        workspace_id = req_body.get("workspace_id")
        action = req_body.get("action", "list")

        if not workspace_id:
            return func.HttpResponse(
                json.dumps({"error": "workspace_id is required", "success": False}),
                status_code=400,
                mimetype="application/json",
            )

        token = get_pbi_token()

        if action == "add":
            user_email = req_body.get("user_email")
            access_right = req_body.get("access_right", "Viewer")
            
            if not user_email:
                return func.HttpResponse(
                    json.dumps({"error": "user_email is required for add action", "success": False}),
                    status_code=400,
                    mimetype="application/json",
                )

            add_body = {
                "emailAddress": user_email,
                "groupUserAccessRight": access_right,
            }
            pbi_request("POST", f"/groups/{workspace_id}/users", token, add_body)

            resultado = {
                "success": True,
                "workspace_id": workspace_id,
                "action": "add",
                "user_email": user_email,
                "access_right": access_right,
                "message": "User added successfully",
            }
        else:
            _, body = pbi_request("GET", f"/groups/{workspace_id}/users", token)
            users = json.loads(body or "{}").get("value", [])

            resultado = {
                "success": True,
                "workspace_id": workspace_id,
                "action": "list",
                "users": [
                    {
                        "emailAddress": u.get("emailAddress"),
                        "displayName": u.get("displayName"),
                        "groupUserAccessRight": u.get("groupUserAccessRight"),
                        "principalType": u.get("principalType"),
                    }
                    for u in users
                ],
                "count": len(users),
            }

        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error("Erro Power BI workspace users: %s", str(e))
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            status_code=500,
            mimetype="application/json",
        )
