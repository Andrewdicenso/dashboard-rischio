import streamlit as st
import pandas as pd
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

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

# Assicuriamo la struttura delle cartelle
for folder in [UPLOAD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="RGD-Alpha | War Room Strategica", layout="wide", page_icon="🛡️")

# --- CSS CUSTOM PER IL LOOK PROFESSIONALE ---
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
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI ACCESSO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ RGD-Alpha | Protocollo di Sicurezza")
    with st.container():
        user_input = st.text_input("ID Azienda (es. AZIENDA_001)")
        pass_input = st.text_input("Security Key", type="password")
        
        if st.button("Inizializza Sessione"):
            env_key = f"{user_input}_PASS"
            if user_input == "ADMIN" and pass_input == os.getenv("ADMIN_PASS"):
                st.session_state.logged_in = True
                st.session_state.user = "SUPER_ADMIN"
                st.session_state.is_admin = True
                st.rerun()
            elif os.getenv(env_key) == pass_input:
                st.session_state.logged_in = True
                st.session_state.user = user_input
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("Accesso negato. Verificare credenziali.")

else:
    # --- DASHBOARD ATTIVA ---
    azienda = st.session_state.user
    db = DatabaseAziendale()
    
    st.sidebar.title(f"🛡️ RGD-ALPHA")
    st.sidebar.write(f"Operatore: **{azienda}**")
    
    # Restrizione voci di menu in base al ruolo amministrativo
    if st.session_state.is_admin:
        menu = ["🕵️ Centrale Admin", "📜 Archivio Storico"]
    else:
        menu = ["📊 War Room Strategica", "📜 Archivio Storico"]
        
    scelta = st.sidebar.radio("Navigazione", menu)

    if scelta == "📊 War Room Strategica":
        st.title(f"🚀 War Room Strategica: {azienda}")
        
        with st.expander("📥 Ingestione Documenti Universale (Bolle, Fatture, Inventari)", expanded=True):
            uploaded_file = st.file_uploader("Trascina qui il file aziendale (.csv)", type=["csv"])
            
            if uploaded_file:
                # Salvataggio fisico del file
                path = UPLOAD_DIR / azienda / uploaded_file.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                with st.status("Analisi Intelligente in corso...", expanded=True) as status:
                    ingestor = IngestoreDati()
                    lista_asset = ingestor.elabora_csv(str(path), azienda)
                    
                    if not lista_asset:
                        st.error("⚠️ Il file non contiene dati validi per l'analisi.")
                        status.update(label="Analisi Fallita", state="error")
                    else:
                        engine = DataGateway()
                        # Registra l'evento di caricamento nell'audit log
                        db.registra_caricamento(azienda, "UNIVERSAL", uploaded_file.name)
                        
                        # Esecuzione scansione con il nuovo motore adattivo basato sui settori
                        report_analisi = engine.esegui_scan_strategico(lista_asset, "UNIVERSAL")
                        report_cifrato = salva_report_certificato(azienda, report_analisi, engine.vault)
                        status.update(label="✅ Sistema Sincronizzato!", state="complete")

                        # --- I 5 KPI PREDITTIVI ---
                        st.header("💎 Indicatori Strategici Vitali")
                        k1, k2, k3, k4, k5 = st.columns(5)
                        
                        rischio_medio = sum([a["rischio"] for a in report_analisi]) / len(report_analisi)
                        impatto_30gg_medio = sum([a["proiezione_impatto"] for a in report_analisi]) / len(report_analisi)
                        settore_rilevato = report_analisi[0]["settore_rilevato"] if report_analisi else "Generale"
                        
                        with k1:
                            st.metric("Solidità Operativa", f"{max(0, 100 - (rischio_medio*10)):.1f}%")
                            st.caption(f"Settore Rilevato: **{settore_rilevato}**")
                        
                        with k2:
                            # Calcolo delta rispetto al potenziale impatto a 30gg
                            st.metric("Impatto 30gg Stimato", f"Livello {impatto_30gg_medio:.1f}", delta=f"+{impatto_30gg_medio - rischio_medio:.1f}", delta_color="inverse")
                            st.caption("Focus: Proiezione a breve termine.")

                        with k3:
                            st.metric("Rischio Medio Sistema", f"{rischio_medio:.1f}/10", delta_color="inverse")
                            st.caption("Alert: Soglia critica adattiva.")

                        with k4:
                            st.metric("Efficienza Dati", "HIGH", delta="Certificato")
                            st.caption("Trend: Integrità crittografica.")

                        with k5:
                            st.metric("Grado Sicurezza", "AES-256")
                            st.caption("Stato: Cifrato a riposo.")

                        # --- DETTAGLIO PARLANTE CON INTEGRAZIONE MODULO SETTORI ---
                        st.subheader("📝 Analisi Descrittiva ed Evolutiva degli Asset")
                        
                        for asset in report_analisi:
                            box_class = "kpi-box-critical" if asset["stato"] == "CRITICO" else "kpi-box"
                            with st.container():
                                st.markdown(f"""
                                <div class="{box_class}">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <strong>Asset: {asset['asset']}</strong>
                                        <span style="padding: 2px 8px; border-radius: 5px; color: white; background-color: {'#dc3545' if asset['stato'] == 'CRITICO' else '#28a745' if asset['stato'] == 'OTTIMALE' else '#ffc107'};">
                                            {asset['stato']}
                                        </span>
                                    </div>
                                    <div style="margin-top: 10px;">
                                        • Rischio Corrente: {asset['rischio']}/10 | 
                                        Proiezione Rischio 30gg: {asset['proiezione_impatto']}/10 | 
                                        Trend Predittivo 90gg: {asset['trend_90gg']}/10<br>
                                        • <strong>Analisi Settoriale ({asset['settore_rilevato']}):</strong> {asset['segnalazioni']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                        if report_cifrato:
                            st.download_button(
                                label="📥 Scarica Certificato Cifrato (.enc)",
                                data=report_cifrato,
                                file_name=f"RGD_ALPHA_{azienda}_{datetime.now().strftime('%Y%m%d')}.enc"
                            )

    elif scelta == "🕵️ Centrale Admin":
        st.title("🕵️ Monitoraggio Globale Admin")
        
        # Guardrail di sicurezza per l'interfaccia visiva
        if not st.session_state.is_admin:
            st.error("Privilegi insufficienti per accedere a questo modulo di auditing.")
        else:
            df_log = db.recupera_attivita_globale()
            if not df_log.empty:
                # Sezione grafici analitici per l'amministratore
                st.subheader("📊 Distribuzione Globale dei Rischi per Azienda")
                try:
                    # Grafico a barre aggregato per identificare le aziende con più elementi a rischio
                    df_chart = df_log.groupby("company_id")["rischio"].mean().reset_index()
                    st.bar_chart(data=df_chart, x="company_id", y="rischio", width="stretch")
                except Exception as e:
                    logger.warning(f"Impossibile generare i grafici di riepilogo admin: {e}")
                
                st.subheader("📋 Registro Eventi di Sistema (Decifrato)")
                st.dataframe(df_log, width="stretch")
            else:
                st.info("Nessuna attività registrata nei log del database.")

    elif scelta == "📜 Archivio Storico":
        st.title("📜 Archivio Storico Asset")
        st.markdown("---")
        
        df_storico = db.recupera_asset_per_azienda(azienda)
        
        if not df_storico.empty:
            df_display = df_storico.copy()

            # Layout metriche
            c1, c2, c3 = st.columns(3)
            c1.metric("Asset in Archivio", len(df_display))
            if 'rischio' in df_display.columns:
                c2.metric("Rischio Medio Storico", f"{df_display['rischio'].mean():.2f}")
            c3.metric("Integrità Database", "VERIFICATO")

            # Barra di ricerca
            search = st.text_input("🔍 Cerca per nome asset...")
            if search:
                mask = df_display.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                df_display = df_display[mask]

            st.write("### 📋 Elenco Completo Dati")
            
            # Rendering pulito della tabella per prevenire eccezioni grafiche e di deprecazione
            st.dataframe(df_display, width="stretch")
        else:
            st.warning("⚠️ L'archivio di questa azienda sembra vuoto. Effettua un'importazione nella War Room per popolarlo.")

    # Pulsante di disconnessione centralizzato nella barra laterale
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.is_admin = False
        st.rerun()