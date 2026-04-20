from core.secure_vault import SecureVault

class DataGateway:
    def __init__(self, storage_provider):
        self.storage = storage_provider
        self.vault = SecureVault() # Inizializza la sicurezza

    def save_entity(self, entity_name, data):
        # 1. Cripta il dato PRIMA di salvarlo
        encrypted_data = self.vault.encrypt_data(str(data))
        # 2. Salva il dato criptato
        return self.storage.write(entity_name, encrypted_data)

    def esegui_scan_strategico(self, lista_asset):
        """Scansiona una lista di asset e restituisce solo quelli che richiedono attenzione."""
        report = []
        for asset in lista_asset:
            # Controlliamo se l'asset ha un metodo di allerta
            if hasattr(asset, 'genera_alert'):
                alert = asset.genera_alert()
                if alert["stato"] == "CRITICO":
                    report.append(alert)
        return report