from core.entities import AssetDiValore
from core.secure_vault import SecureVault
import os

class IngestorStrategico:
    def __init__(self):
        # SecureVault ora gestisce automaticamente la persistenza della chiave in data/vault.key
        self.vault = SecureVault(key_path="data/vault.key")

    def da_csv(self, file_path):
        """
        Legge i dati e li protegge immediatamente.
        Assicurarsi che file_path sia un percorso valido in data/uploads/
        """
        if not os.path.exists(file_path):
            print(f"ERRORE: File non trovato in {file_path}")
            return []

        asset_list = []
        # Qui in futuro potresti aggiungere la lettura reale con pandas:
        # df = pd.read_csv(file_path)
        
        # Dati simulati per mantenere la logica attuale
        dati_grezzi = [
            {"id": 4, "nome": "Nuovo Componente", "costo": 20, "prezzo": 40, "rischio": 3},
            {"id": 5, "nome": "Fornitura a Rischio", "costo": 100, "prezzo": 105, "rischio": 9}
        ]
        
        for riga in dati_grezzi:
            # Protezione immediata: il nome viene criptato prima di entrare nell'entità
            nome_criptato = self.vault.encrypt_data(riga["nome"])
            
            asset = AssetDiValore(
                riga["id"], 
                nome_criptato, 
                riga["costo"], 
                riga["prezzo"], 
                riga["rischio"]
            )
            asset_list.append(asset)
            
        return asset_list