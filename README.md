# Gemba Virtual VOC + Kaizen

Aplicativo simples em Python/Streamlit para registrar, organizar e visualizar entradas de Gemba Walk, Voz do Cliente, oportunidades de melhoria, demandas de mercado e sinais para Engenharia.

## Objetivo

Este app foi pensado para apoiar um Kaizen de Voz do Cliente, permitindo:

- registrar observações do Gemba;
- classificar entradas como reclamação, sugestão, elogio, dúvida, demanda de mercado, nova tecnologia etc.;
- calcular uma prioridade automática simples;
- acompanhar status dos registros;
- visualizar dashboard com indicadores;
- exportar a base em CSV.

## Estrutura

```text
app.py                  Aplicativo principal em Streamlit
requirements.txt        Dependências do projeto
README.md               Instruções de uso
data/                   Pasta onde a base CSV será criada
```

## Como rodar localmente

1. Instale o Python 3.10 ou superior.
2. Clone ou baixe este repositório.
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Rode o aplicativo:

```bash
streamlit run app.py
```

5. Acesse o endereço exibido no terminal, normalmente:

```text
http://localhost:8501
```

## Funcionalidades

### 1. Novo registro
Formulário para adicionar uma entrada do Gemba Virtual.

Campos principais:

- data;
- registrado por;
- setor/perfil;
- local do Gemba;
- origem da informação;
- tipo de entrada;
- foco do registro;
- produto/linha relacionada;
- descrição;
- evidência;
- frequência;
- impacto;
- responsável;
- status;
- ação sugerida.

### 2. Dashboard
Indicadores visuais:

- total de registros;
- registros de prioridade alta;
- registros em aberto;
- registros concluídos;
- entradas por tipo;
- distribuição por prioridade;
- principais origens;
- status dos registros.

### 3. Matriz de priorização
A prioridade é calculada com base em:

- frequência percebida;
- impacto no cliente/mercado;
- impacto potencial para Engenharia;
- existência de evidência.

Classificação:

- até 5 pontos: baixa prioridade;
- 6 a 8 pontos: média prioridade;
- 9 ou mais pontos: alta prioridade.

### 4. Roteiro Gemba
Tela com perguntas orientativas para investigar onde a Voz do Cliente aparece e quais entradas devem ser criadas no sistema.

### 5. Base completa
Exibição e exportação da base CSV.

## Como publicar no GitHub

```bash
git init
git add .
git commit -m "Adicionar app Gemba Virtual VOC Kaizen"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/gemba-virtual-kaizen.git
git push -u origin main
```

## Possíveis melhorias futuras

- login por usuário;
- upload real de anexos;
- edição de registros;
- envio automático por e-mail;
- integração com SharePoint;
- integração com Power BI;
- módulo de agente virtual de mercado;
- árvore inteligente de perguntas;
- histórico de ações por registro;
- controle de responsáveis e prazos.

## Observação

Este app é um MVP para validação do fluxo. Para uso corporativo, recomenda-se avaliar requisitos de segurança, controle de acesso, backup, validação de dados e integração com sistemas oficiais da empresa.
