import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURAZIONE LOGIN ---
UTENTI_VALIDI = {
    "AZIENDA_001": "pass123",
    "AZIENDA_002": "sicurezza456"
}

st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

# --- LOGICA DI LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Accesso Area Riservata")
    user = st.text_input("ID Azienda")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if UTENTI_VALIDI.get(user) == password:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Credenziali errate!")
else:
    # --- AREA RISERVATA ---
    azienda = st.session_state.user
    st.title(f"📊 Dashboard Strategica - {azienda}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Connessione DB
    conn = sqlite3.connect("azienda.db", check_same_thread=False)
    query = f"SELECT nome, rischio, data_inserimento FROM asset WHERE company_id = '{azienda}'"
    df = pd.read_sql_query(query, conn)

    if not df.empty:
        st.table(df)
        
        # --- FUNZIONE ESPORTAZIONE REPORT ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Report in CSV",
            data=csv,
            file_name=f'report_{azienda}_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        
        # --- GRAFICO ---
        st.bar_chart(df.set_index('nome')['rischio'])
    else:
        st.info("Nessun dato storico per questa azienda.")