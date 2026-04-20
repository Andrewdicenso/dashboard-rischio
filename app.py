import streamlit as st
import pandas as pd
import os

# --- LOGICA GUIDA ---
def mostra_guida():
    with st.expander("📖 Guida operativa"):
        st.write("""
        Benvenuto nella tua area di analisi strategica. 
        1. **Carica Dati**: Trascina il file CSV con i tuoi dati correnti.
        2. **Analisi**: Il sistema elaborerà i dati in tempo reale.
        3. **Ottimizzazione**: Usa il modulo feedback qui sotto per richiedere nuovi parametri o funzionalità specifiche per il tuo settore.
        """)

# --- CONFIGURAZIONE LOGIN ---
UTENTI_VALIDI = {"AZIENDA_001": "pass123", "AZIENDA_002": "sicurezza456"}
st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

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
    st.title(f"📊 Dashboard - {azienda}")
    mostra_guida() 
    
    user_folder = f"uploads/{azienda}"
    if not os.path.exists(user_folder): 
        os.makedirs(user_folder)
    
    last_file_path = os.path.join(user_folder, "last_file.txt")
    uploaded_file = st.file_uploader("Carica o aggiorna il tuo file CSV")
    
    target_file = uploaded_file if uploaded_file else None
    
    if uploaded_file is None and os.path.exists(last_file_path):
        with open(last_file_path, "r") as f:
            filename = f.read()
            old_path = os.path.join(user_folder, filename)
            if os.path.exists(old_path):
                st.info(f"Stai visualizzando l'ultimo file caricato: {filename}")
                target_file = open(old_path, "rb")

    if target_file:
        df = pd.read_csv(target_file)
        st.dataframe(df)
        
        if uploaded_file:
            with open(last_file_path, "w") as f: 
                f.write(uploaded_file.name)
            with open(os.path.join(user_folder, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())

    # --- MODULO FEEDBACK (SEMPRE VISIBILE) ---
    st.divider()
    st.subheader("📩 Hai bisogno di un adeguamento?")
    with st.form("form_feedback"):
        richiesta = st.text_area("Descrivi l'aggiunta o la modifica necessaria per il tuo settore:")
        submit_button = st.form_submit_button("Invia richiesta")
        
        if submit_button:
            with open("richieste_clienti.txt", "a") as f:
                f.write(f"Azienda: {azienda} - Richiesta: {richiesta}\n")
            st.success("Richiesta inviata correttamente! Ti contatteremo per l'implementazione.")