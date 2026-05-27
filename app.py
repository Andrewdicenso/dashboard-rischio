import streamlit as st
import pandas as pd
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# --- MODULI CORE ---
from core.ingestor import IngestoreDati
from core.engine import DataGateway, salva_report_certificato
from core.database import DatabaseAziendale
from consulente import ConsulenteAziendale

# --- CONFIGURAZIONE AMBIENTE ---
load_dotenv()
PROJECT_ROOT = Path(__file__).parent
DATA_ROOT = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_ROOT / "uploads"

for folder in [UPLOAD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="RGD-Alpha | War Room Strategica", layout="wide", page_icon="🛡️")

# --- CSS ---
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

# --- LOGIN UTENTE ---
db = DatabaseAziendale()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Accesso Utente")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Accedi"):
        utente = db.get_utente_by_email(email)

        if utente and bcrypt.checkpw(password.encode(), utente["password_hash"].encode()):
            st.session_state.logged_in = True
            st.session_state.user = utente
            st.rerun()
        else:
            st.error("❌ Credenziali non valide.")
else:
    # --- SESSIONE ATTIVA ---
    utente = st.session_state.user
    azienda = utente["azienda"]
    is_admin = (utente["ruolo"] == "admin")

    st.sidebar.title("🛡️ RGD-ALPHA")
    st.sidebar.write(f"Operatore: **{azienda}**")

    if is_admin:
        menu = ["🕵️ Centrale Admin", "📜 Archivio Storico"]
    else:
        menu = ["📊 War Room Strategica", "📜 Archivio Storico"]

    scelta = st.sidebar.radio("Navigazione", menu)

    # -------------------------
    #   DASHBOARD CLIENTE
    # -------------------------
    if scelta == "📊 War Room Strategica" and not is_admin:
        st.title(f"🚀 War Room Strategica: {azienda}")

        with st.expander("📥 Ingestione Documenti Universale", expanded=True):
            uploaded_file = st.file_uploader("Carica file CSV", type=["csv"])

            if uploaded_file:
                path = UPLOAD_DIR / azienda / uploaded_file.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.status("Analisi in corso...", expanded=True):
                    ingestor = IngestoreDati()
                    lista_asset = ingestor.elabora_csv(str(path), azienda)

                    if not lista_asset:
                        st.error("⚠️ File non valido.")
                    else:
                        engine = DataGateway()
                        db.registra_caricamento(azienda, "UNIVERSAL", uploaded_file.name)

                        report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL")
                        report_cifrato = salva_report_certificato(azienda, report_analisi, engine.vault)

                        st.success("Analisi completata!")

                        # KPI
                        st.header("💎 Indicatori Strategici Vitali")
                        k1, k2, k3, k4, k5 = st.columns(5)

                        rischio_medio = sum(a["rischio"] for a in report_analisi) / len(report_analisi)
                        impatto_30gg_medio = sum(a["proiezione_impatto"] for a in report_analisi) / len(report_analisi)
                        settore_rilevato = report_analisi[0]["settore_rilevato"]

                        with k1:
                            st.metric("Solidità Operativa", f"{max(0, 100 - rischio_medio*10):.1f}%")

                        with k2:
                            st.metric("Impatto 30gg", f"{impatto_30gg_medio:.1f}")

                        with k3:
                            st.metric("Rischio Medio", f"{rischio_medio:.1f}/10")

                        with k4:
                            st.metric("Efficienza Dati", "HIGH")

                        with k5:
                            st.metric("Sicurezza", "AES-256")

                        st.subheader("📝 Analisi Asset")
                        for asset in report_analisi:
                            box = "kpi-box-critical" if asset["stato"] == "CRITICO" else "kpi-box"
                            st.markdown(f"""
                            <div class="{box}">
                                <strong>{asset['asset']}</strong> — {asset['stato']}<br>
                                Rischio: {asset['rischio']} | Impatto 30gg: {asset['proiezione_impatto']}
                            </div>
                            """, unsafe_allow_html=True)

                        if report_cifrato:
                            st.download_button(
                                "📥 Scarica Certificato Cifrato",
                                report_cifrato,
                                file_name=f"RGD_{azienda}_{datetime.now().strftime('%Y%m%d')}.enc"
                            )

    # -------------------------
    #   DASHBOARD ADMIN
    # -------------------------
    if scelta == "🕵️ Centrale Admin" and is_admin:
        st.title("🕵️ Centrale Admin — Monitoraggio Globale")

        df_log = db.recupera_attivita_globale()
        if not df_log.empty:
            st.subheader("📊 Rischio Medio per Azienda")
            df_chart = df_log.groupby("company_id")["rischio"].mean().reset_index()
            st.bar_chart(df_chart, x="company_id", y="rischio")

            st.subheader("📋 Registro Eventi")
            st.dataframe(df_log)
        else:
            st.info("Nessuna attività registrata.")

    # -------------------------
    #   ARCHIVIO STORICO
    # -------------------------
    if scelta == "📜 Archivio Storico":
        st.title("📜 Archivio Storico Asset")
        df_storico = db.recupera_asset_per_azienda(azienda)

        if not df_storico.empty:
            st.dataframe(df_storico)
        else:
            st.warning("Archivio vuoto.")

    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
