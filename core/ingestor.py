import pandas as pd
import os
from datetime import datetime
from core.secure_vault import SecureVault
from core.entities import AssetDiMercato
from core.database import DatabaseAziendale

class IngestoreDati:
    def __init__(self, key_path="core/security/vault.key"):
        self.vault = SecureVault(key_path=key_path)
        self.db = DatabaseAziendale() # Connessione per logging admin

    def elabora_csv(self, file_path, company_id):
        if not os.path.exists(file_path):
            print(f"❌ Errore: File {file_path} non trovato.")
            return []

        df = pd.read_csv(file_path)
        asset_list = []
        
        # Registrazione attività nel log admin (Scalabilità & Supervisione)
        nome_file = os.path.basename(file_path)
        self.db.registra_caricamento(company_id, "Ingestione CSV", nome_file)

        # Otteniamo la data odierna come fallback (standard)
        data_default = datetime.now().strftime("%Y-%m-%d")

        for _, row in df.iterrows():
            # LOGICA "VIAGGIO NEL TEMPO":
            # Cerchiamo una colonna 'data'. Se non c'è, usiamo quella odierna.
            data_riga = row.get('data', data_default)

            nuovo_asset = AssetDiMercato(
                id_asset=None, 
                nome=row.get('nome', 'Asset_Generico'), 
                valore=row.get('valore', 0.5), 
                impatto=row.get('impatto', 5),
                data_rilevazione=data_riga  # Passiamo la data (storica o attuale)
            )
            asset_list.append(nuovo_asset)
        
        print(f"✅ Elaborati {len(asset_list)} asset per l'azienda {company_id} (Data: {data_riga if 'data' in df.columns else 'Odierna'})")
        return asset_list

    def cifra_report_finale(self, contenuto_report, output_path):
        encrypted_data = self.vault.encrypt_data(str(contenuto_report))
        with open(output_path, "wb") as f:
            f.write(encrypted_data)
        print(f"🔐 Report cifrato in: {output_path}")