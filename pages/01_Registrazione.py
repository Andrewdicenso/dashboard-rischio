import streamlit as st
import bcrypt
from core.database import DatabaseAziendale

st.set_page_config(page_title="Registrazione | RGD-Alpha", page_icon="📝")

db = DatabaseAziendale()

st.title("📝 Registrazione Nuovo Account")

st.markdown("""
Compila i campi per creare un nuovo account aziendale.
L'accesso sarà immediatamente disponibile dopo la registrazione.
""")

email = st.text_input("Email aziendale")
password = st.text_input("Password", type="password")
password2 = st.text_input("Conferma Password", type="password")
azienda = st.text_input("Nome Azienda")

if st.button("Crea Account"):
    if not email or not password or not password2 or not azienda:
        st.error("⚠️ Tutti i campi sono obbligatori.")
    elif password != password2:
        st.error("⚠️ Le password non coincidono.")
    else:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            db.crea_utente(email, hashed, "cliente", azienda)
            st.success("🎉 Account creato con successo! Ora puoi effettuare il login.")
        except Exception:
            st.error("❌ Errore: email già registrata o problema interno.")
