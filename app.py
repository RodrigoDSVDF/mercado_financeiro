import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta

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

# ------------------- FUNÇÕES DE BUSCA OPTIMIZADAS -------------------
@st.cache_data(ttl=300)
def get_macro_bcb(serie):
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/1?formato=json"
        data = requests.get(url, timeout=5).json()
        return float(data[0]['valor'])
    except Exception:
        fallback = {432: 10.50, 12: 10.40, 4447: 4.50}
        return fallback.get(serie, 0.0)

@st.cache_data(ttl=300)
def get_market_summary():
    try:
        df = yf.download(["^BVSP", "USDBRL=X"], period="2d", progress=False)
        # Normalização de colunas para evitar MultiIndex
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
                    'Ticker': ticker.replace('.SA', ''),
                    'Preço': round(close_hoje, 2),
                    'Variação (%)': round(var, 2),
                    'Volume Diário': int(v_vol)
                })
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=['Ticker', 'Preço', 'Variação (%)', 'Volume Diário'])

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
        data = requests.get(url, timeout=5).json()
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        start_date = datetime.now() - timedelta(days=days)
        df = df[df['data'] >= start_date].sort_values('data')
        df['Date'] = df['data'].dt.date
        return df[['Date', 'valor']].rename(columns={'valor': name})
    except Exception:
        return pd.DataFrame(columns=['Date', name])

def calculate_quant_metrics(ticker, period="1y"):
    """Usa .history() para garantir retorno unidimensional limpo e sem erros de tipo."""
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

# ------------------- DATA LOADING -------------------
summary = get_market_summary()
selic = get_macro_bcb(432)
cdi = get_macro_bcb(12)
ipca = get_macro_bcb(4447)
juro_real = (((1 + (selic/100)) / (1 + (ipca/100))) - 1) * 100

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style='margin:0; font-size: 1.4rem; color: #f0f6fc;'>QUANT TERMINAL</h2>
            <div class="live-badge"><span class="pulse-dot"></span>LIVE</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.metric("Ibovespa", f"{summary['ibov']:,.0f}".replace(",", "."), f"{summary['ibov_pct']:.2f}%")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("Dólar Comercial", f"R$ {summary['dolar']:.4f}", f"{summary['dolar_pct']:.2f}%")
    
    st.markdown("<hr style='border-color: #30363d; margin: 25px 0;'/>", unsafe_allow_html=True)
    st.subheader("📌 Política Monetária")
    st.metric("SELIC Meta", f"{selic:.2f}%")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("IPCA (Acum. 12m)", f"{ipca:.2f}%")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    st.metric("Juro Real Est. Lqd.", f"{juro_real:.2f}%")
    
    st.markdown("<hr style='border-color: #30363d; margin: 25px 0;'/>", unsafe_allow_html=True)
    st.caption(f"Refreshed at: {datetime.now().strftime('%H:%M:%S')} BRT")

# ------------------- CORPO PRINCIPAL -------------------
st.markdown("""
    <div style="background: linear-gradient(90deg, #161b22 0%, #0d1117 100%); padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 25px;">
        <h1 style="margin: 0; color: #f0f6fc; font-size: 2rem;">Market Analytics & Quantitative Dashboard</h1>
        <p style="margin: 5px 0 0 0; color: #8b949e; font-size: 0.95rem;">Análise estrutural de volatilidade, liquidez de ativos e tracking macroeconômico brasileiro.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Global & Macro", 
    "🎯 Analytics Quantitativo", 
    "📋 Screeners de Mercado", 
    "⚙️ Fundamentos Estruturais"
])

# ------------------- TAB 1: VISÃO GLOBAL -------------------
with tab1:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem; margin-bottom:15px;'>Dinâmica Macro (Últimos 12 meses)</h3>", unsafe_allow_html=True)
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
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.markdown("<p style='color:#8b949e; font-size:0.85rem; font-weight:600;'>SPREAD HISTÓRICO: SELIC VS INFLAÇÃO (IPCA)</p>", unsafe_allow_html=True)
        df_selic_h = get_historical_macro(4390, "SELIC", days=365)
        df_ipca_h = get_historical_macro(4447, "IPCA", days=365)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_selic_h['Date'], y=df_selic_h['SELIC'], name='SELIC (%)', line=dict(color='#3fb950')))
        fig2.add_trace(go.Scatter(x=df_ipca_h['Date'], y=df_ipca_h['IPCA'], name='IPCA 12M (%)', line=dict(color='#d15704')))
        fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig2, use_container_width=True)

# ------------------- TAB 2: ANALYTICS QUANTITATIVO -------------------
with tab2:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem;'>Desestruturação e Análise de Risco</h3>", unsafe_allow_html=True)
    
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
        q_col2.metric("Maximum Drawdown do Período", f"{max_dd:.2f}%")
        q_col3.metric("Último Fechamento", f"R$ {current_close:.2f}")
        
        # Gráficos Quant
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Close'], name='Preço Base', line=dict(color='#f0f6fc')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_50'], name='MMA 50', line=dict(color='#f9826c', dash='dash')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_200'], name='MMA 200', line=dict(color='#58a6ff', dash='dot')))
        fig_price.update_layout(title="Rastreamento de Tendências & Médias Móveis", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_price, use_container_width=True)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Vol_21d'], name='Vol 21d', fill='tozeroy', line=dict(color='#dbab09')))
        fig_vol.update_layout(title="Cluster de Volatilidade Móvel (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220)
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.error("Dados indisponíveis para o ativo ou período selecionado.")

# ------------------- TAB 3: SCREENERS DE MERCADO -------------------
with tab3:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem; margin-bottom: 15px;'>Monitor de Liquidez B3</h3>", unsafe_allow_html=True)
    
    config_tabela = {
        "Ticker": st.column_config.TextColumn("Ativo", width="small"),
        "Preço": st.column_config.NumberColumn("Último Preço", format="R$ %.2f"),
        "Variação (%)": st.column_config.NumberColumn("Retorno Diário", format="%.2f%%"),
        "Volume Diário": st.column_config.NumberColumn("Volume Financeiro", format="%d")
    }
    
    sub_tab1, sub_tab2 = st.tabs(["⚡ Ações de Alta Liquidez", "🏢 Real Estate (FIIs)"])
    
    with sub_tab1:
        df_stocks = get_batch_assets(TICKERS_STOCKS)
        st.dataframe(df_stocks, column_config=config_tabela, use_container_width=True, hide_index=True)
        
    with sub_tab2:
        df_fiis = get_batch_assets(TICKERS_FIIS)
        st.dataframe(df_fiis, column_config=config_tabela, use_container_width=True, hide_index=True)

# ------------------- TAB 4: FUNDAMENTOS -------------------
with tab4:
    st.markdown("<h3 style='color: #f0f6fc; font-size: 1.2rem; margin-bottom: 15px;'>Dados Estruturais Macroeconômicos</h3>", unsafe_allow_html=True)
    
    macro_data = {
        'Indicador Estrutural': ['PIB Corrente Real', 'Taxa de Desemprego (PNAD)', 'Balança Comercial (YTD)', 'Dívida Bruta / PIB'],
        'Métrica': ['R$ 10,9 Trilhões', '6.4%', 'US$ 98.4 Bilhões', '74.5%'],
        'Dataset de Origem': ['IBGE', 'IBGE', 'MDIC', 'Banco Central']
    }
    st.table(pd.DataFrame(macro_data))
    
    st.markdown("<hr style='border-color: #30363d;'/><p style='font-size: 0.8rem; color: #8b949e;'>Aviso: Os dados exibidos neste terminal são estritamente para fins informativos e analíticos, não configurando hipótese de recomendação ou assessoria de investimentos.</p>", unsafe_allow_html=True)
