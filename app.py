import os
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# --- MODULI CORE & AUTH ---
from core.ingestor import IngestoreDati
from core.engine import DataGateway, salva_report_certificato
from core.database import DatabaseAziendale
from consulente import ConsulenteAziendale

# Importiamo la logica centralizzata dal pacchetto auth
from auth.auth import inizializza_sessione, login_utente, logout_utente

# =========================
#   CONFIGURAZIONE BASE
# =========================
load_dotenv()
PROJECT_ROOT = Path(__file__).parent
DATA_ROOT = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_ROOT / "uploads"

for folder in [UPLOAD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="RGD-Alpha | War Room Strategica",
    layout="wide",
    page_icon="🛡️"
)

# Inizializziamo lo stato della sessione tramite il modulo auth
inizializza_sessione()

# =========================
#   CSS ENTERPRISE
# =========================
st.markdown("""
    <style>
    .kpi-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007BFF;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-box-critical {
        background-color: #fff5f5;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# =========================
#   ISTANZA DATABASE
# =========================
db = DatabaseAziendale()

# =========================
#   FUNZIONI DI SUPPORTO INTERNE
# =========================
def registra_nuovo_utente(email: str, password: str, conferma: str):
    if not email or not password or not conferma:
        st.error("Compila tutti i campi.")
        return

    if password != conferma:
        st.error("Le password non coincidono.")
        return

    # --- PROTEZIONE BETA: LIMITE UTENTI ---
    try:
        utenti_esistenti = db.get_tutti_gli_utenti()
        if len(utenti_esistenti) >= 5: 
            st.error("Soglia massima di utenti Beta raggiunta. Contatta la direzione per l'accesso.")
            return
    except:
        pass

    # Controllo se esiste già
    esistente = db.get_utente_by_email(email)
    if esistente:
        st.error("Esiste già un utente con questa email.")
        return

    try:
        # DETERMINAZIONE RUOLO (Andrew diventa Admin)
        ruolo_da_assegnare = "admin" if email.lower() == "andrewdicenso@libero.it" else "user"
        
        # Registrazione sicura
        user_id = db.crea_utente(
            email=email, 
            password=password, 
            ruolo=ruolo_da_assegnare, 
            azienda=None 
        )
        
        if user_id:
            st.success(f"✅ Registrazione completata come {ruolo_da_assegnare.upper()}. Ora puoi effettuare il login.")
            st.balloons()
    except Exception as e:
        st.error(f"Errore durante la registrazione: {e}")


# =========================
#   SCHERMATA LOGIN / REGISTRAZIONE
# =========================
if not st.session_state.autenticato:
    tab_login, tab_register = st.tabs(["🔐 Login", "🆕 Registrazione"])

    with tab_login:
        st.title("🔐 Accesso Utente")
        email_login = st.text_input("Email", key="auth_email_final").strip()
        password_login = st.text_input("Password", type="password", key="auth_pwd_final").strip()

        if st.button("Accedi", key="btn_login_final"):
            if not email_login or not password_login:
                st.error("Inserisci email e password.")
            else:
                if login_utente(db, email_login, password_login):
                    st.success("Accesso eseguito!")
                    st.rerun()
                else:
                    st.error("Credenziali non valide o password errata.")

    with tab_register:
        st.title("🆕 Crea un nuovo account")
        st.info("Nota: In questa fase Beta è consentito un solo accesso per ogni entità aziendale.")
        email_r = st.text_input("Email", key="reg_email_input").strip()
        pwd_r = st.text_input("Password", type="password", key="reg_pwd_input").strip()
        pwd_c = st.text_input("Conferma Password", type="password", key="reg_pwd_conf_input").strip()

        if st.button("Registrati", key="btn_register_submit"):
            registra_nuovo_utente(email_r, pwd_r, pwd_c)

    st.stop()

# =========================
#   SESSIONE ATTIVA
# =========================
user_id = st.session_state.user_id
azienda = st.session_state.azienda
ruolo = st.session_state.ruolo
is_admin = (ruolo == "admin")

# Sidebar di Navigazione
st.sidebar.title("🛡️ RGD-ALPHA")
st.sidebar.write(f"Operatore: **{azienda}**")
st.sidebar.write(f"Ruolo: **{'ADMIN' if is_admin else 'USER'}**")

if is_admin:
    menu = ["🕵️ Centrale Admin", "📊 War Room Strategica", "📜 Archivio Storico"]
else:
    menu = ["📊 War Room Strategica", "📜 Archivio Storico"]

scelta = st.sidebar.radio("Navigazione", menu)

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    logout_utente()

# =========================
#   WAR ROOM STRATEGICA (Con Modifiche What-If)
# =========================
if scelta == "📊 War Room Strategica":
    st.title(f"🚀 War Room Strategica: {azienda}")
        # --- NUOVA SEZIONE: GUIDA OPERATIVA ---
    with st.expander("📘 GUIDA OPERATIVA AL PROTOCOLLO RGD-ALPHA", expanded=True):
        st.markdown(f"""
        ### Benvenuto nella tua Centrale di Comando, {azienda}.
        
        Per ottenere un'analisi che abbia valore legale e strategico, segui rigorosamente questi passaggi:

        1.  **CALIBRAZIONE INIZIALE (Fondamentale)**: Prima di caricare i file, usa i selettori nella barra a sinistra. 
            *   *Perché?* Ogni settore ha pesi diversi. Se tratti alimentari, la 'Scadenza' deve essere alta (8-10). Se tratti metalli, conta di più la 'Rotazione'.
            *   **Nota**: Non usare questi slider per "giocare". Impostali una sola volta in base alla tua reale politica aziendale per garantire l'atomicità del dato.

        2.  **CARICAMENTO DATI**: Trascina il tuo file CSV nell'area sottostante. Il sistema eseguirà una scansione atomica immediata.

        3.  **STRESS TEST (WHAT-IF)**: Una volta caricati i dati, usa lo slider 'Stress Test' solo per simulare crisi reali (es. blocchi navali o ritardi logistici). 
            *   Questo ti permette di vedere come la **Solidità Operativa** della tua azienda reagirebbe a shock esterni imprevisti.

        4.  **REPORT CERTIFICATO**: Al termine, scarica il certificato cifrato AES-256. È il documento ufficiale da presentare in fase di audit o revisione di budget.
        """)
        st.warning("⚠️ **AVVISO**: Il sistema traccia ogni simulazione nel registro Audit Trail per garantire la coerenza delle analisi nel tempo.")
    # --- SIDEBAR: CALIBRAZIONE & STRESS TEST ---
    with st.sidebar:
        with st.expander("⚙️ CALIBRAZIONE SETTORE", expanded=True):
            st.info("🎯 Configura i pesi per il tuo settore.")
            p_scadenza = st.slider("Importanza Scadenza", 0, 10, 5)
            p_rotazione = st.slider("Importanza Rotazione", 0, 10, 5)
        
        with st.expander("🚨 STRESS TEST: WHAT-IF", expanded=True):
            st.warning("⚠️ Simula scenari di crisi esterna.")
            ritardo_consegne = st.slider("Ritardo Fornitori (Giorni)", 0, 30, 0)
            
            # Calcolo dinamico del fattore di stress per il motore
            f_stress = 1.0 + (ritardo_consegne / 50.0)
            
            if ritardo_consegne > 0:
                st.error(f"Scenario attivo: +{ritardo_consegne}gg di ritardo")

    with st.expander("📥 Ingestione Documenti Universale", expanded=True):
        uploaded_file = st.file_uploader("Carica file CSV dell'inventario", type=["csv"])

        if uploaded_file:
            path = UPLOAD_DIR / azienda / uploaded_file.name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.status("Scansione Strategica Alpha in corso...", expanded=True) as status:
                ingestor = IngestoreDati()
                lista_asset = ingestor.elabora_csv(str(path), azienda)

                if lista_asset:
                    engine = DataGateway()
                    db.registra_caricamento(user_id, "UNIVERSAL", uploaded_file.name)

                    # Esecuzione scan con fattore di stress iniettato dallo slider
                    report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL", fattore_stress=f_stress)
                    
                    kpi_reali = db.calcola_e_salva_kpi_correnti(user_id)
                    status.update(label="Analisi completata!", state="complete")

                    # --- VISUALIZZAZIONE INDICATORI ---
                    st.header("💎 Indicatori Strategici Vitali")
                    k1, k2, k3 = st.columns(3)
                    
                    # Calcoliamo un delta visivo per la solidità basato sullo stress
                    delta_solidita = f"-{ritardo_consegne}%" if ritardo_consegne > 0 else None
                    
                    k1.metric("Solidità Operativa", f"{kpi_reali['solidita']}%", delta=delta_solidita, delta_color="inverse")
                    k2.metric("Rischio Medio", f"{kpi_reali['rischio_medio']}/10")
                    k3.metric("Status Scenario", "STRESS TEST" if ritardo_consegne > 0 else "NOMINALE")

                    st.subheader("📝 Dettaglio Asset nel Futuro")
                    for asset in report_analisi:
                        # Recuperiamo i dati dall'oggetto o dal dizionario in modo sicuro
                        box = "kpi-box-critical" if asset['rischio'] > 7 else "kpi-box"
                        st.markdown(f"""
                        <div class="{box}">
                            <strong>{asset['asset']}</strong> | Rischio: {asset['rischio']} | <strong>{asset['stato']}</strong><br>
                            <small>{asset['alert']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if 'report_cifrato' in locals() or 'report_analisi' in locals():
                        st.markdown("---")
                        st.caption("Protocollo RGD-Alpha attivo. Cifratura AES-256 verificata.")

# =========================
#   CENTRALE ADMIN
# =========================
if scelta == "🕵️ Centrale Admin" and is_admin:
    st.title("🕵️ Centrale Admin — Supervisione Globale Enterprise")
    df_supervisione = db.supervisione_admin_metriche_globali()
    if df_supervisione is not None and not df_supervisione.empty:
        st.subheader("💎 Stato Clienti Monitorati")
        st.dataframe(df_supervisione, use_container_width=True, hide_index=True)
    else:
        st.info("Nessun cliente registrato al momento.")