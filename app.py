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
    page_title="Raio-X da Carteira",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- FUNÇÕES DE BUSCA DE DADOS (com cache) -------------------

@st.cache_data(ttl=300)  # cache de 5 minutos
def get_macro():
    """Obtém dados macro: Selic, CDI, Ibovespa, Dólar."""
    try:
        # Selic (meta) - SGS Banco Central
        selic_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        selic_data = requests.get(selic_url).json()
        selic = float(selic_data[0]['valor'])
    except:
        selic = 13.75  # fallback

    try:
        # CDI (taxa diária acumulada no ano) - SGS
        cdi_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/1?formato=json"
        cdi_data = requests.get(cdi_url).json()
        cdi = float(cdi_data[0]['valor'])
    except:
        cdi = 13.65

    try:
        # Ibovespa
        ibov = yf.Ticker("^BVSP").history(period="1d")['Close'].iloc[-1]
    except:
        ibov = 120000

    try:
        # Dólar
        dolar = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        dolar = 5.20

    return {
        'selic': selic,
        'cdi': cdi,
        'ibov': ibov,
        'dolar': dolar
    }


@st.cache_data(ttl=300)
def get_historical_returns(ticker, period="1y"):
    """Retorna retornos diários e preço atual para um ticker."""
    try:
        # Adiciona .SA para B3
        if not ticker.endswith('.SA') and not ticker.startswith('^'):
            ticker_yf = ticker + '.SA'
        else:
            ticker_yf = ticker

        data = yf.download(ticker_yf, period=period, progress=False)
        if data.empty:
            return None, None
        # Retornos diários
        data['retorno'] = data['Close'].pct_change()
        retornos = data['retorno'].dropna()
        preco_atual = data['Close'].iloc[-1]
        return retornos, preco_atual
    except:
        return None, None


@st.cache_data(ttl=3600)
def get_sector(ticker):
    """Obtém o setor do ativo (dicionário manual para os mais comuns)."""
    # Mapeamento manual para ativos da B3 (expandir conforme necessário)
    sector_map = {
        'PETR4': 'Petróleo e Gás',
        'VALE3': 'Mineração',
        'ITUB4': 'Financeiro',
        'BBDC4': 'Financeiro',
        'ABEV3': 'Bebidas',
        'WEGE3': 'Máquinas',
        'RENT3': 'Aluguel de Carros',
        'BBAS3': 'Financeiro',
        'B3SA3': 'Financeiro',
        'ELET3': 'Energia Elétrica',
        'ELET6': 'Energia Elétrica',
        'SUZB3': 'Papel e Celulose',
        'RAIL3': 'Logística',
        'HAPV3': 'Saúde',
        'GGBR4': 'Siderurgia',
        'BRKM5': 'Química',
        'JBSS3': 'Alimentos',
        'LREN3': 'Varejo',
        'MGLU3': 'Varejo',
        'NTCO3': 'Cosméticos',
        'CIEL3': 'Tecnologia',
        'TOTS3': 'Tecnologia',
        'TAEE11': 'Energia',
    }
    # Remove sufixo .SA se presente
    ticker_clean = ticker.replace('.SA', '').upper()
    return sector_map.get(ticker_clean, 'Outros')


@st.cache_data(ttl=300)
def get_benchmark_returns(period="1y"):
    """Retorna retorno do CDI e Ibovespa no período."""
    # CDI (usando taxa acumulada) - vamos calcular aproximado
    # Para simplificar, usamos a Selic como proxy para CDI (próximo)
    macro = get_macro()
    # Retorno CDI (estimado) - na prática seria o acumulado, mas para MVP usamos a Selic anualizada
    cdi_ret = macro['cdi'] / 100  # converte para decimal

    # Ibovespa
    ibov = yf.Ticker("^BVSP")
    hist = ibov.history(period=period)
    if len(hist) > 0:
        ibov_ret = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1
    else:
        ibov_ret = 0.0
    return cdi_ret, ibov_ret


# ------------------- FUNÇÃO PRINCIPAL DE ANÁLISE -------------------

def analyze_portfolio(portfolio):
    """
    portfolio: dict {ticker: quantidade}
    Retorna dict com métricas e DataFrames para visualização.
    """
    tickers = list(portfolio.keys())
    quantidades = list(portfolio.values())

    # Buscar preços atuais e retornos históricos (1 ano)
    prices = []
    retornos_lista = []
    setores = []
    for ticker in tickers:
        ret, preco = get_historical_returns(ticker)
        if ret is not None and preco is not None:
            retornos_lista.append(ret)
            prices.append(preco)
        else:
            # Fallback: preço fictício e retorno zero
            prices.append(0.0)
            retornos_lista.append(pd.Series([0]))
        setor = get_sector(ticker)
        setores.append(setor)

    # Valor total investido
    valores = [p * q for p, q in zip(prices, quantidades)]
    total = sum(valores)

    if total == 0:
        return None

    # Peso de cada ativo
    pesos = [v / total for v in valores]

    # Concentração setorial
    sector_df = pd.DataFrame({'setor': setores, 'peso': pesos})
    sector_concentration = sector_df.groupby('setor')['peso'].sum().sort_values(ascending=False)
    max_concentration = sector_concentration.max() * 100  # em %

    # Rentabilidade da carteira (retorno ponderado dos últimos 12 meses)
    # Alinha os retornos diários (todos os ativos têm que ter mesma data)
    # Para simplificar, calculamos retorno acumulado de cada ativo no período
    retornos_acum = []
    for ret_series in retornos_lista:
        if len(ret_series) > 0:
            # retorno acumulado = (1+ret).prod() - 1
            acum = (1 + ret_series).prod() - 1
        else:
            acum = 0.0
        retornos_acum.append(acum)

    retorno_carteira = sum(p * r for p, r in zip(pesos, retornos_acum))

    # Benchmarks (CDI e Ibov)
    cdi_ret, ibov_ret = get_benchmark_returns()

    # Volatilidade (desvio padrão dos retornos diários ponderados)
    # Junta todos os retornos diários em um único DataFrame (alinhados por data)
    # Isso é mais complexo; para MVP, calculamos a volatilidade como média ponderada das volatilidades individuais
    volatilidades = [ret.std() for ret in retornos_lista if len(ret) > 1]
    if volatilidades:
        vol_carteira = sum(p * v for p, v in zip(pesos, volatilidades)) if len(volatilidades) > 0 else 0.0
    else:
        vol_carteira = 0.0

    # Score (nota de 0 a 100) - baseado em:
    # - Concentração: quanto menor, melhor (max 50% -> nota 0; 10% -> nota 100)
    # - Rentabilidade vs CDI: quanto maior, melhor
    # - Volatilidade: quanto menor, melhor (usando uma escala)

    # Nota concentração
    if max_concentration <= 20:
        nota_concentracao = 100
    elif max_concentration >= 60:
        nota_concentracao = 0
    else:
        nota_concentracao = 100 - (max_concentration - 20) * (100 / 40)

    # Nota rentabilidade (comparada com CDI)
    excesso_ret = retorno_carteira - cdi_ret
    # Mapeia: se > 5% => 100; se < -5% => 0
    nota_rentabilidade = np.clip((excesso_ret + 0.05) / 0.10 * 100, 0, 100)

    # Nota volatilidade (quanto menor melhor)
    # Consideramos vol anualizada (multiplicando por sqrt(252))
    vol_anual = vol_carteira * np.sqrt(252)
    if vol_anual <= 0.10:
        nota_volatilidade = 100
    elif vol_anual >= 0.30:
        nota_volatilidade = 0
    else:
        nota_volatilidade = 100 - (vol_anual - 0.10) * (100 / 0.20)

    # Score final (média ponderada)
    score = 0.4 * nota_concentracao + 0.3 * nota_rentabilidade + 0.3 * nota_volatilidade
    score = np.clip(score, 0, 100)

    # Preparar dados para gráficos
    # Gráfico de setores
    sector_plot = sector_concentration.reset_index()
    sector_plot.columns = ['Setor', 'Peso']

    # Gráfico de rentabilidade comparativa
    comp_returns = pd.DataFrame({
        'Carteira': [retorno_carteira * 100],
        'CDI': [cdi_ret * 100],
        'Ibovespa': [ibov_ret * 100]
    }).melt(var_name='Benchmark', value_name='Retorno (%)')

    # Resultado
    result = {
        'score': round(score, 1),
        'concentration': round(max_concentration, 1),
        'volatility': round(vol_anual * 100, 2),  # em %
        'return_carteira': round(retorno_carteira * 100, 2),
        'return_cdi': round(cdi_ret * 100, 2),
        'return_ibov': round(ibov_ret * 100, 2),
        'sector_df': sector_plot,
        'comp_returns': comp_returns,
        'portfolio_details': pd.DataFrame({
            'Ativo': tickers,
            'Preço (R$)': [round(p, 2) for p in prices],
            'Quantidade': quantidades,
            'Valor (R$)': [round(v, 2) for v in valores],
            'Peso (%)': [round(p*100, 2) for p in pesos],
            'Setor': setores,
            'Retorno (%)': [round(r*100, 2) for r in retornos_acum]
        })
    }
    return result


# ------------------- INTERFACE STREAMLIT -------------------

# Sidebar com dados macro
with st.sidebar:
    st.header("📈 Mercado Hoje")
    macro = get_macro()
    col1, col2 = st.columns(2)
    col1.metric("Selic", f"{macro['selic']:.2f}%")
    col2.metric("CDI", f"{macro['cdi']:.2f}%")
    st.metric("Ibovespa", f"{macro['ibov']:,.0f}".replace(',', '.'))
    st.metric("Dólar", f"R$ {macro['dolar']:.2f}")

    st.markdown("---")
    st.caption("Dados atualizados a cada 5 minutos")

# Título principal
st.title("🔍 Raio-X da Carteira")
st.markdown("### Descubra se sua carteira está bem diversificada e rentável")

# Formulário de entrada
with st.form("portfolio_form"):
    st.subheader("📋 Informe seus ativos")

    # Número de ativos (dinâmico)
    num_ativos = st.number_input("Quantos ativos você possui?", min_value=1, max_value=20, value=3, step=1)

    cols = st.columns(2)
    tickers = []
    quantidades = []

    for i in range(num_ativos):
        with cols[0]:
            ticker = st.text_input(f"Ticker {i+1}", key=f"ticker_{i}", placeholder="Ex: PETR4")
        with cols[1]:
            qtd = st.number_input(f"Quantidade {i+1}", min_value=0.0, step=1.0, key=f"qtd_{i}")
        tickers.append(ticker.strip().upper())
        quantidades.append(qtd)

    # Botão de submit
    submitted = st.form_submit_button("📊 Analisar Carteira", type="primary")

# Processar análise
if submitted:
    # Filtrar ativos com ticker não vazio e quantidade > 0
    portfolio = {}
    for t, q in zip(tickers, quantidades):
        if t and q > 0:
            portfolio[t] = q

    if not portfolio:
        st.warning("⚠️ Preencha pelo menos um ativo com quantidade válida.")
    else:
        with st.spinner("🔎 Calculando o raio-X da sua carteira..."):
            result = analyze_portfolio(portfolio)

        if result is None:
            st.error("❌ Não foi possível obter dados para os ativos informados. Verifique os tickers.")
        else:
            # Exibir resultados
            st.success("✅ Análise concluída com sucesso!")
            st.balloons()

            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 Score", f"{result['score']:.1f}/100")
            col2.metric("🎯 Concentração Setorial", f"{result['concentration']:.1f}%")
            col3.metric("📉 Volatilidade (anual)", f"{result['volatility']:.2f}%")
            col4.metric("📈 Retorno da Carteira (12m)", f"{result['return_carteira']:.2f}%")

            # Gráfico de setores
            st.subheader("📊 Distribuição por Setor")
            fig1 = px.pie(
                result['sector_df'],
                values='Peso',
                names='Setor',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)

            # Gráfico comparativo de rentabilidade
            st.subheader("📈 Rentabilidade vs. Benchmarks")
            fig2 = px.bar(
                result['comp_returns'],
                x='Benchmark',
                y='Retorno (%)',
                color='Benchmark',
                color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'],
                text_auto=True
            )
            fig2.update_layout(yaxis_title='Retorno (%)', showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

            # Tabela detalhada
            st.subheader("📋 Detalhamento da Carteira")
            st.dataframe(
                result['portfolio_details'].style.format({
                    'Preço (R$)': 'R$ {:.2f}',
                    'Valor (R$)': 'R$ {:.2f}',
                    'Peso (%)': '{:.2f}%',
                    'Retorno (%)': '{:.2f}%'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Alertas
            st.markdown("---")
            st.subheader("💡 Insights")

            if result['concentration'] > 50:
                st.warning("⚠️ **Alta concentração setorial:** mais de 50% da sua carteira está em um único setor. Considere diversificar para reduzir riscos.")
            else:
                st.success("✅ **Boa diversificação:** sua carteira está bem distribuída entre setores.")

            if result['return_carteira'] < result['return_cdi']:
                st.warning("⚠️ **Rentabilidade abaixo do CDI:** sua carteira rendeu menos que o CDI no último ano. Avalie a alocação.")
            else:
                st.success("✅ **Rentabilidade acima do CDI:** sua carteira superou o CDI. Bom trabalho!")

            if result['volatility'] > 25:
                st.warning("⚠️ **Alta volatilidade:** sua carteira apresenta oscilações significativas. Pode ser adequada para perfis arrojados, mas requer atenção.")
            else:
                st.success("✅ **Volatilidade controlada:** sua carteira tem risco moderado.")

            # Rodapé
            st.markdown("---")
            st.caption("🚀 Dados fornecidos por Yahoo Finance e Banco Central. Esta é uma ferramenta demonstrativa e não substitui uma consultoria financeira profissional.")
