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
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except:
            locale.setlocale(locale.LC_ALL, '')

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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-primary: #0a0e16;
        --bg-secondary: #11161f;
        --bg-card-from: #141a24;
        --bg-card-to: #0e131b;
        --border-subtle: rgba(148, 163, 184, 0.14);
        --border-hover: rgba(88, 166, 255, 0.5);
        --text-primary: #f0f6fc;
        --text-secondary: #8b949e;
        --text-tertiary: #5c6673;
        --accent-sapphire: #4d8eff;
        --accent-sapphire-glow: rgba(77, 142, 255, 0.35);
        --accent-ice: #7dd3fc;
        --accent-green: #3fb950;
        --accent-red: #f85149;
        --radius-md: 10px;
        --radius-lg: 16px;
        --shadow-card: 0 1px 2px rgba(0, 0, 0, 0.45), 0 10px 26px -12px rgba(0, 0, 0, 0.55);
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-primary);
    }

    [data-testid="stAppViewContainer"] { position: relative; }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
        opacity: 0.025;
        mix-blend-mode: overlay;
        pointer-events: none;
        z-index: 0;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }

    /* ---------- Fita de cotações ---------- */
    .ticker-tape {
        position: relative;
        width: 100%;
        overflow: hidden;
        background: linear-gradient(90deg, var(--bg-secondary), #161d29, var(--bg-secondary));
        border: 1px solid var(--border-subtle);
        border-radius: 999px;
        padding: 11px 0;
        margin-bottom: 22px;
    }
    .ticker-tape::before, .ticker-tape::after {
        content: "";
        position: absolute;
        top: 0; bottom: 0;
        width: 64px;
        z-index: 2;
        pointer-events: none;
    }
    .ticker-tape::before { left: 0; background: linear-gradient(90deg, var(--bg-secondary), transparent); }
    .ticker-tape::after { right: 0; background: linear-gradient(270deg, var(--bg-secondary), transparent); }
    .ticker-track {
        display: flex;
        width: max-content;
        animation: ticker-scroll 34s linear infinite;
    }
    .ticker-tape:hover .ticker-track { animation-play-state: paused; }
    @keyframes ticker-scroll {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }
    .ticker-item {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 0 26px;
        border-right: 1px solid var(--border-subtle);
        white-space: nowrap;
        font-family: 'JetBrains Mono', monospace;
    }
    .ticker-label { color: var(--text-tertiary); font-size: 0.68rem; letter-spacing: 0.09em; font-weight: 600; }
    .ticker-value { color: var(--text-primary); font-weight: 700; font-size: 0.85rem; }
    .ticker-value.up { color: var(--accent-green); }
    .ticker-value.down { color: var(--accent-red); }
    .ticker-delta { font-size: 0.78rem; font-weight: 600; }
    .ticker-delta.up { color: var(--accent-green); }
    .ticker-delta.down { color: var(--accent-red); }

    /* ---------- Banner principal ---------- */
    .hero-banner {
        position: relative;
        background:
            radial-gradient(circle at 12% 18%, rgba(77, 142, 255, 0.16), transparent 45%),
            linear-gradient(135deg, #121826 0%, #0a0e16 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        margin-bottom: 26px;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
        background-size: 34px 34px;
        pointer-events: none;
    }
    .hero-tag {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.1em;
        color: var(--accent-ice);
        background: rgba(77, 142, 255, 0.1);
        border: 1px solid rgba(77, 142, 255, 0.28);
        padding: 5px 11px;
        border-radius: 7px;
        margin-bottom: 14px;
    }
    .hero-title { position: relative; margin: 0; font-size: 2rem; }
    .hero-subtitle { position: relative; margin: 6px 0 0 0; color: var(--text-secondary); font-size: 0.95rem; max-width: 640px; }

    /* ---------- Labels e títulos de seção ---------- */
    .section-label {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--text-tertiary);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .section-label::before {
        content: "";
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--accent-sapphire);
        flex-shrink: 0;
    }
    .section-title {
        position: relative;
        padding-left: 14px;
        margin: 4px 0 18px 0 !important;
        font-size: 1.2rem !important;
    }
    .section-title::before {
        content: "";
        position: absolute;
        left: 0; top: 3px; bottom: 3px;
        width: 3px;
        border-radius: 3px;
        background: linear-gradient(180deg, var(--accent-sapphire), var(--accent-ice));
    }

    hr, hr.divider {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 24px 0 18px 0;
    }
    .disclaimer { font-size: 0.8rem; color: var(--text-tertiary); }
    .metric-gap { margin-bottom: 12px; }

    /* ---------- Cards de métrica ---------- */
    div[data-testid="stMetric"] {
        background: linear-gradient(160deg, var(--bg-card-from) 0%, var(--bg-card-to) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 15px 20px;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
        transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    }
    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-sapphire), var(--accent-ice));
        opacity: 0;
        transition: opacity 0.22s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: var(--border-hover);
        transform: translateY(-3px);
        box-shadow: 0 14px 30px -12px var(--accent-sapphire-glow), var(--shadow-card);
    }
    div[data-testid="stMetric"]:hover::before { opacity: 1; }
    div[data-testid="stMetricLabel"] > div {
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] > div {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 1.8rem !important;
        color: var(--text-primary) !important;
    }

    /* ---------- Correção: labels de metric na sidebar não cortam ---------- */
    section[data-testid="stSidebar"] div[data-testid="stMetricLabel"] > div {
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.35 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stMetricValue"] > div {
        font-size: 1.4rem !important;
    }

    /* ---------- Abas ---------- */
    button[data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-secondary);
        border-bottom: 2px solid transparent;
        padding: 10px 20px;
        transition: color 0.18s ease, border-color 0.18s ease;
    }
    button[data-baseweb="tab"]:hover { color: var(--text-primary); }
    button[aria-selected="true"] {
        color: var(--accent-ice) !important;
        border-bottom-color: var(--accent-sapphire) !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-primary);
        border-right: 1px solid var(--border-subtle);
    }
    .sidebar-brand {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 22px;
    }
    .sidebar-brand h2 {
        margin: 0;
        font-size: 1.3rem;
        letter-spacing: -0.01em;
    }
    .sidebar-eyebrow {
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.92rem;
        margin: 4px 0 14px 0;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(46, 160, 67, 0.15);
        color: var(--accent-green);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        border: 1px solid rgba(46, 160, 67, 0.3);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.04em;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: var(--accent-green);
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

    /* ---------- Scrollbar customizada ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: #1f2630; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-sapphire); }
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

# ------------------- FUNÇÕES UTILITÁRIAS -------------------
def parse_br_number(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip()
    if not s:
        return None
    try:
        return locale.atof(s)
    except:
        pass
    try:
        s_temp = re.sub(r'\.(?=\d{3})', '', s)
        s_temp = s_temp.replace(',', '.')
        return float(s_temp)
    except:
        pass
    try:
        return float(s)
    except:
        return None

def is_missing(value):
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False

def fmt_br(value, decimals=0, prefix="", suffix="", fallback="Indisponível"):
    if is_missing(value):
        return fallback
    texto = f"{value:,.{decimals}f}"
    if decimals > 0:
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        texto = texto.replace(",", ".")
    return f"{prefix}{texto}{suffix}"

def fmt_pct(value, decimals=2, fallback="Indisponível"):
    if is_missing(value):
        return fallback
    return f"{value:.{decimals}f}%"

# ------------------- FUNÇÕES DE BUSCA -------------------
@st.cache_data(ttl=300)
def get_macro_bcb(serie):
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return parse_br_number(data[0]['valor'])
    except Exception as e:
        print(f"Erro ao buscar série {serie}: {e}")
        return None

@st.cache_data(ttl=3600)
def get_ipca_acumulado_12m():
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
        df = df.sort_values('data').tail(13)
        if len(df) < 13:
            return None
        acumulado = 1.0
        for _, row in df.iterrows():
            acumulado *= (1 + row['valor'] / 100)
        return (acumulado - 1) * 100
    except Exception as e:
        print(f"Erro ao calcular IPCA acumulado: {e}")
        return None

@st.cache_data(ttl=86400)
def get_annual_gdp():
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
        df = df.sort_values('data').tail(4)
        return df['valor'].sum() / 1e12
    except Exception as e:
        print(f"Erro ao buscar PIB: {e}")
        return None

@st.cache_data(ttl=300)
def get_market_summary():
    try:
        df = yf.download(["^BVSP", "USDBRL=X"], period="5d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns]

        ibov_serie = df['Close_^BVSP'].dropna()
        dolar_serie = df['Close_USDBRL=X'].dropna()

        if len(ibov_serie) < 2 or len(dolar_serie) < 2:
            raise ValueError("Histórico insuficiente.")

        ibov_hoje = ibov_serie.iloc[-1]
        ibov_pct = ((ibov_hoje / ibov_serie.iloc[-2]) - 1) * 100
        dolar_hoje = dolar_serie.iloc[-1]
        dolar_pct = ((dolar_hoje / dolar_serie.iloc[-2]) - 1) * 100
        return {'ibov': ibov_hoje, 'ibov_pct': ibov_pct, 'dolar': dolar_hoje, 'dolar_pct': dolar_pct}
    except Exception as e:
        print(f"Erro ao buscar resumo de mercado: {e}")
        return {'ibov': None, 'ibov_pct': None, 'dolar': None, 'dolar_pct': None}

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

# ------------------- RENDERIZAÇÃO -------------------
def render_ticker_tape(summary, selic, ipca, juro_real):
    def item(label, value_html, delta=None, value_class=""):
        value_class_attr = f" {value_class}" if value_class else ""
        if delta is None or is_missing(delta):
            delta_html = ""
        else:
            arrow = "▲" if delta >= 0 else "▼"
            cls = "up" if delta >= 0 else "down"
            delta_html = f"<span class='ticker-delta {cls}'>{arrow} {abs(delta):.2f}%</span>"
        return (
            f'<div class="ticker-item">'
            f'<span class="ticker-label">{label}</span>'
            f'<span class="ticker-value{value_class_attr}">{value_html}</span>'
            f'{delta_html}</div>'
        )

    juro_cls = "" if is_missing(juro_real) else ("up" if juro_real >= 0 else "down")

    items = [
        item("IBOVESPA", fmt_br(summary['ibov'], decimals=0), summary['ibov_pct']),
        item("USD/BRL", fmt_br(summary['dolar'], decimals=4, prefix="R$ "), summary['dolar_pct']),
        item("SELIC META", fmt_pct(selic)),
        item("IPCA 12M", fmt_pct(ipca)),
        item("JURO REAL", fmt_pct(juro_real), value_class=juro_cls),
    ]
    track_html = "".join(items) * 2

    st.markdown(
        f'<div class="ticker-tape"><div class="ticker-track">{track_html}</div></div>',
        unsafe_allow_html=True
    )

# ------------------- CARREGAMENTO DE DADOS -------------------
summary = get_market_summary()
selic = get_macro_bcb(432)
cdi = get_macro_bcb(12)
ipca = get_ipca_acumulado_12m()

if not is_missing(selic) and not is_missing(ipca):
    juro_real = (((1 + (selic / 100)) / (1 + (ipca / 100))) - 1) * 100
else:
    juro_real = None

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <h2>TERMINAL QUANT</h2>
            <div class="live-badge"><span class="pulse-dot"></span>AO VIVO</div>
        </div>
    """, unsafe_allow_html=True)

    st.metric("Ibovespa", fmt_br(summary['ibov'], decimals=0), fmt_pct(summary['ibov_pct'], fallback=None))
    st.markdown("<div class='metric-gap'></div>", unsafe_allow_html=True)
    st.metric("Dólar Comercial", fmt_br(summary['dolar'], decimals=4, prefix="R$ "), fmt_pct(summary['dolar_pct'], fallback=None))

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-eyebrow'>📌 Política Monetária</p>", unsafe_allow_html=True)

    st.metric("SELIC Meta", fmt_pct(selic))
    st.markdown("<div class='metric-gap'></div>", unsafe_allow_html=True)
    st.metric("IPCA (12 meses)", fmt_pct(ipca))
    st.markdown("<div class='metric-gap'></div>", unsafe_allow_html=True)
    st.metric("Juro Real", fmt_pct(juro_real))

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.caption(f"Atualizado em: {datetime.now().strftime('%H:%M:%S')} BRT")

# ------------------- CORPO PRINCIPAL -------------------
render_ticker_tape(summary, selic, ipca, juro_real)

st.markdown("""
    <div class="hero-banner">
        <span class="hero-tag">⌁ TERMINAL QUANT · DADOS B3 / BCB</span>
        <h1 class="hero-title">Analytics de Mercado &amp; Dashboard Quantitativo</h1>
        <p class="hero-subtitle">Análise estrutural de volatilidade, liquidez de ativos e monitoramento macroeconômico brasileiro.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Global & Macro",
    "🎯 Análise Quantitativa",
    "📋 Monitor de Mercado",
    "⚙️ Dados Estruturais"
])

# ------------------- TAB 1 -------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p class='section-label'>Performance relativa: Ibovespa vs Dólar (base 100)</p>", unsafe_allow_html=True)
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
        st.markdown("<p class='section-label'>Spread histórico: Selic vs IPCA Acumulado (12 meses)</p>", unsafe_allow_html=True)

        # --- CORREÇÃO: usar série 10844 para IPCA acumulado ---
        df_selic_h = get_historical_macro(432, "SELIC", days=365)
        df_ipca_h  = get_historical_macro(10844, "IPCA Acumulado", days=365)   # <--- ALTERADO

        fig2 = go.Figure()

        if not df_selic_h.empty:
            fig2.add_trace(go.Scatter(
                x=df_selic_h['Date'],
                y=df_selic_h['SELIC'],
                name='SELIC (%)',
                line=dict(color='#3fb950', width=2)
            ))

        if not df_ipca_h.empty:
            fig2.add_trace(go.Scatter(
                x=df_ipca_h['Date'],
                y=df_ipca_h['IPCA Acumulado'],
                name='IPCA Acum. 12m (%)',
                line=dict(color='#d15704', width=2)
            ))

        # --- LINHA HORIZONTAL EM 0 (referência) ---
        fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        # --- ANOTAÇÃO DO SPREAD ATUAL (Juro Real) ---
        if not is_missing(juro_real):
            data_atual = datetime.now().strftime("%d/%m/%Y")
            anotacao = f"Juro Real atual: {juro_real:.2f}% ({data_atual})"
            fig2.add_annotation(
                x=0.98,
                y=0.98,
                xref="paper",
                yref="paper",
                text=anotacao,
                showarrow=False,
                font=dict(color="white", size=11, family="JetBrains Mono"),
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor="white",
                borderwidth=1,
                borderpad=4,
                opacity=0.9,
                align="right"
            )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='divider'/>", unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Análise de correlação paralela: todas as ações da carteira (base histórica 100)</p>", unsafe_allow_html=True)

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

# ------------------- TAB 2 -------------------
with tab2:
    st.markdown("<h3 class='section-title'>Análise de Risco e Volatilidade Individual</h3>", unsafe_allow_html=True)

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

        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Close'], name='Preço', line=dict(color='#f0f6fc')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_50'], name='Média Móvel 50d', line=dict(color='#f9826c', dash='dash')))
        fig_price.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['MMA_200'], name='Média Móvel 200d', line=dict(color='#58a6ff', dash='dot')))
        fig_price.update_layout(title="Tendências de Preço & Médias Móveis", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_price, use_container_width=True)

        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=quant_df['Date'], y=quant_df['Vol_21d'], name='Volatilidade', fill='tozeroy', line=dict(color='#dbab09')))
        fig_vol.update_layout(title="Volatilidade Móvel Histórica (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220)
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.error("Dados indisponíveis para o ativo ou período selecionado.")

# ------------------- TAB 3 -------------------
with tab3:
    st.markdown("<h3 class='section-title'>Monitor de Liquidez B3</h3>", unsafe_allow_html=True)

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

# ------------------- TAB 4 -------------------
with tab4:
    st.markdown("<h3 class='section-title'>Dados Estruturais da Economia</h3>", unsafe_allow_html=True)

    gdp_annual = get_annual_gdp()
    unemployment = get_macro_bcb(24369)
    trade_balance = get_macro_bcb(26073)
    gross_debt = get_macro_bcb(13790)

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

    st.markdown("<hr class='divider'/><p class='disclaimer'>Aviso: os dados exibidos neste terminal são estritamente para fins informativos e analíticos, não configurando hipótese de recomendação ou assessoria de investimentos.</p>", unsafe_allow_html=True)
