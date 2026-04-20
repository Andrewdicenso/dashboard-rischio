from core.entities import AssetDiValore
from core.secure_vault import SecureVault

class IngestorStrategico:
    def __init__(self):
        self.vault = SecureVault()

    def da_csv(self, file_path):
        asset_list = []
        dati_grezzi = [
            {"id": 4, "nome": "Nuovo Componente", "costo": 20, "prezzo": 40, "rischio": 3},
            {"id": 5, "nome": "Fornitura a Rischio", "costo": 100, "prezzo": 105, "rischio": 9}
        ]
        
        for riga in dati_grezzi:
            # Protezione immediata: criptiamo il nome dell'asset appena lo leggiamo
            nome_criptato = self.vault.encrypt_data(riga["nome"])
            
            asset = AssetDiValore(riga["id"], nome_criptato, riga["costo"], riga["prezzo"], riga["rischio"])
            asset_list.append(asset)
            
        return asset_list