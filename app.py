import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE LOGIN (mantenuta invariata) ---
UTENTI_VALIDI = {"AZIENDA_001": "pass123", "AZIENDA_002": "sicurezza456"}

# --- AREA RISERVATA (logica aggiornata) ---
# ... (mantieni la parte di login precedente) ...

    # --- UPLOAD DINAMICO ---
    st.subheader("Carica il tuo file dati (CSV)")
    uploaded_file = st.file_uploader("Trascina qui il tuo file fornitori/dati")
    
    # Cartella dedicata per azienda per evitare sovrapposizioni
    user_folder = f"uploads/{azienda}"
    if not os.path.exists(user_folder): os.makedirs(user_folder)

    if uploaded_file is not None:
        # Salviamo il file
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        
        # Leggiamo i dati dinamicamente
        df = pd.read_csv(uploaded_file)
        st.success(f"Dati caricati da {uploaded_file.name}")
        
        # Visualizzazione dinamica
        st.write("### Analisi dei tuoi dati")
        st.dataframe(df) # Tabella interattiva
        
        # Grafico automatico: usa la prima colonna numerica trovata
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.bar_chart(df.set_index(df.columns[0])[numeric_cols[0]])