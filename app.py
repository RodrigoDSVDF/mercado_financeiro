import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
import locale
import re

# ------------------- CONFIGURAÇÃO DO LOCALE (para números BR) -------------------
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')  # Windows
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')  # Fallback
        except:
            locale.setlocale(locale.LC_ALL, '')  # Locale padrão do sistema

# ------------------- CONFIGURAÇÃO DA PÁGINA -------------------
st.set_page_config(
    page_title="Terminal Quant - Mercado Financeiro BR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- ESTILIZAÇÃO CUSTOMIZADA (CSS) -------------------
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0d1117;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px 20px;
        transition: transform 0.2s, border-color 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] > div {
        color: #8b949e !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] > div {
        font-family: 'JetBrains+Mono', monospace;
        font-weight: 700;
        font-size: 1.8rem !important;
        color: #f0f6fc !important;
    }
    
    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
        color: #8b949e;
        border-bottom: 2px solid transparent;
        padding: 10px 20px;
    }
    button[aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }
    
    div[data-testid="stDataFrame"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(46, 160, 67, 0.3);
        font-family: 'JetBrains+Mono', monospace;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #3fb950;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(63, 185, 80, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0); }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------- CONSTANTES & TICKERS -------------------
TICKERS_STOCKS = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
    'WEGE3.SA', 'RENT3.SA', 'BBAS3.SA', 'B3SA3.SA', 'ELET3.SA'
]
TICKERS_FIIS = [
    'HGLG11.SA', 'KNRI11.SA', 'VISC11.SA', 'MXRF11.SA', 'XPLG11.SA'
]

# ------------------- FUNÇÃO CORRIGIDA: CONVERTE NÚMERO BR/AMERICANO -------------------
def parse_br_number(valor):
    """
    Converte números nos formatos brasileiro ('14,50') ou americano ('14.50') para float.
    Também remove pontos de milhar automaticamente.
    """
    if isinstance(valor, (int, float)):
        return float(valor)
    
    s = str(valor).strip()
    if not s:
        return None
    
    # Estratégia 1: Usar o locale configurado (resolve vírgula decimal e pontos de milhar)
    try:
        return locale.atof(s)
    except:
        pass
    
    # Estratégia 2: Remover pontos de milhar (ex: 1.000,50 -> 1000,50) e trocar vírgula por ponto
    try:
        # Remove pontos que estão separando milhares (ex: 1.000 -> 1000)
        s_temp = re.sub(r'\.(?=\d{3})', '', s)
        # Troca a vírgula decimal por ponto
        s_temp = s_temp.replace(',', '.')
        return float(s_temp)
    except:
        pass
    
    # Estratégia 3: Último recurso - tenta converter direto (caso já venha com ponto)
    try:
        return float(s)
    except:
        return None

# ------------------- FUNÇÕES DE BUSCA OTIMIZADAS -------------------
@st.cache_data(ttl=300)
def get_macro_bcb(serie):
    """Busca o último valor de uma série do BCB."""
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            valor_bruto = data[0]['valor']
            return parse_br_number(valor_bruto)
    except Exception as e:
        print(f"Erro ao buscar série {serie}: {e}")
        return None

@st.cache_data(ttl=3600)
def get_ipca_acumulado_12m():
    """
    Calcula o IPCA acumulado em 12 meses a partir dos dados mensais (série 433).
    Isso garante que o dado seja correto, mesmo se a série 4447 estiver atrasada.
    """
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].apply(parse_br_number)
        df = df.sort_values('data').tail(13)  # Pega os últimos 13 meses (precisa de 12 variações)
        if len(df) < 13:
            return None  # Não tem dados suficientes
        # Calcula o acumulado: (1 + r1)*(1 + r2)*... - 1
        acumulado = 1.0
        for _, row in df.iterrows():
            taxa = row['valor'] / 100  # converte percentual para decimal
            acumulado *= (1 + taxa)
        return (acumulado - 1) * 100  # retorna em percentual
    except Exception as e:
        print(f"Erro ao calcular IPCA acumulado: {e}")
        return None

@st.cache_data(ttl=86400)  # Atualiza 1x por dia (dados macro mudam devagar)
def get_annual_gdp():
    """Busca os 4 últimos trimestres do PIB e soma para obter o PIB Anual Corrente."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.22099/dados?formato=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].apply(parse_br_number)
        df = df.sort_values('data').tail(4)  # últimos 4 trimestres
        total_milhoes = df['valor'].sum()
        return total_milhoes / 1e12  # Converte para trilhões
    except Exception as e:
        print(f"Erro ao buscar PIB: {e}")
        return None

@st.cache_data(ttl=300)
def get_market_summary():
    try:
        df = yf.download(["^BVSP", "USDBRL=X"], period="2d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns]
            
        ibov_hoje = df['Close_^BVSP'].iloc[-1]
        ibov_ontem = df['Close_^BVSP'].iloc[-2]
        ibov_pct = ((ibov_hoje / ibov_ontem) - 1) * 100
        
        dolar_hoje = df['Close_USDBRL=X'].iloc[-1]
        dolar_ontem = df['Close_USDBRL=X'].iloc[-2]
        dolar_pct = ((dolar_hoje / dolar_ontem) - 1) * 100
        return {'ibov': ibov_hoje, 'ibov_pct': ibov_pct, 'dolar': dolar_hoje, 'dolar_pct': dolar_pct}
    except Exception:
        return {'ibov': 120000.0, 'ibov_pct': 0.0, 'dolar': 5.0, 'dolar_pct': 0.0}

@st.cache_data(ttl=300)
def get_batch_assets(tickers):
    try:
        df = yf.download(tickers, period="5d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns]
            
        data = []
        for ticker in tickers:
            col_close = f"Close_{ticker}"
            col_vol = f"Volume_{ticker}"
            if col_close in df.columns:
                close_hoje = df[col_close].dropna().iloc[-1]
                close_ontem = df[col_close].dropna().iloc[-2]
                v_vol = df[col_vol].dropna().iloc[-1] if col_vol in df.columns else 0
                var = ((close_hoje / close_ontem) - 1) * 100
                data.append({
                    'Ativo': ticker.replace('.SA', ''),
                    'Preço': round(close_hoje, 2),
                    'Variação (%)': round(var, 2),
                    'Volume Diário': int(v_vol)
                })
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=['Ativo', 'Preço', 'Variação (%)', 'Volume Diário'])

@st.cache_data(ttl=3600)
def get_historical_data(tickers, period="1y"):
    try:
        df = yf.download(tickers, period=period, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns]
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_historical_macro(serie, name, days=365):
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame(columns=['Date', name])
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].apply(parse_br_number)
        start_date = datetime.now() - timedelta(days=days)
        df = df[df['data'] >= start_date].sort_values('data')
        df['Date'] = df['data'].dt.date
        return df[['Date', 'valor']].rename(columns={'valor': name})
    except Exception:
        return pd.DataFrame(columns=['Date', name])

def calculate_quant_metrics(ticker, period="1y"):
    try:
        objeto_ticker = yf.Ticker(ticker)
        df = objeto_ticker.history(period=period)
        if df.empty: 
            return None
            
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Returns'] = df['Close'].pct_change()
        df['Vol_21d'] = df['Returns'].rolling(21).std() * np.sqrt(252) * 100
        df['MMA_50'] = df['Close'].rolling(50).mean()
        df['MMA_200'] = df['Close'].rolling(200).mean()
        
        rolling_max = df['Close'].cummax()
        df['Drawdown'] = (df['Close'] - rolling_max) / rolling_max * 100
        return df
    except Exception:
        return None

# ------------------- CARREGAMENTO DE DADOS -------------------
summary = get_market_summary()
selic = get_macro_bcb(432)          # Taxa SELIC diária (anualizada)
cdi = get_macro_bcb(12)             # Taxa CDI diária (anualizada) - não usado, mas mantido

# --- IPCA agora é calculado a partir dos dados mensais ---
ipca = get_ipca_acumulado_12m()

# Se algum dado não veio, coloca um valor padrão "N/A" visualmente
if selic is None:
    selic = 0.0
if ipca is None:
    ipca = 0.0

# Cálculo do juro real
juro_real = (((1 + (selic/100)) / (1 + (ipca/100))) - 1) * 100 if (selic and ipca) else 0.0

# ------------------- BARRA LATERAL (SIDEBAR) -------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style='margin:0; font-size: 1.4rem; color: #f0f6fc;'>TERMINAL QUANT</h2>
            <div class="live-badge"><span class="pulse-dot"></span>AO VIVO</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.metric("Ibovespa", f"{summary['ibov']:,.0f}".replace(",", "."), f"{summary['ibov_pct']:.2f}%")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("Dólar Comercial", f"R$ {summary['dolar']:.4f}", f"{summary['dolar_pct']:.2f}%")
    
    st.markdown("<hr style='border-color: #30363d; margin: 25px 0;'/>", unsafe_allow_html=True)
    st.subheader("📌 Política Monetária")
    
    st.metric("SELIC Meta", f"{selic:.2f}%" if selic != 0.0 else "Indisponível")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("IPCA (Acum. 12m)", f"{ipca:.2f}%" if ipca != 0.0 else "Indisponível")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("Juro Real Estimado", f"{juro_real:.2f}%" if juro_real != 0.0 else "Indisponível")
    
    st.markdown("<hr style='border-color: #30363d; margin: 25px 0;'/>", unsafe_allow_html=True)
    st.caption(f"Atualizado em: {datetime.now().strftime('%H:%M:%S')} BRT")

# ------------------- CORPO PRINCIPAL -------------------
st.markdown("""
    <div style="background: linear-gradient(90deg, #161b22 0%, #0d1117 100%); padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 25px;">
        <h1 style="margin: 0; color: #f0f6fc; font-size: 2rem;">Analytics de Mercado & Dashboard Quantitativo</h1>
        <p style="margin: 5px 0 0 0; color: #8b949e; font-size: 0.95rem;">Análise estrutural de volatilidade, liquidez de ativos e monitoramento macroeconômico brasileiro.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Global & Macro", 
    "🎯 Análise Quantitativa", 
    "📋 Monitor de Mercado", 
    "⚙️ Dados Estruturais"
])

# ------------------- TAB 1: VISÃO GLOBAL & MACRO -------------------
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p style='color:#8b949e; font-size:0.85rem; font-weight:600;'>PERFORMANCE RELATIVA: IBOVESPA VS DÓLAR (BASE 100)</p>", unsafe_allow_html=True)
        df_hist = get_historical_data(["^BVSP", "USDBRL=X"], period="1y")
        if not df_hist.empty and 'Close_^BVSP' in df_hist.columns:
            df_norm = df_hist.copy().dropna(subset=['Close_^BVSP', 'Close_USDBRL=X'])
            df_norm['Ibovespa'] = (df_norm['Close_^BVSP'] / df_norm['Close_^BVSP'].iloc[0]) * 100
            df_norm['Dólar'] = (df_norm['Close_USDBRL=X'] / df_norm['Close_USDBRL=X'].iloc[0]) * 100
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_norm['Date'], y=df_norm['Ibovespa'], name='Ibovespa', line=dict(color='#58a6ff', width=2)))
            fig.add_trace(go.Scatter(x=df_norm['Date'], y=df_norm['Dólar'], name='Dólar', line=dict(color='#f9826c', width=2)))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.markdown("<p style='color:#8b949e; font-size:0.85rem; font-weight:600;'>SPREAD HISTÓRICO: SELIC VS INFLAÇÃO (IPCA)</p>", unsafe_allow_html=True)
        # Para os gráficos, usamos a série 432 para SELIC histórica e a série 433 para IPCA mensal (mostrando a variação mensal)
        df_selic_h = get_historical_macro(432, "SELIC", days=365)
        df_ipca_h = get_historical_macro(433, "IPCA Mensal", days=365)  # Usamos 433 para ter histórico mensal
        
        fig2 = go.Figure()
        if not df_selic_h.empty:
            fig2.add_trace(go.Scatter(x=df_selic_h['Date'], y=df_selic_h['SELIC'], name='SELIC (%)', line=dict(color='#3fb950')))
        if not df_ipca_h.empty:
            fig2.add_trace(go.Scatter(x=df_ipca_h['Date'], y=df_ipca_h['IPCA Mensal'], name='IPCA Mensal (%)', line=dict(color='#d15704')))
        fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig2, use_container_width=True)

    # GRÁFICO DE COMPARAÇÃO DE AÇÕES
    st.markdown("<hr style='border-color: #30363d; margin: 30px 0 20px 0;'/>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; font-size:0.85rem; font-weight:600; text-transform: uppercase;'>ANÁLISE DE CORRELAÇÃO PARALELA: TODAS AS AÇÕES DA CARTEIRA (BASE HISTÓRICA 100)</p>", unsafe_allow_html=True)
    
    df_all_stocks = get_historical_data(TICKERS_STOCKS, period="1y")
    if not df_all_stocks.empty:
        fig_comp = go.Figure()
        for ticker in TICKERS_STOCKS:
            col_name = f"Close_{ticker}"
            if col_name in df_all_stocks.columns:
                series_clean = df_all_stocks[col_name].dropna()
                if not series_clean.empty:
                    base_val = series_clean.iloc[0]
                    norm_series = (df_all_stocks[col_name] / base_val) * 100
                    fig_comp.add_trace(go.Scatter(
                        x=df_all_stocks['Date'], 
                        y=norm_series, 
                        name=ticker.replace('.SA', ''),
                        mode='lines',
                        line=dict(width=1.5),
                        hovertemplate="%{hovertext}<br>Desempenho: %{y:.1f}%<extra></extra>",
                        hovertext=ticker.replace('.SA', '')
                    ))
        fig_comp.update_layout(
            template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=15, b=10), 
            height=450,
            xaxis=dict(title="Período"),
            yaxis=dict(title="Retorno Acumulado (%)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ------------------- TAB 2: ANÁLISE QUANTITATIVA -------------------
with tab2:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem;'>Análise de Risco e Volatilidade Individual</h3>", unsafe_allow_html=True)
    
    c_sel1, c_sel2 = st.columns([2, 1])
    with c_sel1:
        asset_selected = st.selectbox("Selecione um ativo da B3:", TICKERS_STOCKS, index=0)
    with c_sel2:
        time_window = st.selectbox("Janela Temporal:", ["3m", "6m", "1y", "2y"], index=2)
    
    quant_df = calculate_quant_metrics(asset_selected, period=time_window)
    
    if quant_df is not None and not quant_df.empty:
        q_col1, q_col2, q_col3 = st.columns(3)
        current_vol = quant_df['Vol_21d'].iloc[-1]
        max_dd = quant_df['Drawdown'].min()
        current_close = quant_df['Close'].iloc[-1]
        
        q_col1.metric("Volatilidade Histórica (21d Anualizada)", f"{current_vol:.2f}%")
        q_col2.metric("Drawdown Máximo do Período", f"{max_dd:.2f}%")
        q_col3.metric("Último Fechamento", f"R$ {current_close:.2f}")
        
        # Gráficos Quantitativos
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Close'], name='Preço', line=dict(color='#f0f6fc')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_50'], name='Média Móvel 50 dias', line=dict(color='#f9826c', dash='dash')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_200'], name='Média Móvel 200 dias', line=dict(color='#58a6ff', dash='dot')))
        fig_price.update_layout(title="Tendências de Preço & Médias Móveis", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_price, use_container_width=True)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Vol_21d'], name='Volatilidade', fill='tozeroy', line=dict(color='#dbab09')))
        fig_vol.update_layout(title="Volatilidade Móvel Histórica (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220)
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.error("Dados indisponíveis para o ativo ou período selecionado.")

# ------------------- TAB 3: MONITOR DE MERCADO -------------------
with tab3:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem; margin-bottom: 15px;'>Monitor de Liquidez B3</h3>", unsafe_allow_html=True)
    
    config_tabela = {
        "Ativo": st.column_config.TextColumn("Ativo", width="small"),
        "Preço": st.column_config.NumberColumn("Último Preço", format="R$ %.2f"),
        "Variação (%)": st.column_config.NumberColumn("Retorno Diário", format="%.2f%%"),
        "Volume Diário": st.column_config.NumberColumn("Volume Financeiro", format="%d")
    }
    
    sub_tab1, sub_tab2 = st.tabs(["⚡ Ações (Alta Liquidez)", "🏢 Fundos Imobiliários (FIIs)"])
    
    with sub_tab1:
        df_stocks = get_batch_assets(TICKERS_STOCKS)
        st.dataframe(df_stocks, column_config=config_tabela, use_container_width=True, hide_index=True)
        
    with sub_tab2:
        df_fiis = get_batch_assets(TICKERS_FIIS)
        st.dataframe(df_fiis, column_config=config_tabela, use_container_width=True, hide_index=True)

# ------------------- TAB 4: DADOS ESTRUTURAIS (DINÂMICO) -------------------
with tab4:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem; margin-bottom: 15px;'>Dados Estruturais da Economia</h3>", unsafe_allow_html=True)
    
    # Busca os dados AO VIVO
    gdp_annual = get_annual_gdp()
    unemployment = get_macro_bcb(24369)   # Taxa de desemprego PNAD
    trade_balance = get_macro_bcb(26073)  # Balança comercial (acum. ano) em US$ milhões
    gross_debt = get_macro_bcb(13790)     # Dívida bruta / PIB
    
    # Formatação para exibição
    gdp_str = f"R$ {gdp_annual:.1f} Trilhões" if gdp_annual else "Indisponível"
    unemp_str = f"{unemployment:.1f}%" if unemployment is not None else "Indisponível"
    trade_str = f"US$ {trade_balance/1000:.1f} Bilhões" if trade_balance else "Indisponível"
    debt_str = f"{gross_debt:.1f}%" if gross_debt is not None else "Indisponível"
    
    macro_data = {
        'Indicador Econômico': ['PIB Corrente Real', 'Taxa de Desemprego (PNAD)', 'Balança Comercial (Acum. Ano)', 'Dívida Bruta / PIB'],
        'Valor Atual': [gdp_str, unemp_str, trade_str, debt_str],
        'Fonte dos Dados': ['IBGE / BCB (SGS 22099)', 'IBGE / BCB (SGS 24369)', 'MDIC / BCB (SGS 26073)', 'Banco Central (SGS 13790)']
    }
    st.table(pd.DataFrame(macro_data))
    
    st.markdown("<hr style='border-color: #30363d;'/><p style='font-size: 0.8rem; color: #8b949e;'>Aviso: Os dados exibidos neste terminal são estritamente para fins informativos e analíticos, não configurando hipótese de recomendação ou assessoria de investimentos.</p>", unsafe_allow_html=True)
