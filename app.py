import os
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

APP_TITLE = "Gemba Virtual VOC + Kaizen"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "gemba_registros.csv"
SIPOC_FILE = DATA_DIR / "sipoc_registros.csv"

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
    "tema",
    "supplier",
    "input",
    "processo_atual",
    "output_esperado",
    "customer",
    "dor_atual",
    "oportunidade_app",
    "prioridade",
    "responsavel",
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
PRIORIDADES = ["Baixa", "Média", "Alta"]


def init_data_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    if not SIPOC_FILE.exists():
        pd.DataFrame(columns=SIPOC_COLUMNS).to_csv(SIPOC_FILE, index=False, encoding="utf-8-sig")


def load_data() -> pd.DataFrame:
    init_data_file()
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]


def save_data(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


def load_sipoc() -> pd.DataFrame:
    init_data_file()
    df = pd.read_csv(SIPOC_FILE, encoding="utf-8-sig")
    for col in SIPOC_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[SIPOC_COLUMNS]


def save_sipoc(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(SIPOC_FILE, index=False, encoding="utf-8-sig")


def gerar_id(df: pd.DataFrame) -> str:
    ano = datetime.now().year
    existentes = df["id_registro"].astype(str).str.extract(rf"GV-{ano}-(\d+)")[0].dropna()
    prox = int(existentes.astype(int).max()) + 1 if not existentes.empty else 1
    return f"GV-{ano}-{prox:04d}"


def calcular_pontuacao(frequencia: str, impacto_cliente: str, impacto_eng: str, evidencia: str) -> tuple[int, str]:
    freq_map = {
        "Caso único": 1,
        "Algumas vezes": 2,
        "Recorrente": 3,
        "Não sei": 1,
    }
    impacto_map = {
        "Baixo": 1,
        "Médio": 2,
        "Alto": 3,
        "Crítico": 4,
        "Não sei": 1,
    }
    evidencia_score = 2 if evidencia and evidencia != "Sem evidência" else 0
    score = freq_map.get(frequencia, 1) + impacto_map.get(impacto_cliente, 1) + impacto_map.get(impacto_eng, 1) + evidencia_score
    if score >= 9:
        prioridade = "Alta"
    elif score >= 6:
        prioridade = "Média"
    else:
        prioridade = "Baixa"
    return score, prioridade


def render_header():
    st.set_page_config(page_title=APP_TITLE, page_icon="📋", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
        .mini-card {
            border-radius: 14px; padding: 14px 16px; color: #0f172a; min-height: 150px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08); border: 1px solid rgba(15,23,42,0.07);
            margin-bottom: 12px;
        }
        .sipoc-s {background: #E8F1FF;}
        .sipoc-i {background: #EAFBF3;}
        .sipoc-p {background: #FFF7E8;}
        .sipoc-o {background: #FBEAF4;}
        .sipoc-c {background: #F1EBFF;}
        .section-title {font-weight: 700; font-size: 1.0rem; margin-bottom: 8px;}
        .small-text {font-size: 0.92rem; line-height: 1.3rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("📋 Gemba Virtual VOC + Kaizen")
    st.caption("Aplicativo para registrar observações de Gemba, Voz do Cliente, oportunidades de melhoria e mapear entradas com SIPOC interativo.")


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


def page_sipoc(df_gemba: pd.DataFrame, sipoc_df: pd.DataFrame):
    st.subheader("SIPOC Interativo")
    st.caption("Use esta tela durante a reunião para mapear entradas da Voz do Cliente e transformar observações em estrutura de processo.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Linhas SIPOC", len(sipoc_df))
    c2.metric("Fornecedores mapeados", sipoc_df["supplier"].replace("", pd.NA).dropna().nunique() if not sipoc_df.empty else 0)
    c3.metric("Oportunidades registradas", sipoc_df["oportunidade_app"].replace("", pd.NA).dropna().shape[0] if not sipoc_df.empty else 0)

    with st.expander("Sugestão de uso na reunião", expanded=False):
        st.markdown(
            """
            1. Defina um **tema** da reunião, por exemplo: *Reclamações de produto*.
            2. Preencha as colunas **Supplier, Input, Processo, Output e Customer**.
            3. Registre a **dor atual** e a **oportunidade para o app**.
            4. Ao final, salve e exporte o CSV.
            """
        )

    tab1, tab2, tab3 = st.tabs(["Editor SIPOC", "Visual da reunião", "Gerar rascunho a partir do Gemba"])

    with tab1:
        st.markdown("#### Preenchimento colaborativo")
        editor_df = sipoc_df.copy()
        if editor_df.empty:
            editor_df = pd.DataFrame([
                {
                    "tema": "Ex.: Sugestão de melhoria",
                    "supplier": "Comercial",
                    "input": "Sugestão recebida de médico",
                    "processo_atual": "Chega por WhatsApp e fica disperso",
                    "output_esperado": "Registro técnico estruturado",
                    "customer": "Engenharia",
                    "dor_atual": "Informação se perde",
                    "oportunidade_app": "Criar entrada específica no app",
                    "prioridade": "Alta",
                    "responsavel": "Engenharia/Comercial",
                }
            ])

        edited = st.data_editor(
            editor_df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "tema": st.column_config.TextColumn("Tema", help="Assunto discutido na reunião"),
                "supplier": st.column_config.TextColumn("Supplier"),
                "input": st.column_config.TextColumn("Input"),
                "processo_atual": st.column_config.TextColumn("Processo atual"),
                "output_esperado": st.column_config.TextColumn("Output esperado"),
                "customer": st.column_config.TextColumn("Customer"),
                "dor_atual": st.column_config.TextColumn("Dor atual"),
                "oportunidade_app": st.column_config.TextColumn("Oportunidade para o app"),
                "prioridade": st.column_config.SelectboxColumn("Prioridade", options=PRIORIDADES),
                "responsavel": st.column_config.TextColumn("Responsável"),
            },
            key="sipoc_editor"
        )

        csave, cclear = st.columns([1,1])
        with csave:
            if st.button("Salvar SIPOC", type="primary"):
                edited = edited.fillna("")
                save_sipoc(edited[SIPOC_COLUMNS])
                st.success("Mapa SIPOC salvo com sucesso.")
        with cclear:
            if st.button("Limpar mapa SIPOC"):
                vazio = pd.DataFrame(columns=SIPOC_COLUMNS)
                save_sipoc(vazio)
                st.success("Mapa SIPOC limpo. Atualize a página se quiser recomeçar do zero.")

        csv = edited.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("Baixar SIPOC em CSV", data=csv, file_name="sipoc_reuniao.csv", mime="text/csv")

    with tab2:
        st.markdown("#### Visual resumido")
        visual_df = sipoc_df if not sipoc_df.empty else edited
        visual_df = visual_df.fillna("")
        if visual_df.empty:
            st.info("Preencha o editor SIPOC para visualizar o mapa.")
        else:
            temas = [f"{i+1}. {t if str(t).strip() else 'Sem tema'}" for i, t in enumerate(visual_df["tema"].tolist())]
            idx = st.selectbox("Escolha a linha SIPOC para destacar", range(len(temas)), format_func=lambda i: temas[i])
            row = visual_df.iloc[idx]

            cols = st.columns(5)
            blocks = [
                ("Supplier", row.get("supplier", ""), "sipoc-s"),
                ("Input", row.get("input", ""), "sipoc-i"),
                ("Process", row.get("processo_atual", ""), "sipoc-p"),
                ("Output", row.get("output_esperado", ""), "sipoc-o"),
                ("Customer", row.get("customer", ""), "sipoc-c"),
            ]
            for col, (title, text, css) in zip(cols, blocks):
                col.markdown(
                    f"<div class='mini-card {css}'><div class='section-title'>{title}</div><div class='small-text'>{text or '-'}</div></div>",
                    unsafe_allow_html=True,
                )

            st.markdown("#### Complementos")
            c1, c2, c3 = st.columns(3)
            c1.text_area("Dor atual", value=row.get("dor_atual", ""), height=140, disabled=True)
            c2.text_area("Oportunidade para o app", value=row.get("oportunidade_app", ""), height=140, disabled=True)
            c3.markdown(
                f"**Prioridade:** {row.get('prioridade', '-') or '-'}  \n\n**Responsável:** {row.get('responsavel', '-') or '-'}  \n\n**Tema:** {row.get('tema', '-') or '-'}"
            )

    with tab3:
        st.markdown("#### Criar um rascunho usando a base do Gemba")
        if df_gemba.empty:
            st.info("Ainda não há registros no Gemba para gerar sugestões.")
        else:
            base = df_gemba.copy()
            base["supplier_sugerido"] = base["origem_informacao"].fillna("")
            base["input_sugerido"] = base["tipo_entrada"].fillna("") + " | " + base["descricao"].fillna("").str[:70]
            sugestao = base[["supplier_sugerido", "input_sugerido", "responsavel", "prioridade"]].head(12)
            st.dataframe(sugestao, use_container_width=True, hide_index=True)
            st.markdown("Use essas linhas como apoio para preencher o SIPOC na aba **Editor SIPOC**.")


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
            "SIPOC Interativo",
            "Matriz de priorização",
            "Roteiro Gemba",
            "Base completa",
        ],
    )

    if menu == "Novo registro":
        page_novo_registro(df)
    elif menu == "Dashboard":
        page_dashboard(df)
    elif menu == "SIPOC Interativo":
        page_sipoc(df, sipoc_df)
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
