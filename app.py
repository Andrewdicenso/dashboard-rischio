import streamlit as st
import pandas as pd
import os
from pathlib import Path
# Import delle classi di logica
from core.ingestor import IngestorStrategico
from core.engine import DataGateway

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Dashboard Rischio Aziendale", layout="wide")

LOG_DIR = Path("data/logs")
UPLOAD_DIR = Path("data/uploads")

LOG_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

LOG_CANDIDATURE = LOG_DIR / "richieste_candidature.txt"
LOG_FEEDBACK = LOG_DIR / "richieste_clienti.txt"

# --- LOGICA GUIDA ---
def mostra_guida():
    with st.expander("📖 Guida operativa"):
        st.write("""
        Benvenuto nella tua area di analisi strategica. 
        1. **Seleziona Contesto**: Indica al sistema cosa stai caricando (Magazzino, Fornitori, ecc.).
        2. **Carica Dati**: Trascina il file CSV.
        3. **Analisi**: Il Protocollo RGD-Alpha elaborerà i dati secondo le specifiche del contesto selezionato.
        """)

# --- STATO SESSIONE ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

# --- LOGICA DI ACCESSO ---
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
        with st.form("richiesta_accesso_form"):
            nome_azienda = st.text_input("Nome Azienda")
            email_aziendale = st.text_input("Email Aziendale")
            if st.form_submit_button("Invia Candidatura"):
                if nome_azienda and email_aziendale:
                    with open(LOG_CANDIDATURE, "a") as f:
                        f.write(f"Azienda: {nome_azienda} | Email: {email_aziendale}\n")
                    st.success("Candidatura inviata!")

else:
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
    
    # --- DASHBOARD AZIENDA (CON CONTESTO E ANALISI) ---
    else:
        st.title(f"📊 Dashboard - {azienda}")
        mostra_guida() 
        
        contesto = st.selectbox("Seleziona il contesto dell'analisi:", 
                                ["Magazzino", "Fornitori", "Performance Vendite"])
        
        user_context_folder = UPLOAD_DIR / azienda / contesto
        user_context_folder.mkdir(parents=True, exist_ok=True)
        
        uploaded_file = st.file_uploader(f"Carica file CSV per: {contesto}")
        
        if uploaded_file:
            file_path = user_context_folder / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.info(f"File salvato correttamente in area {contesto}.")
            
            # --- ESECUZIONE ANALISI AUTOMATICA ---
            ingestor = IngestorStrategico()
            engine = DataGateway(storage_provider=None) 
            
            # 1. Ingestione e protezione (con contesto)
            lista_asset = ingestor.da_csv(str(file_path), contesto)
            
            # 2. Esecuzione Scan Strategico
            report_critici = engine.esegui_scan_strategico(lista_asset, contesto)
            
            # --- OUTPUT REPORT DI SINTESI ---
            if report_critici:
                st.warning(f"⚠️ Attenzione: Rilevati {len(report_critici)} elementi critici in {contesto}")
                df_report = pd.DataFrame(report_critici)
                st.dataframe(df_report)
                
                # Bottone download
                csv_report = df_report.to_csv(index=False)
                st.download_button("📥 Scarica Report Analisi", csv_report, "report_analisi.csv", "text/csv")
            else:
                st.success("✅ Analisi completata: Nessuna criticità rilevata.")

        st.divider()
        st.subheader("📩 Hai bisogno di un adeguamento?")
        with st.form("form_feedback"):
            richiesta = st.text_area("Descrivi la modifica necessaria:")
            if st.form_submit_button("Invia richiesta"):
                with open(LOG_FEEDBACK, "a") as f:
                    f.write(f"Azienda: {azienda} - Richiesta: {richiesta}\n")
                st.success("Richiesta inviata correttamente!")