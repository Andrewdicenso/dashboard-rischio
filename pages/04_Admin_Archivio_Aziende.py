import streamlit as st
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Archivio Aziende", page_icon="🏢")

db = DatabaseAziendale()

st.title("🏢 Archivio Storico per Azienda")

if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

azienda = st.text_input("ID Azienda da ispezionare")

if azienda:
    df = db.recupera_asset_per_azienda(azienda)
    if df.empty:
        st.warning("Nessun dato per questa azienda.")
    else:
        st.dataframe(df, use_container_width=True)
