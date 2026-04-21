from core.entities import AssetDiValore
from core.secure_vault import SecureVault
import os
import pandas as pd

class IngestorStrategico:
    def __init__(self):
        self.vault = SecureVault(key_path="data/vault.key")

    def da_csv(self, file_path, contesto):
        """
        Legge i dati, applica la logica specifica per contesto e protegge le informazioni.
        """
        if not os.path.exists(file_path):
            print(f"ERRORE: File non trovato in {file_path}")
            return []

        # Lettura reale del file
        df = pd.read_csv(file_path)
        asset_list = []

        # Logica di riconoscimento basata sul contesto
        for _, riga in df.iterrows():
            nome = riga["nome"]
            rischio = riga["rischio"]
            
            # Applicazione regole di business specifiche per contesto
            if contesto == "Magazzino":
                # Esempio: Il magazzino applica una penalità di rischio maggiore su item a bassa rotazione
                rischio = rischio * 1.2 
            elif contesto == "Fornitori":
                # Esempio: I fornitori sono valutati più severamente
                rischio = rischio * 1.5
            
            # Protezione dati sensibili
            nome_criptato = self.vault.encrypt_data(str(nome))
            
            # Creazione entità
            asset = AssetDiValore(
                id=riga["id"],
                nome=nome_criptato,
                costo=riga.get("costo", 0),
                prezzo=riga.get("prezzo", 0),
                rischio=rischio
            )
            asset_list.append(asset)
            
        print(f"INGESTOR: Elaborati {len(asset_list)} asset per contesto '{contesto}'.")
        return asset_list