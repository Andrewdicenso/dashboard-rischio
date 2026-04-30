import streamlit as st
import pandas as pd
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- MODULI CORE ---
from core.ingestor import IngestorStrategico
from core.engine import DataGateway, salva_report_certificato
from core.database import DatabaseAziendale  # Importato per la gestione Admin
from consulente import ConsulenteAziendale

# --- CONFIGURAZIONE AMBIENTE ---
load_dotenv()
PROJECT_ROOT = Path(__file__).parent
DATA_ROOT = PROJECT_ROOT / "data"
LOG_DIR = DATA_ROOT / "logs"
UPLOAD_DIR = DATA_ROOT / "uploads"

for folder in [LOG_DIR, UPLOAD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "sistema_analisi.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

st.set_page_config(page_title="RGD-Alpha | War Room Strategica", layout="wide")

# --- FUNZIONI DI SUPPORTO E TRASPARENZA ---
def mostra_guida_estensiva():
    with st.expander("📖 PROTOCOLLO RGD-ALPHA: MANIFESTO STRATEGICO"):
        st.markdown("""
        ### Benvenuto nella tua War Room.
        Questo non è un semplice software di analisi; è un **Sistema di Validazione e Certificazione Strategica**. 
        
        **Cosa ci rende unici sul mercato:**
        1.  **Cifratura alla Fonte (Military Grade):** Siamo gli unici a proteggere l'identità dei tuoi asset con tecnologia AES-256 prima ancora del salvataggio.
        2.  **Analisi Predittiva del Rischio Pesato:** Applichiamo coefficienti dinamici (es. x1.2 Magazzino, x1.5 Fornitori).
        3.  **Certificazione Indelebile:** Ogni analisi genera un report '.enc' cifrato e firmato.
        """)

def verifica_integrita_file(uploaded_file, contesto):
    try:
        df_prev = pd.read_csv(uploaded_file, nrows=5)
        requisiti = {"Magazzino": "quantita", "Fornitori": "stato", "Performance Vendite": "volume"}
        col = requisiti.get(contesto)
        if col and col not in df_prev.columns:
            return False, f"Il file deve contenere la colonna '{col}' per il contesto {contesto}."
        return True, "Struttura verificata."
    except Exception as e: 
        return False, f"Errore tecnico: {str(e)}"

# --- LOGICA DI ACCESSO SCALABILE ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.is_admin = False

if not st.session_state.logged_in:
    st.title("🛡️ Accesso Area Riservata")
    user_input = st.text_input("ID Azienda", key="login_user")
    pass_input = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Accedi", key="login_btn"):
        # Controllo Admin Super (da .env)
        if user_input == "ADMIN" and pass_input == os.getenv("ADMIN_PASS"):
            st.session_state.logged_in = True
            st.session_state.user = "SUPER_ADMIN"
            st.session_state.is_admin = True
            st.rerun()
        
        # Controllo Dinamico Clienti (cerca AZIENDA_XXX_PASS nel .env)
        env_key = f"{user_input}_PASS"
        if os.getenv(env_key) == pass_input:
            st.session_state.logged_in = True
            st.session_state.user = user_input
            st.session_state.is_admin = False
            st.rerun()
        else: 
            st.error("Credenziali non valide o Account non censito.")
else:
    # --- INTERFACCIA POST-LOGIN ---
    azienda = st.session_state.user
    db = DatabaseAziendale()

    # Sidebar per navigazione se Admin
    menu = ["Dashboard Cliente"]
    if st.session_state.is_admin:
        menu.append("🕵️ Centrale di Controllo Admin")
    
    scelta = st.sidebar.radio("Navigazione", menu)

    if scelta == "Dashboard Cliente":
        st.title(f"📊 Dashboard Strategica - {azienda}")
        mostra_guida_estensiva()
        
        contesto = st.selectbox("Area di analisi:", ["Magazzino", "Fornitori", "Performance Vendite"], key="select_context")
        uploaded_file = st.file_uploader(f"Carica CSV per {contesto}", key="file_up")
        
        if uploaded_file:
            is_valido, msg = verifica_integrita_file(uploaded_file, contesto)
            if not is_valido:
                st.error(f"⚠️ {msg}")
            else:
                # Salvataggio e Registrazione Silenziosa per Admin
                file_path = UPLOAD_DIR / azienda / contesto / uploaded_file.name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "wb") as f: 
                    f.write(uploaded_file.getbuffer())
                
                db.registra_caricamento(azienda, contesto, uploaded_file.name) # <--- Traccia per Admin
                
                st.info(f"💡 Analisi RGD-Alpha in corso...")
                with st.status("Elaborazione...", expanded=True) as status:
                    ingestor = IngestorStrategico()
                    lista_asset = ingestor.da_csv(str(file_path), contesto)
                    engine = DataGateway()
                    report_analisi = engine.esegui_scan_strategico(lista_asset, contesto)
                    report_cifrato = salva_report_certificato(azienda, report_analisi, engine.vault)
                    status.update(label="Analisi Certificata!", state="complete")
                
                # --- KPI ---
                st.subheader("📈 Metriche KPI")
                c = st.columns(5)
                kpi = ConsulenteAziendale(azienda).get_all_kpi()
                c[0].metric("CAC", f"€{kpi['cac']:.2f}")
                c[1].metric("LTV", f"€{kpi['ltv']:.2f}")
                c[2].metric("ROI", f"{kpi['roi']*100:.1f}%")
                
                if report_analisi:
                    st.dataframe(pd.DataFrame(report_analisi), use_container_width=True)
                    st.download_button("📥 Scarica Report", data=report_cifrato, file_name=f"report_{azienda}.enc")

    elif scelta == "🕵️ Centrale di Controllo Admin":
        st.title("🕵️ Centrale di Controllo Admin (Stealth Mode)")
        st.write("Benvenuto Capo. Qui puoi vedere i movimenti di tutti i clienti in tempo reale.")
        
        df_log = db.recupera_attivita_globale()
        if not df_log.empty:
            st.dataframe(df_log, use_container_width=True)
        else:
            st.info("Nessuna attività registrata dai clienti al momento.")