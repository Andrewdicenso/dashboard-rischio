import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
UTENTI_VALIDI = {"AZIENDA_001": "pass123", "AZIENDA_002": "sicurezza456"}
st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

# --- LOGICA LOGIN ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Accesso Area Riservata")
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
    azienda = st.session_state.user
    st.title(f"📊 Dashboard Strategica - {azienda}")
    if st.sidebar.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

    # --- UPLOAD DINAMICO ---
    st.subheader("Carica il tuo file dati (CSV)")
    uploaded_file = st.file_uploader("Trascina qui il tuo file fornitori/dati")
    
    user_folder = f"uploads/{azienda}"
    if not os.path.exists(user_folder): 
        os.makedirs(user_folder)

    if uploaded_file is not None:
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f: 
            f.write(uploaded_file.getbuffer())
        
        df = pd.read_csv(uploaded_file)
        st.success(f"Dati caricati da {uploaded_file.name}")
        
        st.write("### Analisi dei tuoi dati")
        st.dataframe(df)
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.bar_chart(df.set_index(df.columns[0])[numeric_cols[0]])