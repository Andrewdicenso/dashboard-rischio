import streamlit as st
import sqlite3
import pandas as pd
import os

# --- CONFIGURAZIONE ---
UTENTI_VALIDI = {"AZIENDA_001": "pass123", "AZIENDA_002": "sicurezza456"}
st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

# --- LOGICA LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔒 Accesso Area Riservata")
    user = st.text_input("ID Azienda")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if UTENTI_VALIDI.get(user) == password:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else: st.error("Credenziali errate!")
else:
    azienda = st.session_state.user
    st.title(f"📊 Dashboard Strategica - {azienda}")
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    # --- UPLOAD INTELLIGENTE ---
    st.subheader("Carica Documenti")
    uploaded_file = st.file_uploader("Trascina qui i tuoi documenti (CSV, PNG, JPG, PDF)")
    
    if uploaded_file is not None:
        if not os.path.exists("uploads"): os.makedirs("uploads")
        file_path = os.path.join("uploads", f"{azienda}_{uploaded_file.name}")
        
        # Logica di smistamento
        if uploaded_file.name.endswith('.csv'):
            with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.success(f"Dati caricati: {uploaded_file.name}")
            # Qui potremmo aggiungere la logica per fondere i dati in futuro
        elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.info(f"Documento informativo archiviato: {uploaded_file.name}")
        else:
            st.warning(f"Formato non riconosciuto come documento necessario: {uploaded_file.name}")

    # --- VISUALIZZAZIONE DATI ---
    conn = sqlite3.connect("azienda.db", check_same_thread=False)
    query = f"SELECT nome, rischio, data_inserimento FROM asset WHERE company_id = '{azienda}'"
    df = pd.read_sql_query(query, conn)

    if not df.empty:
        st.table(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Report", data=csv, file_name=f'report_{azienda}.csv', mime='text/csv')
        st.bar_chart(df.set_index('nome')['rischio'])
    else: st.info("Nessun dato storico nel database.")