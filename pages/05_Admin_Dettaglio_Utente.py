import streamlit as st
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Dettaglio Utente", page_icon="🔍")

db = DatabaseAziendale()

st.title("🔍 Dettaglio Utente")

# Controllo permessi
if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

email = st.text_input("Inserisci l'email dell'utente da ispezionare")

if email:
    utente = db.get_utente_by_email(email)

    if not utente:
        st.warning("Nessun utente trovato con questa email.")
        st.stop()

    st.subheader("📌 Informazioni Utente")
    st.write(f"**ID:** {utente['id']}")
    st.write(f"**Email:** {utente['email']}")
    st.write(f"**Ruolo:** {utente['ruolo']}")
    st.write(f"**Azienda:** {utente['azienda']}")

    st.markdown("---")

    st.subheader("📁 Asset Caricati dall'Azienda")
    df_asset = db.recupera_asset_per_azienda(utente["azienda"])
    if df_asset.empty:
        st.info("Nessun asset registrato.")
    else:
        st.dataframe(df_asset, use_container_width=True)

    st.markdown("---")

    st.subheader("📝 Log Attività Aziendali")
    df_log = db.recupera_attivita_globale()
    df_log = df_log[df_log["company_id"] == utente["azienda"]]

    if df_log.empty:
        st.info("Nessuna attività registrata.")
    else:
        st.dataframe(df_log, use_container_width=True)
