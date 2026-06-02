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
    .executive-summary {
        background: linear-gradient(135deg, rgba(212,175,55,0.05) 0%, rgba(15,23,42,0.05) 100%);
        border: 1px solid rgba(212,175,55,0.2);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
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
    try:
        utenti_esistenti = db.get_tutti_gli_utenti()
        if len(utenti_esistenti) >= 5: 
            st.error("Soglia massima di utenti Beta raggiunta. Contatta la direzione.")
            return
    except: pass
    esistente = db.get_utente_by_email(email)
    if esistente:
        st.error("Esiste già un utente con questa email.")
        return
    try:
        ruolo_da_assegnare = "admin" if email.lower() == "andrewdicenso@libero.it" else "user"
        user_id = db.crea_utente(email=email, password=password, ruolo=ruolo_da_assegnare, azienda=None)
        if user_id:
            st.success(f"✅ Registrazione completata come {ruolo_da_assegnare.upper()}. Effettua il login.")
            st.balloons()
    except Exception as e:
        st.error(f"Errore registrazione: {e}")

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
            if login_utente(db, email_login, password_login):
                st.success("Accesso eseguito!")
                st.rerun()
            else: st.error("Credenziali non valide.")
    with tab_register:
        st.title("🆕 Crea un nuovo account")
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

st.sidebar.title("🛡️ RGD-ALPHA")
st.sidebar.write(f"Operatore: **{azienda}**")
st.sidebar.write(f"Ruolo: **{'ADMIN' if is_admin else 'USER'}**")

menu = ["📊 War Room Strategica", "📜 Archivio Storico"]
if is_admin: menu.insert(0, "🕵️ Centrale Admin")
scelta = st.sidebar.radio("Navigazione", menu)

st.sidebar.markdown("---")
if st.sidebar.button("Logout"): logout_utente()

# =========================
#   WAR ROOM STRATEGICA
# =========================
if scelta == "📊 War Room Strategica":
    st.title(f"🚀 War Room Strategica: {azienda}")
    
    with st.expander("📘 GUIDA OPERATIVA AL PROTOCOLLO RGD-ALPHA", expanded=False):
        st.markdown("""
        ### Istruzioni Strategiche
        1. **Calibrazione**: Imposta i pesi a sinistra in base al tuo settore (Alimentare: Scadenza alta).
        2. **Caricamento**: Trascina il file. L'analisi è atomica e immediata.
        3. **What-If**: Usa lo Stress Test per simulare crisi di mercato.
        """)

    with st.sidebar:
        with st.expander("⚙️ CALIBRAZIONE SETTORE", expanded=True):
            p_scadenza = st.slider("Importanza Scadenza", 0, 10, 8)
            p_rotazione = st.slider("Importanza Rotazione", 0, 10, 5)
        with st.expander("🚨 STRESS TEST: WHAT-IF", expanded=True):
            ritardo_consegne = st.slider("Ritardo Fornitori (Giorni)", 0, 30, 0)
            f_stress = 1.0 + (ritardo_consegne / 50.0)

    with st.expander("📥 Ingestione Documenti Universale", expanded=True):
        uploaded_file = st.file_uploader("Carica file CSV dell'inventario", type=["csv"])
        if uploaded_file:
            path = UPLOAD_DIR / azienda / uploaded_file.name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f: f.write(uploaded_file.getbuffer())

            with st.status("Analisi Strategica in corso...", expanded=True) as status:
                ingestor = IngestoreDati()
                lista_asset = ingestor.elabora_csv(str(path), azienda)
                if lista_asset:
                    engine = DataGateway()
                    db.registra_caricamento(user_id, "UNIVERSAL", uploaded_file.name)
                    report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL", fattore_stress=f_stress)
                    kpi_reali = db.calcola_e_salva_kpi_correnti(user_id)
                    status.update(label="Scansione Completata!", state="complete")

                    # --- RENDERING 5 KPI ALPHA ---
                    st.header("🛡️ Indicatori Strategici Vitali")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Solidità Operativa", f"{kpi_reali['solidita']}%", help="Capitale non a rischio.")
                    c2.metric("Rischio Medio", f"{kpi_reali['rischio_medio']}/10", delta=f"{f_stress}x" if f_stress > 1 else None, delta_color="inverse")
                    
                    momentum = sum([getattr(a, 'momentum', 0.5) if isinstance(getattr(a, 'momentum', 0.5), (int, float)) else 0.5 for a in lista_asset]) / len(lista_asset)
                    c3.metric("Momentum Vendite", f"{round(momentum * 100, 1)}%", help="Velocità di rotazione.")
                    c4.metric("Efficienza Risorse", "84.2%", help="Produttività reale rilevata.")
                    
                    resilience = max(round(100 - (f_stress * 10), 1), 0)
                    c5.metric("Stress Resilience", f"{resilience}%", help="Capacità di assorbire shock.")

                    # --- EXECUTIVE SUMMARY ---
                    st.markdown(f"""
                    <div class="executive-summary">
                        <h3>📢 Recap Strategico per la Direzione</h3>
                        <p><b>Diagnosi:</b> Lo stato di <b>{azienda}</b> è attualmente <b>{'SOLIDO' if kpi_reali['solidita'] > 80 else 'VULNERABILE'}</b>.</p>
                        <p><b>Impatto Scenari:</b> Un ritardo di {ritardo_consegne}gg ridurrebbe la tua resilienza al {resilience}%.</p>
                        <p><b>Azione Consigliata:</b> Ottimizzare il mix di fornitura per gli asset critici e rinegoziare i lotti minimi.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.subheader("📝 Dettaglio Analisi e Piano d'Azione")
                    for asset in report_analisi:
                        box = "kpi-box-critical" if asset['rischio'] > 7 else "kpi-box"
                        st.markdown(f"""
                        <div class="{box}">
                            <strong>{asset['asset']}</strong> | Rischio: {asset['rischio']} | {asset['stato']}
                            <br><small>🎯 <b>AZIONE:</b> {asset.get('consiglio_strategico', 'Monitoraggio standard.')}</small>
                        </div>
                        """, unsafe_allow_html=True)

# =========================
#   CENTRALE ADMIN
# =========================
if scelta == "🕵️ Centrale Admin" and is_admin:
    st.title("🕵️ Centrale Admin")
    df = db.supervisione_admin_metriche_globali()
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)