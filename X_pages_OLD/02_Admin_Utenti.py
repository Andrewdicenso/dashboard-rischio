import streamlit as st
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Utenti", page_icon="🧑‍💻")

db = DatabaseAziendale()

st.title("🧑‍💻 Gestione Utenti Registrati")

if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

df_utenti = db.get_tutti_gli_utenti()

if df_utenti.empty:
    st.info("Nessun utente registrato.")
else:
    st.subheader("Elenco Utenti")
    st.dataframe(df_utenti[["id", "email", "ruolo", "azienda", "data_creazione"]], use_container_width=True)
