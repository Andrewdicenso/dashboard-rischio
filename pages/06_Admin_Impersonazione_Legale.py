import streamlit as st
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Vista Cliente", page_icon="🛰️")

db = DatabaseAziendale()

st.title("🛰️ Vista Cliente (Modalità Sicura)")

if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

azienda = st.text_input("Inserisci il nome dell'azienda da visualizzare")

if azienda:
    st.subheader(f"📊 War Room (Modalità Lettura) — {azienda}")

    df_asset = db.recupera_asset_per_azienda(azienda)

    if df_asset.empty:
        st.warning("Nessun dato disponibile per questa azienda.")
    else:
        st.dataframe(df_asset, use_container_width=True)

    st.markdown("---")

    st.subheader("📜 Log Attività")
    df_log = db.recupera_attivita_globale()
    df_log = df_log[df_log["company_id"] == azienda]

    if df_log.empty:
        st.info("Nessuna attività registrata.")
    else:
        st.dataframe(df_log, use_container_width=True)
