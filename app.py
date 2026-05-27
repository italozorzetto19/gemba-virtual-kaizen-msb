
from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
import html
import json
import uuid

import pandas as pd
import plotly.express as px
import streamlit as st


APP_TITLE = "VOC Kaizen + SIPOC"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "gemba_registros.csv"
SIPOC_FILE = DATA_DIR / "sipoc_registros.csv"
FLOW_FILE = DATA_DIR / "fluxogramas.json"

COLUMNS = [
    "id_registro",
    "data_registro",
    "registrado_por",
    "setor_registrante",
    "local_gemba",
    "origem_informacao",
    "stakeholder_origem",
    "tipo_entrada",
    "foco_registro",
    "produto_linha",
    "descricao",
    "evidencia",
    "frequencia_percebida",
    "impacto_percebido",
    "impacto_engenharia",
    "status",
    "responsavel",
    "acao_sugerida",
    "observacoes",
    "pontuacao",
    "prioridade",
]

# SIPOC enxuto: somente as 5 colunas pedidas.
SIPOC_COLUMNS = [
    "fornecedores",
    "entradas",
    "processo",
    "saidas",
    "clientes",
]

SETORES = [
    "Comercial", "Engenharia", "Qualidade", "P&D", "Produção", "Regulatórios",
    "Compras", "Logística", "Marketing", "Diretoria", "Fornecedor/Parceiro", "Outro"
]

LOCAIS_GEMBA = [
    "Comercial", "Qualidade/SAC", "Engenharia/P&D", "Produção", "Regulatórios",
    "Logística/Expedição", "Treinamento", "Feira/Evento", "Fornecedor", "Cliente/Hospital", "Outro"
]

ORIGENS = [
    "Cliente", "Médico", "Enfermeiro/equipe assistencial", "Comprador/Hospital",
    "Distribuidor", "Representante", "Comercial interno", "Fornecedor", "Concorrente",
    "Feira/Congresso", "Observação interna", "Agente virtual/Radar de mercado", "Outro"
]

TIPOS_ENTRADA = [
    "Reclamação", "Sugestão de melhoria", "Elogio", "Dúvida recorrente",
    "Pedido de novo produto/medida", "Nova tecnologia/inovação", "Comparação com concorrente",
    "Ideia interna", "Problema de embalagem", "Problema de rotulagem/IFU",
    "Demanda de mercado", "Fornecedor sugerindo solução", "Outro"
]

FOCOS = [
    "Produto MSB", "Produto concorrente", "Novo produto", "Nova tecnologia", "Embalagem",
    "Rotulagem", "IFU/Instrução de uso", "Processo interno", "Atendimento/Suporte",
    "Preço/Prazo/Disponibilidade", "Portfólio", "Outro"
]

STATUS = ["Novo", "Em triagem", "Em análise", "Ação aberta", "Monitoramento", "Concluído", "Descartado"]

FLOW_TYPES = {
    "Início/Fim": {
        "class": "terminal",
        "svg": '<ellipse cx="80" cy="45" rx="70" ry="30"></ellipse>',
        "default": "Início",
    },
    "Processo": {
        "class": "process",
        "svg": '<rect x="12" y="15" width="136" height="60" rx="8"></rect>',
        "default": "Processo",
    },
    "Decisão": {
        "class": "decision",
        "svg": '<polygon points="80,8 150,45 80,82 10,45"></polygon>',
        "default": "Decisão?",
    },
    "Documento": {
        "class": "document",
        "svg": '<path d="M15 12 H145 V62 Q105 88 15 66 Z"></path>',
        "default": "Documento",
    },
    "Input/Output": {
        "class": "io",
        "svg": '<polygon points="28,12 150,12 132,78 10,78"></polygon>',
        "default": "Entrada/Saída",
    },
    "Database": {
        "class": "database",
        "svg": '<ellipse cx="80" cy="18" rx="65" ry="12"></ellipse><path d="M15 18 V70 C15 85 145 85 145 70 V18"></path><ellipse cx="80" cy="70" rx="65" ry="12"></ellipse>',
        "default": "Base de dados",
    },
    "Atraso/Espera": {
        "class": "delay",
        "svg": '<path d="M25 12 H88 C126 12 150 28 150 45 C150 62 126 78 88 78 H25 Z"></path>',
        "default": "Aguardar",
    },
    "Armazenamento": {
        "class": "storage",
        "svg": '<path d="M20 12 H140 V58 L80 84 L20 58 Z"></path>',
        "default": "Armazenar",
    },
}


def init_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    if not SIPOC_FILE.exists():
        pd.DataFrame(columns=SIPOC_COLUMNS).to_csv(SIPOC_FILE, index=False, encoding="utf-8-sig")
    if not FLOW_FILE.exists():
        FLOW_FILE.write_text("{}", encoding="utf-8")


def load_data() -> pd.DataFrame:
    init_files()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]


def save_data(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


def load_sipoc() -> pd.DataFrame:
    init_files()
    df = pd.read_csv(SIPOC_FILE, encoding="utf-8-sig")

    # Compatibilidade com versões antigas do arquivo.
    rename_map = {
        "supplier": "fornecedores",
        "input": "entradas",
        "processo_atual": "processo",
        "output_esperado": "saidas",
        "customer": "clientes",
    }
    df = df.rename(columns=rename_map)

    for col in SIPOC_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[SIPOC_COLUMNS].fillna("")
    return df


def save_sipoc(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df = df.copy().fillna("")
    df[SIPOC_COLUMNS].to_csv(SIPOC_FILE, index=False, encoding="utf-8-sig")


def load_flows() -> dict:
    init_files()
    try:
        return json.loads(FLOW_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_flows(flows: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    FLOW_FILE.write_text(json.dumps(flows, ensure_ascii=False, indent=2), encoding="utf-8")


def sipoc_key(row: pd.Series, index: int) -> str:
    seed = "|".join(str(row.get(c, "")) for c in SIPOC_COLUMNS)
    if not seed.strip("| "):
        seed = f"linha_{index}"
    return f"sipoc_{index}_{abs(hash(seed))}"


def gerar_id(df: pd.DataFrame) -> str:
    ano = datetime.now().year
    existentes = df["id_registro"].astype(str).str.extract(rf"GV-{ano}-(\d+)")[0].dropna()
    prox = int(existentes.astype(int).max()) + 1 if not existentes.empty else 1
    return f"GV-{ano}-{prox:04d}"


def calcular_pontuacao(frequencia: str, impacto_cliente: str, impacto_eng: str, evidencia: str) -> tuple[int, str]:
    freq_map = {"Caso único": 1, "Algumas vezes": 2, "Recorrente": 3, "Não sei": 1}
    impacto_map = {"Baixo": 1, "Médio": 2, "Alto": 3, "Crítico": 4, "Não sei": 1}
    evidencia_score = 2 if evidencia and evidencia != "Sem evidência" else 0
    score = freq_map.get(frequencia, 1) + impacto_map.get(impacto_cliente, 1) + impacto_map.get(impacto_eng, 1) + evidencia_score
    if score >= 9:
        prioridade = "Alta"
    elif score >= 6:
        prioridade = "Média"
    else:
        prioridade = "Baixa"
    return score, prioridade


def safe(text: str) -> str:
    return html.escape(str(text or "")).replace("\n", "<br>")


def render_header():
    st.set_page_config(page_title=APP_TITLE, page_icon="📌", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.3rem; padding-bottom: 1rem;}
        div[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}
        .hero {
            background: linear-gradient(135deg, #08035f 0%, #17108f 58%, #311b92 100%);
            color: white; padding: 20px 24px; border-radius: 20px; margin-bottom: 18px;
            box-shadow: 0 12px 30px rgba(8,3,95,0.18);
        }
        .hero h1 {font-size: 2.0rem; margin: 0; letter-spacing: 0.4px;}
        .hero p {margin: 6px 0 0 0; opacity: 0.9;}
        .section-label {font-size: .82rem; text-transform: uppercase; letter-spacing: .08em; color:#64748b; font-weight:800;}
        .sipoc-header {
            background: #08035f; color: white; text-align: center; padding: 18px; border-radius: 18px 18px 0 0;
            font-size: 2.1rem; font-weight: 900; letter-spacing: 2px; margin-top: 10px;
        }
        .sipoc-row {
            border: 2px solid #08035f; border-top: 0; padding: 18px 14px 22px 14px; border-radius: 0 0 18px 18px;
            background: linear-gradient(180deg,#ffffff,#f8fafc);
        }
        .sipoc-card {
            background: #fffef0; border: 2px solid #5146e5; border-radius: 12px; min-height: 190px;
            padding: 14px 12px; text-align:center; box-shadow: 0 6px 16px rgba(15,23,42,0.08);
        }
        .sipoc-card .top {font-weight: 800; color:#111827;}
        .sipoc-card .letter {font-size: 2.5rem; color: #e00000; font-weight: 900; margin-top: 7px;}
        .sipoc-card .sub {font-size: .8rem; color:#08035f; font-weight: 800; margin-bottom: 10px;}
        .sipoc-card .txt {font-size: .95rem; color:#111827; line-height: 1.35rem;}
        .arrow-big {font-size: 2.4rem; color:#08035f; font-weight: 900; text-align:center; padding-top:75px;}
        .flow-wrap {
            background: #fff; border: 2px solid #5b5cf6; border-radius: 16px; padding: 18px 20px;
            box-shadow: 0 8px 22px rgba(15,23,42,.08); margin-top: 12px;
        }
        .flow-title {
            background: #08035f; color:#fff; padding: 12px 16px; border-radius: 13px; text-align:center;
            font-weight: 900; letter-spacing: .08em; margin-bottom: 16px;
        }
        .flow-lane {display:flex; align-items:center; gap:18px; overflow-x:auto; padding: 10px 2px 18px 2px;}
        .flow-step {min-width: 170px; max-width: 230px; text-align:center;}
        .flow-arrow {font-size: 2.1rem; color:#08035f; font-weight:900; margin-top: -10px;}
        .flow-svg svg {width:160px; height:90px;}
        .flow-svg svg * {fill:#fff5b7; stroke:#d97706; stroke-width:2.2;}
        .flow-step.terminal svg * {fill:#ccfbf1; stroke:#0f766e;}
        .flow-step.decision svg * {fill:#fee2e2; stroke:#dc2626;}
        .flow-step.io svg * {fill:#dbeafe; stroke:#2563eb;}
        .flow-step.database svg * {fill:#e0f2fe; stroke:#0284c7;}
        .flow-step.delay svg * {fill:#fed7aa; stroke:#ea580c;}
        .flow-step.storage svg * {fill:#dcfce7; stroke:#16a34a;}
        .flow-text {
            margin-top: 8px; border: 1px solid #cbd5e1; border-radius: 10px; padding: 9px 10px;
            color:#0f172a; background:#f8fafc; font-size:.92rem; line-height:1.25rem; min-height:52px;
        }
        .yesno {
            margin-top:6px; font-size:.78rem; font-weight:800; color:#0f172a;
            background:#e2e8f0; border-radius:999px; display:inline-block; padding:3px 9px;
        }
        .hint-card {
            border: 1px solid #dbe3ef; background: #f8fafc; padding: 14px 16px; border-radius: 14px;
            color: #334155; margin-bottom: 12px;
        }
        .small-muted {color:#64748b; font-size:.9rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero">
          <h1>📌 VOC Kaizen + SIPOC</h1>
          <p>Gestão visual das entradas da Voz do Cliente, análise SIPOC e construção interativa do fluxograma do processo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_novo_registro(df: pd.DataFrame):
    st.subheader("Novo registro do Gemba Virtual")
    st.info("Use este formulário para registrar entradas identificadas no Gemba: relatos do cliente, sugestões, reclamações, dúvidas, elogios, demandas de mercado ou oportunidades técnicas.")

    with st.form("form_novo_registro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_registro = st.date_input("Data do registro", value=date.today())
            registrado_por = st.text_input("Registrado por", placeholder="Nome do colaborador")
            setor = st.selectbox("Setor/perfil de quem registra", SETORES)
        with col2:
            local = st.selectbox("Local do Gemba", LOCAIS_GEMBA)
            origem = st.selectbox("Origem da informação", ORIGENS)
            stakeholder = st.text_input("Quem gerou a voz?", placeholder="Ex.: médico, distribuidor, cliente, fornecedor")
        with col3:
            tipo = st.selectbox("Tipo de entrada", TIPOS_ENTRADA)
            foco = st.selectbox("Foco do registro", FOCOS)
            produto = st.text_input("Produto/linha relacionada", placeholder="Ex.: Cateter balão, PICC, Duplo J")

        descricao = st.text_area("Descrição do relato / observação", height=120, placeholder="Descreva o que foi observado, ouvido ou identificado.")

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            frequencia = st.selectbox("Frequência percebida", ["Caso único", "Algumas vezes", "Recorrente", "Não sei"])
        with col5:
            impacto_cliente = st.selectbox("Impacto percebido no cliente/mercado", ["Baixo", "Médio", "Alto", "Crítico", "Não sei"])
        with col6:
            impacto_eng = st.selectbox("Impacto potencial para Engenharia", ["Baixo", "Médio", "Alto", "Crítico", "Não sei"])
        with col7:
            evidencia = st.selectbox("Evidência disponível", ["Sem evidência", "Foto", "Vídeo", "E-mail", "Mensagem", "Amostra física", "Link", "Catálogo", "Outro"])

        col8, col9 = st.columns(2)
        with col8:
            responsavel = st.text_input("Responsável sugerido", placeholder="Ex.: Engenharia, Qualidade, Comercial")
            status = st.selectbox("Status inicial", STATUS)
        with col9:
            acao = st.text_area("Ação sugerida", height=90, placeholder="Ex.: avaliar tecnicamente, monitorar, abrir estudo, revisar IFU")
            observacoes = st.text_area("Observações", height=90)

        submitted = st.form_submit_button("Salvar registro")

    if submitted:
        if not registrado_por or not descricao:
            st.error("Preencha pelo menos 'Registrado por' e 'Descrição'.")
            return
        pontuacao, prioridade = calcular_pontuacao(frequencia, impacto_cliente, impacto_eng, evidencia)
        new_row = {
            "id_registro": gerar_id(df),
            "data_registro": str(data_registro),
            "registrado_por": registrado_por,
            "setor_registrante": setor,
            "local_gemba": local,
            "origem_informacao": origem,
            "stakeholder_origem": stakeholder,
            "tipo_entrada": tipo,
            "foco_registro": foco,
            "produto_linha": produto,
            "descricao": descricao,
            "evidencia": evidencia,
            "frequencia_percebida": frequencia,
            "impacto_percebido": impacto_cliente,
            "impacto_engenharia": impacto_eng,
            "status": status,
            "responsavel": responsavel,
            "acao_sugerida": acao,
            "observacoes": observacoes,
            "pontuacao": pontuacao,
            "prioridade": prioridade,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success(f"Registro salvo: {new_row['id_registro']} | Prioridade: {prioridade} | Pontuação: {pontuacao}")


def filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    if df.empty:
        return df
    df = df.copy()
    df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
    tipos = st.sidebar.multiselect("Tipo de entrada", sorted(df["tipo_entrada"].dropna().unique()))
    prioridades = st.sidebar.multiselect("Prioridade", sorted(df["prioridade"].dropna().unique()))
    status = st.sidebar.multiselect("Status", sorted(df["status"].dropna().unique()))
    setores = st.sidebar.multiselect("Setor registrante", sorted(df["setor_registrante"].dropna().unique()))
    if tipos:
        df = df[df["tipo_entrada"].isin(tipos)]
    if prioridades:
        df = df[df["prioridade"].isin(prioridades)]
    if status:
        df = df[df["status"].isin(status)]
    if setores:
        df = df[df["setor_registrante"].isin(setores)]
    return df


def page_dashboard(df: pd.DataFrame):
    st.subheader("Dashboard do Gemba Virtual")
    if df.empty:
        st.warning("Ainda não existem registros. Cadastre o primeiro registro no menu 'Novo registro'.")
        return
    fdf = filtros(df)
    total = len(fdf)
    alta = len(fdf[fdf["prioridade"] == "Alta"])
    em_aberto = len(fdf[~fdf["status"].isin(["Concluído", "Descartado"])])
    concluidos = len(fdf[fdf["status"] == "Concluído"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", total)
    col2.metric("Prioridade alta", alta)
    col3.metric("Em aberto", em_aberto)
    col4.metric("Concluídos", concluidos)

    col5, col6 = st.columns(2)
    with col5:
        tipo_count = fdf["tipo_entrada"].value_counts().reset_index()
        tipo_count.columns = ["Tipo", "Quantidade"]
        fig = px.bar(tipo_count, x="Tipo", y="Quantidade", title="Entradas por tipo")
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        prio_count = fdf["prioridade"].value_counts().reset_index()
        prio_count.columns = ["Prioridade", "Quantidade"]
        fig = px.pie(prio_count, names="Prioridade", values="Quantidade", title="Distribuição por prioridade")
        st.plotly_chart(fig, use_container_width=True)

    col7, col8 = st.columns(2)
    with col7:
        origem_count = fdf["origem_informacao"].value_counts().reset_index().head(10)
        origem_count.columns = ["Origem", "Quantidade"]
        fig = px.bar(origem_count, x="Origem", y="Quantidade", title="Principais origens")
        st.plotly_chart(fig, use_container_width=True)
    with col8:
        status_count = fdf["status"].value_counts().reset_index()
        status_count.columns = ["Status", "Quantidade"]
        fig = px.bar(status_count, x="Status", y="Quantidade", title="Status dos registros")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Base filtrada")
    st.dataframe(fdf.sort_values("id_registro", ascending=False), use_container_width=True, hide_index=True)
    csv = fdf.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("Baixar CSV filtrado", data=csv, file_name="gemba_virtual_filtrado.csv", mime="text/csv")


def render_sipoc_visual(row: pd.Series):
    values = {
        "Fornecedores": row.get("fornecedores", ""),
        "Entradas": row.get("entradas", ""),
        "Processo": row.get("processo", ""),
        "Saídas": row.get("saidas", ""),
        "Clientes": row.get("clientes", ""),
    }
    letters = {"Fornecedores": "S", "Entradas": "I", "Processo": "P", "Saídas": "O", "Clientes": "C"}
    subtitles = {"Fornecedores": "Suppliers", "Entradas": "Inputs", "Processo": "Process", "Saídas": "Outputs", "Clientes": "Customers"}

    st.markdown("<div class='sipoc-header'>SIPOC</div><div class='sipoc-row'>", unsafe_allow_html=True)
    cols = st.columns([1, .18, 1, .18, 1, .18, 1, .18, 1])
    card_order = ["Fornecedores", "Entradas", "Processo", "Saídas", "Clientes"]
    col_i = 0
    for i, item in enumerate(card_order):
        with cols[col_i]:
            st.markdown(
                f"""
                <div class="sipoc-card">
                    <div class="top">{item}</div>
                    <div class="letter">{letters[item]}</div>
                    <div class="sub">{subtitles[item]}</div>
                    <div class="txt">{safe(values[item]) or "-"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        col_i += 1
        if i < len(card_order) - 1:
            with cols[col_i]:
                st.markdown("<div class='arrow-big'>➜</div>", unsafe_allow_html=True)
            col_i += 1
    st.markdown("</div>", unsafe_allow_html=True)


def get_flow_for_key(flows: dict, key: str, row: pd.Series | None = None) -> list[dict]:
    if key in flows and isinstance(flows[key], list):
        return flows[key]
    processo = ""
    if row is not None:
        processo = str(row.get("processo", "") or "")
    return [
        {"id": str(uuid.uuid4()), "tipo": "Início/Fim", "texto": "Início", "sim": "", "nao": ""},
        {"id": str(uuid.uuid4()), "tipo": "Input/Output", "texto": "Receber entrada VOC", "sim": "", "nao": ""},
        {"id": str(uuid.uuid4()), "tipo": "Processo", "texto": processo or "Registrar no app", "sim": "", "nao": ""},
        {"id": str(uuid.uuid4()), "tipo": "Decisão", "texto": "Necessita análise técnica?", "sim": "Sim: encaminhar", "nao": "Não: monitorar"},
        {"id": str(uuid.uuid4()), "tipo": "Processo", "texto": "Definir responsável", "sim": "", "nao": ""},
        {"id": str(uuid.uuid4()), "tipo": "Início/Fim", "texto": "Fim", "sim": "", "nao": ""},
    ]


def render_flowchart(steps: list[dict]):
    html_parts = ["<div class='flow-wrap'><div class='flow-title'>FLUXOGRAMA DO PROCESSO</div><div class='flow-lane'>"]
    for i, step in enumerate(steps):
        tipo = step.get("tipo", "Processo")
        cfg = FLOW_TYPES.get(tipo, FLOW_TYPES["Processo"])
        texto = step.get("texto", "")
        yesno = ""
        if tipo == "Decisão":
            sim = step.get("sim", "")
            nao = step.get("nao", "")
            if sim or nao:
                yesno = f"<div class='yesno'>{safe(sim)} &nbsp; | &nbsp; {safe(nao)}</div>"
        html_parts.append(
            f"""
            <div class="flow-step {cfg['class']}">
                <div class="flow-svg">
                    <svg viewBox="0 0 160 90">{cfg['svg']}</svg>
                </div>
                <div class="flow-text">{safe(texto) or "-"}</div>
                {yesno}
            </div>
            """
        )
        if i < len(steps) - 1:
            html_parts.append("<div class='flow-arrow'>➜</div>")
    html_parts.append("</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def page_sipoc(sipoc_df: pd.DataFrame):
    st.subheader("SIPOC + Construtor de Fluxograma")
    st.markdown(
        """
        <div class="hint-card">
        <b>Uso em reunião:</b> primeiro preencha somente as 5 colunas do SIPOC.
        Depois salve e escolha uma linha para montar o fluxograma com ícones tradicionais.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["1. Matriz SIPOC", "2. Visual + Fluxograma"])

    with tab1:
        st.markdown("### Matriz para preenchimento")
        st.caption("Apenas as 5 colunas do SIPOC. Adicione quantas linhas precisar durante a reunião.")

        editor_df = sipoc_df.copy()
        if editor_df.empty:
            editor_df = pd.DataFrame([
                {
                    "fornecedores": "Comercial / Médico / Distribuidor",
                    "entradas": "Relato de melhoria, reclamação, dúvida ou demanda de mercado",
                    "processo": "Informação chega por WhatsApp, e-mail ou conversa e pode ficar dispersa",
                    "saidas": "Entrada VOC estruturada e priorizada",
                    "clientes": "Engenharia / Qualidade / Comercial",
                }
            ])

        edited = st.data_editor(
            editor_df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "fornecedores": st.column_config.TextColumn("S — Supplier / Fornecedor", width="medium"),
                "entradas": st.column_config.TextColumn("I — Input / Entrada", width="large"),
                "processo": st.column_config.TextColumn("P — Processo", width="large"),
                "saidas": st.column_config.TextColumn("O — Output / Saída", width="large"),
                "clientes": st.column_config.TextColumn("C — Customer / Cliente", width="medium"),
            },
            key="sipoc_editor_somente_5_colunas",
        )

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Salvar SIPOC", type="primary"):
                edited = edited.fillna("")
                save_sipoc(edited[SIPOC_COLUMNS])
                st.success("SIPOC salvo. Vá para a aba Visual + Fluxograma.")
        with c2:
            if st.button("Limpar SIPOC"):
                save_sipoc(pd.DataFrame(columns=SIPOC_COLUMNS))
                st.success("SIPOC limpo. Atualize a página para reiniciar.")
        with c3:
            csv = edited.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("Baixar SIPOC CSV", data=csv, file_name="sipoc.csv", mime="text/csv")

    with tab2:
        visual_df = sipoc_df.copy()
        if visual_df.empty:
            st.info("Preencha e salve a matriz SIPOC na aba 1 para visualizar.")
            return

        visual_df = visual_df.fillna("")
        labels = []
        for i, row in visual_df.iterrows():
            entrada = str(row.get("entradas", "")).strip()
            labels.append(f"{i+1}. {entrada[:80] if entrada else 'Linha SIPOC'}")

        idx = st.selectbox("Escolha a linha SIPOC", list(range(len(labels))), format_func=lambda i: labels[i])
        row = visual_df.iloc[idx]
        key = sipoc_key(row, idx)

        render_sipoc_visual(row)

        st.markdown("### Fluxograma do processo")
        flows = load_flows()
        steps = get_flow_for_key(flows, key, row)
        render_flowchart(steps)

        st.markdown("### Ferramenta de construção")
        st.caption("Clique em iniciar montagem para abrir o construtor. A seleção do tipo de tarefa define automaticamente o ícone do fluxograma.")

        if "builder_open" not in st.session_state:
            st.session_state.builder_open = False

        colb1, colb2, colb3 = st.columns([1.2, 1, 2])
        with colb1:
            if st.button("Iniciar montagem", type="primary"):
                st.session_state.builder_open = True
        with colb2:
            if st.button("Resetar fluxo"):
                flows[key] = get_flow_for_key({}, key, row)
                save_flows(flows)
                st.success("Fluxo resetado.")
                st.rerun()

        if st.session_state.builder_open:
            with st.container(border=True):
                st.markdown("#### Montagem do fluxograma")
                st.markdown("<span class='small-muted'>Adicione, edite, reordene ou remova etapas. Para decisões, preencha os caminhos de Sim e Não.</span>", unsafe_allow_html=True)

                # Editor das etapas existentes
                steps_df = pd.DataFrame(steps)
                if steps_df.empty:
                    steps_df = pd.DataFrame(columns=["tipo", "texto", "sim", "nao"])
                if "tipo" not in steps_df.columns:
                    steps_df["tipo"] = "Processo"
                if "texto" not in steps_df.columns:
                    steps_df["texto"] = ""
                if "sim" not in steps_df.columns:
                    steps_df["sim"] = ""
                if "nao" not in steps_df.columns:
                    steps_df["nao"] = ""

                edited_steps = st.data_editor(
                    steps_df[["tipo", "texto", "sim", "nao"]],
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=False,
                    column_config={
                        "tipo": st.column_config.SelectboxColumn("Tipo de tarefa / ícone", options=list(FLOW_TYPES.keys()), required=True),
                        "texto": st.column_config.TextColumn("Texto da etapa", width="large"),
                        "sim": st.column_config.TextColumn("Caminho Sim", width="medium"),
                        "nao": st.column_config.TextColumn("Caminho Não", width="medium"),
                    },
                    key=f"flow_editor_{key}",
                )

                ca, cb, cc = st.columns([1, 1, 2])
                with ca:
                    if st.button("Salvar fluxograma", type="primary"):
                        new_steps = []
                        for _, srow in edited_steps.fillna("").iterrows():
                            tipo = srow.get("tipo", "Processo") or "Processo"
                            texto = srow.get("texto", "") or FLOW_TYPES.get(tipo, FLOW_TYPES["Processo"])["default"]
                            new_steps.append({
                                "id": str(uuid.uuid4()),
                                "tipo": tipo,
                                "texto": texto,
                                "sim": srow.get("sim", ""),
                                "nao": srow.get("nao", ""),
                            })
                        flows[key] = new_steps
                        save_flows(flows)
                        st.success("Fluxograma salvo.")
                        st.rerun()
                with cb:
                    if st.button("Fechar montagem"):
                        st.session_state.builder_open = False
                        st.rerun()
                with cc:
                    flow_json = json.dumps(steps, ensure_ascii=False, indent=2)
                    st.download_button("Baixar fluxograma JSON", data=flow_json.encode("utf-8"), file_name="fluxograma.json", mime="application/json")


def page_matriz(df: pd.DataFrame):
    st.subheader("Matriz de priorização")
    st.write("A pontuação é calculada com base em frequência, impacto no cliente/mercado, impacto para Engenharia e evidência disponível.")
    st.table(pd.DataFrame([
        {"Critério": "Frequência", "Baixo": "Caso único = 1", "Médio": "Algumas vezes = 2", "Alto": "Recorrente = 3"},
        {"Critério": "Impacto no cliente/mercado", "Baixo": "1", "Médio": "2", "Alto": "3", "Crítico": "4"},
        {"Critério": "Impacto para Engenharia", "Baixo": "1", "Médio": "2", "Alto": "3", "Crítico": "4"},
        {"Critério": "Evidência", "Baixo": "Sem evidência = 0", "Médio": "", "Alto": "Com evidência = 2"},
    ]))
    st.markdown("**Classificação:** até 5 = Baixa | 6 a 8 = Média | 9 ou mais = Alta")

    if not df.empty:
        st.markdown("### Registros de maior prioridade")
        top = df.sort_values(["pontuacao"], ascending=False).head(15)
        st.dataframe(top[["id_registro", "tipo_entrada", "produto_linha", "prioridade", "pontuacao", "status", "descricao"]], use_container_width=True, hide_index=True)


def page_roteiro():
    st.subheader("Roteiro de Gemba Walk VOC")
    st.markdown("""
Use este roteiro para investigar onde a Voz do Cliente aparece e quais entradas devem existir no aplicativo.

**Perguntas sugeridas:**

1. Que tipo de informação de cliente chega até este setor?
2. Como essa informação chega hoje? WhatsApp, e-mail, ligação, reunião ou sistema?
3. A informação é registrada em algum lugar?
4. Quais informações costumam se perder?
5. O que deveria chegar para Engenharia?
6. Quais relatos são reclamações, sugestões, elogios, dúvidas ou demandas de mercado?
7. Existem exemplos recentes?
8. Que evidência normalmente acompanha o relato?
9. Quem deveria receber a informação depois do registro?
10. Qual entrada seria mais útil no aplicativo?

**Saída esperada do Gemba:** lista de entradas, responsáveis, fontes, problemas atuais e oportunidades de padronização.
""")


def main():
    render_header()
    df = load_data()
    sipoc_df = load_sipoc()
    menu = st.sidebar.radio(
        "Menu",
        [
            "Novo registro",
            "Dashboard",
            "SIPOC + Fluxograma",
            "Matriz de priorização",
            "Roteiro Gemba",
            "Base completa",
        ],
    )

    if menu == "Novo registro":
        page_novo_registro(df)
    elif menu == "Dashboard":
        page_dashboard(df)
    elif menu == "SIPOC + Fluxograma":
        page_sipoc(sipoc_df)
    elif menu == "Matriz de priorização":
        page_matriz(df)
    elif menu == "Roteiro Gemba":
        page_roteiro()
    elif menu == "Base completa":
        st.subheader("Base completa")
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("Baixar base completa", data=csv, file_name="gemba_registros.csv", mime="text/csv")


if __name__ == "__main__":
    main()
