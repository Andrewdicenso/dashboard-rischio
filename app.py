import streamlit as st
import pandas as pd
import os
from pathlib import Path

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

# Utilizziamo Path per una gestione del file system cross-platform e sicura
LOG_DIR = Path("data/logs")
UPLOAD_DIR = Path("data/uploads")

# Creazione sicura delle directory: exist_ok=True evita l'errore se la cartella esiste già
LOG_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Definiamo i file path usando Path
LOG_CANDIDATURE = LOG_DIR / "richieste_candidature.txt"
LOG_FEEDBACK = LOG_DIR / "richieste_clienti.txt"

# --- LOGICA GUIDA ---
def mostra_guida():
    with st.expander("📖 Guida operativa"):
        st.write("""
        Benvenuto nella tua area di analisi strategica. 
        1. **Carica Dati**: Trascina il file CSV con i tuoi dati correnti.
        2. **Analisi**: Il sistema elaborerà i dati in tempo reale.
        3. **Ottimizzazione**: Usa il modulo feedback qui sotto per richiedere nuovi parametri o funzionalità specifiche per il tuo settore.
        """)

# --- STATO SESSIONE ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- LOGICA DI ACCESSO E CANDIDATURA ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔒 Login Area Riservata", "📩 Richiedi Accreditamento"])
    
    with tab1:
        st.title("🔒 Accesso Area Riservata")
        UTENTI_VALIDI = {"AZIENDA_001": "pass123", "AZIENDA_002": "sicurezza456", "ADMIN_PRINCIPALE": "admin_super"}
        user = st.text_input("ID Azienda")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if UTENTI_VALIDI.get(user) == password:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else: 
                st.error("Credenziali errate!")

    with tab2:
        st.subheader("Richiesta di Accreditamento War Room")
        st.markdown("*RGandja | Intelligence Operativa*\n\nL'accesso alla War Room è riservato esclusivamente ad aziende selezionate.")
        
        with st.form("richiesta_accesso_form"):
            nome_azienda = st.text_input("Nome Azienda")
            sito_web = st.text_input("Sito Web Aziendale")
            referente = st.text_input("Referente Tecnico")
            email_aziendale = st.text_input("Email Aziendale")
            note = st.text_area("Breve descrizione dell'esigenza (opzionale)")
            submit_button = st.form_submit_button("Invia Candidatura")
            
            if submit_button:
                if nome_azienda and email_aziendale:
                    with open(LOG_CANDIDATURE, "a") as f:
                        f.write(f"Azienda: {nome_azienda} | Sito: {sito_web} | Ref: {referente} | Email: {email_aziendale} | Note: {note}\n")
                    st.success("Candidatura inviata!")
                else:
                    st.error("Per favore, compila almeno il Nome Azienda e l'Email.")

else:
    # --- DASHBOARD LOGGATA ---
    azienda = st.session_state.user
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- LOGICA ADMIN ---
    if azienda == "ADMIN_PRINCIPALE":
        st.title("🛡️ Centrale di Controllo Admin")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Leggi richieste accesso"):
                if LOG_CANDIDATURE.exists():
                    with open(LOG_CANDIDATURE, "r") as f:
                        st.text(f.read())
        with col2:
            if st.button("Leggi feedback adeguamento"):
                if LOG_FEEDBACK.exists():
                    with open(LOG_FEEDBACK, "r") as f:
                        st.text(f.read())
    
    # --- DASHBOARD AZIENDA ---
    else:
        st.title(f"📊 Dashboard - {azienda}")
        mostra_guida() 
        
        user_folder = UPLOAD_DIR / azienda
        user_folder.mkdir(parents=True, exist_ok=True)
        
        uploaded_file = st.file_uploader("Carica o aggiorna il tuo file CSV")
        
        if uploaded_file:
            # Salvataggio file con Path
            file_path = user_folder / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)

        st.divider()
        st.subheader("📩 Hai bisogno di un adeguamento?")
        with st.form("form_feedback"):
            richiesta = st.text_area("Descrivi la modifica necessaria:")
            if st.form_submit_button("Invia richiesta"):
                with open(LOG_FEEDBACK, "a") as f:
                    f.write(f"Azienda: {azienda} - Richiesta: {richiesta}\n")
                st.success("Richiesta inviata correttamente!")