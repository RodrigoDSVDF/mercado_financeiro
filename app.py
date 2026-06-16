import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
import time

# ------------------- CONFIGURAÇÃO DA PÁGINA -------------------
st.set_page_config(
    page_title="Dashboard do Mercado Financeiro BR",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- FUNÇÕES DE BUSCA (com cache) -------------------

@st.cache_data(ttl=300)  # atualiza a cada 5 minutos
def get_selic():
    """Obtém a taxa Selic meta atual (SGS - BCB)."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        data = requests.get(url).json()
        return float(data[0]['valor'])
    except:
        return 13.75  # fallback

@st.cache_data(ttl=300)
def get_cdi():
    """Obtém a taxa CDI acumulada no ano (SGS - BCB)."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/1?formato=json"
        data = requests.get(url).json()
        return float(data[0]['valor'])
    except:
        return 13.65

@st.cache_data(ttl=300)
def get_ipca():
    """Obtém o IPCA acumulado nos últimos 12 meses (SGS - BCB)."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4447/dados/ultimos/1?formato=json"
        data = requests.get(url).json()
        return float(data[0]['valor'])
    except:
        return 4.5

@st.cache_data(ttl=300)
def get_ibov():
    """Obtém o valor atual do Ibovespa."""
    try:
        ticker = yf.Ticker("^BVSP")
        hist = ticker.history(period="1d")
        return hist['Close'].iloc[-1]
    except:
        return 120000.0

@st.cache_data(ttl=300)
def get_dolar():
    """Obtém a cotação do Dólar (USDBRL)."""
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="1d")
        return hist['Close'].iloc[-1]
    except:
        return 5.20

@st.cache_data(ttl=3600)
def get_historical_ibov(period="1y"):
    """Retorna histórico do Ibovespa para o período."""
    try:
        ticker = yf.Ticker("^BVSP")
        hist = ticker.history(period=period)
        hist = hist.reset_index()
        hist['Date'] = pd.to_datetime(hist['Date']).dt.date
        return hist[['Date', 'Close']].rename(columns={'Close': 'Ibovespa'})
    except:
        return pd.DataFrame(columns=['Date', 'Ibovespa'])

@st.cache_data(ttl=3600)
def get_historical_dolar(period="1y"):
    """Retorna histórico do Dólar para o período."""
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period=period)
        hist = hist.reset_index()
        hist['Date'] = pd.to_datetime(hist['Date']).dt.date
        return hist[['Date', 'Close']].rename(columns={'Close': 'Dólar'})
    except:
        return pd.DataFrame(columns=['Date', 'Dólar'])

@st.cache_data(ttl=3600)
def get_historical_selic(period="1y"):
    """Obtém histórico da Selic (SGS - BCB) para o período."""
    try:
        # Usamos a série 4390 (Selic meta anualizada) - dados diários
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
        data = requests.get(url).json()
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        # Filtra pelo período
        start_date = datetime.now() - timedelta(days=365)
        df = df[df['data'] >= start_date]
        df = df.sort_values('data')
        df['Date'] = df['data'].dt.date
        return df[['Date', 'valor']].rename(columns={'valor': 'Selic'})
    except:
        return pd.DataFrame(columns=['Date', 'Selic'])

@st.cache_data(ttl=3600)
def get_historical_ipca(period="1y"):
    """Obtém histórico do IPCA (SGS - BCB) - dados mensais."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4447/dados?formato=json"
        data = requests.get(url).json()
        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        # Filtra último ano
        start_date = datetime.now() - timedelta(days=365)
        df = df[df['data'] >= start_date]
        df = df.sort_values('data')
        df['Date'] = df['data'].dt.date
        return df[['Date', 'valor']].rename(columns={'valor': 'IPCA'})
    except:
        return pd.DataFrame(columns=['Date', 'IPCA'])

@st.cache_data(ttl=300)
def get_top_stocks():
    """Retorna lista das principais ações da B3 com preço e variação."""
    tickers = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
        'WEGE3.SA', 'RENT3.SA', 'BBAS3.SA', 'B3SA3.SA', 'ELET3.SA',
        'SUZB3.SA', 'RAIL3.SA', 'HAPV3.SA', 'GGBR4.SA', 'BRKM5.SA',
        'JBSS3.SA', 'LREN3.SA', 'MGLU3.SA', 'NTCO3.SA', 'CIEL3.SA'
    ]
    data = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                close_hoje = hist['Close'].iloc[-1]
                close_ontem = hist['Close'].iloc[-2]
                var = ((close_hoje / close_ontem) - 1) * 100
                data.append({
                    'Ticker': ticker.replace('.SA', ''),
                    'Preço (R$)': round(close_hoje, 2),
                    'Variação (%)': round(var, 2)
                })
            else:
                # fallback
                data.append({'Ticker': ticker.replace('.SA', ''), 'Preço (R$)': 0.0, 'Variação (%)': 0.0})
        except:
            data.append({'Ticker': ticker.replace('.SA', ''), 'Preço (R$)': 0.0, 'Variação (%)': 0.0})
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def get_top_fiis():
    """Retorna lista dos principais FIIs com preço e variação."""
    tickers = [
        'HGLG11.SA', 'KNRI11.SA', 'VISC11.SA', 'MXRF11.SA', 'BRCR11.SA',
        'HGRU11.SA', 'BCFF11.SA', 'XPLG11.SA', 'HSML11.SA', 'RBRR11.SA'
    ]
    data = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                close_hoje = hist['Close'].iloc[-1]
                close_ontem = hist['Close'].iloc[-2]
                var = ((close_hoje / close_ontem) - 1) * 100
                data.append({
                    'Ticker': ticker.replace('.SA', ''),
                    'Preço (R$)': round(close_hoje, 2),
                    'Variação (%)': round(var, 2)
                })
            else:
                data.append({'Ticker': ticker.replace('.SA', ''), 'Preço (R$)': 0.0, 'Variação (%)': 0.0})
        except:
            data.append({'Ticker': ticker.replace('.SA', ''), 'Preço (R$)': 0.0, 'Variação (%)': 0.0})
    return pd.DataFrame(data)

# ------------------- INDICADORES ECONÔMICOS (dados estáticos + atualização via API) -------------------

@st.cache_data(ttl=86400)  # atualiza 1x por dia
def get_economic_indicators():
    """Retorna um dicionário com indicadores econômicos diversos."""
    # Para dados que não têm API fácil, usamos valores fixos (atualizados manualmente)
    # Em produção, pode-se integrar com IBGE, IPEA, etc.
    return {
        'PIB (2023)': 'R$ 10,9 trilhões',
        'Taxa de Desemprego (2024)': '6,5%',
        'Balança Comercial (2024)': 'US$ 98,4 bi',
        'Reservas Internacionais': 'US$ 355 bi',
        'Dívida Bruta/PIB': '74,5%',
        'Rating Soberano': 'BB- (S&P)'
    }

# ------------------- INTERFACE STREAMLIT -------------------

# Sidebar com resumo rápido
with st.sidebar:
    st.header("📊 Resumo do Dia")
    selic = get_selic()
    cdi = get_cdi()
    ipca = get_ipca()
    ibov = get_ibov()
    dolar = get_dolar()

    col1, col2 = st.columns(2)
    col1.metric("Selic", f"{selic:.2f}%")
    col2.metric("CDI", f"{cdi:.2f}%")
    st.metric("IPCA (12m)", f"{ipca:.2f}%")
    st.metric("Ibovespa", f"{ibov:,.0f}".replace(',', '.'))
    st.metric("Dólar", f"R$ {dolar:.2f}")

    st.markdown("---")
    st.caption("Dados atualizados a cada 5 minutos")

# Título principal
st.title("📈 Dashboard do Mercado Financeiro Brasileiro")
st.markdown("### Análise completa de indicadores macro, ações e FIIs")

# Abas para organização
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📈 Gráficos Históricos", "📋 Ações & FIIs", "🏦 Indicadores Econômicos"])

# ------------------- TAB 1: VISÃO GERAL -------------------
with tab1:
    st.subheader("Cotações em Tempo Real")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ibovespa", f"{ibov:,.0f}".replace(',', '.'), delta=None)
    col2.metric("Dólar (USDBRL)", f"R$ {dolar:.2f}")
    col3.metric("Selic", f"{selic:.2f}%")
    col4.metric("IPCA (últimos 12m)", f"{ipca:.2f}%")

    st.markdown("---")
    st.subheader("📊 Principais Índices (últimos 30 dias)")
    # Gráfico de linha com Ibovespa e Dólar (escalas separadas)
    df_ibov = get_historical_ibov(period="1mo")
    df_dolar = get_historical_dolar(period="1mo")
    if not df_ibov.empty and not df_dolar.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_ibov['Date'], y=df_ibov['Ibovespa'], name='Ibovespa', yaxis='y1'))
        fig.add_trace(go.Scatter(x=df_dolar['Date'], y=df_dolar['Dólar'], name='Dólar (R$)', yaxis='y2'))
        fig.update_layout(
            yaxis=dict(title='Ibovespa', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
            yaxis2=dict(title='Dólar (R$)', overlaying='y', side='right', titlefont=dict(color='red'), tickfont=dict(color='red')),
            legend=dict(x=0.01, y=0.99),
            xaxis_title='Data'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados históricos indisponíveis no momento.")

# ------------------- TAB 2: GRÁFICOS HISTÓRICOS -------------------
with tab2:
    st.subheader("📉 Evolução Histórica (últimos 12 meses)")

    # Seletor de período
    periodo = st.selectbox("Período", ["1m", "3m", "6m", "1y", "2y", "5y"], index=3)

    # Busca dados
    df_ibov = get_historical_ibov(period=periodo)
    df_dolar = get_historical_dolar(period=periodo)
    df_selic = get_historical_selic(period=periodo)
    df_ipca = get_historical_ipca(period=periodo)

    # Gráfico 1: Ibovespa e Dólar (eixo duplo)
    if not df_ibov.empty and not df_dolar.empty:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_ibov['Date'], y=df_ibov['Ibovespa'], name='Ibovespa', yaxis='y1', line=dict(color='blue')))
        fig1.add_trace(go.Scatter(x=df_dolar['Date'], y=df_dolar['Dólar'], name='Dólar (R$)', yaxis='y2', line=dict(color='red')))
        fig1.update_layout(
            yaxis=dict(title='Ibovespa', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
            yaxis2=dict(title='Dólar (R$)', overlaying='y', side='right', titlefont=dict(color='red'), tickfont=dict(color='red')),
            xaxis_title='Data',
            legend=dict(x=0.01, y=0.99),
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("Dados do Ibovespa ou Dólar indisponíveis.")

    # Gráfico 2: Selic e IPCA (eixo duplo)
    if not df_selic.empty and not df_ipca.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_selic['Date'], y=df_selic['Selic'], name='Selic (%)', yaxis='y1', line=dict(color='green')))
        fig2.add_trace(go.Scatter(x=df_ipca['Date'], y=df_ipca['IPCA'], name='IPCA (%)', yaxis='y2', line=dict(color='orange')))
        fig2.update_layout(
            yaxis=dict(title='Selic (%)', titlefont=dict(color='green'), tickfont=dict(color='green')),
            yaxis2=dict(title='IPCA (%)', overlaying='y', side='right', titlefont=dict(color='orange'), tickfont=dict(color='orange')),
            xaxis_title='Data',
            legend=dict(x=0.01, y=0.99),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Dados da Selic ou IPCA indisponíveis.")

# ------------------- TAB 3: AÇÕES E FIIs -------------------
with tab3:
    st.subheader("📋 Principais Ações da B3")
    df_stocks = get_top_stocks()
    if not df_stocks.empty:
        # Aplicar cores na variação
        def color_var(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
            return f'color: {color}'
        st.dataframe(
            df_stocks.style.applymap(color_var, subset=['Variação (%)']).format({'Preço (R$)': 'R$ {:.2f}', 'Variação (%)': '{:.2f}%'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Não foi possível carregar as ações.")

    st.markdown("---")
    st.subheader("🏢 Principais Fundos Imobiliários (FIIs)")
    df_fiis = get_top_fiis()
    if not df_fiis.empty:
        st.dataframe(
            df_fiis.style.applymap(color_var, subset=['Variação (%)']).format({'Preço (R$)': 'R$ {:.2f}', 'Variação (%)': '{:.2f}%'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Não foi possível carregar os FIIs.")

    # Download dos dados
    csv = df_stocks.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar dados das ações (CSV)", data=csv, file_name="acoes_b3.csv", mime="text/csv")

# ------------------- TAB 4: INDICADORES ECONÔMICOS -------------------
with tab4:
    st.subheader("🏦 Indicadores Macroeconômicos")
    eco = get_economic_indicators()
    cols = st.columns(3)
    for i, (key, value) in enumerate(eco.items()):
        cols[i % 3].metric(key, value)

    st.markdown("---")
    st.subheader("📚 Fontes dos dados")
    st.markdown("""
    - **Selic, CDI, IPCA**: Banco Central do Brasil (SGS)
    - **Ibovespa, Ações, FIIs, Dólar**: Yahoo Finance
    - **Indicadores econômicos**: IBGE, IPEA, Banco Central (dados estáticos para demonstração)
    """)

    st.caption("🚀 Este dashboard é uma ferramenta demonstrativa e não constitui recomendação de investimento.")

# ------------------- RODAPÉ -------------------
st.markdown("---")
st.caption("Desenvolvido com ❤️ usando Streamlit | Dados atualizados automaticamente")
