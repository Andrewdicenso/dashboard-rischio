from core.secure_vault import SecureVault

class DataGateway:
    def __init__(self, storage_provider):
        self.storage = storage_provider
        self.vault = SecureVault(key_path="data/vault.key")

    def save_entity(self, entity_name, data):
        encrypted_data = self.vault.encrypt_data(str(data))
        return self.storage.write(entity_name, encrypted_data)

    def esegui_scan_strategico(self, lista_asset, contesto):
        """
        Scansiona la lista asset applicando logiche di soglia dinamiche 
        basate sul contesto (Magazzino, Fornitori, ecc.).
        """
        report = []
        
        # Definiamo soglie critiche dinamiche in base al contesto
        soglie = {
            "Magazzino": 7.5,
            "Fornitori": 6.0,
            "Performance Vendite": 8.0
        }
        
        soglia_critica = soglie.get(contesto, 7.0) # Default a 7.0 se contesto non trovato
        
        for asset in lista_asset:
            # Recuperiamo il valore di rischio (decriptando se necessario o usando attributo)
            # Assumiamo che l'asset abbia un attributo 'rischio'
            rischio_attuale = asset.rischio
            
            if rischio_attuale >= soglia_critica:
                # Se l'asset ha un metodo alert, lo usiamo, altrimenti creiamo un alert base
                alert = asset.genera_alert() if hasattr(asset, 'genera_alert') else {
                    "stato": "CRITICO",
                    "messaggio": f"Rischio elevato ({rischio_attuale}) rilevato in {contesto}"
                }
                report.append(alert)
                
        return report