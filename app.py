# app.py
"""
📚 MedStudy Organizer – Rotina Inteligente para Estudante de Medicina
Design premium, claro e funcional. Inclui cronograma semanal inteligente.
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
from dotenv import load_dotenv
load_dotenv()
# ----------------------------- CONFIGURAÇÃO DE PÁGINA E ESTILO -----------------------------
st.set_page_config(
    page_title="MedStudy Organizer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para visual premium e claro
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    .stButton > button {
        border-radius: 40px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        background-color: #3b82f6;
        color: white;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stProgress > div > div {
        background-color: #3b82f6 !important;
    }
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .schedule-table th {
        background-color: #eef2ff;
        color: #1e293b;
        padding: 12px;
        text-align: center;
        font-weight: 600;
    }
    .schedule-table td {
        padding: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------- BANCO DE DADOS -----------------------------
DB_PATH = "medstudy.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Rotina semanal
    c.execute('''
        CREATE TABLE IF NOT EXISTS weekly_routine (
            day_of_week INTEGER PRIMARY KEY,
            type TEXT CHECK(type IN ('plantao', 'faculdade', 'livre'))
        )
    ''')
    # Registros de estudo
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
    # Estatísticas do usuário
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Assuntos
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            name TEXT PRIMARY KEY,
            color TEXT,
            added_date DATE
        )
    ''')
    # NOVO: Cronograma semanal salvo
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
    # Inserir assuntos padrão
    default_subjects = [
        ('Anatomia', '#ef4444'), ('Fisiologia', '#3b82f6'), ('Farmacologia', '#10b981'),
        ('Patologia', '#f59e0b'), ('Semiologia', '#8b5cf6'), ('Clínica Médica', '#ec4899'),
        ('Pediatria', '#14b8a6'), ('Ginecologia', '#d946ef'), ('Cirurgia', '#f97316')
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

# Rotina semanal
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

# Estatísticas do usuário
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

# Streak
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

# Registro de estudo
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

def add_subject(name, color="#3b82f6"):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO subjects (name, color, added_date) VALUES (?, ?, ?)",
                  (name, color, date.today().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# ----------------------------- CRONOGRAMA SEMANAL -----------------------------
def save_weekly_schedule(schedule_df):
    """Salva o DataFrame do cronograma no banco (substitui existente)."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM weekly_schedule")  # Limpa anterior
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

# ----------------------------- FUNÇÕES DE IA (OpenAI) -----------------------------
def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Chave da API OpenAI não encontrada. Configure a variável de ambiente OPENAI_API_KEY.")
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
    # Preparar resumo da rotina
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

Gere um cronograma em formato de tabela, com os seguintes campos para cada dia da semana (0=Segunda a 6=Domingo):
- Horário (ex: "08:00-10:00")
- Matéria/Assunto
- Tipo de atividade (Teoria, Revisão, Questões, Resumo, etc.)
- Observações (opcional)

Seja realista com os horários, considerando que em dias de plantão o estudo deve ser mais leve e curto, em dias de faculdade moderado, e em dias livres mais intenso.
Retorne APENAS um JSON válido com a seguinte estrutura:
{{
  "schedule": [
    {{"day": 0, "time": "08:00-10:00", "subject": "Anatomia", "activity": "Teoria", "notes": ""}},
    ...
  ]
}}
Certifique-se de que o JSON seja válido e contenha entradas para todos os dias com atividades relevantes.
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
        # Tentar extrair JSON da resposta (pode vir com marcação ```json)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        schedule_data = json.loads(content)
        return schedule_data.get("schedule", [])
    except Exception as e:
        st.error(f"Erro ao gerar cronograma: {e}")
        return None

def build_historical_context():
    today = date.today()
    week_ago = today - timedelta(days=7)
    df = get_study_logs(week_ago, today)
    if df.empty:
        return "Nenhum estudo registrado na última semana."
    total_hours = df['hours'].sum()
    days_studied = df['log_date'].nunique()
    avg_hours = total_hours / 7
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
- Horas totais: {total_hours:.1f}h
- Dias estudados: {days_studied}/7
- Média diária: {avg_hours:.1f}h
- {consistency}.
- Matéria mais estudada: {most}
- Matéria menos estudada: {least}
"""
    return context

# ----------------------------- PLANEJAMENTO AUTOMÁTICO -----------------------------
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

# ----------------------------- INTERFACE PRINCIPAL -----------------------------
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/medical-doctor.png", width=80)
        st.title("🩺 MedStudy")
        st.markdown("---")
        menu = st.radio(
            "Navegação",
            ["🏠 Dashboard", "📅 Rotina Semanal", "📆 Cronograma Semanal", "📝 Registrar Estudo", "🧠 Sugestão IA", "📊 Histórico", "⚙️ Assuntos"],
            label_visibility="visible"
        )
        
        xp = int(get_user_stat('xp', 0))
        level = int(get_user_stat('level', 1))
        streak = int(get_user_stat('streak', 0))
        xp_next = level * 100
        progress = min(xp / xp_next, 1.0) if xp_next > 0 else 0
        
        st.markdown("### 🎮 Seu Progresso")
        st.write(f"**Nível {level}**")
        st.progress(progress, text=f"{xp}/{xp_next} XP")
        st.metric("🔥 Streak", f"{streak} dias")
        
        today_str = date.today().isoformat()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(hours) FROM study_logs WHERE log_date=?", (today_str,))
        studied_today = c.fetchone()[0] or 0
        conn.close()
        if studied_today > 0:
            st.success(f"✅ Hoje: {studied_today:.1f}h")
        else:
            st.warning("📌 Nenhum estudo hoje")
        st.markdown("---")
        st.caption("🔒 Seus dados são privados e armazenados localmente.")
    
    # ----------------------------- DASHBOARD -----------------------------
    if menu == "🏠 Dashboard":
        st.title("🏠 Dashboard")
        col1, col2 = st.columns([1.2, 0.8], gap="large")
        with col1:
            st.subheader("📌 Planejamento do dia")
            day_type, suggestion, hours_rec, study_type_rec = get_plan_for_today()
            dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            hoje = dias[date.today().weekday()]
            st.metric("Hoje é", f"{hoje} ({day_type.capitalize()})")
            st.info(suggestion)
            st.write(f"⏱️ Horas recomendadas: **{hours_rec} horas**")
            st.write(f"📚 Tipo sugerido: **{study_type_rec.capitalize()}**")
            if st.button("✨ Registrar estudo rápido"):
                st.session_state['quick_hours'] = hours_rec
                st.session_state['quick_type'] = study_type_rec
                st.rerun()
        with col2:
            st.subheader("📈 Últimos 7 dias")
            start = date.today() - timedelta(days=6)
            df = get_study_logs(start, date.today())
            if not df.empty:
                df['log_date'] = pd.to_datetime(df['log_date'])
                daily = df.groupby('log_date')['hours'].sum().reset_index()
                fig = px.bar(daily, x='log_date', y='hours', color_discrete_sequence=['#3b82f6'])
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados na última semana.")
        
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📊 Distribuição por matéria")
            df_all = get_study_logs()
            if not df_all.empty:
                subject_hours = df_all.groupby('subject')['hours'].sum().reset_index().sort_values('hours', ascending=False)
                fig = px.pie(subject_hours, values='hours', names='subject', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Registre estudos para ver estatísticas.")
        with col4:
            st.subheader("💬 Mensagem do dia")
            if streak >= 5:
                st.success("🌟 Você está voando! Continue com essa constância incrível.")
            elif streak >= 2:
                st.info("💪 Ótimo trabalho! Cada dia conta na sua jornada.")
            else:
                st.warning("🌱 Comece hoje! Pequenos passos levam a grandes conquistas.")
    
    # ----------------------------- ROTINA SEMANAL -----------------------------
    elif menu == "📅 Rotina Semanal":
        st.title("📅 Configurar Rotina Semanal")
        st.markdown("Defina o tipo de cada dia para o planejamento automático.")
        routine = load_weekly_routine()
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        tipos = {"plantao": "🏥 Plantão", "faculdade": "📚 Faculdade", "livre": "🌟 Livre"}
        novo_routine = {}
        cols = st.columns(7)
        for i, dia in enumerate(dias):
            with cols[i]:
                st.markdown(f"**{dia}**")
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
    
    # ----------------------------- CRONOGRAMA SEMANAL (NOVO) -----------------------------
    elif menu == "📆 Cronograma Semanal":
        st.title("📆 Cronograma de Estudos Semanal")
        st.markdown("Visualize, crie ou edite seu cronograma personalizado.")
        
        if not has_schedule():
            st.warning("📌 Você ainda não tem um cronograma salvo. Use a opção abaixo para criar um.")
        else:
            st.success("✅ Cronograma salvo encontrado.")
        
        # Abas para visualizar/editar ou gerar com IA
        tab1, tab2 = st.tabs(["📋 Visualizar/Editar", "🤖 Gerar com IA"])
        
        with tab1:
            if has_schedule():
                df_schedule = load_weekly_schedule()
                # Converter para exibição amigável
                dias_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
                df_schedule['Dia'] = df_schedule['day_of_week'].map(dias_map)
                df_display = df_schedule[['Dia', 'time_slot', 'subject', 'activity_type', 'notes']]
                df_display.columns = ['Dia', 'Horário', 'Matéria', 'Atividade', 'Observações']
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Opção de editar manualmente (formulário para adicionar/remover)
                with st.expander("✏️ Editar cronograma manualmente"):
                    st.markdown("Adicione ou remova blocos de estudo.")
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
                        df_updated = pd.concat([df_schedule, new_row], ignore_index=True)
                        save_weekly_schedule(df_updated)
                        st.success("Bloco adicionado!")
                        st.rerun()
                    
                    st.markdown("---")
                    st.markdown("**Remover bloco**")
                    delete_index = st.selectbox("Selecione o bloco para remover", df_display.index, format_func=lambda x: f"{df_display.iloc[x]['Dia']} {df_display.iloc[x]['Horário']} - {df_display.iloc[x]['Matéria']}")
                    if st.button("🗑️ Remover selecionado"):
                        df_schedule = df_schedule.drop(delete_index).reset_index(drop=True)
                        save_weekly_schedule(df_schedule)
                        st.success("Bloco removido!")
                        st.rerun()
            else:
                st.info("Nenhum cronograma salvo. Vá para a aba 'Gerar com IA' ou crie manualmente.")
                # Opção de criar um vazio manualmente
                if st.button("📝 Criar cronograma vazio para editar"):
                    empty_df = pd.DataFrame(columns=['day_of_week', 'time_slot', 'subject', 'activity_type', 'notes'])
                    save_weekly_schedule(empty_df)
                    st.rerun()
        
        with tab2:
            st.subheader("🤖 Gerar cronograma sugerido pela IA")
            st.markdown("A IA criará um cronograma semanal baseado na sua rotina, histórico e preferências.")
            user_suggestion = st.text_area("Alguma preferência ou sugestão extra? (opcional)", 
                                           placeholder="Ex: Quero focar em Farmacologia e Patologia; prefiro estudar à noite...")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ Gerar sugestão de cronograma", type="primary"):
                    with st.spinner("A IA está preparando seu cronograma personalizado..."):
                        routine = load_weekly_routine()
                        subjects_df = get_subjects()
                        subjects_list = subjects_df['name'].tolist()
                        historical = build_historical_context()
                        schedule_data = generate_ai_weekly_schedule(user_suggestion, routine, subjects_list, historical)
                        if schedule_data:
                            # Converter para DataFrame
                            df_new = pd.DataFrame(schedule_data)
                            df_new = df_new.rename(columns={"day": "day_of_week", "time": "time_slot", "activity": "activity_type", "notes": "notes"})
                            st.session_state['ai_schedule'] = df_new
                            st.success("Cronograma gerado! Revise abaixo e salve se desejar.")
                        else:
                            st.error("Não foi possível gerar o cronograma. Tente novamente.")
            
            if 'ai_schedule' in st.session_state:
                st.markdown("### 📋 Sugestão da IA (pré-visualização)")
                df_ai = st.session_state['ai_schedule']
                dias_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
                df_ai['Dia'] = df_ai['day_of_week'].map(dias_map)
                st.dataframe(df_ai[['Dia', 'time_slot', 'subject', 'activity_type', 'notes']], use_container_width=True, hide_index=True)
                
                col_save, col_discard = st.columns(2)
                with col_save:
                    if st.button("💾 Salvar este cronograma", type="primary"):
                        save_weekly_schedule(df_ai)
                        st.success("Cronograma salvo com sucesso!")
                        del st.session_state['ai_schedule']
                        st.rerun()
                with col_discard:
                    if st.button("🗑️ Descartar"):
                        del st.session_state['ai_schedule']
                        st.rerun()
    
    # ----------------------------- REGISTRAR ESTUDO -----------------------------
    elif menu == "📝 Registrar Estudo":
        st.title("📝 Registrar Sessão de Estudo")
        col1, col2 = st.columns(2)
        with col1:
            data_estudo = st.date_input("Data", value=date.today())
            horas = st.number_input("Horas estudadas", min_value=0.0, max_value=24.0, step=0.5,
                                    value=st.session_state.get('quick_hours', 0.0))
            tipo = st.selectbox("Tipo de estudo", ["teoria", "revisao", "questoes"],
                                index=["teoria", "revisao", "questoes"].index(
                                    st.session_state.get('quick_type', 'teoria')))
        with col2:
            subjects_df = get_subjects()
            subject_list = subjects_df['name'].tolist() if not subjects_df.empty else ["Anatomia", "Fisiologia"]
            assunto = st.selectbox("Matéria / Assunto", subject_list)
            novo_assunto = st.text_input("Ou adicione um novo assunto", placeholder="Ex: Neurologia")
            if novo_assunto and st.button("➕ Adicionar"):
                add_subject(novo_assunto)
                st.success(f"Assunto '{novo_assunto}' adicionado!")
                st.rerun()
            observacoes = st.text_area("Observações", placeholder="Ex: Páginas 100-150, 20 questões...")
        
        if st.button("✅ Registrar", type="primary"):
            if horas > 0:
                final_subject = novo_assunto if novo_assunto else assunto
                if novo_assunto:
                    add_subject(novo_assunto)
                xp_ganho = add_study_log(data_estudo.isoformat(), horas, tipo, final_subject, observacoes)
                st.success(f"Sessão registrada! Você ganhou **{xp_ganho} XP**.")
                st.session_state.pop('quick_hours', None)
                st.session_state.pop('quick_type', None)
                st.rerun()
            else:
                st.warning("Informe pelo menos 0.5 horas.")
    
    # ----------------------------- SUGESTÃO IA -----------------------------
    elif menu == "🧠 Sugestão IA":
        st.title("🧠 Sugestão Inteligente de Estudo")
        st.markdown("A IA analisa seu histórico e sugere um plano personalizado para **hoje**.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tipo_dia = st.selectbox("Tipo de dia", ["plantao", "faculdade", "livre"])
        with col2:
            horas_disp = st.slider("Horas disponíveis", 0.5, 8.0, 2.0, step=0.5)
        with col3:
            energia = st.selectbox("Nível de energia", ["cansada", "normal", "disposta"])
        
        subjects_df = get_subjects()
        subject_options = subjects_df['name'].tolist() if not subjects_df.empty else ["Geral"]
        assunto_foco = st.selectbox("Foco em qual matéria? (opcional)", ["(Nenhum)"] + subject_options)
        if assunto_foco == "(Nenhum)":
            assunto_foco = ""
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔥 Tenho pouco tempo hoje"):
                horas_disp = 1.0
                energia = "cansada"
                st.info("Plano rápido: 1 hora, energia cansada.")
        with col_btn2:
            gerar = st.button("✨ Gerar sugestão com IA", type="primary")
        
        if gerar:
            with st.spinner("Consultando a IA... 🤖"):
                contexto = build_historical_context()
                sugestao = generate_ai_suggestion(tipo_dia, horas_disp, energia, assunto_foco, contexto)
                st.markdown("### 📋 Seu plano de estudo personalizado:")
                st.success(sugestao)
    
    # ----------------------------- HISTÓRICO -----------------------------
    elif menu == "📊 Histórico":
        st.title("📊 Histórico de Estudos")
        df = get_study_logs()
        if not df.empty:
            df['log_date'] = pd.to_datetime(df['log_date']).dt.date
            df = df.sort_values('log_date', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("📉 Análises")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(df, names='study_type', title='Distribuição por tipo', color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                df['week'] = pd.to_datetime(df['log_date']).dt.isocalendar().week
                weekly_hours = df.groupby('week')['hours'].sum().reset_index()
                fig = px.line(weekly_hours, x='week', y='hours', markers=True, title='Horas por semana', color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig, use_container_width=True)
            
            total_horas = df['hours'].sum()
            total_xp = df['xp_earned'].sum()
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total de horas", f"{total_horas:.1f}h")
            col_m2.metric("Total de XP", total_xp)
        else:
            st.info("Nenhum registro ainda. Comece registrando seus estudos!")
    
    # ----------------------------- ASSUNTOS -----------------------------
    elif menu == "⚙️ Assuntos":
        st.title("⚙️ Gerenciar Assuntos")
        st.markdown("Adicione ou visualize matérias para organizar seus estudos.")
        subjects_df = get_subjects()
        st.dataframe(subjects_df, use_container_width=True, hide_index=True)
        with st.form("add_subject_form"):
            nome = st.text_input("Nome da matéria")
            cor = st.color_picker("Cor (opcional)", "#3b82f6")
            submitted = st.form_submit_button("Adicionar")
            if submitted and nome:
                add_subject(nome, cor)
                st.success(f"'{nome}' adicionado!")
                st.rerun()

if __name__ == "__main__":
    main()