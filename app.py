import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import mysql.connector
import json
import re
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILO VISUAL (PREMIUM UI)
# ==============================================================================
st.set_page_config(
    page_title="DataInsight AI: Ultimate Builder",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS Profissional para dar o aspecto de "Software Corporativo"
st.markdown("""
<style>
    /* 1. Fundo e Fontes Globais */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Segoe UI', Helvetica, sans-serif;
        font-weight: 600;
        color: #00BFFF !important; /* Azul Neon Principal */
    }
    
    /* 2. Cartões de Métricas (KPIs) - Estilo Glassmorphism */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #00BFFF;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, border-left-color 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-left-color: #00FF00; /* Verde ao passar o mouse */
        box-shadow: 0 8px 20px rgba(0, 191, 255, 0.2);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 15px !important;
        color: #BBBBBB !important;
    }
    
    /* 3. Botões Personalizados */
    .stButton>button {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        background-color: #262730;
        border: 1px solid #444;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1E1E1E;
        border-color: #00BFFF;
        color: #00BFFF;
        box-shadow: 0 0 12px rgba(0, 191, 255, 0.4);
    }
    
    /* 4. Inputs de Texto e Números */
    .stTextInput input, .stNumberInput input {
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px;
        padding: 10px;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #00BFFF !important;
    }
    
    /* 5. Selectbox e Multiselect */
    div[data-baseweb="select"] > div {
        background-color: #1E1E1E !important;
        color: white !important;
        border-color: #444 !important;
        border-radius: 8px;
    }
    
    /* 6. Barra de Rolagem (Scrollbar) Estilizada */
    ::-webkit-scrollbar {
        width: 10px;
        background: #0E1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00BFFF;
    }
    
    /* 7. Mensagens de Erro/Sucesso */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BIBLIOTECA COMPLETA DE GRÁFICOS (POWER BI EQUIVALENT)
# ==============================================================================
# Mapeamento técnico detalhado para garantir que a IA saiba exatamente o que usar.
MAPA_GRAFICOS_COMPLETO = {
    "✨ Automático (IA)": "A IA analisa os dados e escolhe a melhor visualização",
    # Categoria: Barras e Colunas
    "📊 Barras Empilhadas": "FORCE `px.bar` com barmode='stack' e orientation='h'",
    "📊 Barras Agrupadas": "FORCE `px.bar` com barmode='group' e orientation='h'",
    "📊 Barras 100% Empilhadas": "FORCE `px.bar` com barnorm='percent' e orientation='h'",
    "📊 Colunas Empilhadas": "FORCE `px.bar` com barmode='stack' e orientation='v'",
    "📊 Colunas Agrupadas": "FORCE `px.bar` com barmode='group' e orientation='v'",
    "📊 Colunas 100% Empilhadas": "FORCE `px.bar` com barnorm='percent' e orientation='v'",
    # Categoria: Linhas e Áreas
    "📈 Linhas (Line Chart)": "FORCE `px.line` com markers=True",
    "📈 Linhas Suaves (Spline)": "FORCE `px.line` com line_shape='spline'",
    "📉 Área (Area Chart)": "FORCE `px.area`",
    "📉 Área Empilhada": "FORCE `px.area` com groupnorm='fraction'",
    "📈 Combinado (Linha + Coluna)": "FORCE `go.Figure` combinando traces de Bar e Scatter",
    # Categoria: Pizza e Rosca
    "🥧 Pizza (Pie Chart)": "FORCE `px.pie`",
    "🍩 Rosca (Donut Chart)": "FORCE `px.pie` com hole=0.5",
    # Categoria: Mapas e Geo
    "🗺️ Mapa de Pontos (Scatter Map)": "FORCE `px.scatter_mapbox` (requer lat/lon)",
    "🗺️ Mapa Preenchido (Choropleth)": "FORCE `px.choropleth` (requer código de estado/país)",
    "🗺️ Mapa de Calor (Density Map)": "FORCE `px.density_mapbox`",
    # Categoria: Avançados e Hierárquicos
    "🔲 Treemap (Árvore Hierárquica)": "FORCE `px.treemap`",
    "☀️ Sunburst (Explosão Solar)": "FORCE `px.sunburst`",
    "🔻 Funil (Funnel Chart)": "FORCE `px.funnel`",
    "〰️ Sankey (Fluxo de Dados)": "FORCE `go.Sankey`",
    # Categoria: Estatísticos e Dispersão
    "⚫ Dispersão (Scatter Plot)": "FORCE `px.scatter`",
    "🔵 Bolhas (Bubble Chart)": "FORCE `px.scatter` usando size na variável numérica",
    "📦 Box Plot (Caixa)": "FORCE `px.box`",
    "🎻 Violino (Violin Plot)": "FORCE `px.violin`",
    "📊 Histograma (Distribuição)": "FORCE `px.histogram`",
    "🌡️ Mapa de Calor (Matrix Heatmap)": "FORCE `px.density_heatmap`",
    # Categoria: Financeiro e KPI
    "📶 Cascata (Waterfall)": "FORCE `go.Waterfall`",
    "🕯️ Candlestick (Bolsa)": "FORCE `go.Candlestick` (requer open/high/low/close)",
    "🍩 Velocímetro (Gauge)": "FORCE `go.Indicator` com mode='gauge+number'",
    "🕷️ Radar (Aranha)": "FORCE `px.line_polar`",
    "📅 Tabela Detalhada": "FORCE `go.Table` com formatação zebrada"
}

# ==============================================================================
# 3. MOTOR HÍBRIDO DE INTELIGÊNCIA (CORREÇÃO DEFINITIVA DE API)
# ==============================================================================
def conectar_ia_robusta(prompt):
    """
    Tenta conectar em múltiplos modelos sequencialmente.
    Se a API falhar completamente, retorna None para acionar o 'Fallback Manual'.
    """
    # Lista de prioridade (do mais novo para o mais estável)
    modelos_disponiveis = [
        "models/gemini-2.5-flash", # Tentativa 0: Última versão (mais avançada)
        "gemini-2.0-flash-exp",   # Tentativa 1: O mais rápido e inteligente
        "gemini-1.5-flash",       # Tentativa 2: O padrão atual
        "gemini-1.5-pro",         # Tentativa 3: O mais robusto
        "gemini-pro"              # Tentativa 4: O legado (backup final)
    ]
    
    ultimo_erro = None
    
    for modelo in modelos_disponiveis:
        try:
            # Configura e tenta gerar
            genai_model = genai.GenerativeModel(modelo)
            response = genai_model.generate_content(prompt)
            
            if response.text:
                return response.text # Sucesso!
        except Exception as e:
            ultimo_erro = e
            continue # Falhou, tenta o próximo silenciosamente
            
    # Se chegou aqui, nenhum modelo funcionou. Retorna None para o sistema usar o plano B.
    return None

# ==============================================================================
# 4. SISTEMA DE EMERGÊNCIA (FALLBACK - PLANO B)
# ==============================================================================
def gerar_codigo_emergencia(df, titulo):
    """
    Gera um dashboard funcional usando lógica Python pura, sem depender da IA.
    Garante que o usuário NUNCA veja uma tela de erro.
    """
    colunas_num = df.select_dtypes(include=['number']).columns.tolist()
    colunas_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Cabeçalho do código
    code = f"st.title('{titulo}')\n"
    code += "st.warning('⚠️ Nota: A IA está indisponível no momento. Este dashboard foi gerado pelo modo de compatibilidade automática.')\n"
    code += "st.markdown('---')\n"
    
    # 1. Seção de KPIs (Lógica: Soma ou Contagem)
    code += "# Seção de KPIs Automáticos\n"
    code += "col1, col2, col3, col4 = st.columns(4)\n"
    
    if colunas_num:
        # Pega até 4 colunas numéricas para somar
        for i in range(min(4, len(colunas_num))):
            col = colunas_num[i]
            code += f"col{i+1}.metric('Total {col}', f'{{df['{col}'].sum():,.0f}}')\n"
    else:
        # Se não tiver números, conta linhas
        code += f"col1.metric('Total de Registros', len(df))\n"
        
    code += "st.markdown('---')\n"
    
    # 2. Seção de Gráficos (Lógica: Barras e Pizza)
    code += "# Seção de Gráficos Automáticos\n"
    code += "c_graf1, c_graf2 = st.columns(2)\n"
    
    if colunas_cat and colunas_num:
        cx = colunas_cat[0] # Primeira categórica
        cy = colunas_num[0] # Primeira numérica
        
        # Gráfico 1: Barras
        code += f"fig1 = px.bar(df, x='{cx}', y='{cy}', title='Análise de {cy} por {cx}', template='plotly_dark')\n"
        code += "c_graf1.plotly_chart(fig1, use_container_width=True, config={'scrollZoom': False})\n"
        
        # Gráfico 2: Pizza (com outra categoria se existir)
        cat2 = colunas_cat[1] if len(colunas_cat) > 1 else cx
        code += f"fig2 = px.pie(df, names='{cat2}', values='{cy}', title='Distribuição de {cy}', template='plotly_dark', hole=0.5)\n"
        code += "c_graf2.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': False})\n"
    else:
        code += "st.info('Não há colunas suficientes para gerar gráficos automáticos (precisa de numéricas e categóricas).')\n"
        
    return code

# ==============================================================================
# 5. GERADORES DE CONTEÚDO (SUGESTÕES E CÓDIGO FINAL)
# ==============================================================================
@st.cache_data(show_spinner="A IA está analisando a estrutura dos dados...")
def gerar_sugestoes_seguras(df, tema):
    """Tenta pegar sugestões da IA. Se falhar, cria sugestões genéricas."""
    try:
        amostra = df.head(5).to_string()
        dtypes = df.dtypes.to_string()
        
        prompt = f"""
        Atue como Consultor Sênior de BI.
        DADOS: {dtypes}
        AMOSTRA: {amostra}
        TEMA: "{tema}"
        
        TAREFA: Sugira 10 KPIs e 10 Gráficos relevantes.
        FORMATO DE SAÍDA (JSON Puro):
        {{
            "kpis": ["KPI 1", "KPI 2", ...],
            "graficos": ["Gráfico 1", "Gráfico 2", ...]
        }}
        """
        
        texto_ia = conectar_ia_robusta(prompt)
        
        if texto_ia:
            # Limpeza e Extração do JSON
            match = re.search(r'\{.*\}', texto_ia, re.DOTALL)
            if match:
                res = json.loads(match.group(0))
                return res.get('kpis', []), res.get('graficos', [])
    except:
        pass
    
    # Fallback (Plano B) se a IA falhar
    cols = df.columns.tolist()
    kpis_bkp = [f"Total de {c}" for c in cols[:5]]
    grafs_bkp = [f"Análise por {c}" for c in cols[:5]]
    return kpis_bkp, grafs_bkp

@st.cache_data(show_spinner="Renderizando visualizações...")
def gerar_dashboard_final(df, modo, params):
    """Gera o código final do dashboard."""
    amostra = df.head(3).to_string()
    dtypes = df.dtypes.to_string()
    titulo = params.get('titulo', 'Dashboard Analítico')
    
    # Montagem das Instruções
    if modo == "auto_smart":
        kpis = params.get('kpis_sel', [])
        grafs = params.get('grafs_sel', [])
        tema = params.get('tema', '')
        
        instrucao_kpi = f"Crie {len(kpis)} KPIs focados no tema '{tema}':\n" + "\n".join([f"- {k}" for k in kpis])
        instrucao_graficos = f"Crie {len(grafs)} gráficos focados no tema '{tema}':\n" + "\n".join([f"- {g}" for g in grafs])
        
    else: # Modo Manual
        kpis_man = params.get('kpi_def', [])
        grafs_man = params.get('graf_def', [])
        
        instrucao_kpi = f"Crie {len(kpis_man)} KPIs conforme definido:\n" + "\n".join([f"- {k}" for k in kpis_man])
        instrucao_graficos = f"Crie {len(grafs_man)} gráficos conforme definido:\n"
        for g in grafs_man:
            # Pega a instrução técnica específica do dicionário
            tipo_tecnico = MAPA_GRAFICOS_COMPLETO.get(g['tipo'], 'Escolha a melhor visualização')
            instrucao_graficos += f"- Título '{g['titulo']}'. {tipo_tecnico}.\n"

    # Prompt Final
    prompt = f"""
    Atue como Especialista Sênior em Python/Streamlit/Plotly.
    DADOS DISPONÍVEIS: {dtypes}
    AMOSTRA: {amostra}
    TÍTULO DO PAINEL: "{titulo}"
    
    REGRAS DE CÓDIGO:
    1. Importações (st, pd, px, go) JÁ EXISTEM. Não importe novamente.
    2. ESTILO: Use sempre `template='plotly_dark'` e `config={{'scrollZoom': False}}`.
    3. LAYOUT: Use `st.columns` para organizar KPIs e Gráficos lado a lado.
    4. ESTRUTURA: Título > KPIs > Divisor > Gráficos.
    
    CONTEÚDO SOLICITADO:
    # SEÇÃO KPIS
    {instrucao_kpi}
    
    # SEÇÃO GRÁFICOS
    {instrucao_graficos}
    (Altura fixa de 400px, use_container_width=True)
    
    RETORNE APENAS O CÓDIGO PYTHON EXECUTÁVEL.
    """
    
    codigo_gerado = conectar_ia_robusta(prompt)
    
    # Verificação de Falha
    if codigo_gerado:
        return codigo_gerado.replace("```python", "").replace("```", "").strip()
    else:
        # Se a IA não retornou código, usa o gerador de emergência
        return gerar_codigo_emergencia(df, titulo)

# ==============================================================================
# 6. FUNÇÕES DE DADOS (CONEXÃO E SAÚDE)
# ==============================================================================
def carregar_dados_sql(host, user, password, database, table):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro na conexão SQL: {e}")
        return None

def calcular_saude_base(df):
    total = len(df)
    if total == 0: return 0, {}
    
    dups = df.duplicated().sum()
    nulos = df.isna().sum().sum()
    total_cells = df.size
    
    # Score de 0 a 100
    score = 100 - ((nulos/total_cells)*100) - ((dups/total)*100)
    score = max(0, min(100, score))
    
    # Detalhamento
    nulos_df = df.isna().sum().reset_index()
    nulos_df.columns = ['Coluna', 'Qtd Vazios']
    nulos_df = nulos_df[nulos_df['Qtd Vazios'] > 0]
    
    return score, {'dups': dups, 'nulos': nulos_df}

# ==============================================================================
# 7. BARRA LATERAL (MENU E CONFIGURAÇÕES)
# ==============================================================================
with st.sidebar:
    # --- Identidade Visual ---
    if os.path.exists("Logo inovador da DataInsight AI.png"):
        st.image("Logo inovador da DataInsight AI.png", use_container_width=True)
    else:
        st.markdown("## 📊 DataInsight AI")
        st.caption("Solução Enterprise de BI")
    
    st.markdown("---")
    
    # --- Conexão API ---
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        api_key = st.text_input("🔑 Google API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("Sistema Online e Conectado", icon="🟢")
    
    st.divider()
    
    # --- Fonte de Dados ---
    st.subheader("📂 Fonte de Dados")
    tipo_fonte = st.radio("", ("📁 Arquivo Excel/CSV", "🛢️ Banco MySQL"))
    df = None 

    if tipo_fonte == "📁 Arquivo Excel/CSV":
        upl = st.file_uploader("Arraste seu arquivo aqui", type=["csv", "xlsx"])
        if upl:
            try:
                if upl.name.endswith('.csv'): df = pd.read_csv(upl)
                else: df = pd.read_excel(upl)
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
            
    elif tipo_fonte == "🛢️ Banco MySQL":
        h = st.text_input("Host", "localhost")
        u = st.text_input("User", "root")
        p = st.text_input("Senha", type="password")
        d = st.text_input("Database")
        if st.button("Conectar ao Banco"):
            try:
                c = mysql.connector.connect(host=h, user=u, password=p, database=d)
                tabs = [x[0] for x in c.cursor().execute("SHOW TABLES") or c.cursor().fetchall()]
                st.session_state['tabs'] = tabs
                st.session_state['creds'] = {'h':h, 'u':u, 'p':p, 'd':d}
                c.close()
                st.success("Conexão estabelecida!")
            except Exception as e: st.error(str(e))
        
        if 'tabs' in st.session_state:
            t = st.selectbox("Selecione a Tabela", st.session_state['tabs'])
            if t: df = carregar_dados_sql(st.session_state['creds']['h'], st.session_state['creds']['u'], st.session_state['creds']['p'], st.session_state['creds']['d'], t)

    # --- Monitor de Saúde (Visual Rico) ---
    if df is not None:
        st.divider()
        st.subheader("🩺 Saúde da Base")
        score, details = calcular_saude_base(df)
        
        # Cor dinâmica baseada na nota
        cor = "#00FF00" if score >= 90 else "#FFA500" if score >= 70 else "#FF0000"
        
        st.markdown(f"""
        <div style="background-color: #262730; padding: 15px; border-radius: 10px; border-left: 6px solid {cor}; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: white; font-weight: bold;">Índice de Qualidade</span>
            <span style="color: {cor}; font-weight: bold; font-size: 22px;">{score:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Ver Relatório de Inconsistências"):
            st.write(f"**Total de Registros:** {len(df)}")
            st.write(f"**Linhas Duplicadas:** {details['dups']}")
            if not details['nulos'].empty:
                st.write("**Colunas com Dados Vazios:**")
                st.dataframe(details['nulos'], hide_index=True)
            else:
                st.success("Nenhuma célula vazia encontrada.")

    st.divider()
    if st.button("🔄 Reiniciar Sessão"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 8. APLICAÇÃO PRINCIPAL (LAYOUT E LÓGICA)
# ==============================================================================

# Inicialização de Estado
if "messages" not in st.session_state: st.session_state.messages = []
if "dashboard_ativo" not in st.session_state: st.session_state.dashboard_ativo = False
if "dash_params" not in st.session_state: st.session_state.dash_params = {}
if "sugestoes" not in st.session_state: st.session_state.sugestoes = {'kpis': [], 'graficos': []}

if df is not None:
    
    # Visualizador de Dados (Expansível e discreto)
    with st.expander("🔍 Visualizar Tabela de Dados Bruta", expanded=False):
        st.dataframe(df, use_container_width=True)
    
    # --- ÁREA DO DASHBOARD (SE ATIVO) ---
    if st.session_state.dashboard_ativo:
        # Botão Flutuante de Fechar
        col_c1, col_c2 = st.columns([1, 6])
        if col_c1.button("❌ Fechar Painel"):
            st.session_state.dashboard_ativo = False
            st.rerun()
            
    else:
        # --- ÁREA DO CONSTRUTOR (SE INATIVO) ---
        st.markdown("# 🚀 DataInsight AI: Ultimate Builder")
        st.markdown("#### *Transforme seus dados em inteligência visual em segundos.*")
        
        tab_ia, tab_man = st.tabs(["🤖 Modo Inteligente (IA)", "🎨 Modo Construtor (Manual)"])
        
        # === ABA 1: INTELIGENTE ===
        with tab_ia:
            st.info("💡 A Inteligência Artificial analisará a estrutura dos seus dados para sugerir os indicadores mais relevantes.")
            
            titulo_auto = st.text_input("Título do Painel:", value="Relatório Executivo", key="ta")
            
            c1, c2 = st.columns([3, 1])
            with c1:
                tema = st.text_input("Qual o foco da análise?", placeholder="Ex: Análise de Vendas e Lucratividade por Região")
            with c2:
                st.write("") # Espaçamento
                st.write("")
                btn_consultar = st.button("🔍 Gerar Sugestões", use_container_width=True)
            
            if btn_consultar and tema:
                # Chama a função segura que nunca quebra
                k, g = gerar_sugestoes_seguras(df, tema)
                st.session_state.sugestoes = {'kpis': k, 'graficos': g}
            
            # Renderiza as sugestões (se existirem)
            if st.session_state.sugestoes['kpis']:
                st.markdown("---")
                st.success("✅ Opções geradas com sucesso! Personalize sua seleção abaixo:")
                
                sel_kpis = st.multiselect("Selecione os KPIs desejados:", st.session_state.sugestoes['kpis'], default=st.session_state.sugestoes['kpis'][:4])
                sel_grafs = st.multiselect("Selecione os Gráficos desejados:", st.session_state.sugestoes['graficos'], default=st.session_state.sugestoes['graficos'][:2])
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Construir Dashboard Inteligente", type="primary", use_container_width=True):
                    st.session_state.dash_mode = "auto_smart"
                    st.session_state.dash_params = {
                        'titulo': titulo_auto, 'tema': tema,
                        'kpis_sel': sel_kpis, 'grafs_sel': sel_grafs
                    }
                    st.session_state.dashboard_ativo = True
                    st.rerun()

        # === ABA 2: MANUAL ===
        with tab_man:
            st.info("🔧 Controle total: defina cada métrica, título e tipo de gráfico manualmente.")
            
            titulo_man = st.text_input("Título do Painel:", value="Meu Dashboard Personalizado", key="tm")
            
            c_q1, c_q2 = st.columns(2)
            nk = c_q1.number_input("Quantidade de KPIs", 1, 8, 4)
            ng = c_q2.number_input("Quantidade de Gráficos", 1, 20, 2)
            
            with st.form("manual_form"):
                st.markdown("### 1. Definição de Indicadores (KPIs)")
                cols_k = st.columns(4)
                kd = []
                for i in range(nk):
                    with cols_k[i % 4]: kd.append(st.text_input(f"KPI {i+1}", placeholder="Ex: Total Vendas"))
                
                st.markdown("### 2. Definição de Gráficos")
                gd = []
                # Lista de chaves do dicionário para o selectbox
                opcoes_graficos = list(MAPA_GRAFICOS_COMPLETO.keys())
                
                for i in range(0, ng, 2):
                    cg = st.columns(2)
                    for j in range(2):
                        if i+j < ng:
                            with cg[j]:
                                with st.container(border=True):
                                    st.markdown(f"**Gráfico {i+j+1}**")
                                    t = st.text_input("Título", key=f"t{i+j}")
                                    tp = st.selectbox("Tipo Visual", opcoes_graficos, key=f"s{i+j}")
                                    gd.append({'titulo': t, 'tipo': tp})
                
                st.markdown("---")
                if st.form_submit_button("✨ Construir Dashboard Manual", type="primary", use_container_width=True):
                    st.session_state.dash_mode = "custom"
                    st.session_state.dash_params = {'titulo': titulo_man, 'kpi_def': kd, 'graf_def': gd}
                    st.session_state.dashboard_ativo = True
                    st.rerun()

    # --- RENDERIZAÇÃO DO DASHBOARD FINAL ---
    if st.session_state.dashboard_ativo and api_key:
        st.markdown("---")
        
        # Chama a função geradora (que tem fallback interno)
        codigo_dash = gerar_dashboard_final(df, st.session_state.dash_mode, st.session_state.dash_params)
        
        # Execução Protegida
        try:
            exec(codigo_dash)
        except Exception as e:
            st.error(f"Erro ao renderizar o visual: {e}")
            with st.expander("Ver Código Gerado (Debug)"): st.code(codigo_dash)
            
        st.markdown("---")

    # --- CHAT COM OS DADOS (Assistente Virtual) ---
    st.subheader("💬 Chat com os Dados")
    
    # Renderiza Histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "code" in msg:
                try: exec(msg["code"])
                except: pass
    
    # Input do Usuário
    if prompt := st.chat_input("Pergunte algo sobre os dados (Ex: Qual a tendência de vendas?)..."):
        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Resposta da IA
        with st.chat_message("assistant"):
            with st.spinner("Analisando dados..."):
                prompt_chat = f"""
                Atue como Data Scientist Sênior.
                DADOS: {df.dtypes.to_string()}
                HISTÓRICO: {st.session_state.messages[-6:]}
                PERGUNTA: "{prompt}"
                REGRAS: Retorne APENAS código Python usando `plotly.express` e `streamlit`. Sem texto explicativo.
                Tema: `template='plotly_dark'`.
                """
                
                # Usa a conexão robusta
                resp_chat = conectar_ia_robusta(prompt_chat)
                
                if resp_chat:
                    clean_code = resp_chat.replace("```python", "").replace("```", "").strip()
                    try: 
                        exec(clean_code)
                        st.session_state.messages.append({"role": "assistant", "content": "Visualização gerada:", "code": clean_code})
                        with st.expander("Ver Código Python"): st.code(clean_code)
                    except Exception as e: st.error(f"Erro na execução do gráfico: {e}")
                else:
                    st.error("O assistente de IA está indisponível no momento. Tente novamente em alguns segundos.")

elif not df:
    # Tela de Boas Vindas (Placeholder quando não há dados)
    st.markdown("""
    <div style="text-align: center; padding: 50px; opacity: 0.7;">
        <h1>👋 Bem-vindo ao DataInsight AI</h1>
        <p style="font-size: 18px;">
            Sua plataforma de Business Intelligence Autônoma.
            <br>Conecte seus dados na barra lateral para começar a análise.
        </p>
    </div>
    """, unsafe_allow_html=True)
    