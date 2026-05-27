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

COMPANY_ID = "AZ-TEST-01"  # Deve essere lo stesso della dashboard

# Inizializzazione moduli core
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
            lista_asset = ingestor.elabora_csv(temp_path, COMPANY_ID)

            # Registrazione nel database
            db.registra_caricamento(COMPANY_ID, "UPLOAD_WEB", uploaded_file.name)

            st.success(f"✅ Importazione completata! {len(lista_asset)} asset registrati.")
            os.remove(temp_path)

        except Exception as e:
            st.error(f"❌ Errore durante l'importazione: {e}")

else:
    st.info("⬆️ Carica un file CSV per iniziare.")
