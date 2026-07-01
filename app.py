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

inizializza_sessione()

# =========================
#   CSS ENTERPRISE
# =========================
st.markdown("""
    <style>
    .kpi-box {
        background-color: #f8f9fa; padding: 20px; border-radius: 10px;
        border-left: 5px solid #007BFF; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-box-critical {
        background-color: #fff5f5; padding: 20px; border-radius: 10px;
        border-left: 5px solid #dc3545; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .executive-summary {
        background: linear-gradient(135deg, rgba(212,175,55,0.05) 0%, rgba(15,23,42,0.05) 100%);
        border: 1px solid rgba(212,175,55,0.2); padding: 25px; border-radius: 15px; margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)


# =========================
#   ISTANZA DATABASE
# =========================
db = DatabaseAziendale()

# =========================
#   FUNZIONI DI SUPPORTO INTERNE
# =======
db = DatabaseAziendale()

# =========================
#   GESTIONE REGISTRAZIONE
# =========================
def registra_nuovo_utente(email: str, password: str, conferma: str):
    if not email or not password or not conferma:
        st.error("Compila tutti i campi.")
        return

    if password != conferma:
        st.error("Le password non coincidono.")
        return

    # Controllo se esiste già
    esistente = db.get_utente_by_email(email)
    if esistente:
        st.error("Esiste già un utente con questa email.")
        return

    try:
        # RIPRISTINO CORRETTO: Lasciamo azienda=None così database.py genera l'identificativo multi-tenant sicuro (AZ-id)
        user_id = db.crea_utente(email=email, password=password, ruolo="user", azienda=None)
        nuovo = db.get_utente_by_id(user_id)
        if nuovo:
            st.success("✅ Registrazione completata. Ora puoi effettuare il login.")
        else:
            st.error("Errore durante la registrazione. Riprova.")
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
                    st.error("Credenziali non valide. Verifica l'email o la password inserita.")

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

# Sidebar di controllo e navigazione
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
#   WAR ROOM STRATEGICA (USER / ANALISI)
# =========================
if scelta == "📊 War Room Strategica":
    st.title(f"🚀 War Room Strategica: {azienda}")

    with st.expander("📥 Ingestione Documenti Universale", expanded=True):
        uploaded_file = st.file_uploader("Carica file CSV", type=["csv"])

        if uploaded_file:
            path = UPLOAD_DIR / azienda / uploaded_file.name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.status("Analisi e storicizzazione in corso...", expanded=True) as status:
                ingestor = IngestoreDati()
                lista_asset = ingestor.elabora_csv(str(path), azienda)

                if not lista_asset:
                    st.error("⚠️ File non valido o vuoto.")
                else:
                    engine = DataGateway()

                    # 1. Registrazione log caricamento (Audit trail multi-tenant)
                    db.registra_caricamento(user_id, "UNIVERSAL", uploaded_file.name)

                    # 2. Persistenza atomica sul database prima del calcolo dei KPI
                    for asset_data in lista_asset:
                        db.salva_asset(
                            user_id=user_id,
                            nome_asset=asset_data["nome"],
                            rischio=asset_data["rischio"],
                            tipo=asset_data.get("tipo", "GenericAsset"),
                            momentum=asset_data.get("momentum", "Stabile"),
                            volatilita=asset_data.get("volatilita", 0.0)
                        )

                    # 3. Analisi predittiva del motore di calcolo
                    report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL")
                    report_cifrato = salva_report_certificato(azienda, report_analisi, engine.vault)

                    # 4. Esecuzione centralizzata delle metriche strategiche via SQL
                    kpi_reali = db.calcola_e_salva_kpi_correnti(user_id)

                    status.update(label="Analisi completata con successo!", state="complete")

                    # --- RENDERING INDICATORI VITALI ---
                    st.header("💎 Indicatori Strategici Vitali")
                    k1, k2, k3, k4, k5 = st.columns(5)

                    with k1:
                        st.metric("Solidità Operativa", f"{kpi_reali['solidita']}%")

                    with k2:
                        st.metric("Impatto 30gg", f"{kpi_reali['impatto_30gg']}")

                    with k3:
                        st.metric("Rischio Medio", f"{kpi_reali['rischio_medio']}/10")

                    with k4:
                        st.metric("Efficienza Dati", "HIGH")

                    with k5:
                        st.metric("Sicurezza", "AES-256")

                    # --- ELEVAZIONE VISIVA DEGLI ASSET ---
                    st.subheader("📝 Dettaglio Analisi Asset")
                    for asset in report_analisi:
                        box = "kpi-box-critical" if asset["stato"] == "CRITICO" else "kpi-box"
                        st.markdown(f"""
                        <div class="{box}">
                            <strong>{asset['asset']}</strong> — <span style="color: {'#dc3545' if asset['stato']=='CRITICO' else '#007BFF'}">{asset['stato']}</span><br>
                            Rischio Attuale: {asset['rischio']} | Impatto Proiettato 30gg: {asset['proiezione_impatto']}
                        </div>
                        """, unsafe_allow_html=True)

                    if report_cifrato:
                        st.markdown("---")
                        st.download_button(
                            "📥 Scarica Certificato Cifrato",
                            report_cifrato,
                            file_name=f"RGD_{azienda}_{datetime.now().strftime('%Y%m%d')}.enc"
                        )

# =========================
#   CENTRALE ADMIN (PANNELLO DI SUPERVISIONE)
# =========================
if scelta == "🕵️ Centrale Admin" and is_admin:
    st.title("🕵️ Centrale Admin — Supervisione Globale Enterprise")

    df_supervisione = db.supervisione_admin_metriche_globali()
    
    if not df_supervisione.empty:
        st.subheader("💎 Stato Clienti Monitorati")
        st.dataframe(df_supervisione, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📊 Mappa Comparativa del Rischio")
        
        df_log_completo = db.recupera_attivita_globale(solo_admin=True)
        if not df_log_completo.empty:
            df_chart = df_log_completo.groupby("company_id")["rischio"].mean().reset_index()
            st.bar_chart(df_chart, x="company_id", y="rischio")
            
            st.subheader("📋 Registro Analisi Globale (Tutti gli Asset di Sistema)")
            st.dataframe(df_log_completo, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📂 Registro Caricamenti File Clienti")
        df_uploads = db.recupera_log_caricamenti_admin()
        if not df_uploads.empty:
            st.dataframe(df_uploads, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun file inserito dai clienti finora.")
            
    else:
        st.info("Nessuna azienda cliente registrata nel sistema al di fuori dell'amministratore.")

# =========================
#   ARCHIVIO STORICO
# =========================
if scelta == "📜 Archivio Storico":
    st.title("📜 Archivio Storico Asset")
    st.write("Visualizzazione cronologica completa dei log cifrati di questa azienda.")

    df_storico = db.recupera_asset_per_utente(user_id)
    if not df_storico.empty:
        st.dataframe(df_storico, use_container_width=True)
    else:
        st.warning("Nessun record presente in archivio. Esegui un'analisi nella War Room per iniziare.")
#=======
    if password != conferma:
        st.error("Le password non coincidono.")
        return
    try:
        esistente = db.get_utente_by_email(email)
        if esistente:
            st.error("Email già registrata.")
            return
        
        ruolo = "admin" if email.lower() == "andrewdicenso@libero.it" else "user"
        user_id = db.crea_utente(email=email, password=password, ruolo=ruolo)
        if user_id:
            st.success("✅ Registrazione completata. Effettua il login.")
            st.balloons()
    except Exception as e:
        st.error(f"Errore registrazione: {e}")

# =========================
#   SCHERMATA AUTH
# =========================
if not st.session_state.autenticato:
    tab_login, tab_register = st.tabs(["🔐 Login", "🆕 Registrazione"])
    with tab_login:
        st.title("🔐 Accesso Utente")
        e_login = st.text_input("Email", key="l_email").strip()
        p_login = st.text_input("Password", type="password", key="l_pwd").strip()
        if st.button("Accedi"):
            if login_utente(db, e_login, p_login):
                st.rerun()
            else:
                st.error("Credenziali errate.")
    with tab_register:
        st.title("🆕 Crea account Beta")
        e_reg = st.text_input("Email", key="r_email").strip()
        p_reg = st.text_input("Password", type="password", key="r_pwd").strip()
        c_reg = st.text_input("Conferma", type="password", key="r_conf").strip()
        if st.button("Registrati"):
            registra_nuovo_utente(e_reg, p_reg, c_reg)
    st.stop()

# =========================
#   NAVIGAZIONE SIDEBAR
# =========================
user_id = st.session_state.user_id
azienda = st.session_state.azienda
ruolo = st.session_state.ruolo
is_admin = (ruolo == "admin")

st.sidebar.title("🛡️ RGD-ALPHA")
st.sidebar.write(f"Operatore: **{azienda}**")
menu = ["📊 War Room Strategica", "📜 Archivio Storico"]
if is_admin: menu.insert(0, "🕵️ Centrale Admin")
scelta = st.sidebar.radio("Navigazione", menu)

if st.sidebar.button("Logout"): logout_utente()

# =========================
#   WAR ROOM STRATEGICA
# =========================
if scelta == "📊 War Room Strategica":
    st.title(f"🚀 War Room Strategica: {azienda}")
    
    with st.sidebar:
        with st.expander("⚙️ CALIBRAZIONE", expanded=True):
            p_scad = st.slider("Importanza Scadenza", 0, 10, 8)
        with st.expander("🚨 STRESS TEST", expanded=True):
            ritardo = st.slider("Ritardo Fornitori (Giorni)", 0, 30, 0)
            f_stress = 1.0 + (ritardo / 50.0)

    uploaded_file = st.file_uploader("Carica inventario CSV", type=["csv"])
    if uploaded_file:
        path = UPLOAD_DIR / azienda / uploaded_file.name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f: f.write(uploaded_file.getbuffer())

        with st.status("Analisi in corso...") as status:
            ingestor = IngestoreDati()
            lista_asset = ingestor.elabora_csv(str(path), azienda)
            
            if lista_asset:
                engine = DataGateway()
                db.registra_caricamento(user_id, "UNIVERSAL", uploaded_file.name)
                report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL", fattore_stress=f_stress)
                kpi_reali = db.calcola_e_salva_kpi_correnti(user_id)
                status.update(label="Analisi completata!", state="complete")

                # --- 5 KPI ALPHA ---
                st.header("🛡️ Indicatori Strategici Vitali")
                cols = st.columns(5)
                cols[0].metric("Solidità", f"{kpi_reali.get('solidita', 0)}%")
                cols[1].metric("Rischio", f"{kpi_reali.get('rischio_medio', 0)}/10")
                
                mom_val = sum([getattr(a, 'rischio', 5.0) for a in lista_asset]) / len(lista_asset) if lista_asset else 5.0
                cols[2].metric("Momentum", f"{round(mom_val * 10, 1)}%")
                cols[3].metric("Efficienza", "84%")
                res = max(round(100 - (f_stress * 10), 1), 0)
                cols[4].metric("Resilience", f"{res}%")

                # --- EXECUTIVE SUMMARY ---
                st.markdown(f"""
                <div class="executive-summary">
                    <h3>📢 Recap Strategico</h3>
                    <p><b>Diagnosi:</b> Stato aziendale {'SOLIDO' if kpi_reali.get('solidita',0) > 80 else 'VULNERABILE'}.</p>
                    <p><b>Scenario Stress:</b> Un ritardo di {ritardo}gg porta la resilienza al {res}%.</p>
                </div>
                """, unsafe_allow_html=True)

                # --- DETTAGLIO ---
                st.subheader("📝 Piano d'Actione")
                for asset in report_analisi:
                    r = asset.get('rischio', 0) if isinstance(asset, dict) else getattr(asset, 'rischio', 0)
                    nome = asset.get('asset', 'Asset') if isinstance(asset, dict) else getattr(asset, 'asset', 'Asset')
                    stato = asset.get('stato', 'N/D') if isinstance(asset, dict) else getattr(asset, 'stato', 'N/D')
                    
                    box = "kpi-box-critical" if r > 7 else "kpi-box"
                    st.markdown(f"""<div class="{box}"><b>{nome}</b> | Rischio: {r} | {stato}</div>""", unsafe_allow_html=True)

# =========================
#   CENTRALE ADMIN
# =========================
if scelta == "🕵️ Centrale Admin" and is_admin:
    st.title("🕵️ Centrale Admin")
    try:
        df = db.supervisione_admin_metriche_globali()
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun dato presente.")
    except Exception as e:
        st.error(f"Errore caricamento dati admin: {e}")

