<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entenda os Indicadores Económicos</title>
    <!-- Tailwind CSS para estilização rápida e moderna -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Font Awesome para ícones consistentes -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js para o gráfico interactivo do simulador -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Configuração personalizada do Tailwind -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            navy: '#0b3b5c',
                            teal: '#1a7f7a',
                            lightBg: '#f8fafc',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body {
            font-family: 'Inter', sans-serif;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
            animation: fadeIn 0.4s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between">

    <div class="max-w-6xl w-full mx-auto px-4 py-8 flex-grow">
        <!-- Cabeçalho Principal -->
        <header class="text-center mb-10">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 text-blue-800 text-sm font-semibold mb-3 border border-blue-100">
                <i class="fas fa-graduation-cap"></i>
                <span>Plataforma de Estudo Interactiva</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-brand-navy to-brand-teal bg-clip-text text-transparent">
                📊 Indicadores Económicos Descomplicados
            </h1>
            <p class="mt-3 text-lg text-slate-600 max-w-2xl mx-auto">
                Aprenda como funcionam as engrenagens da economia brasileira através de conceitos simples, analogias e simulações práticas.
            </p>
        </header>

        <!-- Layout de Colunas (Navegação à esquerda, Conteúdo à direita no Desktop) -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            <!-- Barra de Navegação por Abas (Menu) -->
            <nav class="lg:col-span-1 bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-1 h-fit">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">Conceitos Chave</p>
                <button onclick="switchTab('selic')" id="btn-selic" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 bg-brand-navy text-white shadow-sm">
                    <i class="fas fa-coins w-5 text-center text-lg"></i>
                    <span>Taxa SELIC</span>
                </button>
                <button onclick="switchTab('ipca')" id="btn-ipca" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-chart-line w-5 text-center text-lg"></i>
                    <span>IPCA (Inflação)</span>
                </button>
                <button onclick="switchTab('pib')" id="btn-pib" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-building w-5 text-center text-lg"></i>
                    <span>PIB</span>
                </button>
                <button onclick="switchTab('desemprego')" id="btn-desemprego" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-user-friends w-5 text-center text-lg"></i>
                    <span>Desemprego</span>
                </button>
                <button onclick="switchTab('dividapib')" id="btn-dividapib" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-hand-holding-usd w-5 text-center text-lg"></i>
                    <span>Dívida / PIB</span>
                </button>
                <button onclick="switchTab('balanca')" id="btn-balanca" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-ship w-5 text-center text-lg"></i>
                    <span>Balança Comercial</span>
                </button>

                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mt-6 mb-2">Praticar e Testar</p>
                <button onclick="switchTab('simulador')" id="btn-simulador" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-calculator w-5 text-center text-lg text-amber-500"></i>
                    <span class="text-amber-600">Simulador Real</span>
                </button>
                <button onclick="switchTab('quiz')" id="btn-quiz" class="tab-btn w-full text-left px-4 py-3 rounded-xl font-semibold flex items-center gap-3 transition-all duration-200 text-slate-600 hover:bg-slate-50">
                    <i class="fas fa-gamepad w-5 text-center text-lg text-emerald-500"></i>
                    <span class="text-emerald-600">Testar Conhecimento</span>
                </button>
            </nav>

            <!-- Zona de Conteúdo -->
            <main class="lg:col-span-3">

                <!-- TAB: SELIC -->
                <article id="tab-selic" class="tab-content active bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-teal-50 text-teal-600 rounded-xl text-2xl">
                                <i class="fas fa-coins"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">Taxa SELIC</h2>
                                <p class="text-sm text-slate-500">Taxa básica de juro da economia</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-teal-50 text-teal-800 font-bold text-lg rounded-xl border border-teal-100">
                            14.50% a.a.
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                A SELIC (Sistema Especial de Liquidação e de Custódia) é a taxa básica de juro da economia brasileira. É a ferramenta mais poderosa do Banco Central para travar a escalada de preços (inflação).
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                Imagine a economia como um <strong>carro numa descida</strong>. Se começar a correr depressa demais (inflação a disparar), o Banco Central pisa no travão aumentando a taxa SELIC. Com o juro alto, os empréstimos ficam caros, o consumo diminui e a velocidade do carro estabiliza.
                            </p>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-100">
                            <div class="p-4 bg-slate-50 rounded-xl">
                                <h4 class="font-bold text-slate-800 text-sm mb-2"><i class="fas fa-arrow-up text-red-500 mr-2"></i>Quando a SELIC sobe:</h4>
                                <ul class="text-xs text-slate-600 space-y-1 list-disc list-inside">
                                    <li>Financiamentos e empréstimos ficam mais caros.</li>
                                    <li>A inflação tende a descer.</li>
                                    <li>Aplicações de Renda Fixa rendem mais.</li>
                                </ul>
                            </div>
                            <div class="p-4 bg-slate-50 rounded-xl">
                                <h4 class="font-bold text-slate-800 text-sm mb-2"><i class="fas fa-arrow-down text-emerald-500 mr-2"></i>Quando a SELIC desce:</h4>
                                <ul class="text-xs text-slate-600 space-y-1 list-disc list-inside">
                                    <li>Fica mais barato comprar a prazo ou financiar.</li>
                                    <li>A economia e o comércio são estimulados.</li>
                                    <li>Renda Fixa rende menos, empurrando investidores para a bolsa.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </article>

                <!-- TAB: IPCA -->
                <article id="tab-ipca" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-red-50 text-red-600 rounded-xl text-2xl">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">IPCA</h2>
                                <p class="text-sm text-slate-500">Índice Nacional de Preços ao Consumidor Amplo</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-red-50 text-red-800 font-bold text-lg rounded-xl border border-red-100">
                            ~4.72% (acum. 12m)
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                É a inflação oficial do país. Este índice reflecte a variação mensal do custo de vida das famílias, abrangendo sectores cruciais como alimentação, transporte, habitação e saúde.
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                É o famoso <strong>"monstro da perda de poder de compra"</strong>. Se em Janeiro uma cesta de compras custava R$ 100 e a inflação anual é de 5%, a mesma cesta vai custar R$ 105 em Dezembro. O seu salário precisa de subir ao mesmo ritmo para não empobrecer.
                            </p>
                        </div>

                        <div class="p-5 bg-blue-50 rounded-xl border border-blue-100 text-sm text-blue-900">
                            <h4 class="font-bold mb-1"><i class="fas fa-bullseye mr-2"></i>A Meta de Inflação</h4>
                            <p class="text-slate-600 text-xs">
                                O Conselho Monetário Nacional define uma meta de inflação para o ano. Se o IPCA ameaça furar o limite máximo, o Banco Central é forçado a intervir subindo a taxa SELIC para arrefecer o mercado.
                            </p>
                        </div>
                    </div>
                </article>

                <!-- TAB: PIB -->
                <article id="tab-pib" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl text-2xl">
                                <i class="fas fa-building"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">PIB</h2>
                                <p class="text-sm text-slate-500">Produto Interno Bruto</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-emerald-50 text-emerald-800 font-bold text-lg rounded-xl border border-emerald-100">
                            ~R$ 12.7 Trilhões
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                O PIB representa a soma de todos os bens e serviços finais produzidos no país ao longo de um determinado período. É o principal termómetro para avaliar a riqueza e o crescimento económico nacional.
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                Pense no PIB como o <strong>bolo do rendimento da casa</strong>. Se o PIB cresce, o bolo está a crescer, significando que as empresas estão a vender mais e a abrir postos de trabalho. Se o PIB encolhe durante dois trimestres seguidos, dizemos que o país entrou em "recessão técnica".
                            </p>
                        </div>
                    </div>
                </article>

                <!-- TAB: DESEMPREGO -->
                <article id="tab-desemprego" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-violet-50 text-violet-600 rounded-xl text-2xl">
                                <i class="fas fa-user-friends"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">Taxa de Desemprego</h2>
                                <p class="text-sm text-slate-500">População ativa sem trabalho à procura de emprego</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-violet-50 text-violet-800 font-bold text-lg rounded-xl border border-violet-100">
                            ~5.8% (PNAD Continua)
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                Corresponde à percentagem de pessoas em idade de trabalhar que não têm emprego, mas que estão activamente empenhadas em encontrar uma oportunidade de trabalho.
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                Imagine uma <strong>equipa de futebol com jogadores suplentes</strong>. Se a taxa de desemprego é baixa, quase todos os atletas disponíveis estão em campo a jogar (economia aquecida). Se é alta, há demasiados talentos parados no banco de reservas, sem contribuir para a riqueza colectiva.
                            </p>
                        </div>
                    </div>
                </article>

                <!-- TAB: DIVIDA/PIB -->
                <article id="tab-dividapib" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-orange-50 text-orange-600 rounded-xl text-2xl">
                                <i class="fas fa-hand-holding-usd"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">Relação Dívida / PIB</h2>
                                <p class="text-sm text-slate-500">Métrica de sustentabilidade fiscal do Governo</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-orange-50 text-orange-800 font-bold text-lg rounded-xl border border-orange-100">
                            ~80.4%
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                Mede a proporção do endividamento público em relação a tudo o que o país produz. É o principal indicador observado por credores e agências de classificação de risco para avaliar a solvência de uma nação.
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                Imagine um trabalhador que aufere R$ 10.000 de salário por ano e tem uma dívida total acumulada de R$ 8.040. A sua relação dívida/receita é de 80.4%. O trabalhador consegue pagar as contas, mas se a dívida subir acima de 100%, os bancos começam a duvidar da sua capacidade de pagamento e aumentam os juros aplicados.
                            </p>
                        </div>
                    </div>
                </article>

                <!-- TAB: BALANÇA COMERCIAL -->
                <article id="tab-balanca" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
                        <div class="flex items-center gap-3">
                            <div class="p-3 bg-indigo-50 text-indigo-600 rounded-xl text-2xl">
                                <i class="fas fa-ship"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-bold text-brand-navy">Balança Comercial</h2>
                                <p class="text-sm text-slate-500">Exportações versus Importações do País</p>
                            </div>
                        </div>
                        <span class="px-4 py-2 bg-indigo-50 text-indigo-800 font-bold text-lg rounded-xl border border-indigo-100">
                            Superávit ~US$ 97 Bi
                        </span>
                    </div>

                    <div class="space-y-6">
                        <div>
                            <h3 class="font-bold text-lg text-brand-navy mb-2">O que é?</h3>
                            <p class="text-slate-600 leading-relaxed">
                                É o saldo comercial que resulta da diferença entre o valor total das exportações (bens vendidos ao exterior) e o valor total das importações (bens comprados ao estrangeiro).
                            </p>
                        </div>

                        <div class="bg-amber-50/50 border-l-4 border-amber-500 p-5 rounded-r-xl">
                            <h4 class="font-bold text-amber-900 flex items-center gap-2 mb-2">
                                <i class="fas fa-lightbulb"></i> Analogia do Dia a Dia
                            </h4>
                            <p class="text-amber-950 text-sm leading-relaxed">
                                Pense na balança comercial como a <strong>sua balança familiar de compras</strong>. Se vende mais produtos e prestações de serviços do que as coisas que compra em sites internacionais, fica com saldo positivo (superávit) e acumula divisas fortes (como dólares).
                            </p>
                        </div>
                    </div>
                </article>

                <!-- TAB: SIMULADOR DE JUROS REAL -->
                <article id="tab-simulador" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="border-b border-slate-100 pb-5 mb-6">
                        <h2 class="text-2xl font-bold text-brand-navy flex items-center gap-2">
                            <i class="fas fa-calculator text-amber-500"></i>
                            <span>Simulador de Rendimento Real</span>
                        </h2>
                        <p class="text-sm text-slate-500 mt-1">Veja como a SELIC e o IPCA (inflação) competem directamente pelo seu dinheiro acumulado.</p>
                    </div>

                    <!-- Controlos do Simulador -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-2">Montante Inicial (R$)</label>
                            <input id="sim-amount" type="number" value="10000" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none" oninput="runSimulation()">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-2">Taxa Selic Anual (%)</label>
                            <input id="sim-selic" type="number" step="0.25" value="14.50" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none" oninput="runSimulation()">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-2">Inflação Anual IPCA (%)</label>
                            <input id="sim-ipca" type="number" step="0.1" value="4.72" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none" oninput="runSimulation()">
                        </div>
                    </div>

                    <!-- Resultados Visuais -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                        <div class="space-y-4">
                            <div class="p-4 bg-slate-50 rounded-xl">
                                <span class="text-xs text-slate-400 font-bold uppercase block">Rendimento Bruto Estimado (1 Ano)</span>
                                <span id="res-nominal" class="text-2xl font-extrabold text-blue-900">R$ 11.450,00</span>
                                <span class="text-xs text-slate-500 block">Montante inicial mais os juros brutos prometidos</span>
                            </div>
                            <div class="p-4 bg-red-50 rounded-xl">
                                <span class="text-xs text-red-500 font-bold uppercase block">Impacto Corrosivo do IPCA</span>
                                <span id="res-loss" class="text-2xl font-extrabold text-red-700">- R$ 472,00</span>
                                <span class="text-xs text-slate-500 block">O valor que perdeu em poder de compra em apenas um ano</span>
                            </div>
                            <div class="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                                <span class="text-xs text-emerald-600 font-bold uppercase block">Ganho Real Efectivo</span>
                                <span id="res-real" class="text-2xl font-extrabold text-emerald-800">R$ 978,00</span>
                                <span class="text-xs text-emerald-600 block">O seu verdadeiro ganho líquido acima do poder de compra</span>
                            </div>
                        </div>

                        <!-- Gráfico do Rendimento -->
                        <div class="relative flex justify-center items-center h-64">
                            <canvas id="simulationChart"></canvas>
                        </div>
                    </div>
                </article>

                <!-- TAB: QUIZ INTERACTIVO -->
                <article id="tab-quiz" class="tab-content bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-sm">
                    <div class="border-b border-slate-100 pb-5 mb-6 flex justify-between items-center">
                        <div>
                            <h2 class="text-2xl font-bold text-brand-navy flex items-center gap-2">
                                <i class="fas fa-gamepad text-emerald-500"></i>
                                <span>Teste os Seus Conhecimentos</span>
                            </h2>
                            <p class="text-sm text-slate-500 mt-1">Será que percebeu mesmo o impacto dos indicadores na nossa economia?</p>
                        </div>
                        <span id="quiz-score" class="px-3 py-1 bg-emerald-50 text-emerald-800 text-sm font-bold rounded-lg">Pontuação: 0/5</span>
                    </div>

                    <!-- Área Dinâmica do Quiz -->
                    <div id="quiz-box" class="space-y-6">
                        <!-- Pergunta Ativa -->
                        <div class="p-5 bg-slate-50 rounded-xl border border-slate-100">
                            <span id="question-num" class="text-xs font-bold text-emerald-600 uppercase">Pergunta 1 de 5</span>
                            <h3 id="question-text" class="text-lg font-bold text-brand-navy mt-1">Qual é a principal taxa utilizada pelo Banco Central para travar uma subida descontrolada da inflação?</h3>
                        </div>

                        <!-- Opções -->
                        <div id="quiz-options" class="grid grid-cols-1 gap-3">
                            <button class="w-full text-left px-5 py-4 rounded-xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 font-medium transition-all duration-150">A) Taxa IPCA</button>
                            <button class="w-full text-left px-5 py-4 rounded-xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 font-medium transition-all duration-150">B) Taxa Selic</button>
                            <button class="w-full text-left px-5 py-4 rounded-xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/20 font-medium transition-all duration-150">C) Produto Interno Bruto</button>
                        </div>

                        <!-- Feedback Box -->
                        <div id="quiz-feedback" class="hidden p-4 rounded-xl font-semibold flex items-center gap-3"></div>

                        <!-- Controlos Adicionais -->
                        <div class="flex justify-end">
                            <button id="next-btn" onclick="nextQuestion()" class="hidden px-6 py-3 bg-brand-navy text-white font-bold rounded-xl hover:bg-brand-teal transition-colors flex items-center gap-2">
                                <span>Próxima Pergunta</span>
                                <i class="fas fa-arrow-right"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Tela de Resultado Final do Quiz (Invisível no início) -->
                    <div id="quiz-result-screen" class="hidden text-center py-8 space-y-4">
                        <div class="text-6xl text-emerald-500">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-brand-navy">Parabéns! Quiz Concluído!</h3>
                        <p id="final-score-text" class="text-slate-600 text-lg">Acertou em 5 de 5 perguntas.</p>
                        <button onclick="resetQuiz()" class="px-6 py-3 bg-brand-navy hover:bg-brand-teal text-white font-bold rounded-xl transition-colors">
                            Tentar Novamente
                        </button>
                    </div>
                </article>

            </main>
        </div>

        <!-- Botão Aceder Plataforma de Investimentos Completa -->
        <div class="mt-12 text-center">
            <a href="https://mercadofinanceiro-mzeuhzkjsyfrmaehvjutr5.streamlit.app" target="_blank" class="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-brand-navy to-brand-teal text-white font-bold text-lg rounded-full shadow-lg shadow-brand-navy/30 hover:shadow-xl hover:shadow-brand-navy/40 transition-all duration-300 transform hover:-translate-y-1">
                <span>Aceder à Plataforma Principal</span>
                <i class="fas fa-arrow-right"></i>
            </a>
        </div>
    </div>

    <!-- Notas de Rodapé -->
    <footer class="bg-white border-t border-slate-100 py-6 mt-12">
        <div class="max-w-6xl mx-auto px-4 text-center text-xs text-slate-400 space-y-2">
            <p><i class="fas fa-database text-brand-teal"></i> Dados educativos actualizados com base nos padrões estatísticos do Banco Central e IBGE.</p>
            <p>Esta ferramenta é estritamente didáctica e não substitui qualquer conselho ou assessoria financeira oficial.</p>
        </div>
    </footer>

    <!-- Lógica de Controlo das Abas, Gráficos e Quiz -->
    <script>
        // Transição suave de abas no ecran principal
        function switchTab(tabId) {
            // Remove active de todas as abas
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            // Remove active dos botões de controlo
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('bg-brand-navy', 'text-white', 'shadow-sm');
                btn.classList.add('text-slate-600', 'hover:bg-slate-50');
            });

            // Ativa a aba atual
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            // Ativa o botão atual
            const activeBtn = document.getElementById(`btn-${tabId}`);
            activeBtn.classList.remove('text-slate-600', 'hover:bg-slate-50');
            activeBtn.classList.add('bg-brand-navy', 'text-white', 'shadow-sm');

            // Caso mude para o simulador, refresca o gráfico
            if (tabId === 'simulador') {
                setTimeout(runSimulation, 50);
            }
        }

        // --- SISTEMA DO SIMULADOR DE JUROS E INFLAÇÃO ---
        let simChart = null;

        function runSimulation() {
            const amountInput = document.getElementById('sim-amount');
            const selicInput = document.getElementById('sim-selic');
            const ipcaInput = document.getElementById('sim-ipca');

            const initialAmount = parseFloat(amountInput.value) || 0;
            const selicRate = (parseFloat(selicInput.value) || 0) / 100;
            const ipcaRate = (parseFloat(ipcaInput.value) || 0) / 100;

            // Cálculos
            const nominalReturn = initialAmount * (1 + selicRate);
            const nominalInterest = nominalReturn - initialAmount;
            
            // Perda pelo poder de compra
            const purchasingLoss = initialAmount * ipcaRate;
            
            // Ganho real efectivo
            const realYield = Math.max(0, nominalInterest - purchasingLoss);

            // Formatação de Moedas
            const formatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

            document.getElementById('res-nominal').innerText = formatter.format(nominalReturn);
            document.getElementById('res-loss').innerText = `- ${formatter.format(purchasingLoss)}`;
            document.getElementById('res-real').innerText = formatter.format(realYield);

            // Desenhar ou actualizar gráfico Chart.js
            const ctx = document.getElementById('simulationChart').getContext('2d');
            
            if (simChart) {
                simChart.destroy();
            }

            simChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Investimento Inicial', 'Ganho Real', 'Perda p/ Inflação'],
                    datasets: [{
                        data: [initialAmount, realYield, purchasingLoss],
                        backgroundColor: ['#e2e8f0', '#10b981', '#ef4444'],
                        borderWidth: 2,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: {
                                    family: 'Inter',
                                    size: 11
                                }
                            }
                        }
                    }
                }
            });
        }

        // --- SISTEMA DO QUIZ INTERACTIVO ---
        const quizQuestions = [
            {
                question: "Qual é o principal índice utilizado como a inflação oficial no Brasil?",
                options: [
                    "A) Taxa Selic",
                    "B) IPCA (Índice Nacional de Preços ao Consumidor Amplo)",
                    "C) PIB (Produto Interno Bruto)"
                ],
                correct: 1,
                explanation: "O IPCA mede as flutuações de preços nos bens de consumo e serviços das famílias e é a inflação oficial!"
            },
            {
                question: "Se a Taxa SELIC subir agressivamente, o que é provável acontecer aos financiamentos de habitações?",
                options: [
                    "A) Ficam consideravelmente mais baratos.",
                    "B) Mantêm o preço inalterado porque dependem de taxas de câmbio.",
                    "C) Ficam mais caros e difíceis de obter."
                ],
                correct: 2,
                explanation: "O aumento da taxa SELIC encarece o custo do dinheiro, tornando os empréstimos e financiamentos mais dispendiosos."
            },
            {
                question: "O que representa exactamente uma relação Dívida Pública / PIB de 80%?",
                options: [
                    "A) Que o país deve o equivalente a 80% de tudo o que produz num ano.",
                    "B) Que 80% da população está empregada pelo estado.",
                    "C) Que o PIB cresceu 80% nos últimos meses."
                ],
                correct: 0,
                explanation: "Esta métrica relaciona o total do endividamento público com a totalidade do PIB anual do país."
            },
            {
                question: "Se o país regista um Superávit na Balança Comercial, isso significa que:",
                options: [
                    "A) O país comprou mais coisas do que as que vendeu.",
                    "B) O país vendeu (exportou) mais mercadorias do que importou.",
                    "C) A taxa de desemprego bateu mínimos históricos."
                ],
                correct: 1,
                explanation: "Superávit comercial ocorre quando as exportações de bens e serviços superam as importações."
            },
            {
                question: "O que constitui a taxa de 'Juro Real'?",
                options: [
                    "A) O juro cobrado directamente pelos bancos comerciais.",
                    "B) A taxa básica Selic sem o desconto dos impostos.",
                    "C) O rendimento obtido após o desconto do impacto inflacionário (IPCA)."
                ],
                correct: 2,
                explanation: "O juro real calcula o real crescimento do poder de compra descontando a inflação."
            }
        ];

        let currentQuestionIndex = 0;
        let score = 0;
        let hasAnswered = false;

        function renderQuestion() {
            hasAnswered = false;
            document.getElementById('quiz-feedback').classList.add('hidden');
            document.getElementById('next-btn').classList.add('hidden');

            const q = quizQuestions[currentQuestionIndex];
            document.getElementById('question-num').innerText = `Pergunta ${currentQuestionIndex + 1} de ${quizQuestions.length}`;
            document.getElementById('question-text').innerText = q.question;

            const optionsContainer = document.getElementById('quiz-options');
            optionsContainer.innerHTML = '';

            q.options.forEach((opt, idx) => {
                const btn = document.createElement('button');
                btn.className = "w-full text-left px-5 py-4 rounded-xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/10 font-semibold transition-all duration-150";
                btn.innerText = opt;
                btn.onclick = () => checkAnswer(idx, btn);
                optionsContainer.appendChild(btn);
            });
        }

        function checkAnswer(selectedIdx, clickedButton) {
            if (hasAnswered) return;
            hasAnswered = true;

            const q = quizQuestions[currentQuestionIndex];
            const feedbackBox = document.getElementById('quiz-feedback');
            
            // Bloqueia as outras opções visivelmente
            const optionsButtons = document.getElementById('quiz-options').querySelectorAll('button');
            optionsButtons.forEach((btn, idx) => {
                btn.disabled = true;
                if (idx === q.correct) {
                    btn.classList.add('border-emerald-500', 'bg-emerald-50', 'text-emerald-800');
                } else if (idx === selectedIdx) {
                    btn.classList.add('border-red-500', 'bg-red-50', 'text-red-800');
                } else {
                    btn.classList.add('opacity-50');
                }
            });

            feedbackBox.classList.remove('hidden');
            if (selectedIdx === q.correct) {
                score++;
                document.getElementById('quiz-score').innerText = `Pontuação: ${score}/${quizQuestions.length}`;
                feedbackBox.className = "p-4 rounded-xl font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-3";
                feedbackBox.innerHTML = `<i class="fas fa-check-circle text-xl text-emerald-600"></i><div><strong>Resposta Correcta!</strong><p class="text-xs font-normal mt-0.5">${q.explanation}</p></div>`;
            } else {
                feedbackBox.className = "p-4 rounded-xl font-semibold bg-red-50 text-red-800 border border-red-200 flex items-center gap-3";
                feedbackBox.innerHTML = `<i class="fas fa-times-circle text-xl text-red-600"></i><div><strong>Ups, não é correcto!</strong><p class="text-xs font-normal mt-0.5">${q.explanation}</p></div>`;
            }

            document.getElementById('next-btn').classList.remove('hidden');
        }

        function nextQuestion() {
            currentQuestionIndex++;
            if (currentQuestionIndex < quizQuestions.length) {
                renderQuestion();
            } else {
                // Fim de Quiz - mostra ecran final
                document.getElementById('quiz-box').classList.add('hidden');
                document.getElementById('quiz-result-screen').classList.remove('hidden');
                document.getElementById('final-score-text').innerText = `Acertou em ${score} de ${quizQuestions.length} perguntas de economia!`;
            }
        }

        function resetQuiz() {
            currentQuestionIndex = 0;
            score = 0;
            document.getElementById('quiz-score').innerText = `Pontuação: 0/5`;
            document.getElementById('quiz-box').classList.remove('hidden');
            document.getElementById('quiz-result-screen').classList.add('hidden');
            renderQuestion();
        }

        // Inicializar simulador e quiz ao carregar a página
        window.onload = function() {
            runSimulation();
            renderQuestion();
        }
    </script>
</body>
</html>
