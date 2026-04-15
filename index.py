"""
SISTEMA DE ESTUDOS - SOLO LEVELING (Banco do Brasil)
=====================================================
Requisitos: pip install streamlit plotly
Executar:   streamlit run solo_leveling_bb.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import math
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Solo Leveling BB",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS TEMÁTICO SOLO LEVELING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

/* FUNDO GLOBAL */
.stApp {
    background-color: #050a14;
    color: #c8d8f0;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #080f1e;
    border-right: 1px solid #1a2a4a;
}

/* TÍTULOS */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #5b9cf6 !important;
    letter-spacing: 2px;
}

/* CARDS PERSONALIZADOS */
.sl-card {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%);
    border: 1px solid #1e3a6e;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    position: relative;
}

.sl-card-gold {
    border: 1px solid #b8860b;
    background: linear-gradient(135deg, #1a1200 0%, #2a1e00 100%);
}

.sl-card-purple {
    border: 1px solid #7b2fff;
    background: linear-gradient(135deg, #0e0520 0%, #1a0835 100%);
}

.sl-card-red {
    border: 1px solid #cc2222;
    background: linear-gradient(135deg, #1a0000 0%, #2e0505 100%);
}

.sl-card-green {
    border: 1px solid #00aa55;
    background: linear-gradient(135deg, #001a0e 0%, #002e18 100%);
}

/* RANK BADGE */
.rank-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 4px;
    font-family: 'Orbitron', monospace;
    font-weight: 900;
    font-size: 22px;
    letter-spacing: 4px;
    margin-bottom: 8px;
}
.rank-E { background: #1a1a2e; color: #6666aa; border: 2px solid #3333aa; }
.rank-D { background: #0a1f0a; color: #33cc33; border: 2px solid #22aa22; }
.rank-C { background: #1a1000; color: #ccaa00; border: 2px solid #aa8800; }
.rank-B { background: #1a0a00; color: #ff6600; border: 2px solid #cc4400; }
.rank-A { background: #1a0000; color: #ff2222; border: 2px solid #cc0000; }
.rank-S { background: #100020; color: #cc44ff; border: 2px solid #9911dd; }

/* XP BAR */
.xp-bar-container {
    width: 100%;
    height: 18px;
    background: #0a1020;
    border: 1px solid #1e3a6e;
    border-radius: 9px;
    overflow: hidden;
    margin: 8px 0;
}
.xp-bar-fill {
    height: 100%;
    border-radius: 9px;
    transition: width 0.5s ease;
    background: linear-gradient(90deg, #1a4aff 0%, #5b9cf6 50%, #1a4aff 100%);
}
.xp-bar-fill-gold {
    background: linear-gradient(90deg, #b8860b 0%, #ffd700 50%, #b8860b 100%);
}

/* STAT LINES */
.stat-line {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #0d1f3c;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
}
.stat-label { color: #5b7a9f; }
.stat-value { color: #5b9cf6; font-weight: bold; }

/* NOTIFICAÇÃO */
.system-msg {
    background: #050a14;
    border: 1px solid #5b9cf6;
    border-left: 4px solid #5b9cf6;
    padding: 12px 16px;
    margin: 8px 0;
    font-family: 'Share Tech Mono', monospace;
    color: #5b9cf6;
    font-size: 13px;
    border-radius: 0 6px 6px 0;
}

.system-msg-gold {
    border-color: #ffd700;
    border-left-color: #ffd700;
    color: #ffd700;
}

.system-msg-red {
    border-color: #ff4444;
    border-left-color: #ff4444;
    color: #ff4444;
}

.system-msg-purple {
    border-color: #cc44ff;
    border-left-color: #cc44ff;
    color: #cc44ff;
}

/* SKILL GRID */
.skill-item {
    background: #0a1628;
    border: 1px solid #1e3a6e;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
}

/* BOSS CARD */
.boss-card {
    background: linear-gradient(135deg, #1a0000 0%, #2e0505 100%);
    border: 2px solid #cc2222;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    margin: 10px 0;
}

/* BOTÕES */
.stButton > button {
    background: linear-gradient(90deg, #0a1f4a, #1a3a7a) !important;
    color: #5b9cf6 !important;
    border: 1px solid #2a5aaa !important;
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 1px !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #1a3a7a, #2a5aaa) !important;
    border-color: #5b9cf6 !important;
    color: #ffffff !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: #0a1628;
    border: 1px solid #1e3a6e;
    border-radius: 8px;
    padding: 12px;
}
[data-testid="stMetricLabel"] { color: #5b7a9f !important; }
[data-testid="stMetricValue"] { color: #5b9cf6 !important; font-family: 'Orbitron', monospace !important; }

/* INPUTS */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: #0a1628 !important;
    border: 1px solid #1e3a6e !important;
    color: #c8d8f0 !important;
    border-radius: 6px !important;
}

/* SLIDER */
.stSlider > div > div > div > div { background: #5b9cf6 !important; }

/* EXPANDER */
.streamlit-expanderHeader {
    background: #0a1628 !important;
    border: 1px solid #1e3a6e !important;
    border-radius: 6px !important;
    color: #5b9cf6 !important;
    font-family: 'Orbitron', monospace !important;
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    background: #080f1e !important;
    border: 1px solid #1e3a6e !important;
    color: #5b7a9f !important;
    border-radius: 6px 6px 0 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTabs [aria-selected="true"] {
    background: #0a1628 !important;
    color: #5b9cf6 !important;
    border-bottom-color: #0a1628 !important;
}

/* DATAFRAME */
.stDataFrame { border: 1px solid #1e3a6e; border-radius: 8px; }

hr { border-color: #1e3a6e !important; }

.glow-text {
    text-shadow: 0 0 8px #5b9cf6, 0 0 16px #5b9cf6;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONSTANTES DO JOGO
# ─────────────────────────────────────────────
RANKS = [
    {"name": "E", "label": "Iniciante", "min_xp": 0,     "max_xp": 499,   "color": "#3333aa", "desc": "Construindo o hábito"},
    {"name": "D", "label": "Candidato", "min_xp": 500,   "max_xp": 1499,  "color": "#22aa22", "desc": "Base teórica sólida"},
    {"name": "C", "label": "Estudante", "min_xp": 1500,  "max_xp": 3499,  "color": "#aa8800", "desc": "Simulados acima de 50%"},
    {"name": "B", "label": "Competidor","min_xp": 3500,  "max_xp": 6999,  "color": "#cc4400", "desc": "Simulados acima de 65%"},
    {"name": "A", "label": "Finalista", "min_xp": 7000,  "max_xp": 12999, "color": "#cc0000", "desc": "Simulados acima de 75%"},
    {"name": "S", "label": "Aprovado",  "min_xp": 13000, "max_xp": 99999, "color": "#9911dd", "desc": "Pronto para o edital"},
]

XP_RULES = {
    "bloco_estudo": 30,
    "questao_certa": 5,
    "simulado_completo": 100,
    "semana_completa": 50,
    "revisao_ponto_fraco": 20,
    "simulado_acima_70": 20,
    "dia_perdido": -15,
}

MATERIAS = [
    "Matemática",
    "Português",
    "Conhecimentos Bancários",
    "Informática",
    "Redação",
    "Atualidades",
]

DUNGEONS = {
    "E": [
        {"nome": "Dungeon Aritmética Básica", "xp": 40, "dificuldade": "F", "desc": "Porcentagem, razão, regra de três"},
        {"nome": "Dungeon Interpretação Textual", "xp": 40, "dificuldade": "F", "desc": "Compreensão e inferência de texto"},
        {"nome": "Dungeon SFN Básico", "xp": 50, "dificuldade": "E", "desc": "Sistema Financeiro Nacional e Bacen"},
    ],
    "D": [
        {"nome": "Dungeon Juros Compostos", "xp": 70, "dificuldade": "E", "desc": "Juros compostos, desconto, amortização"},
        {"nome": "Dungeon Gramática Aplicada", "xp": 70, "dificuldade": "E", "desc": "Concordância, regência, crase"},
        {"nome": "Dungeon Produtos Bancários", "xp": 80, "dificuldade": "D", "desc": "Crédito, câmbio, investimentos"},
    ],
    "C": [
        {"nome": "Dungeon Estatística", "xp": 100, "dificuldade": "D", "desc": "Média, mediana, moda, desvio padrão"},
        {"nome": "Dungeon Redação Dissertativa", "xp": 90, "dificuldade": "D", "desc": "Estrutura, argumentação, coesão"},
        {"nome": "Dungeon Mercado Financeiro", "xp": 110, "dificuldade": "C", "desc": "Renda fixa, renda variável, derivativos"},
    ],
    "B": [
        {"nome": "Dungeon Probabilidade", "xp": 130, "dificuldade": "C", "desc": "Análise combinatória + probabilidade"},
        {"nome": "Dungeon Legislação Bancária", "xp": 120, "dificuldade": "C", "desc": "LGPD, prevenção à lavagem, compliance"},
        {"nome": "Dungeon Raciocínio Lógico Avançado", "xp": 140, "dificuldade": "B", "desc": "Sequências, silogismos, lógica proposicional"},
    ],
    "A": [
        {"nome": "Dungeon Simulado Full", "xp": 200, "dificuldade": "B", "desc": "Simulado completo 50 questões"},
        {"nome": "Dungeon Redação Avançada", "xp": 180, "dificuldade": "A", "desc": "Redação nota máxima com feedback"},
    ],
}

BOSSES = [
    {"nome": "Guardião das Questões Básicas", "rank": "E→D", "xp": 150, "requisito": 300,
     "desc": "Vença simulado de 30 questões com 60% de aproveitamento", "color": "#22aa22"},
    {"nome": "Senhor da Gramática", "rank": "D→C", "xp": 250, "requisito": 1000,
     "desc": "Resolva 50 questões de Português com 65% de acerto", "color": "#aa8800"},
    {"nome": "Arquimago Estatístico", "rank": "C→B", "xp": 400, "requisito": 2500,
     "desc": "Vença simulado completo com 60% + estatística acima de 50%", "color": "#cc4400"},
    {"nome": "Dragão do Mercado Financeiro", "rank": "B→A", "xp": 600, "requisito": 5000,
     "desc": "Simulado completo com 70% de aproveitamento geral", "color": "#cc0000"},
    {"nome": "O Monarca — Banco do Brasil", "rank": "A→S", "xp": 1000, "requisito": 10000,
     "desc": "Simulado completo com 80%+. Você está pronto para a prova.", "color": "#9911dd"},
]

HABILIDADES_PASSIVAS = [
    {"nome": "Foco Apurado", "nivel": "D", "desc": "Pomodoro de 25min sem distrações ativado"},
    {"nome": "Mente Lógica", "nivel": "C", "desc": "+5% XP em Matemática e Raciocínio Lógico"},
    {"nome": "Revisão Cirúrgica", "nivel": "C", "desc": "Sistema de revisão por erros ativado"},
    {"nome": "Resistência Mental", "nivel": "B", "desc": "Penalidade de dia perdido reduzida 50%"},
    {"nome": "Instinto do Concurseiro", "nivel": "A", "desc": "Identifica padrões da Cesgranrio automaticamente"},
    {"nome": "Domínio Total", "nivel": "S", "desc": "Todas as matérias desbloqueadas e dominadas"},
]


# ─────────────────────────────────────────────
#  ESTADO DO JOGO (PERSISTÊNCIA EM JSON)
# ─────────────────────────────────────────────
SAVE_FILE = "sl_save.json"

def estado_inicial():
    return {
        "xp_total": 0,
        "nivel": 1,
        "rank": "E",
        "streak": 0,
        "dias_estudados": 0,
        "simulados_feitos": 0,
        "bosses_derrotados": [],
        "dungeons_completas": [],
        "historico_xp": [],
        "historico_simulados": [],
        "desempenho_materias": {m: {"acertos": 0, "erros": 0, "questoes": 0} for m in MATERIAS},
        "log_atividades": [],
        "ultima_sessao": None,
        "semanas_completas": 0,
    }

def carregar_estado():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                dados = json.load(f)
                base = estado_inicial()
                base.update(dados)
                return base
        except:
            pass
    return estado_inicial()

def salvar_estado(estado):
    with open(SAVE_FILE, "w") as f:
        json.dump(estado, f, indent=2, default=str)

def get_rank_info(xp):
    for r in RANKS:
        if r["min_xp"] <= xp <= r["max_xp"]:
            return r
    return RANKS[-1]

def get_nivel(xp):
    return max(1, int(math.log(max(1, xp / 10), 1.4)) + 1)

def xp_para_prox_rank(rank_name, xp_atual):
    for r in RANKS:
        if r["name"] == rank_name:
            return r["max_xp"] - xp_atual + 1
    return 0

def progresso_rank(rank_name, xp_atual):
    for r in RANKS:
        if r["name"] == rank_name:
            span = r["max_xp"] - r["min_xp"]
            prog = xp_atual - r["min_xp"]
            return min(100, int((prog / span) * 100))
    return 100

def adicionar_log(estado, msg, tipo="info"):
    ts = datetime.now().strftime("%d/%m %H:%M")
    estado["log_atividades"].insert(0, {"ts": ts, "msg": msg, "tipo": tipo})
    estado["log_atividades"] = estado["log_atividades"][:50]

def ganhar_xp(estado, quantidade, motivo=""):
    xp_antes = estado["xp_total"]
    rank_antes = get_rank_info(xp_antes)["name"]
    estado["xp_total"] = max(0, estado["xp_total"] + quantidade)
    rank_depois = get_rank_info(estado["xp_total"])["name"]
    estado["nivel"] = get_nivel(estado["xp_total"])
    estado["rank"] = rank_depois
    estado["historico_xp"].append({
        "data": datetime.now().strftime("%Y-%m-%d"),
        "xp": quantidade,
        "total": estado["xp_total"],
        "motivo": motivo,
    })
    rank_up = rank_antes != rank_depois
    return rank_up, rank_antes, rank_depois


# ─────────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────────
if "estado" not in st.session_state:
    st.session_state.estado = carregar_estado()
if "notificacoes" not in st.session_state:
    st.session_state.notificacoes = []
if "rank_up_msg" not in st.session_state:
    st.session_state.rank_up_msg = None

estado = st.session_state.estado


# ─────────────────────────────────────────────
#  SIDEBAR — PERFIL DO HUNTER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='text-align:center;font-size:16px;letter-spacing:3px;'>⚔ HUNTER PROFILE ⚔</h2>", unsafe_allow_html=True)
    st.markdown("---")

    rank_info = get_rank_info(estado["xp_total"])
    rank_n = rank_info["name"]
    prog = progresso_rank(rank_n, estado["xp_total"])

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:16px">
        <div class="rank-badge rank-{rank_n}">{rank_n}</div>
        <div style="color:#5b9cf6;font-family:'Orbitron',monospace;font-size:14px;margin-top:4px">{rank_info['label']}</div>
        <div style="color:#5b7a9f;font-size:12px;margin-top:2px">{rank_info['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-line"><span class="stat-label">LEVEL</span><span class="stat-value">{estado['nivel']}</span></div>
    <div class="stat-line"><span class="stat-label">XP TOTAL</span><span class="stat-value">{estado['xp_total']:,}</span></div>
    <div class="stat-line"><span class="stat-label">STREAK</span><span class="stat-value">{estado['streak']} dias</span></div>
    <div class="stat-line"><span class="stat-label">SIMULADOS</span><span class="stat-value">{estado['simulados_feitos']}</span></div>
    <div class="stat-line"><span class="stat-label">BOSSES</span><span class="stat-value">{len(estado['bosses_derrotados'])}/5</span></div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#5b7a9f;font-size:12px;font-family:monospace'>Progresso para rank {RANKS[RANKS.index(rank_info)+1]['name'] if rank_info != RANKS[-1] else 'MAX'}:</div>", unsafe_allow_html=True)
    st.progress(prog / 100)
    st.markdown(f"<div style='color:#5b9cf6;font-size:12px;font-family:monospace;text-align:right'>{prog}%  ({xp_para_prox_rank(rank_n, estado['xp_total'])} XP restantes)</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#5b7a9f;font-size:11px;font-family:monospace;text-align:center'>HABILIDADES DESBLOQUEADAS</div>", unsafe_allow_html=True)
    rank_order = ["E", "D", "C", "B", "A", "S"]
    rank_idx = rank_order.index(rank_n)
    for hab in HABILIDADES_PASSIVAS:
        h_idx = rank_order.index(hab["nivel"])
        if h_idx <= rank_idx:
            st.markdown(f"""
            <div class="skill-item">
              <span style='color:#5b9cf6'>✦</span> 
              <span style='color:#c8d8f0;font-weight:bold'>{hab['nome']}</span><br>
              <span style='color:#5b7a9f;font-size:11px'>{hab['desc']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 Salvar Progresso"):
        salvar_estado(estado)
        st.success("Progresso salvo!")

    if st.button("🗑 Resetar (Nova Jornada)"):
        st.session_state.estado = estado_inicial()
        estado = st.session_state.estado
        salvar_estado(estado)
        st.rerun()


# ─────────────────────────────────────────────
#  RANK UP NOTIFICATION
# ─────────────────────────────────────────────
if st.session_state.rank_up_msg:
    rm = st.session_state.rank_up_msg
    st.markdown(f"""
    <div class="system-msg-purple" style="text-align:center;padding:16px;font-size:15px">
    ⚠ SISTEMA ⚠<br><br>
    Rank aumentou: <b>{rm[0]}</b> → <b>{rm[1]}</b><br>
    Novas dungeons desbloqueadas!<br>
    Habilidades passivas ativadas!
    </div>
    """, unsafe_allow_html=True)
    st.session_state.rank_up_msg = None


# ─────────────────────────────────────────────
#  TÍTULO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:20px 0 10px">
  <h1 style="font-size:28px;letter-spacing:6px;margin:0">⚔ SOLO LEVELING ⚔</h1>
  <div style="color:#5b7a9f;font-family:'Share Tech Mono',monospace;font-size:13px;margin-top:4px;letter-spacing:2px">SISTEMA DE ESTUDOS — BANCO DO BRASIL</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ─────────────────────────────────────────────
#  TABS PRINCIPAIS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Dashboard",
    "📚 Missões Diárias",
    "📅 Cronograma",
    "⚔ Dungeons",
    "👹 Boss Fight",
    "📊 Desempenho",
    "📜 Log",
])


# ═══════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ═══════════════════════════════════════════
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("XP Total", f"{estado['xp_total']:,}")
    with col2:
        st.metric("Nível", estado["nivel"])
    with col3:
        st.metric("Streak", f"{estado['streak']} dias")
    with col4:
        st.metric("Rank", estado["rank"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de XP ao longo do tempo
    if len(estado["historico_xp"]) > 0:
        hist = estado["historico_xp"]
        datas = [h["data"] for h in hist]
        totais = [h["total"] for h in hist]

        fig_xp = go.Figure()
        fig_xp.add_trace(go.Scatter(
            x=datas, y=totais,
            mode="lines+markers",
            line=dict(color="#5b9cf6", width=2),
            marker=dict(color="#5b9cf6", size=6),
            fill="tozeroy",
            fillcolor="rgba(91,156,246,0.1)",
            name="XP Total"
        ))
        fig_xp.update_layout(
            paper_bgcolor="#050a14",
            plot_bgcolor="#080f1e",
            font=dict(color="#5b7a9f"),
            title=dict(text="Evolução de XP", font=dict(color="#5b9cf6", size=14)),
            xaxis=dict(gridcolor="#0d1f3c", tickfont=dict(color="#5b7a9f")),
            yaxis=dict(gridcolor="#0d1f3c", tickfont=dict(color="#5b7a9f")),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_xp, use_container_width=True)
    else:
        st.markdown("""
        <div class="system-msg">
        [ SISTEMA ] Nenhum dado de XP ainda. Complete sua primeira missão para iniciar a jornada.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabela de ranks
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>SISTEMA DE RANKS</h3>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, r in enumerate(RANKS):
        with cols[i]:
            is_current = r["name"] == rank_n
            border = "2px solid " + r["color"] if is_current else "1px solid #1e3a6e"
            bg = "#1a0030" if is_current else "#0a1628"
            st.markdown(f"""
            <div style="text-align:center;background:{bg};border:{border};border-radius:8px;padding:12px 4px">
              <div style="color:{r['color']};font-family:'Orbitron',monospace;font-weight:900;font-size:20px">{r['name']}</div>
              <div style="color:#5b7a9f;font-size:10px;margin-top:4px">{r['label']}</div>
              <div style="color:#3a5a7f;font-size:9px;margin-top:2px">{r['min_xp']:,} XP</div>
              {"<div style='color:#cc44ff;font-size:9px;margin-top:4px'>◄ ATUAL</div>" if is_current else ""}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabela de XP
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>TABELA DE XP</h3>", unsafe_allow_html=True)
    xp_data = {
        "Ação": ["Bloco de estudo (1h)", "Questão acertada", "Simulado completo", "Semana completa", "Revisão ponto fraco", "Simulado acima de 70%", "Dia perdido (penalidade)"],
        "XP": ["+30", "+5", "+100", "+50", "+20", "+20", "-15"],
    }
    for i, (acao, xp) in enumerate(zip(xp_data["Ação"], xp_data["XP"])):
        color = "#ff4444" if "-" in xp else "#5b9cf6"
        st.markdown(f"""
        <div class="stat-line">
          <span class="stat-label">{acao}</span>
          <span style="color:{color};font-family:'Share Tech Mono',monospace;font-weight:bold">{xp} XP</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  TAB 2 — MISSÕES DIÁRIAS
# ═══════════════════════════════════════════
with tab2:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>MISSÕES DIÁRIAS</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg">
    [ SISTEMA ] Registre cada bloco de estudo concluído. Seja honesto — o sistema te acompanha.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # BLOCO DE ESTUDO
    st.markdown("<h3 style='font-size:14px'>REGISTRAR BLOCO DE ESTUDO</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        materia_sel = st.selectbox("Matéria estudada", MATERIAS)
        blocos = st.number_input("Blocos completados (1h cada)", min_value=1, max_value=3, value=1, step=1)
    with col2:
        questoes_feitas = st.number_input("Questões respondidas", min_value=0, max_value=200, value=20, step=5)
        pct_acerto = st.slider("Taxa de acerto (%)", 0, 100, 60, step=5)

    if st.button("⚔ COMPLETAR MISSÃO DE ESTUDO"):
        xp_blocos = blocos * XP_RULES["bloco_estudo"]
        questoes_certas = int(questoes_feitas * pct_acerto / 100)
        xp_questoes = min(questoes_certas * XP_RULES["questao_certa"], 30)
        xp_ganho = xp_blocos + xp_questoes

        rank_up, r_antes, r_depois = ganhar_xp(estado, xp_ganho, f"Estudo: {materia_sel}")
        estado["dias_estudados"] += 1
        estado["streak"] += 1
        estado["ultima_sessao"] = datetime.now().strftime("%Y-%m-%d")

        dm = estado["desempenho_materias"][materia_sel]
        dm["acertos"] += questoes_certas
        dm["erros"] += (questoes_feitas - questoes_certas)
        dm["questoes"] += questoes_feitas

        adicionar_log(estado, f"+{xp_ganho} XP | {materia_sel} | {blocos} bloco(s) | {questoes_certas}/{questoes_feitas} acertos", "xp")

        st.markdown(f"""
        <div class="system-msg-gold">
        ⚠ MISSÃO CONCLUÍDA ⚠<br><br>
        Matéria: {materia_sel}<br>
        XP por blocos: +{xp_blocos}<br>
        XP por acertos: +{xp_questoes}<br>
        ─────────────────<br>
        TOTAL GANHO: +{xp_ganho} XP<br>
        XP atual: {estado['xp_total']:,}
        </div>
        """, unsafe_allow_html=True)

        if rank_up:
            st.session_state.rank_up_msg = (r_antes, r_depois)
            st.balloons()

        salvar_estado(estado)
        st.rerun()

    st.markdown("---")

    # REGISTRO DE REVISÃO
    st.markdown("<h3 style='font-size:14px'>REGISTRAR REVISÃO</h3>", unsafe_allow_html=True)
    tipo_rev = st.selectbox("Tipo de revisão", ["24h (erros de ontem)", "7 dias (semanal)", "15 dias (ponto fraco)"])
    mat_rev = st.selectbox("Matéria revisada", MATERIAS, key="mat_rev")

    if st.button("📋 COMPLETAR REVISÃO"):
        rank_up, r_antes, r_depois = ganhar_xp(estado, XP_RULES["revisao_ponto_fraco"], f"Revisão: {mat_rev}")
        adicionar_log(estado, f"+{XP_RULES['revisao_ponto_fraco']} XP | Revisão {tipo_rev} | {mat_rev}", "revisao")
        st.markdown(f"""
        <div class="system-msg">
        [ REVISÃO REGISTRADA ] +{XP_RULES['revisao_ponto_fraco']} XP<br>
        Tipo: {tipo_rev} | Matéria: {mat_rev}
        </div>
        """, unsafe_allow_html=True)
        if rank_up:
            st.session_state.rank_up_msg = (r_antes, r_depois)
        salvar_estado(estado)
        st.rerun()

    st.markdown("---")

    # SEMANA COMPLETA
    st.markdown("<h3 style='font-size:14px'>BÔNUS DE STREAK</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌟 REGISTRAR SEMANA COMPLETA (+50 XP)"):
            rank_up, r_antes, r_depois = ganhar_xp(estado, XP_RULES["semana_completa"], "Semana completa")
            estado["semanas_completas"] = estado.get("semanas_completas", 0) + 1
            estado["streak"] = max(estado["streak"], 7)
            adicionar_log(estado, f"+{XP_RULES['semana_completa']} XP | Semana completa — Streak mantido!", "bonus")
            st.success(f"+{XP_RULES['semana_completa']} XP! Semana completa registrada.")
            if rank_up:
                st.session_state.rank_up_msg = (r_antes, r_depois)
            salvar_estado(estado)
            st.rerun()
    with col2:
        if st.button("💀 REGISTRAR DIA PERDIDO (-15 XP)"):
            ganhar_xp(estado, XP_RULES["dia_perdido"], "Dia perdido")
            estado["streak"] = 0
            adicionar_log(estado, f"{XP_RULES['dia_perdido']} XP | Dia perdido — Streak zerado.", "penalidade")
            st.warning("Streak zerado. Retome amanhã.")
            salvar_estado(estado)
            st.rerun()


# ═══════════════════════════════════════════
#  TAB 3 — CRONOGRAMA
# ═══════════════════════════════════════════
with tab3:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>📅 CRONOGRAMA SEMANAL</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg">
    [ SISTEMA ] Plano otimizado para aprovação no Banco do Brasil. 3h/dia | 2 blocos principais + 1 rotativo.
    Baseado no que mais cai na Cesgranrio. Siga a ordem — ela foi calculada por impacto na prova.
    </div>
    """, unsafe_allow_html=True)

    CRONOGRAMA = [
        {
            "dia": "SEGUNDA-FEIRA",
            "emoji": "🔵",
            "blocos": [
                {"slot": "Bloco 1 (1h)", "materia": "Matemática", "topico": "Porcentagem, razão e proporção, regra de três", "cor": "#1a4aff", "tipo": "Teoria (vídeo 40min) + Questões (20min)"},
                {"slot": "Bloco 2 (1h)", "materia": "Português", "topico": "Interpretação de texto — inferência e coesão", "cor": "#5b9cf6", "tipo": "Teoria (vídeo 40min) + Questões (20min)"},
                {"slot": "Bloco 3 (1h) — Rotativo", "materia": "Conhecimentos Bancários", "topico": "Sistema Financeiro Nacional: Bacen, CMN, estrutura", "cor": "#aa8800", "tipo": "Vídeo resumido (30min) + Questões (30min)"},
            ],
            "dica": "Segunda é o dia de maior energia. Ataque Matemática no bloco 1 quando o cérebro está mais fresco."
        },
        {
            "dia": "TERÇA-FEIRA",
            "emoji": "🔵",
            "blocos": [
                {"slot": "Bloco 1 (1h)", "materia": "Matemática", "topico": "Juros simples e compostos — fórmulas e exercícios", "cor": "#1a4aff", "tipo": "Teoria (30min) + Questões cronometradas (30min)"},
                {"slot": "Bloco 2 (1h)", "materia": "Português", "topico": "Concordância verbal e nominal — regras principais", "cor": "#5b9cf6", "tipo": "Teoria (30min) + Questões (30min)"},
                {"slot": "Bloco 3 (1h) — Rotativo", "materia": "Revisão 24h", "topico": "Refaça os erros de segunda-feira", "cor": "#22aa22", "tipo": "100% questões — só os erros"},
            ],
            "dica": "Revisão 24h é obrigatória. Refazer o erro em 24h grava 40% mais do que reler o conteúdo."
        },
        {
            "dia": "QUARTA-FEIRA",
            "emoji": "🟡",
            "blocos": [
                {"slot": "Bloco 1 (1h)", "materia": "Matemática", "topico": "Raciocínio lógico — sequências e proposições", "cor": "#1a4aff", "tipo": "Teoria (30min) + Questões (30min)"},
                {"slot": "Bloco 2 (1h)", "materia": "Conhecimentos Bancários", "topico": "Produtos bancários: CDB, LCI, LCA, poupança, câmbio", "cor": "#aa8800", "tipo": "Teoria (40min) + Questões (20min)"},
                {"slot": "Bloco 3 (1h) — Rotativo", "materia": "Informática", "topico": "Pacote Office, Windows, atalhos e conceitos básicos", "cor": "#5b7a9f", "tipo": "Vídeo (30min) + Questões (30min)"},
            ],
            "dica": "Quarta é o pico da semana. Raciocínio lógico é sua força — use para ganhar confiança antes de KB."
        },
        {
            "dia": "QUINTA-FEIRA",
            "emoji": "🟡",
            "blocos": [
                {"slot": "Bloco 1 (1h)", "materia": "Português", "topico": "Regência verbal e nominal + crase (as mais cobradas)", "cor": "#5b9cf6", "tipo": "Teoria (30min) + Questões (30min)"},
                {"slot": "Bloco 2 (1h)", "materia": "Matemática", "topico": "Estatística básica: média, mediana, moda, desvio padrão", "cor": "#1a4aff", "tipo": "Teoria bem devagar (45min) + Questões (15min) — ponto fraco!"},
                {"slot": "Bloco 3 (1h) — Rotativo", "materia": "Revisão 7 dias", "topico": "Revisão do conteúdo da semana passada", "cor": "#22aa22", "tipo": "Somente questões — mínimo 30 questões"},
            ],
            "dica": "Estatística é sua fraqueza declarada. Dedique mais tempo aqui. Use o método: entenda 1 conceito por vez, não tudo junto."
        },
        {
            "dia": "SEXTA-FEIRA",
            "emoji": "🟠",
            "blocos": [
                {"slot": "Bloco 1 (1h)", "materia": "Conhecimentos Bancários", "topico": "Mercado financeiro: renda fixa, renda variável, fundos", "cor": "#aa8800", "tipo": "Teoria (40min) + Questões (20min)"},
                {"slot": "Bloco 2 (1h)", "materia": "Redação", "topico": "Estrutura da dissertação argumentativa — introdução e tese", "cor": "#cc2222", "tipo": "Escreva 1 parágrafo de introdução e peça feedback a alguém"},
                {"slot": "Bloco 3 (1h) — Rotativo", "materia": "Atualidades + Bancos", "topico": "Notícias do BB, Bacen, economia — leia 3 notícias e faça resumo", "cor": "#3a5a7f", "tipo": "Leitura ativa (30min) + Questões de atualidades recentes (30min)"},
            ],
            "dica": "Sexta é o dia mais cansativo. Redação e atualidades são mais leves — sem cálculo. Preserve energia para o simulado de sábado."
        },
        {
            "dia": "SÁBADO",
            "emoji": "🔴",
            "blocos": [
                {"slot": "Bloco 1+2+3 (3h)", "materia": "⚔ BOSS FIGHT — SIMULADO", "topico": "Simulado completo: 30–50 questões estilo Cesgranrio", "cor": "#cc44ff", "tipo": "2h simulado + 1h correção detalhada — marque todos os erros"},
            ],
            "dica": "Trate o simulado como prova real. Sem pausas, sem checar resposta no meio. Após: anote 100% dos erros e ajuste o plano da próxima semana."
        },
        {
            "dia": "DOMINGO",
            "emoji": "🟢",
            "blocos": [
                {"slot": "Opcional (1h)", "materia": "Revisão 15 dias / Ponto Fraco", "topico": "Pegue a matéria mais fraca da semana e refaça 20 questões", "cor": "#22aa22", "tipo": "Somente questões dos pontos fracos identificados no simulado"},
            ],
            "dica": "Domingo é descanso e revisão leve. Se o simulado de sábado mostrou uma fraqueza crítica, use 1h aqui para atacá-la. Senão, descanse."
        },
    ]

    TOPICOS_DETALHADOS = {
        "Matemática": {
            "cor": "#1a4aff",
            "prioridade": "🔴 MÁXIMA",
            "peso_prova": "~25% das questões",
            "topicos": [
                ("Porcentagem e Variação Percentual", "Semana 1–2", "Alta"),
                ("Razão, Proporção e Regra de Três", "Semana 1–2", "Alta"),
                ("Juros Simples", "Semana 2–3", "Alta"),
                ("Juros Compostos e Desconto", "Semana 3–4", "Muito Alta"),
                ("Amortização (SAC e Price)", "Semana 4–5", "Alta"),
                ("Raciocínio Lógico — Proposições", "Semana 3–4", "Alta"),
                ("Raciocínio Lógico — Sequências", "Semana 4–5", "Média"),
                ("Análise Combinatória", "Semana 5–6", "Média"),
                ("Probabilidade", "Semana 6–7", "Alta"),
                ("Estatística Básica (média, mediana, moda)", "Semana 5–6", "Alta"),
                ("Desvio Padrão e Variância", "Semana 6–7", "Média"),
                ("Funções de 1º e 2º grau (básico)", "Semana 7–8", "Baixa"),
            ]
        },
        "Português": {
            "cor": "#5b9cf6",
            "prioridade": "🔴 MÁXIMA",
            "peso_prova": "~20% das questões",
            "topicos": [
                ("Interpretação e Compreensão de Texto", "Semana 1–2", "Muito Alta"),
                ("Inferência e Vocabulário em Contexto", "Semana 2–3", "Alta"),
                ("Concordância Verbal", "Semana 2–3", "Alta"),
                ("Concordância Nominal", "Semana 3–4", "Alta"),
                ("Regência Verbal e Nominal", "Semana 3–4", "Alta"),
                ("Crase — Regras Essenciais", "Semana 4–5", "Alta"),
                ("Pontuação — Vírgula obrigatória/proibida", "Semana 5–6", "Média"),
                ("Ortografia e Acentuação", "Semana 5–6", "Média"),
                ("Pronomes — colocação e emprego", "Semana 6–7", "Média"),
                ("Figuras de Linguagem (cobradas em texto)", "Semana 7–8", "Baixa"),
                ("Redação Dissertativa — Estrutura", "Semana 4 em diante", "Média"),
            ]
        },
        "Conhecimentos Bancários": {
            "cor": "#aa8800",
            "prioridade": "🟡 ALTA",
            "peso_prova": "~25% das questões",
            "topicos": [
                ("Sistema Financeiro Nacional — Estrutura", "Semana 1–2", "Muito Alta"),
                ("Bacen — Funções e Instrumentos", "Semana 1–2", "Muito Alta"),
                ("CMN — Composição e Atribuições", "Semana 2–3", "Alta"),
                ("Produtos Bancários — CDB, LCI, LCA, Poupança", "Semana 2–3", "Alta"),
                ("Crédito — CDC, leasing, cheque especial", "Semana 3–4", "Alta"),
                ("Câmbio — conceitos básicos", "Semana 3–4", "Média"),
                ("Mercado de Capitais — Ações, BDR, ETF", "Semana 4–5", "Alta"),
                ("Renda Fixa — Tesouro Direto, debêntures", "Semana 4–5", "Alta"),
                ("Fundos de Investimento", "Semana 5–6", "Alta"),
                ("Previdência Privada — PGBL, VGBL", "Semana 5–6", "Média"),
                ("LGPD aplicada ao setor bancário", "Semana 6–7", "Alta"),
                ("Prevenção à Lavagem de Dinheiro (PLD)", "Semana 6–7", "Alta"),
                ("Compliance e Governança Corporativa", "Semana 7–8", "Média"),
                ("Banco do Brasil — história, missão, produtos", "Semana 8", "Alta"),
            ]
        },
        "Informática": {
            "cor": "#5b7a9f",
            "prioridade": "🟠 MÉDIA",
            "peso_prova": "~15% das questões",
            "topicos": [
                ("Windows 10/11 — operações básicas", "Semana 1–2", "Alta"),
                ("Word — formatação, mala direta, revisão", "Semana 2–3", "Alta"),
                ("Excel — fórmulas, gráficos, filtros", "Semana 3–4", "Alta"),
                ("Internet — navegadores, HTTP, HTTPS", "Semana 4–5", "Alta"),
                ("E-mail — protocolos POP, IMAP, SMTP", "Semana 4–5", "Média"),
                ("Segurança da Informação — conceitos", "Semana 5–6", "Alta"),
                ("Vírus, malware, phishing, ransomware", "Semana 5–6", "Alta"),
                ("Redes — conceitos básicos, LAN, WAN, VPN", "Semana 6–7", "Média"),
                ("Cloud Computing — conceitos", "Semana 6–7", "Média"),
                ("Banco de Dados — conceitos básicos", "Semana 7–8", "Baixa"),
            ]
        },
        "Redação": {
            "cor": "#cc2222",
            "prioridade": "🟠 MÉDIA",
            "peso_prova": "Eliminatória",
            "topicos": [
                ("Estrutura da dissertação argumentativa", "Semana 2–3", "Muito Alta"),
                ("Introdução — apresentação e tese", "Semana 3–4", "Muito Alta"),
                ("Desenvolvimento — argumentos e exemplos", "Semana 4–5", "Alta"),
                ("Conclusão — proposta de intervenção", "Semana 5–6", "Alta"),
                ("Coesão — conectivos e pronomes referenciais", "Semana 4–6", "Alta"),
                ("Coerência e progressão temática", "Semana 5–7", "Alta"),
                ("Praticar 1 redação por semana (sexta)", "Semana 3 em diante", "Muito Alta"),
            ]
        },
        "Atualidades": {
            "cor": "#3a5a7f",
            "prioridade": "🟢 BAIXA",
            "peso_prova": "~5–10% das questões",
            "topicos": [
                ("Economia brasileira — últimos 6 meses", "Contínuo", "Média"),
                ("Política monetária — Selic, inflação", "Contínuo", "Alta"),
                ("Notícias do Banco do Brasil", "Contínuo", "Alta"),
                ("Regulação bancária recente — Bacen", "Contínuo", "Média"),
                ("Tecnologia financeira — Pix, Open Finance", "Semana 3–5", "Alta"),
            ]
        },
    }

    # Cronograma semanal
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px;margin-top:16px'>PLANO SEMANAL</h3>", unsafe_allow_html=True)

    for dia_info in CRONOGRAMA:
        is_sabado = dia_info["dia"] == "SÁBADO"
        is_domingo = dia_info["dia"] == "DOMINGO"
        card_class = "sl-card-red" if is_sabado else ("sl-card-green" if is_domingo else "sl-card")
        with st.expander(f"{dia_info['emoji']} {dia_info['dia']}", expanded=(dia_info["dia"] == "SEGUNDA-FEIRA")):
            st.markdown(f"""
            <div class="system-msg" style="margin-bottom:12px">
            💡 {dia_info['dica']}
            </div>
            """, unsafe_allow_html=True)
            for bloco in dia_info["blocos"]:
                st.markdown(f"""
                <div class="sl-card" style="border-color:{bloco['cor']};margin:8px 0">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
                    <span style="color:{bloco['cor']};font-family:'Orbitron',monospace;font-size:11px;letter-spacing:1px">{bloco['slot']}</span>
                    <span style="color:#c8d8f0;font-weight:bold;font-size:13px">{bloco['materia']}</span>
                  </div>
                  <div style="color:#c8d8f0;font-size:13px;margin-bottom:6px">📖 {bloco['topico']}</div>
                  <div style="color:#5b7a9f;font-size:11px;font-family:'Share Tech Mono',monospace">⏱ {bloco['tipo']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>TÓPICOS POR MATÉRIA — SEQUÊNCIA DE ESTUDOS</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg">
    [ SISTEMA ] Estude os tópicos nesta ordem. Ela foi definida por: frequência nas provas da Cesgranrio + dependência de conceitos anteriores.
    </div>
    """, unsafe_allow_html=True)

    for materia, dados in TOPICOS_DETALHADOS.items():
        with st.expander(f"{'📐' if materia=='Matemática' else '📝' if materia=='Português' else '🏦' if materia=='Conhecimentos Bancários' else '💻' if materia=='Informática' else '✍️' if materia=='Redação' else '📰'} {materia} — {dados['prioridade']} | {dados['peso_prova']}"):
            for topico, periodo, impacto in dados["topicos"]:
                cor_imp = "#cc2222" if impacto == "Muito Alta" else "#cc6600" if impacto == "Alta" else "#aa8800" if impacto == "Média" else "#3a5a7f"
                st.markdown(f"""
                <div class="stat-line">
                  <span class="stat-label" style="font-size:12px">{topico}</span>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:11px">
                    <span style="color:#5b7a9f">{periodo}</span>
                    <span style="color:{cor_imp};margin-left:12px">{impacto}</span>
                  </span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>SISTEMA DE REVISÃO INTELIGENTE</h3>", unsafe_allow_html=True)
    revisoes = [
        ("24h depois", "Refaça somente as questões erradas do dia anterior", "#22aa22", "Fixa 40% mais do que reler o conteúdo"),
        ("7 dias depois", "Resolva um novo conjunto de questões do mesmo tópico", "#aa8800", "Consolida na memória de longo prazo"),
        ("15 dias depois", "Se ainda estiver errando muito: assista vídeo curto + questões", "#cc6600", "Identifica ponto fraco real — priorize na semana seguinte"),
        ("Sábado — Boss Fight", "Simulado completo. Corrija 100% dos erros e anote padrões", "#cc44ff", "O simulado direciona toda a semana seguinte"),
    ]
    for titulo, desc, cor, motivo in revisoes:
        st.markdown(f"""
        <div class="sl-card" style="border-color:{cor};margin:8px 0">
          <div style="color:{cor};font-family:'Orbitron',monospace;font-size:12px;margin-bottom:6px">{titulo}</div>
          <div style="color:#c8d8f0;font-size:13px;margin-bottom:4px">{desc}</div>
          <div style="color:#5b7a9f;font-size:11px;font-family:'Share Tech Mono',monospace">💡 {motivo}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  TAB 4 — DUNGEONS
# ═══════════════════════════════════════════
with tab4:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>DUNGEONS DISPONÍVEIS</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg">
    [ SISTEMA ] Dungeons são missões temáticas de cada matéria. Complete para ganhar XP bônus.
    Dungeons de ranks superiores ao seu estão bloqueadas.
    </div>
    """, unsafe_allow_html=True)

    rank_order = ["E", "D", "C", "B", "A", "S"]
    rank_idx_atual = rank_order.index(rank_n)

    for rank_key, dungeons in DUNGEONS.items():
        rank_k_idx = rank_order.index(rank_key)
        bloqueado = rank_k_idx > rank_idx_atual

        cor_header = "#5b7a9f" if bloqueado else "#5b9cf6"
        icone = "🔒" if bloqueado else "⚔"
        st.markdown(f"""
        <div style="color:{cor_header};font-family:'Orbitron',monospace;font-size:13px;margin:16px 0 8px;letter-spacing:2px">
        {icone} DUNGEONS RANK {rank_key} {'[BLOQUEADO]' if bloqueado else '[DISPONÍVEL]'}
        </div>
        """, unsafe_allow_html=True)

        for d in dungeons:
            dungeon_id = f"{rank_key}_{d['nome']}"
            ja_feita = dungeon_id in estado["dungeons_completas"]

            col1, col2 = st.columns([4, 1])
            with col1:
                status_color = "#22aa22" if ja_feita else ("#3a3a5a" if bloqueado else "#c8d8f0")
                st.markdown(f"""
                <div class="sl-card" style="{'opacity:0.4' if bloqueado else ''}">
                  <div style="display:flex;justify-content:space-between;align-items:start">
                    <div>
                      <div style="color:{status_color};font-weight:bold;font-size:14px">
                        {'✓ ' if ja_feita else ''}{d['nome']}
                      </div>
                      <div style="color:#5b7a9f;font-size:12px;margin-top:4px">{d['desc']}</div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;margin-left:12px">
                      <div style="color:#ffd700;font-family:'Share Tech Mono',monospace;font-size:13px">+{d['xp']} XP</div>
                      <div style="color:#5b7a9f;font-size:11px">Rank {d['dificuldade']}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if not bloqueado and not ja_feita:
                    if st.button(f"Entrar", key=f"dung_{dungeon_id}"):
                        rank_up, r_antes, r_depois = ganhar_xp(estado, d["xp"], f"Dungeon: {d['nome']}")
                        estado["dungeons_completas"].append(dungeon_id)
                        adicionar_log(estado, f"+{d['xp']} XP | Dungeon concluída: {d['nome']}", "dungeon")
                        st.markdown(f"""
                        <div class="system-msg-gold">
                        DUNGEON COMPLETA! +{d['xp']} XP
                        </div>
                        """, unsafe_allow_html=True)
                        if rank_up:
                            st.session_state.rank_up_msg = (r_antes, r_depois)
                        salvar_estado(estado)
                        st.rerun()
                elif ja_feita:
                    st.markdown("<div style='color:#22aa22;font-size:12px;text-align:center;padding-top:16px'>✓ Completa</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#3a3a5a;font-size:12px;text-align:center;padding-top:16px'>🔒 Bloqueada</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  TAB 5 — BOSS FIGHT (SIMULADO)
# ═══════════════════════════════════════════
with tab5:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>BOSS FIGHT — SIMULADOS</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg-red">
    ⚠ ALERTA ⚠ — Boss Fight ativado. Não é treino. É combate real. Trate como o dia da prova.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bosses
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>BOSSES DA JORNADA</h3>", unsafe_allow_html=True)
    for boss in BOSSES:
        ja_derrotado = boss["nome"] in estado["bosses_derrotados"]
        disponivel = estado["xp_total"] >= boss["requisito"]

        if ja_derrotado:
            borda = "#22aa22"
            bg = "linear-gradient(135deg,#001a0e,#002e18)"
            status_txt = "✓ DERROTADO"
            status_color = "#22aa22"
        elif disponivel:
            borda = boss["color"]
            bg = "linear-gradient(135deg,#1a0000,#2e0505)"
            status_txt = "DISPONÍVEL"
            status_color = boss["color"]
        else:
            borda = "#1e3a6e"
            bg = "linear-gradient(135deg,#050a14,#080f1e)"
            status_txt = f"Requer {boss['requisito']:,} XP"
            status_color = "#3a5a7f"

        st.markdown(f"""
        <div style="background:{bg};border:2px solid {borda};border-radius:10px;padding:16px;margin:8px 0;opacity:{'1' if disponivel or ja_derrotado else '0.5'}">
          <div style="display:flex;justify-content:space-between;align-items:start">
            <div>
              <div style="color:{borda};font-family:'Orbitron',monospace;font-weight:900;font-size:15px">{boss['nome']}</div>
              <div style="color:#5b7a9f;font-size:12px;margin-top:4px">{boss['desc']}</div>
              <div style="color:#5b7a9f;font-size:11px;margin-top:4px">Rank: {boss['rank']} | Recompensa: +{boss['xp']} XP</div>
            </div>
            <div style="text-align:right;flex-shrink:0;margin-left:12px">
              <div style="color:{status_color};font-size:13px;font-family:'Share Tech Mono',monospace">{status_txt}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if disponivel and not ja_derrotado:
            if st.button(f"⚔ Desafiar {boss['nome'].split()[0]}", key=f"boss_{boss['nome']}"):
                st.session_state[f"boss_ativo_{boss['nome']}"] = True
                st.rerun()

        if st.session_state.get(f"boss_ativo_{boss['nome']}", False):
            with st.expander(f"Registrar resultado — {boss['nome']}", expanded=True):
                pct_boss = st.slider("Aproveitamento no simulado (%)", 0, 100, 65, key=f"pct_{boss['nome']}")
                if st.button("CONFIRMAR RESULTADO", key=f"conf_{boss['nome']}"):
                    xp_boss = boss["xp"]
                    if pct_boss >= 70:
                        xp_boss += XP_RULES["simulado_acima_70"]
                    rank_up, r_antes, r_depois = ganhar_xp(estado, xp_boss, f"Boss: {boss['nome']}")
                    estado["bosses_derrotados"].append(boss["nome"])
                    estado["simulados_feitos"] += 1
                    estado["historico_simulados"].append({
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "boss": boss["nome"],
                        "pct": pct_boss,
                        "xp": xp_boss,
                    })
                    adicionar_log(estado, f"+{xp_boss} XP | Boss derrotado: {boss['nome']} | {pct_boss}%", "boss")
                    st.session_state[f"boss_ativo_{boss['nome']}"] = False
                    if rank_up:
                        st.session_state.rank_up_msg = (r_antes, r_depois)
                        st.balloons()
                    salvar_estado(estado)
                    st.rerun()

    st.markdown("---")

    # Simulado avulso
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>SIMULADO SEMANAL (AVULSO)</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class="system-msg">
    Todo sábado é um boss fight. Mesmo sem ser um boss oficial, registre seu simulado aqui.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        questoes_sim = st.number_input("Questões totais", min_value=10, max_value=80, value=40, step=5, key="qs_sim")
        acertos_sim = st.number_input("Acertos", min_value=0, max_value=80, value=24, step=1, key="ac_sim")
    with col2:
        notas_por_materia = {}
        with st.expander("Desempenho por matéria (opcional)"):
            for m in MATERIAS[:4]:
                notas_por_materia[m] = st.slider(f"{m} (%)", 0, 100, 60, step=5, key=f"sim_{m}")

    if st.button("⚔ REGISTRAR SIMULADO SEMANAL"):
        pct_geral = int((acertos_sim / max(questoes_sim, 1)) * 100)
        xp_sim = XP_RULES["simulado_completo"]
        if pct_geral >= 70:
            xp_sim += XP_RULES["simulado_acima_70"]

        rank_up, r_antes, r_depois = ganhar_xp(estado, xp_sim, f"Simulado semanal {pct_geral}%")
        estado["simulados_feitos"] += 1
        estado["historico_simulados"].append({
            "data": datetime.now().strftime("%Y-%m-%d"),
            "boss": "Simulado semanal",
            "pct": pct_geral,
            "xp": xp_sim,
        })

        for m, pct in notas_por_materia.items():
            questoes_m = questoes_sim // 4
            acertos_m = int(questoes_m * pct / 100)
            estado["desempenho_materias"][m]["acertos"] += acertos_m
            estado["desempenho_materias"][m]["erros"] += (questoes_m - acertos_m)
            estado["desempenho_materias"][m]["questoes"] += questoes_m

        adicionar_log(estado, f"+{xp_sim} XP | Simulado semanal | {acertos_sim}/{questoes_sim} ({pct_geral}%)", "boss")

        st.markdown(f"""
        <div class="system-msg-gold" style="font-size:15px;padding:16px">
        ⚠ BOSS FIGHT CONCLUÍDO ⚠<br><br>
        Aproveitamento: {pct_geral}%<br>
        XP ganho: +{xp_sim}<br>
        {'✓ Bônus de 70%+ desbloqueado!' if pct_geral >= 70 else ''}<br>
        XP total: {estado['xp_total']:,}
        </div>
        """, unsafe_allow_html=True)

        if rank_up:
            st.session_state.rank_up_msg = (r_antes, r_depois)
            st.balloons()

        salvar_estado(estado)
        st.rerun()

    # Histórico de simulados
    if estado["historico_simulados"]:
        st.markdown("<br><h3 style='font-size:14px'>HISTÓRICO DE BOSS FIGHTS</h3>", unsafe_allow_html=True)
        for s in reversed(estado["historico_simulados"][-10:]):
            cor = "#22aa22" if s["pct"] >= 70 else ("#aa8800" if s["pct"] >= 50 else "#cc2222")
            st.markdown(f"""
            <div class="stat-line">
              <span class="stat-label">{s['data']} · {s.get('boss','Simulado')}</span>
              <span style="color:{cor};font-family:'Share Tech Mono',monospace">{s['pct']}% · +{s['xp']} XP</span>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  TAB 6 — DESEMPENHO
# ═══════════════════════════════════════════
with tab6:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>ANÁLISE DE DESEMPENHO</h2>", unsafe_allow_html=True)

    dm = estado["desempenho_materias"]
    nomes = []
    acertos_pct = []
    questoes_tot = []
    status_list = []

    for m, dados in dm.items():
        q = dados["questoes"]
        a = dados["acertos"]
        pct = int((a / max(q, 1)) * 100)
        nomes.append(m)
        acertos_pct.append(pct)
        questoes_tot.append(q)
        if q == 0:
            status_list.append("Sem dados")
        elif pct >= 70:
            status_list.append("Forte")
        elif pct >= 50:
            status_list.append("Médio")
        else:
            status_list.append("Fraco")

    # Radar chart
    if any(q > 0 for q in questoes_tot):
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=acertos_pct,
            theta=nomes,
            fill="toself",
            fillcolor="rgba(91,156,246,0.15)",
            line=dict(color="#5b9cf6", width=2),
            marker=dict(color="#5b9cf6", size=6),
            name="Acerto %"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#080f1e",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e3a6e", tickfont=dict(color="#5b7a9f")),
                angularaxis=dict(gridcolor="#1e3a6e", tickfont=dict(color="#c8d8f0")),
            ),
            paper_bgcolor="#050a14",
            font=dict(color="#5b7a9f"),
            title=dict(text="Radar de Desempenho por Matéria", font=dict(color="#5b9cf6", size=14)),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.markdown("""
        <div class="system-msg">
        [ SISTEMA ] Nenhuma questão registrada ainda. Complete missões de estudo para ver seu radar.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cards de matéria
    st.markdown("<h3 style='font-size:14px;letter-spacing:2px'>STATUS POR MATÉRIA</h3>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    for i, (m, dados) in enumerate(dm.items()):
        q = dados["questoes"]
        a = dados["acertos"]
        e = dados["erros"]
        pct = int((a / max(q, 1)) * 100)
        status = status_list[i]
        cor = {"Forte": "#22aa22", "Médio": "#aa8800", "Fraco": "#cc2222", "Sem dados": "#3a5a7f"}[status]

        col = col_a if i % 2 == 0 else col_b
        with col:
            st.markdown(f"""
            <div class="sl-card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <span style="color:#c8d8f0;font-weight:bold;font-size:13px">{m}</span>
                <span style="color:{cor};font-size:12px;font-family:'Share Tech Mono',monospace">{status}</span>
              </div>
              <div class="xp-bar-container">
                <div class="xp-bar-fill" style="width:{pct}%;background:{'linear-gradient(90deg,#22aa22,#44cc44)' if pct>=70 else 'linear-gradient(90deg,#aa8800,#ccaa00)' if pct>=50 else 'linear-gradient(90deg,#cc2222,#ff4444)'}"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:6px">
                <span style="color:#5b7a9f;font-size:11px">{q} questões</span>
                <span style="color:{cor};font-size:12px;font-family:'Share Tech Mono',monospace">{pct}%</span>
              </div>
              <div style="display:flex;gap:16px;margin-top:4px">
                <span style="color:#22aa22;font-size:11px">✓ {a} acertos</span>
                <span style="color:#cc2222;font-size:11px">✗ {e} erros</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Prioridade recomendada
    st.markdown("<br><h3 style='font-size:14px;letter-spacing:2px'>PRIORIDADE RECOMENDADA PARA ESTA SEMANA</h3>", unsafe_allow_html=True)

    materias_com_dados = [(nomes[i], acertos_pct[i]) for i in range(len(nomes)) if questoes_tot[i] > 0]
    if materias_com_dados:
        ordenadas = sorted(materias_com_dados, key=lambda x: x[1])
        for m, pct in ordenadas:
            cor = "#cc2222" if pct < 50 else "#aa8800" if pct < 70 else "#22aa22"
            prioridade = "MÁXIMA" if pct < 50 else "ALTA" if pct < 70 else "MANUTENÇÃO"
            st.markdown(f"""
            <div class="stat-line">
              <span class="stat-label">{m}</span>
              <span style="color:{cor};font-family:'Share Tech Mono',monospace;font-size:12px">{prioridade} · {pct}%</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="system-msg">
        Prioridades disponíveis após registrar questões nas missões diárias.
        </div>
        """, unsafe_allow_html=True)

    # Histórico de simulados como gráfico
    if len(estado["historico_simulados"]) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        datas_sim = [s["data"] for s in estado["historico_simulados"]]
        pcts_sim = [s["pct"] for s in estado["historico_simulados"]]

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=datas_sim, y=pcts_sim,
            mode="lines+markers",
            line=dict(color="#cc44ff", width=2),
            marker=dict(color="#cc44ff", size=8),
            name="Aproveitamento %"
        ))
        fig_sim.add_hline(y=70, line_dash="dot", line_color="#22aa22", annotation_text="Meta 70%")
        fig_sim.add_hline(y=50, line_dash="dot", line_color="#cc2222", annotation_text="Mín. 50%")
        fig_sim.update_layout(
            paper_bgcolor="#050a14",
            plot_bgcolor="#080f1e",
            font=dict(color="#5b7a9f"),
            title=dict(text="Evolução nos Simulados", font=dict(color="#5b9cf6", size=14)),
            yaxis=dict(range=[0, 105], gridcolor="#0d1f3c", tickfont=dict(color="#5b7a9f")),
            xaxis=dict(gridcolor="#0d1f3c", tickfont=dict(color="#5b7a9f")),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_sim, use_container_width=True)


# ═══════════════════════════════════════════
#  TAB 7 — LOG
# ═══════════════════════════════════════════
with tab7:
    st.markdown("<h2 style='font-size:16px;letter-spacing:3px'>LOG DE ATIVIDADES</h2>", unsafe_allow_html=True)

    if estado["log_atividades"]:
        for entry in estado["log_atividades"]:
            tipo = entry.get("tipo", "info")
            cores = {
                "xp": "#5b9cf6",
                "bonus": "#ffd700",
                "dungeon": "#cc44ff",
                "boss": "#ff4444",
                "revisao": "#22aa22",
                "penalidade": "#cc2222",
                "info": "#5b7a9f",
            }
            cor = cores.get(tipo, "#5b7a9f")
            st.markdown(f"""
            <div style="display:flex;gap:12px;padding:6px 0;border-bottom:1px solid #0d1f3c;font-family:'Share Tech Mono',monospace;font-size:12px">
              <span style="color:#3a5a7f;flex-shrink:0;min-width:75px">{entry['ts']}</span>
              <span style="color:{cor}">{entry['msg']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="system-msg">
        [ SISTEMA ] Nenhuma atividade registrada ainda. Comece sua primeira missão.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:14px'>ESTATÍSTICAS DA JORNADA</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Dias estudados", estado["dias_estudados"])
    with col2:
        st.metric("Semanas completas", estado.get("semanas_completas", 0))
    with col3:
        total_q = sum(dm["questoes"] for dm in estado["desempenho_materias"].values())
        total_a = sum(dm["acertos"] for dm in estado["desempenho_materias"].values())
        st.metric("Questões feitas", total_q)
    with col4:
        pct_geral = int((total_a / max(total_q, 1)) * 100)
        st.metric("Acerto geral", f"{pct_geral}%")

    dungeons_feitas = len(estado["dungeons_completas"])
    total_dungeons = sum(len(v) for v in DUNGEONS.values())
    st.markdown(f"""
    <div style="margin-top:16px">
    <div class="stat-line"><span class="stat-label">Dungeons completas</span><span class="stat-value">{dungeons_feitas}/{total_dungeons}</span></div>
    <div class="stat-line"><span class="stat-label">Bosses derrotados</span><span class="stat-value">{len(estado['bosses_derrotados'])}/5</span></div>
    <div class="stat-line"><span class="stat-label">XP total acumulado</span><span class="stat-value">{estado['xp_total']:,}</span></div>
    </div>
    """, unsafe_allow_html=True)