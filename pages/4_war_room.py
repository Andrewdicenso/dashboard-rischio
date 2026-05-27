import streamlit as st
import pandas as pd
import plotly.express as px
import os

from core.database import DatabaseAziendale
from core.analyst import AnalistaRischio

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(page_title="War Room - RGandja", layout="wide")
st.title("🚨 WAR ROOM - Monitoraggio Criticità in Tempo Reale")

COMPANY_ID = "AZ-TEST-01"

# ---------------------------------------------------------
# INIZIALIZZAZIONE
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "db", "azienda.db")

db = DatabaseAziendale(db_folder=os.path.dirname(DB_PATH), db_name=os.path.basename(DB_PATH))
analista = AnalistaRischio(db=db)

# ---------------------------------------------------------
# RECUPERO DATI
# ---------------------------------------------------------
df = db.recupera_asset_per_azienda(COMPANY_ID)

if df.empty:
    st.warning("⚠️ Nessun dato disponibile. Importa prima dei CSV.")
    st.stop()

# ---------------------------------------------------------
# CALCOLO RISCHI E TREND
# ---------------------------------------------------------
st.subheader("🔥 Asset con rischio più elevato")

df_rischio = df.groupby("nome")["rischio"].mean().reset_index()
df_rischio = df_rischio.sort_values("rischio", ascending=False)

st.dataframe(df_rischio, use_container_width=True)

# ---------------------------------------------------------
# ASSET CRITICI
# ---------------------------------------------------------
critici = df_rischio[df_rischio["rischio"] >= 7]

st.markdown("---")
st.subheader("🚨 Asset Critici (Rischio ≥ 7)")

if critici.empty:
    st.success("Nessun asset critico al momento.")
else:
    st.error("⚠️ ATTENZIONE: Sono presenti asset critici!")
    st.dataframe(critici, use_container_width=True)

# ---------------------------------------------------------
# TREND NEGATIVI
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📉 Trend Negativi (Peggioramento)")

trend_negativi = []

for asset in df["nome"].unique():
    report = analista.calcola_trend_predittivo(asset, COMPANY_ID)
    if report["delta_immediato"] > 0 and report["pendenza_trend"] > 0:
        trend_negativi.append({
            "asset": asset,
            "rischio_attuale": report["valore_attuale"],
            "delta": report["delta_immediato"],
            "pendenza": report["pendenza_trend"]
        })

if not trend_negativi:
    st.success("Nessun trend negativo rilevato.")
else:
    df_trend = pd.DataFrame(trend_negativi)
    st.warning("⚠️ Sono presenti asset in peggioramento!")
    st.dataframe(df_trend, use_container_width=True)

# ---------------------------------------------------------
# GRAFICO RIEPILOGATIVO
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Distribuzione del Rischio")

fig = px.histogram(
    df,
    x="rischio",
    nbins=10,
    title="Distribuzione dei livelli di rischio",
    color_discrete_sequence=["#FF4B4B"]
)

st.plotly_chart(fig, use_container_width=True)
