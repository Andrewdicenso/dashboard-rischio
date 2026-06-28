import streamlit as st
import plotly.graph_objects as go
import os
import json

from core.consulente import ConsulenteAziendale

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(page_title="KPI Dashboard - RGandja", layout="wide")
st.title("📊 KPI Aziendali - RGandja Intelligence")

# ---------------------------------------------------------
# CARICAMENTO CONFIGURAZIONE
# ---------------------------------------------------------
CONFIG_PATH = os.path.join("config.json")

if not os.path.exists(CONFIG_PATH):
    st.error("❌ File config.json non trovato. Impossibile caricare i KPI.")
    st.stop()

COMPANY_ID = st.session_state.get("COMPANY_ID", "AZIENDA_01")
kpi = consulente.get_all_kpi()

# ---------------------------------------------------------
# FUNZIONE PER CREARE INDICATORI KPI
# ---------------------------------------------------------
def kpi_card(titolo, valore, delta, suffix=""):
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=valore,
        number={"suffix": suffix},
        delta={"reference": valore - delta, "relative": True},
        title={"text": titolo}
    ))
    fig.update_layout(height=200)
    return fig

# ---------------------------------------------------------
# VISUALIZZAZIONE KPI
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

with col1:
    st.plotly_chart(kpi_card("CAC", kpi["cac"], kpi["cac_delta"]), use_container_width=True)

with col2:
    st.plotly_chart(kpi_card("LTV", kpi["ltv"], kpi["ltv_delta"]), use_container_width=True)

with col3:
    st.plotly_chart(kpi_card("Churn Rate", kpi["churn"], kpi["churn_delta"], suffix=""), use_container_width=True)

with col4:
    st.plotly_chart(kpi_card("ROI", kpi["roi"], kpi["roi_delta"], suffix=""), use_container_width=True)

with col5:
    st.plotly_chart(kpi_card("Efficienza", kpi["eff"], 0, suffix=""), use_container_width=True)

# ---------------------------------------------------------
# SPIEGAZIONE KPI
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📘 Interpretazione KPI")

st.write("""
- **CAC (Costo Acquisizione Cliente)**  
  Quanto spendi per ottenere un nuovo cliente.

- **LTV (Valore del Cliente nel Tempo)**  
  Quanto guadagni da un cliente durante tutto il suo ciclo di vita.

- **Churn Rate**  
  Percentuale di clienti che abbandonano.

- **ROI (Ritorno sull’Investimento)**  
  Quanto rende ogni euro investito.

- **Efficienza Operativa**  
  Quanto bene l’azienda utilizza le proprie risorse.
""")
