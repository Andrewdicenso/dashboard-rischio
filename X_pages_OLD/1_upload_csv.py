import streamlit as st
import pandas as pd
import os

from core.ingestor import IngestoreDati
from core.database import DatabaseAziendale

# ---------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------
st.set_page_config(page_title="Upload CSV - RGandja", layout="wide")
st.title("📤 Caricamento CSV Aziendale")
st.write("Carica un file CSV per importare automaticamente gli asset nel sistema RGandja.")

# ---------------------------------------------------------
# VERIFICA LOGIN
# ---------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Devi effettuare il login per accedere a questa pagina.")
    st.stop()

utente = st.session_state.user
user_id = utente["id"]
azienda = utente["azienda"]

# ---------------------------------------------------------
# INIZIALIZZAZIONE MODULI CORE
# ---------------------------------------------------------
ingestor = IngestoreDati()
db = DatabaseAziendale()

# ---------------------------------------------------------
# UPLOAD FILE
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Seleziona un file CSV", type=["csv"])

if uploaded_file is not None:
    st.success("📄 File caricato correttamente!")

    # Mostra anteprima
    df_preview = pd.read_csv(uploaded_file)
    st.subheader("📊 Anteprima del file")
    st.dataframe(df_preview)

    # Pulsante per importare
    if st.button("🚀 Importa nel Sistema"):
        try:
            # Salvataggio temporaneo
            temp_path = "data/temp_upload.csv"
            df_preview.to_csv(temp_path, index=False)

            # Elaborazione tramite IngestoreDati
            lista_asset = ingestor.elabora_csv(temp_path, azienda)

            # Registrazione nel database (multi-tenant)
            db.registra_caricamento(user_id, "UPLOAD_WEB", uploaded_file.name)

            st.success(f"✅ Importazione completata! {len(lista_asset)} asset registrati per {azienda}.")
            os.remove(temp_path)

        except Exception as e:
            st.error(f"❌ Errore durante l'importazione: {e}")

else:
    st.info("⬆️ Carica un file CSV per iniziare.")

