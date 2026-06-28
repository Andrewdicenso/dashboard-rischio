import streamlit as st
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Log Attività", page_icon="📜")

db = DatabaseAziendale()

st.title("📜 Log Attività Globali")

if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

df_log = db.recupera_attivita_globale()

if df_log.empty:
    st.info("Nessuna attività registrata.")
else:
    st.subheader("Registro Eventi")
    st.dataframe(df_log, use_container_width=True)
