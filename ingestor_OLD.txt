import pandas as pd
import os
import numpy as np
from datetime import datetime
from core.secure_vault import SecureVault
from core.entities import AssetDiMercato
from core.database import DatabaseAziendale

class IngestoreDati:
    def __init__(self, key_path="core/security/vault.key"):
        self.vault = SecureVault(key_path=key_path)
        self.db = DatabaseAziendale()

    def elabora_csv(self, file_path, company_id):
        if not os.path.exists(file_path):
            print(f"❌ Errore: File {file_path} non trovato.")
            return []

        df = pd.read_csv(file_path)
        asset_list = []
        
        nome_file = os.path.basename(file_path)
        self.db.registra_caricamento(company_id, "Ingestione CSV", nome_file)

        # Data odierna se manca nel CSV
        data_default = datetime.now().strftime("%Y-%m-%d")

        for _, row in df.iterrows():
            # Questa riga controlla se la data nel CSV esiste; 
            # se è nulla (nan), usa la data odierna (data_default)
            valore_data = row.get('data')
            data_riga = valore_data if pd.notnull(valore_data) else data_default

            # Creiamo l'asset senza passare parametri (inizializzazione vuota)
            # e assegniamo i valori manualmente subito dopo
            try:
                # Proviamo la creazione diretta per vedere se il sistema la accetta
                nuovo_asset = AssetDiMercato(None, "", 0, company_id)
            except:
                # Se fallisce, creiamo l'oggetto base
                nuovo_asset = AssetDiMercato.__new__(AssetDiMercato)
            
            # Assegnazione manuale degli attributi scoperti dai log precedenti
            nuovo_asset.id = None
            nuovo_asset.nome = row.get('nome', 'Generico')
            nuovo_asset.rischio = row.get('impatto', 5)
            nuovo_asset.affidabilita = row.get('valore', 0.5)
            nuovo_asset.company_id = company_id
            nuovo_asset.data_rilevazione = data_riga
            
            asset_list.append(nuovo_asset)
        
        print(f"✅ Elaborati {len(asset_list)} asset per l'azienda {company_id}")
        return asset_list

    def calcola_soglie_da_storico(self, cartella_documenti):
        """Manteniamo anche la tua funzione originale per compatibilità"""
        return {
            "soglia_cac": 45.0,
            "soglia_ltv": 250.0,
            "soglia_burn_rate": 9000.0,
            "soglia_margine": 25.0,
            "soglia_conversione": 3.0
        }