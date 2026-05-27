
from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
import json
import uuid

import pandas as pd
import plotly.express as px
import streamlit as st


APP_TITLE = "VOC Kaizen + SIPOC + Fluxograma"
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

SIPOC_COLUMNS = [
    "fornecedores",
    "entradas",
    "processo",
    "saidas",
    "clientes",
]

FLOW_COLUMNS = [
    "ordem",
    "tipo",
    "texto",
    "sim",
    "nao",
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

FLOW_TYPES = [
    "Início/Fim",
    "Processo",
    "Decisão",
    "Documento",
    "Input/Output",
    "Banco de dados",
    "Espera/Atraso",
    "Armazenamento",
]

DOT_SHAPES = {
    "Início/Fim": "oval",
    "Processo": "box",
    "Decisão": "diamond",
    "Documento": "note",
    "Input/Output": "parallelogram",
    "Banco de dados": "cylinder",
    "Espera/Atraso": "cds",
    "Armazenamento": "folder",
}


def default_sipoc() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "fornecedores": "Comercial",
            "entradas": "Relato de cliente, reclamação, sugestão ou dúvida",
            "processo": "Informação chega por WhatsApp, e-mail ou conversa informal",
            "saidas": "Entrada VOC estruturada e priorizada",
            "clientes": "Engenharia / Qualidade / Comercial",
        },
        {
            "fornecedores": "Engenharia",
            "entradas": "Ideia técnica ou oportunidade de melhoria",
            "processo": "Avaliação preliminar da viabilidade técnica",
            "saidas": "Proposta de melhoria ou estudo técnico",
            "clientes": "P&D / Qualidade / Produção",
        },
        {
            "fornecedores": "Médico / Hospital",
            "entradas": "Dificuldade de uso, sugestão de medida ou comparação com concorrente",
            "processo": "Registro pelo app e classificação do tipo de entrada",
            "saidas": "Demanda técnica para triagem",
            "clientes": "Engenharia / Comercial",
        },
        {
            "fornecedores": "Agente Radar",
            "entradas": "Sinal de mercado, nova tecnologia, patente, edital ou concorrente",
            "processo": "Pesquisa online, resumo e classificação do achado",
            "saidas": "Oportunidade de inovação ou benchmarking",
            "clientes": "Engenharia / P&D / Comercial",
        },
        {
            "fornecedores": "",
            "entradas": "",
            "processo": "",
            "saidas": "",
            "clientes": "",
        },
    ])


def default_flow() -> list[dict]:
    return [
        {"ordem": 1, "tipo": "Início/Fim", "texto": "Início", "sim": "", "nao": ""},
        {"ordem": 2, "tipo": "Input/Output", "texto": "Receber entrada VOC", "sim": "", "nao": ""},
        {"ordem": 3, "tipo": "Processo", "texto": "Registrar no app", "sim": "", "nao": ""},
        {"ordem": 4, "tipo": "Decisão", "texto": "Precisa análise técnica?", "sim": "Encaminhar para responsável", "nao": "Manter em monitoramento"},
        {"ordem": 5, "tipo": "Processo", "texto": "Classificar e priorizar", "sim": "", "nao": ""},
        {"ordem": 6, "tipo": "Documento", "texto": "Gerar registro estruturado", "sim": "", "nao": ""},
        {"ordem": 7, "tipo": "Início/Fim", "texto": "Fim", "sim": "", "nao": ""},
    ]


def init_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    if not SIPOC_FILE.exists():
        default_sipoc().to_csv(SIPOC_FILE, index=False, encoding="utf-8-sig")
    if not FLOW_FILE.exists():
        FLOW_FILE.write_text(json.dumps({}, ensure_ascii=False, indent=2), encoding="utf-8")


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

    # Compatibilidade com versões anteriores.
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
    if df.empty:
        df = default_sipoc()
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


def sipoc_key(index: int) -> str:
    # Chave fixa por linha para não perder o fluxograma quando editar texto.
    return f"sipoc_linha_{index}"


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


def clean_label(text: str, max_len: int = 70) -> str:
    text = str(text or "").strip()
    if not text:
        return " "
    text = text.replace('"', "'")
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def render_header():
    st.set_page_config(page_title=APP_TITLE, page_icon="📌", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem;}
        .hero {
            background: linear-gradient(135deg, #08035f 0%, #17108f 60%, #3d2bb8 100%);
            color: white; padding: 20px 24px; border-radius: 20px; margin-bottom: 18px;
            box-shadow: 0 12px 30px rgba(8,3,95,0.18);
        }
        .hero h1 {font-size: 2rem; margin: 0;}
        .hero p {margin: 6px 0 0 0; opacity: 0.92;}
        .sipoc-title {
            background:#08035f; color:white; text-align:center; padding:18px;
            border-radius:18px 18px 0 0; font-size:2rem; font-weight:900; letter-spacing:2px;
        }
        .sipoc-shell {
            border:2px solid #08035f; border-top:0; border-radius:0 0 18px 18px;
            padding:18px 14px 22px; background:#fff;
        }
        .sipoc-card {
            background:#fffdef; border:2px solid #4f46e5; border-radius:14px; padding:14px 12px;
            min-height:185px; text-align:center; box-shadow:0 8px 22px rgba(15,23,42,.08);
        }
        .sipoc-card .top {font-weight:900; color:#111827;}
        .sipoc-card .letter {font-size:2.5rem; color:#e00000; font-weight:900; margin:8px 0 2px;}
        .sipoc-card .sub {font-size:.78rem; color:#08035f; font-weight:900; margin-bottom:10px;}
        .sipoc-card .body {font-size:.95rem; color:#111827; line-height:1.35rem;}
        .sipoc-arrow {font-size:2.2rem; color:#08035f; font-weight:900; padding-top:75px; text-align:center;}
        .info-card {
            border:1px solid #dbe3ef; background:#f8fafc; padding:14px 16px; border-radius:14px;
            color:#334155; margin-bottom:12px;
        }
        .graph-box {
            border:2px solid #4f46e5; background:#ffffff; border-radius:18px; padding:12px 18px 18px;
            box-shadow:0 8px 20px rgba(15,23,42,.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero">
          <h1>📌 VOC Kaizen + SIPOC + Fluxograma</h1>
          <p>Ferramenta visual para reunião: matriz SIPOC enxuta, atualização imediata e construção de fluxograma.</p>
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

    st.markdown("### Base filtrada")
    st.dataframe(fdf.sort_values("id_registro", ascending=False), use_container_width=True, hide_index=True)
    csv = fdf.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("Baixar CSV filtrado", data=csv, file_name="gemba_virtual_filtrado.csv", mime="text/csv")


def render_sipoc_cards(row: pd.Series):
    items = [
        ("Fornecedores", "S", "Suppliers", row.get("fornecedores", "")),
        ("Entradas", "I", "Inputs", row.get("entradas", "")),
        ("Processo", "P", "Process", row.get("processo", "")),
        ("Saídas", "O", "Outputs", row.get("saidas", "")),
        ("Clientes", "C", "Customers", row.get("clientes", "")),
    ]

    st.markdown("<div class='sipoc-title'>SIPOC</div><div class='sipoc-shell'>", unsafe_allow_html=True)
    cols = st.columns([1, .16, 1, .16, 1, .16, 1, .16, 1])
    pos = 0
    for i, (title, letter, subtitle, text) in enumerate(items):
        with cols[pos]:
            st.markdown(
                f"""
                <div class="sipoc-card">
                    <div class="top">{title}</div>
                    <div class="letter">{letter}</div>
                    <div class="sub">{subtitle}</div>
                    <div class="body">{clean_label(text, 150) or "-"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        pos += 1
        if i < len(items) - 1:
            with cols[pos]:
                st.markdown("<div class='sipoc-arrow'>➜</div>", unsafe_allow_html=True)
            pos += 1
    st.markdown("</div>", unsafe_allow_html=True)


def make_flow_dot(steps: list[dict]) -> str:
    lines = [
        'digraph G {',
        'rankdir=LR;',
        'graph [bgcolor="transparent", pad="0.35", nodesep="0.55", ranksep="0.7"];',
        'node [style="filled,rounded", fontname="Arial", fontsize="11", color="#1e1b4b", penwidth="2", fillcolor="#fff7cc", margin="0.10,0.08"];',
        'edge [fontname="Arial", fontsize="10", color="#08035f", penwidth="2.2", arrowsize="0.8"];',
    ]

    cleaned = []
    for i, step in enumerate(steps):
        texto = str(step.get("texto", "") or "").strip()
        tipo = str(step.get("tipo", "") or "Processo")
        if not texto and tipo != "Decisão":
            continue
        if tipo not in DOT_SHAPES:
            tipo = "Processo"
        cleaned.append({
            "id": f"n{i}",
            "tipo": tipo,
            "texto": texto or DOT_SHAPES.get(tipo, "Processo"),
            "sim": str(step.get("sim", "") or "").strip(),
            "nao": str(step.get("nao", "") or "").strip(),
        })

    if not cleaned:
        cleaned = [{"id": "n0", "tipo": "Início/Fim", "texto": "Início", "sim": "", "nao": ""}]

    for item in cleaned:
        shape = DOT_SHAPES.get(item["tipo"], "box")
        fill = "#fff7cc"
        if item["tipo"] == "Início/Fim":
            fill = "#ccfbf1"
        elif item["tipo"] == "Decisão":
            fill = "#fee2e2"
        elif item["tipo"] == "Input/Output":
            fill = "#dbeafe"
        elif item["tipo"] == "Banco de dados":
            fill = "#e0f2fe"
        elif item["tipo"] == "Documento":
            fill = "#fef3c7"
        elif item["tipo"] == "Armazenamento":
            fill = "#dcfce7"

        lines.append(
            f'{item["id"]} [label="{clean_label(item["texto"], 55)}", shape={shape}, fillcolor="{fill}"];'
        )

    extra_count = 0
    for i in range(len(cleaned) - 1):
        item = cleaned[i]
        next_id = cleaned[i + 1]["id"]

        if item["tipo"] == "Decisão":
            sim_label = clean_label(item["sim"] or "Sim", 28)
            nao_label = clean_label(item["nao"] or "Não", 28)
            lines.append(f'{item["id"]} -> {next_id} [label="{sim_label}"];')

            extra_id = f"nao_{extra_count}"
            extra_count += 1
            lines.append(
                f'{extra_id} [label="{nao_label}", shape=note, fillcolor="#f8fafc", color="#94a3b8", style="filled,rounded,dashed"];'
            )
            lines.append(f'{item["id"]} -> {extra_id} [label="Não", style="dashed", color="#64748b"];')
            lines.append(f'{extra_id} -> {next_id} [style="dashed", color="#94a3b8"];')
        else:
            lines.append(f'{item["id"]} -> {next_id};')

    lines.append("}")
    return "\n".join(lines)


def flow_to_df(steps: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(steps)

    # Garante que a tabela sempre tenha as colunas esperadas,
    # mesmo quando ainda não houver etapas cadastradas.
    for col in FLOW_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Correção: pandas não aceita fillna(range(...)).
    # Então criamos uma sequência simples de ordem linha a linha.
    if df.empty:
        df = pd.DataFrame(default_flow())

    df["ordem"] = pd.to_numeric(df["ordem"], errors="coerce")
    df["ordem"] = [
        int(valor) if pd.notna(valor) and int(valor) > 0 else i + 1
        for i, valor in enumerate(df["ordem"])
    ]

    return df[FLOW_COLUMNS]


def df_to_flow(df: pd.DataFrame) -> list[dict]:
    df = df.copy().fillna("")
    if "ordem" in df.columns:
        df["ordem"] = pd.to_numeric(df["ordem"], errors="coerce")
        df = df.sort_values("ordem", na_position="last")
    steps = []
    order = 1
    for _, row in df.iterrows():
        tipo = str(row.get("tipo", "") or "Processo")
        texto = str(row.get("texto", "") or "").strip()
        sim = str(row.get("sim", "") or "").strip()
        nao = str(row.get("nao", "") or "").strip()
        if not texto and not sim and not nao:
            # Mantém a linha se o usuário escolheu um tipo, preenchendo texto padrão.
            texto = tipo
        steps.append({"ordem": order, "tipo": tipo, "texto": texto, "sim": sim, "nao": nao})
        order += 1
    return steps or default_flow()


def page_sipoc(sipoc_df: pd.DataFrame):
    st.subheader("SIPOC + Fluxograma")
    st.markdown(
        """
        <div class="info-card">
        <b>Como usar:</b> preencha a matriz com várias respostas já prontas, clique em <b>Atualizar / Salvar SIPOC</b>,
        escolha a linha e monte o fluxograma como em um app de desenho de processo.
        Linhas incompletas também aparecem no visual.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["1. Matriz SIPOC", "2. Visual + construtor de fluxograma"])

    with tab1:
        st.markdown("### Matriz para preenchimento")
        st.caption("Somente as 5 colunas do SIPOC. Pode deixar campos vazios e completar durante a reunião.")

        editor_df = sipoc_df.copy()
        if editor_df.empty:
            editor_df = default_sipoc()

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
            key="sipoc_editor_5_colunas",
        )

        col1, col2, col3, col4 = st.columns([1.2, 1, 1.2, 2])
        with col1:
            if st.button("Atualizar / Salvar SIPOC", type="primary"):
                save_sipoc(edited.fillna(""))
                st.success("SIPOC atualizado.")
                st.rerun()
        with col2:
            if st.button("Recarregar exemplos"):
                save_sipoc(default_sipoc())
                st.success("Exemplos recarregados.")
                st.rerun()
        with col3:
            if st.button("Limpar SIPOC"):
                save_sipoc(pd.DataFrame(columns=SIPOC_COLUMNS))
                st.success("SIPOC limpo.")
                st.rerun()
        with col4:
            csv = edited.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("Baixar SIPOC CSV", data=csv, file_name="sipoc.csv", mime="text/csv")

    with tab2:
        visual_df = sipoc_df.copy().fillna("")
        if visual_df.empty:
            visual_df = default_sipoc()

        labels = []
        for i, row in visual_df.iterrows():
            base = row.get("entradas") or row.get("fornecedores") or row.get("processo") or f"Linha {i+1}"
            labels.append(f"{i+1}. {clean_label(base, 90)}")

        idx = st.selectbox("Escolha a linha SIPOC", list(range(len(labels))), format_func=lambda i: labels[i])
        row = visual_df.iloc[idx]

        render_sipoc_cards(row)

        st.markdown("### Fluxograma do processo")
        flows = load_flows()
        key = sipoc_key(idx)
        if key not in flows:
            flows[key] = default_flow()
            save_flows(flows)

        steps = flows.get(key, default_flow())
        current_dot = make_flow_dot(steps)

        st.markdown("<div class='graph-box'>", unsafe_allow_html=True)
        st.graphviz_chart(current_dot, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Iniciar montagem / editar fluxograma", expanded=True):
            st.caption("Selecione o tipo de tarefa. O formato do ícone muda automaticamente. Para decisão, preencha Sim e Não.")

            flow_df = flow_to_df(steps)
            edited_flow = st.data_editor(
                flow_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ordem": st.column_config.NumberColumn("Ordem", min_value=1, step=1, width="small"),
                    "tipo": st.column_config.SelectboxColumn("Tipo / ícone", options=FLOW_TYPES, required=True, width="medium"),
                    "texto": st.column_config.TextColumn("Texto da etapa", width="large"),
                    "sim": st.column_config.TextColumn("Se SIM", width="medium"),
                    "nao": st.column_config.TextColumn("Se NÃO", width="medium"),
                },
                key=f"flow_editor_{idx}",
            )

            c1, c2, c3, c4 = st.columns([1.2, 1, 1.2, 2])
            with c1:
                if st.button("Atualizar fluxograma", type="primary"):
                    flows[key] = df_to_flow(edited_flow)
                    save_flows(flows)
                    st.success("Fluxograma atualizado.")
                    st.rerun()
            with c2:
                if st.button("Reiniciar fluxo"):
                    flows[key] = default_flow()
                    save_flows(flows)
                    st.success("Fluxograma reiniciado.")
                    st.rerun()
            with c3:
                flow_json = json.dumps(flows.get(key, default_flow()), ensure_ascii=False, indent=2)
                st.download_button("Baixar JSON", data=flow_json.encode("utf-8"), file_name="fluxograma.json", mime="application/json")
            with c4:
                st.caption("Dica: altere a ordem para reorganizar as etapas. Linhas vazias são ignoradas ao atualizar.")


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
