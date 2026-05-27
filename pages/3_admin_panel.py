import streamlit as st
import pandas as pd
import os
import sqlite3

from core.database import DatabaseAziendale

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Admin Panel - RGandja", layout="wide")
st.title("🛠️ Pannello Amministratore - RGandja")

# ---------------------------------------------------------
# INIZIALIZZAZIONE DATABASE
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "db", "azienda.db")

db = DatabaseAziendale(db_folder=os.path.dirname(DB_PATH), db_name=os.path.basename(DB_PATH))

# ---------------------------------------------------------
# FUNZIONI DI SUPPORTO
# ---------------------------------------------------------
def carica_tabella(nome_tabella: str) -> pd.DataFrame:
    """Carica una tabella generica dal database SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {nome_tabella}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento della tabella {nome_tabella}: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# SEZIONI ADMIN
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📥 Caricamenti", "📨 Richieste"])

# ------------------ TAB 1: CARICAMENTI -------------------
with tab1:
    st.subheader("📥 Storico Caricamenti Dati")

    df_caricamenti = carica_tabella("caricamenti")

    if df_caricamenti.empty:
        st.info("Nessun caricamento registrato.")
    else:
        df_caricamenti = df_caricamenti.sort_values("timestamp", ascending=False)
        st.dataframe(df_caricamenti, use_container_width=True)

# ------------------ TAB 2: RICHIESTE ---------------------
with tab2:
    st.subheader("📨 Storico Richieste")

    df_richieste = carica_tabella("richieste")

    if df_richieste.empty:
        st.info("Nessuna richiesta registrata.")
    else:
        df_richieste = df_richieste.sort_values("timestamp", ascending=False)
        st.dataframe(df_richieste, use_container_width=True)
