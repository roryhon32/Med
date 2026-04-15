# app.py
"""
📚 MedStudy Organizer – Rotina Inteligente para Estudante de Medicina
Design renovado com paleta teal/verde, gráficos aprimorados e novas funcionalidades.
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import json
import calendar

# ----------------------------- CONFIGURAÇÃO DE PÁGINA -----------------------------
st.set_page_config(
    page_title="MedStudy Organizer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------- PALETA DE CORES -----------------------------
COLORS = {
    "primary":    "#006D77",   # verde-escuro
    "secondary":  "#83C5BE",   # verde-acinzentado
    "bg_light":   "#EDF6F9",   # bege claro
    "accent":     "#D9B29C",   # terracota suave
    "accent2":    "#A66953",   # terracota escuro
    "white":      "#FFFFFF",
    "text_dark":  "#1A2E35",
    "text_mid":   "#3D5A63",
    "border":     "#C8E0E3",
}

# Paleta para gráficos
CHART_COLORS = ["#006D77", "#83C5BE", "#D9B29C", "#A66953", "#4A9E99", "#E8C4B2", "#2C8A8F", "#F0DDD0"]

# ----------------------------- CSS PERSONALIZADO -----------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', system-ui, sans-serif;
    }}

    .stApp {{
        background-color: {COLORS['bg_light']};
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(160deg, {COLORS['primary']} 0%, #004E56 100%);
        border-right: none;
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLORS['white']} !important;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        color: rgba(255,255,255,0.85) !important;
    }}
    section[data-testid="stSidebar"] .stProgress > div {{
        background-color: rgba(255,255,255,0.2) !important;
        border-radius: 20px !important;
    }}
    section[data-testid="stSidebar"] .stProgress > div > div {{
        background: linear-gradient(90deg, {COLORS['secondary']}, #A8DAD6) !important;
        border-radius: 20px !important;
    }}
    section[data-testid="stSidebar"] .stMetricValue {{
        color: {COLORS['white']} !important;
    }}

    h1, h2, h3 {{
        color: {COLORS['text_dark']};
        font-weight: 600;
        letter-spacing: -0.02em;
    }}

    div[data-testid="stMetric"] {{
        background: {COLORS['white']};
        border-radius: 18px;
        padding: 20px 18px;
        box-shadow: 0 4px 16px rgba(0,109,119,0.08);
        border: 1px solid {COLORS['border']};
        transition: all 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,109,119,0.14);
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS['primary']} !important;
        font-weight: 700 !important;
    }}

    .stButton > button {{
        border-radius: 30px;
        padding: 0.5rem 1.8rem;
        font-weight: 500;
        border: none;
        background: linear-gradient(135deg, {COLORS['primary']}, #004E56);
        color: white;
        box-shadow: 0 4px 12px rgba(0,109,119,0.25);
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #005A62, {COLORS['primary']});
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,109,119,0.35);
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {COLORS['accent2']}, {COLORS['accent']});
        box-shadow: 0 4px 12px rgba(166,105,83,0.3);
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #8A5440, {COLORS['accent2']});
        box-shadow: 0 8px 20px rgba(166,105,83,0.4);
    }}

    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        border-radius: 12px !important;
        border: 1.5px solid {COLORS['border']} !important;
        background-color: {COLORS['white']} !important;
        color: {COLORS['text_dark']} !important;
    }}
    .stSelectbox div[data-baseweb="select"] > div:focus-within,
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(0,109,119,0.12) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 30px;
        padding: 8px 22px;
        background: {COLORS['white']};
        border: 1.5px solid {COLORS['border']};
        color: {COLORS['text_mid']};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']} !important;
        color: white !important;
        border-color: {COLORS['primary']} !important;
    }}

    .stAlert {{
        border-radius: 14px;
        border-left-width: 5px;
    }}

    .stDataFrame {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {COLORS['border']};
    }}

    /* Cards customizados */
    .med-card {{
        background: {COLORS['white']};
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,109,119,0.07);
        border: 1px solid {COLORS['border']};
        margin-bottom: 12px;
    }}

    .med-badge {{
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }}
    .badge-plantao {{ background: #FFE0D6; color: #C0392B; }}
    .badge-faculdade {{ background: #D6EEF0; color: #006D77; }}
    .badge-livre {{ background: #E8F5E9; color: #2E7D32; }}

    .streak-fire {{
        font-size: 2.5rem;
        text-align: center;
        display: block;
    }}

    /* Sidebar nav */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        padding: 8px 14px;
        border-radius: 10px;
        transition: background 0.15s;
    }}
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        background: rgba(255,255,255,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------- BANCO DE DADOS -----------------------------
DB_PATH = "medstudy.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS weekly_routine (
            day_of_week INTEGER PRIMARY KEY,
            type TEXT CHECK(type IN ('plantao', 'faculdade', 'livre'))
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE,
            hours REAL,
            study_type TEXT,
            subject TEXT,
            notes TEXT,
            xp_earned INTEGER,
            UNIQUE(log_date, subject, study_type)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            name TEXT PRIMARY KEY,
            color TEXT,
            added_date DATE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS weekly_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER,
            time_slot TEXT,
            subject TEXT,
            activity_type TEXT,
            notes TEXT,
            UNIQUE(day_of_week, time_slot)
        )
    ''')
    # Nova tabela: metas de estudo
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_goals (
            subject TEXT PRIMARY KEY,
            weekly_hours REAL,
            monthly_hours REAL
        )
    ''')
    # Nova tabela: notas rápidas
    c.execute('''
        CREATE TABLE IF NOT EXISTS quick_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME,
            subject TEXT,
            content TEXT,
            note_type TEXT
        )
    ''')
    default_subjects = [
        ('Anatomia', '#006D77'), ('Fisiologia', '#83C5BE'), ('Farmacologia', '#D9B29C'),
        ('Patologia', '#A66953'), ('Semiologia', '#4A9E99'), ('Clínica Médica', '#2C8A8F'),
        ('Pediatria', '#5BA69F'), ('Ginecologia', '#C4806A'), ('Cirurgia', '#7DC5BF')
    ]
    c.executemany("INSERT OR IGNORE INTO subjects (name, color) VALUES (?, ?)", default_subjects)
    c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES ('xp', '0')")
    c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES ('level', '1')")
    c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES ('streak', '0')")
    c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES ('last_study_date', '')")
    conn.commit()
    conn.close()

init_db()

# ----------------------------- FUNÇÕES AUXILIARES -----------------------------
def get_db_connection():
    return sqlite3.connect(DB_PATH)

def save_weekly_routine(routine_dict):
    conn = get_db_connection()
    c = conn.cursor()
    for day, type_ in routine_dict.items():
        c.execute("INSERT OR REPLACE INTO weekly_routine (day_of_week, type) VALUES (?, ?)", (day, type_))
    conn.commit()
    conn.close()

def load_weekly_routine():
    conn = get_db_connection()
    df = pd.read_sql("SELECT day_of_week, type FROM weekly_routine", conn)
    conn.close()
    if df.empty:
        default = {0: 'faculdade', 1: 'faculdade', 2: 'faculdade', 3: 'faculdade',
                   4: 'faculdade', 5: 'livre', 6: 'livre'}
        save_weekly_routine(default)
        return default
    return dict(zip(df['day_of_week'], df['type']))

def get_user_stat(key, default=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM user_stats WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_user_stat(key, value):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_stats (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def update_xp(amount):
    current_xp = int(get_user_stat('xp', 0))
    new_xp = current_xp + amount
    level = int(get_user_stat('level', 1))
    xp_needed = level * 100
    if new_xp >= xp_needed:
        new_xp -= xp_needed
        level += 1
        set_user_stat('level', level)
        st.balloons()
        st.success(f"🎉 Parabéns! Você subiu para o nível {level}!")
    set_user_stat('xp', new_xp)
    return new_xp, level

def calculate_streak():
    conn = get_db_connection()
    df = pd.read_sql("SELECT DISTINCT log_date FROM study_logs WHERE hours > 0 ORDER BY log_date DESC", conn)
    conn.close()
    if df.empty:
        return 0
    dates = pd.to_datetime(df['log_date']).dt.date.tolist()
    today = date.today()
    streak = 0
    check_date = today
    if check_date not in dates:
        check_date = today - timedelta(days=1)
    for d in dates:
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def add_study_log(log_date, hours, study_type, subject, notes):
    conn = get_db_connection()
    c = conn.cursor()
    xp_base = int(hours * 10)
    bonus = {'teoria': 2, 'revisao': 3, 'questoes': 5}.get(study_type, 0)
    xp_earned = xp_base + bonus
    c.execute('''
        INSERT OR REPLACE INTO study_logs (log_date, hours, study_type, subject, notes, xp_earned)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (log_date, hours, study_type, subject, notes, xp_earned))
    conn.commit()
    conn.close()
    update_xp(xp_earned)
    new_streak = calculate_streak()
    set_user_stat('streak', new_streak)
    set_user_stat('last_study_date', str(log_date))
    return xp_earned

def get_study_logs(start_date=None, end_date=None):
    conn = get_db_connection()
    query = "SELECT log_date, hours, study_type, subject, notes, xp_earned FROM study_logs"
    params = []
    if start_date and end_date:
        query += " WHERE log_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def get_subjects():
    conn = get_db_connection()
    df = pd.read_sql("SELECT name, color FROM subjects ORDER BY name", conn)
    conn.close()
    return df

def add_subject(name, color="#006D77"):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO subjects (name, color, added_date) VALUES (?, ?, ?)",
                  (name, color, date.today().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def save_weekly_schedule(schedule_df):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM weekly_schedule")
    for _, row in schedule_df.iterrows():
        c.execute('''
            INSERT INTO weekly_schedule (day_of_week, time_slot, subject, activity_type, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['day_of_week'], row['time_slot'], row['subject'], row['activity_type'], row.get('notes', '')))
    conn.commit()
    conn.close()

def load_weekly_schedule():
    conn = get_db_connection()
    df = pd.read_sql("SELECT day_of_week, time_slot, subject, activity_type, notes FROM weekly_schedule ORDER BY day_of_week, time_slot", conn)
    conn.close()
    return df

def has_schedule():
    df = load_weekly_schedule()
    return not df.empty

# Notas rápidas
def add_quick_note(subject, content, note_type):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO quick_notes (created_at, subject, content, note_type) VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), subject, content, note_type))
    conn.commit()
    conn.close()

def get_quick_notes(limit=20):
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM quick_notes ORDER BY created_at DESC LIMIT ?", conn, params=[limit])
    conn.close()
    return df

def delete_quick_note(note_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM quick_notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

# Metas
def save_goal(subject, weekly_hours, monthly_hours):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO study_goals (subject, weekly_hours, monthly_hours) VALUES (?, ?, ?)",
              (subject, weekly_hours, monthly_hours))
    conn.commit()
    conn.close()

def get_goals():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM study_goals", conn)
    conn.close()
    return df

# ----------------------------- OPENAI -----------------------------
def get_openai_client():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Chave da API OpenAI não encontrada. Configure em st.secrets ou variável de ambiente OPENAI_API_KEY.")
        st.stop()
    return OpenAI(api_key=api_key)

def generate_ai_suggestion(day_type, hours, energy, subject_focus, historical_context):
    client = get_openai_client()
    prompt = f"""
Você é um coach de estudos para medicina. A estudante tem hoje um dia tipo: {day_type}.
Tempo disponível: {hours} horas. Nível de energia: {energy}.
{'Assunto(s) de interesse: ' + subject_focus if subject_focus else 'Sem assunto específico definido.'}

{historical_context}

Sugira um plano de estudo detalhado:
- O que estudar (matérias ou tópicos específicos)
- Como estudar (método ativo, revisão, questões)
- Divisão do tempo em blocos com pequenas pausas
- Uma mensagem motivacional leve

Responda em português, de forma clara e encorajadora.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": "Você é um tutor de medicina experiente e motivador."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erro ao gerar sugestão: {str(e)}"

def generate_ai_weekly_schedule(user_input, routine, subjects_list, historical_context):
    client = get_openai_client()
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    routine_desc = "\n".join([f"- {dias[i]}: {routine.get(i, 'faculdade')}" for i in range(7)])
    subjects_str = ", ".join(subjects_list) if subjects_list else "matérias de medicina"
    prompt = f"""
Você é um assistente de organização de estudos para medicina. Crie um cronograma semanal detalhado para a estudante.

Informações:
- Rotina semanal (tipo de dia):
{routine_desc}
- Matérias disponíveis: {subjects_str}
- Histórico recente: {historical_context}
- Solicitações adicionais da estudante: "{user_input if user_input else 'Nenhuma'}"

Gere um cronograma considerando que plantão = estudo leve, faculdade = moderado, livre = intenso.
Retorne APENAS um JSON válido:
{{
  "schedule": [
    {{"day": 0, "time": "08:00-10:00", "subject": "Anatomia", "activity": "Teoria", "notes": ""}},
    ...
  ]
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": "Você é um organizador de estudos. Retorne apenas JSON válido."},
                      {"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        schedule_data = json.loads(content)
        return schedule_data.get("schedule", [])
    except Exception as e:
        st.error(f"Erro ao gerar cronograma: {e}")
        return None

def generate_ai_analysis(historical_context, goals_df, df_logs):
    """Nova função: análise geral de desempenho pela IA"""
    client = get_openai_client()
    goals_str = goals_df.to_string(index=False) if not goals_df.empty else "Sem metas definidas"
    prompt = f"""
Você é um mentor de medicina. Analise o desempenho de estudo da estudante e dê um relatório motivador.

{historical_context}

Metas definidas:
{goals_str}

Forneça:
1. Avaliação geral do desempenho (1-2 frases)
2. Pontos fortes observados
3. Áreas de melhoria
4. Sugestão para a próxima semana
5. Mensagem motivacional personalizada

Responda em português, de forma acolhedora e construtiva.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": "Você é um mentor experiente de medicina."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erro: {str(e)}"

def build_historical_context():
    today = date.today()
    week_ago = today - timedelta(days=7)
    df = get_study_logs(week_ago, today)
    if df.empty:
        return "Nenhum estudo registrado na última semana."
    total_horas = df['hours'].sum()
    days_studied = df['log_date'].nunique()
    avg_hours = total_horas / 7
    if days_studied < 3:
        consistency = "baixa consistência"
    elif days_studied < 5:
        consistency = "consistência moderada"
    else:
        consistency = "ótima consistência"
    subject_counts = df['subject'].value_counts()
    most = subject_counts.index[0] if not subject_counts.empty else "nenhuma"
    least = subject_counts.index[-1] if len(subject_counts) > 1 else "nenhuma"
    context = f"""
Histórico últimos 7 dias:
- Horas totais: {total_horas:.1f}h
- Dias estudados: {days_studied}/7
- Média diária: {avg_hours:.1f}h
- {consistency}
- Matéria mais estudada: {most}
- Matéria menos estudada: {least}
"""
    return context

def get_plan_for_today():
    routine = load_weekly_routine()
    today_weekday = date.today().weekday()
    day_type = routine.get(today_weekday, 'faculdade')
    if day_type == 'plantao':
        suggestion = "Estudo leve (revisão). Ideal: 1-2 horas, flashcards ou resumos."
        hours_rec = 1.5
        study_type_rec = "revisao"
    elif day_type == 'faculdade':
        suggestion = "Estudo moderado. Ideal: 2-3 horas, teoria + questões."
        hours_rec = 2.5
        study_type_rec = "teoria"
    else:
        suggestion = "Estudo intenso. Ideal: 4-6 horas, blocos com pausas."
        hours_rec = 4.0
        study_type_rec = "questoes"
    return day_type, suggestion, hours_rec, study_type_rec

# ----------------------------- HELPERS DE GRÁFICO -----------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(237,246,249,0.5)',
    font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
    margin=dict(l=10, r=10, t=36, b=10),
)

def styled_bar(df, x, y, title, color=None, text=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x], y=df[y],
        marker_color=color or COLORS['primary'],
        marker_line_width=0,
        text=df[text] if text else None,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f}h<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=COLORS['text_dark'])),
        bargap=0.35,
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.04)', zeroline=False),
        xaxis=dict(showgrid=False),
        **PLOTLY_LAYOUT
    )
    return fig

def styled_pie(names, values, title):
    fig = go.Figure(go.Pie(
        labels=names, values=values,
        hole=0.45,
        marker_colors=CHART_COLORS,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.1f}h (%{percent})<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        showlegend=False,
        **PLOTLY_LAYOUT
    )
    return fig

def styled_line(df, x, y, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=2.5, shape='spline'),
        marker=dict(size=7, color=COLORS['accent2'], line=dict(color='white', width=1.5)),
        fill='tozeroy',
        fillcolor='rgba(0,109,119,0.07)',
        hovertemplate='<b>Semana %{x}</b><br>%{y:.1f}h<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.04)', zeroline=False),
        xaxis=dict(showgrid=False),
        **PLOTLY_LAYOUT
    )
    return fig

def styled_heatmap(df_logs):
    """Heatmap de horas por dia (calendário)"""
    if df_logs.empty:
        return None
    df_logs = df_logs.copy()
    df_logs['log_date'] = pd.to_datetime(df_logs['log_date'])
    daily = df_logs.groupby('log_date')['hours'].sum().reset_index()
    daily['weekday'] = daily['log_date'].dt.weekday
    daily['week'] = daily['log_date'].dt.isocalendar().week.astype(int)
    pivot = daily.pivot_table(index='weekday', columns='week', values='hours', fill_value=0)
    dias_labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"S{w}" for w in pivot.columns],
        y=[dias_labels[i] for i in pivot.index],
        colorscale=[[0, '#EDF6F9'], [0.3, '#83C5BE'], [1, '#006D77']],
        showscale=True,
        hovertemplate='<b>%{y}</b> semana %{x}<br>%{z:.1f}h<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text="Heatmap de Estudos", font=dict(size=14)),
        **PLOTLY_LAYOUT
    )
    return fig

# ----------------------------- INTERFACE PRINCIPAL -----------------------------
def main():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0 16px 0; display:flex; align-items:center; gap:10px;">
            <span style="font-size:2.2rem;">🩺</span>
            <div>
                <div style="font-size:1.3rem; font-weight:700; color:white; letter-spacing:-0.02em;">MedStudy</div>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Organizador Inteligente</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        menu = st.radio(
            "Navegação",
            ["🏠 Dashboard", "📅 Rotina Semanal", "📆 Cronograma", "📝 Registrar Estudo",
             "🧠 Sugestão IA", "📊 Histórico & Análises", "🎯 Metas", "📌 Notas Rápidas", "⚙️ Assuntos"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        xp = int(get_user_stat('xp', 0))
        level = int(get_user_stat('level', 1))
        streak = int(get_user_stat('streak', 0))
        xp_next = level * 100
        progress = min(xp / xp_next, 1.0) if xp_next > 0 else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nível", f"⭐ {level}")
        with col2:
            st.metric("Streak", f"🔥 {streak}d")
        st.progress(progress, text=f"{xp}/{xp_next} XP")

        today_str = date.today().isoformat()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(hours) FROM study_logs WHERE log_date=?", (today_str,))
        studied_today = c.fetchone()[0] or 0
        conn.close()

        if studied_today > 0:
            st.success(f"✅ Hoje: {studied_today:.1f}h estudadas")
        else:
            st.warning("📚 Nenhum estudo hoje")

        st.markdown("---")
        st.caption("🔒 Dados armazenados localmente.")

    selected = menu

    # ======================== DASHBOARD ========================
    if selected == "🏠 Dashboard":
        st.markdown(f"# 🏠 Dashboard")
        day_type, suggestion, hours_rec, study_type_rec = get_plan_for_today()
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        hoje = dias[date.today().weekday()]

        badge_class = {"plantao": "badge-plantao", "faculdade": "badge-faculdade", "livre": "badge-livre"}.get(day_type, "badge-faculdade")
        st.markdown(f"""
        <div class="med-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:1.1rem; font-weight:600; color:{COLORS['text_dark']};">{hoje}</span>
                    <span class="med-badge {badge_class}">{day_type.upper()}</span>
                </div>
                <div style="color:{COLORS['text_mid']}; font-size:0.9rem;">{date.today().strftime('%d/%m/%Y')}</div>
            </div>
            <div style="margin-top:10px; color:{COLORS['text_mid']};">{suggestion}</div>
            <div style="margin-top:8px;">
                <span style="color:{COLORS['primary']}; font-weight:600;">⏱ {hours_rec}h recomendadas</span>
                &nbsp;·&nbsp;
                <span style="color:{COLORS['accent2']}; font-weight:500;">📚 {study_type_rec.capitalize()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas principais
        start = date.today() - timedelta(days=6)
        df_week = get_study_logs(start, date.today())
        df_all = get_study_logs()

        total_h_week = df_week['hours'].sum() if not df_week.empty else 0
        total_h_all = df_all['hours'].sum() if not df_all.empty else 0
        total_xp = df_all['xp_earned'].sum() if not df_all.empty else 0
        dias_estudados = df_week['log_date'].nunique() if not df_week.empty else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Horas esta semana", f"{total_h_week:.1f}h")
        col2.metric("Dias estudados (7d)", f"{dias_estudados}/7")
        col3.metric("Total acumulado", f"{total_h_all:.1f}h")
        col4.metric("XP total", f"{int(total_xp)}")

        st.markdown("---")

        col_a, col_b = st.columns([1.3, 0.7])
        with col_a:
            if not df_week.empty:
                df_week['log_date'] = pd.to_datetime(df_week['log_date'])
                daily = df_week.groupby('log_date')['hours'].sum().reset_index()
                daily['log_date'] = daily['log_date'].dt.strftime('%a %d/%m')
                fig = styled_bar(daily, 'log_date', 'hours', "Horas por dia — últimos 7 dias", COLORS['primary'])
                fig.update_layout(height=260)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados na última semana.")

        with col_b:
            if not df_all.empty:
                subject_hours = df_all.groupby('subject')['hours'].sum().reset_index()
                fig = styled_pie(subject_hours['subject'], subject_hours['hours'], "Por matéria")
                fig.update_layout(height=260)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Registre estudos para ver estatísticas.")

        # Heatmap
        if not df_all.empty:
            hm = styled_heatmap(df_all)
            if hm:
                hm.update_layout(height=220)
                st.plotly_chart(hm, use_container_width=True)

        # Mensagem motivacional
        if streak >= 7:
            st.success("🌟 Sequência incrível de 7+ dias! Você é imparável.")
        elif streak >= 3:
            st.info("💪 Boa sequência! Continue assim, cada dia conta.")
        elif streak >= 1:
            st.info("🌱 Ótimo começo! Mantenha o ritmo amanhã.")
        else:
            st.warning("🔥 Que tal registrar seu estudo de hoje?")

        if st.button("⚡ Registrar estudo rápido", use_container_width=True):
            st.session_state['quick_hours'] = hours_rec
            st.session_state['quick_type'] = study_type_rec
            st.session_state['_nav'] = "📝 Registrar Estudo"
            st.rerun()

    # ======================== ROTINA SEMANAL ========================
    elif selected == "📅 Rotina Semanal":
        st.markdown("# 📅 Rotina Semanal")
        st.markdown("Defina o tipo de cada dia para o planejamento automático.")
        routine = load_weekly_routine()
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        tipos = {"plantao": "🏥 Plantão", "faculdade": "🎓 Faculdade", "livre": "📖 Livre"}
        novo_routine = {}
        cols = st.columns(7)
        for i, dia in enumerate(dias):
            with cols[i]:
                st.markdown(f"<div style='text-align:center; font-weight:600; color:{COLORS['primary']};'>{dia[:3]}</div>", unsafe_allow_html=True)
                idx = routine.get(i, 'faculdade')
                opcoes = list(tipos.values())
                chaves = list(tipos.keys())
                default_idx = chaves.index(idx) if idx in chaves else 1
                escolha_label = st.selectbox("", opcoes, index=default_idx, key=f"dia_{i}", label_visibility="collapsed")
                novo_routine[i] = chaves[opcoes.index(escolha_label)]
        if st.button("💾 Salvar rotina", type="primary"):
            save_weekly_routine(novo_routine)
            st.success("Rotina semanal atualizada!")
            st.balloons()

    # ======================== CRONOGRAMA ========================
    elif selected == "📆 Cronograma":
        st.markdown("# 📆 Cronograma Semanal")
        tab1, tab2 = st.tabs(["📋 Visualizar / Editar", "🤖 Gerar com IA"])

        with tab1:
            if has_schedule():
                df_schedule = load_weekly_schedule()
                dias_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
                df_schedule['Dia'] = df_schedule['day_of_week'].map(dias_map)
                df_display = df_schedule[['Dia', 'time_slot', 'subject', 'activity_type', 'notes']].copy()
                df_display.columns = ['Dia', 'Horário', 'Matéria', 'Atividade', 'Observações']
                st.dataframe(df_display, use_container_width=True, hide_index=True)

                with st.expander("✏️ Editar cronograma manualmente"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_day = st.selectbox("Dia", list(dias_map.values()), key="edit_day")
                        edit_time = st.text_input("Horário (ex: 14:00-16:00)", key="edit_time")
                        edit_subject = st.selectbox("Matéria", get_subjects()['name'].tolist(), key="edit_subject")
                    with col2:
                        edit_activity = st.selectbox("Tipo de atividade", ["Teoria", "Revisão", "Questões", "Resumo", "Flashcards"], key="edit_activity")
                        edit_notes = st.text_input("Observações", key="edit_notes")
                    if st.button("➕ Adicionar bloco"):
                        day_num = list(dias_map.keys())[list(dias_map.values()).index(edit_day)]
                        new_row = pd.DataFrame([[day_num, edit_time, edit_subject, edit_activity, edit_notes]],
                                               columns=['day_of_week', 'time_slot', 'subject', 'activity_type', 'notes'])
                        df_updated = pd.concat([df_schedule[['day_of_week','time_slot','subject','activity_type','notes']], new_row], ignore_index=True)
                        save_weekly_schedule(df_updated)
                        st.success("Bloco adicionado!")
                        st.rerun()
                    st.markdown("---")
                    delete_index = st.selectbox("Selecione o bloco para remover", df_display.index,
                        format_func=lambda x: f"{df_display.iloc[x]['Dia']} {df_display.iloc[x]['Horário']} - {df_display.iloc[x]['Matéria']}")
                    if st.button("🗑️ Remover selecionado"):
                        df_schedule_raw = df_schedule[['day_of_week','time_slot','subject','activity_type','notes']].drop(delete_index).reset_index(drop=True)
                        save_weekly_schedule(df_schedule_raw)
                        st.success("Bloco removido!")
                        st.rerun()
            else:
                st.info("Nenhum cronograma salvo. Use a aba 'Gerar com IA' ou crie manualmente.")
                if st.button("Criar cronograma vazio"):
                    save_weekly_schedule(pd.DataFrame(columns=['day_of_week', 'time_slot', 'subject', 'activity_type', 'notes']))
                    st.rerun()

        with tab2:
            st.subheader("Gerar cronograma com IA")
            user_suggestion = st.text_area("Preferências adicionais (opcional)",
                                           placeholder="Ex: Foco em Farmacologia e Patologia; prefiro estudar à noite...")
            if st.button("✨ Gerar cronograma", type="primary"):
                with st.spinner("A IA está criando seu cronograma personalizado..."):
                    routine = load_weekly_routine()
                    subjects_df = get_subjects()
                    subjects_list = subjects_df['name'].tolist()
                    historical = build_historical_context()
                    schedule_data = generate_ai_weekly_schedule(user_suggestion, routine, subjects_list, historical)
                    if schedule_data:
                        df_new = pd.DataFrame(schedule_data)
                        df_new = df_new.rename(columns={"day": "day_of_week", "time": "time_slot", "activity": "activity_type", "notes": "notes"})
                        st.session_state['ai_schedule'] = df_new
                        st.success("Cronograma gerado! Revise e salve se desejar.")
                    else:
                        st.error("Não foi possível gerar o cronograma. Tente novamente.")

            if 'ai_schedule' in st.session_state:
                st.markdown("### Sugestão da IA")
                df_ai = st.session_state['ai_schedule']
                dias_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
                df_ai_show = df_ai.copy()
                df_ai_show['Dia'] = df_ai_show['day_of_week'].map(dias_map)
                st.dataframe(df_ai_show[['Dia', 'time_slot', 'subject', 'activity_type', 'notes']], use_container_width=True, hide_index=True)
                col_save, col_discard = st.columns(2)
                with col_save:
                    if st.button("💾 Salvar cronograma", type="primary"):
                        save_weekly_schedule(df_ai)
                        st.success("Cronograma salvo!")
                        del st.session_state['ai_schedule']
                        st.rerun()
                with col_discard:
                    if st.button("🗑️ Descartar"):
                        del st.session_state['ai_schedule']
                        st.rerun()

    # ======================== REGISTRAR ESTUDO ========================
    elif selected == "📝 Registrar Estudo":
        st.markdown("# 📝 Registrar Sessão de Estudo")
        col1, col2 = st.columns(2)
        with col1:
            data_estudo = st.date_input("Data", value=date.today())
            horas = st.number_input("Horas estudadas", min_value=0.0, max_value=24.0, step=0.5,
                                    value=st.session_state.get('quick_hours', 0.0))
            tipo = st.selectbox("Tipo de estudo", ["teoria", "revisao", "questoes"],
                                format_func=lambda x: {"teoria": "📖 Teoria", "revisao": "🔄 Revisão", "questoes": "✏️ Questões"}[x],
                                index=["teoria", "revisao", "questoes"].index(st.session_state.get('quick_type', 'teoria')))
        with col2:
            subjects_df = get_subjects()
            subject_list = subjects_df['name'].tolist() if not subjects_df.empty else ["Anatomia", "Fisiologia"]
            assunto = st.selectbox("Matéria / Assunto", subject_list)
            novo_assunto = st.text_input("Ou adicione novo assunto", placeholder="Ex: Neurologia")
            if novo_assunto and st.button("➕ Adicionar assunto"):
                add_subject(novo_assunto)
                st.success(f"'{novo_assunto}' adicionado!")
                st.rerun()
            observacoes = st.text_area("Observações", placeholder="Ex: Páginas 100-150, 20 questões...")

        xp_preview = int(horas * 10) + {'teoria': 2, 'revisao': 3, 'questoes': 5}.get(tipo, 0)
        st.info(f"💡 Você ganhará **{xp_preview} XP** com essa sessão.")

        if st.button("✅ Registrar sessão", type="primary"):
            if horas > 0:
                final_subject = novo_assunto if novo_assunto else assunto
                if novo_assunto:
                    add_subject(novo_assunto)
                xp_ganho = add_study_log(data_estudo.isoformat(), horas, tipo, final_subject, observacoes)
                st.success(f"Sessão registrada! Você ganhou **{xp_ganho} XP** 🎉")
                st.session_state.pop('quick_hours', None)
                st.session_state.pop('quick_type', None)
                st.rerun()
            else:
                st.warning("Informe pelo menos 0.5 horas.")

    # ======================== SUGESTÃO IA ========================
    elif selected == "🧠 Sugestão IA":
        st.markdown("# 🧠 Sugestão Inteligente de Estudo")
        st.markdown("A IA analisa seu histórico e monta um plano personalizado para **hoje**.")

        col1, col2, col3 = st.columns(3)
        with col1:
            tipo_dia = st.selectbox("Tipo de dia", ["plantao", "faculdade", "livre"],
                                    format_func=lambda x: {"plantao":"🏥 Plantão","faculdade":"🎓 Faculdade","livre":"📖 Livre"}[x])
        with col2:
            horas_disp = st.slider("Horas disponíveis", 0.5, 8.0, 2.0, step=0.5)
        with col3:
            energia = st.selectbox("Nível de energia", ["cansada", "normal", "disposta"],
                                   format_func=lambda x: {"cansada":"😴 Cansada","normal":"😊 Normal","disposta":"⚡ Disposta"}[x])

        subjects_df = get_subjects()
        subject_options = subjects_df['name'].tolist() if not subjects_df.empty else ["Geral"]
        assunto_foco = st.selectbox("Foco em qual matéria? (opcional)", ["(Nenhum)"] + subject_options)
        if assunto_foco == "(Nenhum)":
            assunto_foco = ""

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⏱️ Tenho pouco tempo"):
                horas_disp = 1.0
                energia = "cansada"
                st.info("Plano rápido: 1 hora, energia baixa.")
        with col_btn2:
            gerar = st.button("✨ Gerar plano com IA", type="primary")

        if gerar:
            with st.spinner("A IA está criando seu plano..."):
                contexto = build_historical_context()
                sugestao = generate_ai_suggestion(tipo_dia, horas_disp, energia, assunto_foco, contexto)
                st.markdown("### Seu plano de estudo personalizado:")
                st.markdown(f"""
                <div class="med-card">
                    {sugestao.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

        # Análise completa de desempenho
        st.markdown("---")
        st.subheader("📈 Análise de Desempenho pela IA")
        if st.button("🔍 Analisar meu desempenho geral"):
            with st.spinner("Analisando seus dados..."):
                contexto = build_historical_context()
                goals_df = get_goals()
                df_logs = get_study_logs()
                analise = generate_ai_analysis(contexto, goals_df, df_logs)
                st.markdown(f"""
                <div class="med-card">
                    {analise.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

    # ======================== HISTÓRICO & ANÁLISES ========================
    elif selected == "📊 Histórico & Análises":
        st.markdown("# 📊 Histórico & Análises")

        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            start_filter = st.date_input("De", value=date.today() - timedelta(days=30))
        with col_f2:
            end_filter = st.date_input("Até", value=date.today())

        df = get_study_logs(start_filter, end_filter)

        if not df.empty:
            df['log_date'] = pd.to_datetime(df['log_date']).dt.date
            df = df.sort_values('log_date', ascending=False)

            # Métricas do período
            col1, col2, col3 = st.columns(3)
            col1.metric("Horas no período", f"{df['hours'].sum():.1f}h")
            col2.metric("Sessões registradas", len(df))
            col3.metric("XP no período", int(df['xp_earned'].sum()))

            # Tabela
            with st.expander("📋 Ver tabela completa"):
                st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                # Barras por tipo
                type_hours = df.groupby('study_type')['hours'].sum().reset_index()
                type_map = {'teoria': 'Teoria', 'revisao': 'Revisão', 'questoes': 'Questões'}
                type_hours['study_type'] = type_hours['study_type'].map(type_map).fillna(type_hours['study_type'])
                fig = styled_bar(type_hours, 'study_type', 'hours', "Horas por tipo de estudo",
                                 color=[COLORS['primary'], COLORS['secondary'], COLORS['accent']])
                fig.update_layout(height=280)
                st.plotly_chart(fig, use_container_width=True)

            with col_g2:
                # Pizza por matéria
                subj_hours = df.groupby('subject')['hours'].sum().reset_index().sort_values('hours', ascending=False)
                fig = styled_pie(subj_hours['subject'], subj_hours['hours'], "Distribuição por matéria")
                fig.update_layout(height=280)
                st.plotly_chart(fig, use_container_width=True)

            # Linha de horas por semana
            df_line = df.copy()
            df_line['log_date'] = pd.to_datetime(df_line['log_date'])
            df_line['week'] = df_line['log_date'].dt.isocalendar().week.astype(int)
            weekly_hours = df_line.groupby('week')['hours'].sum().reset_index()
            fig = styled_line(weekly_hours, 'week', 'hours', "Evolução semanal de horas")
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

            # Heatmap
            hm = styled_heatmap(df_line)
            if hm:
                hm.update_layout(height=230)
                st.plotly_chart(hm, use_container_width=True)

            # Top matérias
            st.subheader("🏆 Ranking de matérias")
            subj_rank = df.groupby('subject').agg(
                horas=('hours', 'sum'),
                sessoes=('hours', 'count'),
                xp=('xp_earned', 'sum')
            ).sort_values('horas', ascending=False).reset_index()
            subj_rank.columns = ['Matéria', 'Horas', 'Sessões', 'XP']
            st.dataframe(subj_rank, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro no período selecionado.")

    # ======================== METAS ========================
    elif selected == "🎯 Metas":
        st.markdown("# 🎯 Metas de Estudo")
        st.markdown("Defina metas semanais e mensais por matéria para acompanhar seu progresso.")

        subjects_df = get_subjects()
        goals_df = get_goals()

        with st.form("add_goal_form"):
            st.subheader("Nova meta")
            col1, col2, col3 = st.columns(3)
            with col1:
                goal_subject = st.selectbox("Matéria", subjects_df['name'].tolist())
            with col2:
                goal_weekly = st.number_input("Horas/semana", min_value=0.0, max_value=40.0, step=0.5, value=2.0)
            with col3:
                goal_monthly = st.number_input("Horas/mês", min_value=0.0, max_value=200.0, step=1.0, value=8.0)
            if st.form_submit_button("💾 Salvar meta", type="primary"):
                save_goal(goal_subject, goal_weekly, goal_monthly)
                st.success(f"Meta salva para {goal_subject}!")
                st.rerun()

        if not goals_df.empty:
            st.markdown("---")
            st.subheader("Progresso das metas")
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            df_week_logs = get_study_logs(week_start, today)
            df_month_logs = get_study_logs(month_start, today)

            for _, row in goals_df.iterrows():
                subj = row['subject']
                wh = float(row['weekly_hours'])
                mh = float(row['monthly_hours'])

                actual_w = df_week_logs[df_week_logs['subject'] == subj]['hours'].sum() if not df_week_logs.empty else 0
                actual_m = df_month_logs[df_month_logs['subject'] == subj]['hours'].sum() if not df_month_logs.empty else 0

                prog_w = min(actual_w / wh, 1.0) if wh > 0 else 0
                prog_m = min(actual_m / mh, 1.0) if mh > 0 else 0

                st.markdown(f"""
                <div class="med-card">
                    <div style="font-weight:600; color:{COLORS['primary']}; margin-bottom:8px;">{subj}</div>
                    <div style="font-size:0.85rem; color:{COLORS['text_mid']};">Semana: {actual_w:.1f}h / {wh}h</div>
                """, unsafe_allow_html=True)
                st.progress(prog_w, text=f"Semana: {prog_w*100:.0f}%")
                st.markdown(f'<div style="font-size:0.85rem; color:{COLORS["text_mid"]};">Mês: {actual_m:.1f}h / {mh}h</div>', unsafe_allow_html=True)
                st.progress(prog_m, text=f"Mês: {prog_m*100:.0f}%")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhuma meta definida ainda.")

    # ======================== NOTAS RÁPIDAS ========================
    elif selected == "📌 Notas Rápidas":
        st.markdown("# 📌 Notas Rápidas")
        st.markdown("Anote dúvidas, insights ou pontos importantes durante o estudo.")

        subjects_df = get_subjects()
        col1, col2 = st.columns([2, 1])
        with col1:
            note_content = st.text_area("Nota", placeholder="Escreva aqui sua anotação, dúvida ou insight...", height=120)
        with col2:
            note_subject = st.selectbox("Matéria", ["Geral"] + subjects_df['name'].tolist())
            note_type = st.selectbox("Tipo", ["💡 Insight", "❓ Dúvida", "📋 Resumo", "⚠️ Revisar", "✅ Revisado"])

        if st.button("📌 Salvar nota", type="primary"):
            if note_content.strip():
                add_quick_note(note_subject, note_content, note_type)
                st.success("Nota salva!")
                st.rerun()
            else:
                st.warning("Digite algum conteúdo para a nota.")

        st.markdown("---")
        notes_df = get_quick_notes()
        if not notes_df.empty:
            filter_subj = st.selectbox("Filtrar por matéria", ["Todas"] + notes_df['subject'].unique().tolist())
            filter_type = st.selectbox("Filtrar por tipo", ["Todos"] + notes_df['note_type'].unique().tolist())
            filtered = notes_df.copy()
            if filter_subj != "Todas":
                filtered = filtered[filtered['subject'] == filter_subj]
            if filter_type != "Todos":
                filtered = filtered[filtered['note_type'] == filter_type]

            for _, note in filtered.iterrows():
                col_n, col_del = st.columns([10, 1])
                with col_n:
                    st.markdown(f"""
                    <div class="med-card" style="padding:14px 18px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="font-weight:600; color:{COLORS['primary']};">{note['subject']}</span>
                            <span style="font-size:0.78rem; color:{COLORS['text_mid']};">{note['created_at'][:16]}</span>
                        </div>
                        <span style="font-size:0.8rem; color:{COLORS['text_mid']};">{note['note_type']}</span>
                        <div style="margin-top:6px; color:{COLORS['text_dark']};">{note['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_note_{note['id']}"):
                        delete_quick_note(note['id'])
                        st.rerun()
        else:
            st.info("Nenhuma nota registrada ainda.")

    # ======================== ASSUNTOS ========================
    elif selected == "⚙️ Assuntos":
        st.markdown("# ⚙️ Gerenciar Assuntos")
        subjects_df = get_subjects()
        st.dataframe(subjects_df, use_container_width=True, hide_index=True)
        with st.form("add_subject_form"):
            st.subheader("Adicionar nova matéria")
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da matéria")
            with col2:
                cor = st.color_picker("Cor", COLORS['primary'])
            submitted = st.form_submit_button("➕ Adicionar", type="primary")
            if submitted and nome:
                add_subject(nome, cor)
                st.success(f"'{nome}' adicionado!")
                st.rerun()

if __name__ == "__main__":
    main()