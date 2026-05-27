import streamlit as st
import bcrypt
from core.database import DatabaseAziendale

st.set_page_config(page_title="Admin | Gestione Accessi", page_icon="🔐")

db = DatabaseAziendale()

st.title("🔐 Gestione Avanzata Accessi Utenti")

# Controllo permessi
if "user" not in st.session_state or st.session_state.user.get("ruolo") != "admin":
    st.error("Accesso riservato all'amministratore.")
    st.stop()

df_utenti = db.get_tutti_gli_utenti()

if df_utenti.empty:
    st.info("Nessun utente registrato.")
    st.stop()

st.subheader("📋 Utenti Registrati")
st.dataframe(df_utenti, use_container_width=True)

st.markdown("---")

st.subheader("⚙️ Azioni Amministrative")

email = st.text_input("Email utente da gestire")

if email:
    utente = db.get_utente_by_email(email)

    if not utente:
        st.warning("Nessun utente trovato.")
        st.stop()

    st.write(f"**Utente:** {utente['email']}")
    st.write(f"**Ruolo attuale:** {utente['ruolo']}")
    st.write(f"**Azienda:** {utente['azienda']}")

    st.markdown("### 🔄 Cambia Ruolo")
    nuovo_ruolo = st.selectbox("Nuovo ruolo", ["cliente", "admin"])

    if st.button("Aggiorna Ruolo"):
        try:
            with db._get_conn() as conn:
                conn.execute("UPDATE utenti SET ruolo = ? WHERE id = ?", (nuovo_ruolo, utente["id"]))
            st.success("Ruolo aggiornato.")
        except:
            st.error("Errore aggiornamento ruolo.")

    st.markdown("---")

    st.markdown("### 🔐 Reset Password")
    nuova_password = st.text_input("Nuova password", type="password")

    if st.button("Imposta nuova password"):
        if nuova_password:
            hashed = bcrypt.hashpw(nuova_password.encode(), bcrypt.gensalt()).decode()
            try:
                with db._get_conn() as conn:
                    conn.execute("UPDATE utenti SET password_hash = ? WHERE id = ?", (hashed, utente["id"]))
                st.success("Password aggiornata.")
            except:
                st.error("Errore aggiornamento password.")

    st.markdown("---")

    st.markdown("### 🚫 Sospendi / Riattiva Utente")
    stato = st.selectbox("Stato account", ["attivo", "sospeso"])

    if st.button("Aggiorna Stato"):
        try:
            with db._get_conn() as conn:
                conn.execute("UPDATE utenti SET ruolo = ? WHERE id = ?", (f"{stato}", utente["id"]))
            st.success("Stato aggiornato.")
        except:
            st.error("Errore aggiornamento stato.")
