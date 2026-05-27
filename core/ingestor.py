import pandas as pd
import os
from datetime import datetime
from core.secure_vault import SecureVault
from core.entities import AssetDiMercato, AssetDiValore, AssetDiRelazione, AssetStrategico
from core.database import DatabaseAziendale

class IngestoreDati:
    """
    INGESTORE UNIVERSALE RGD-ALPHA:
    Sistema adattivo capace di mappare qualsiasi documento aziendale.
    Include auto-rilevamento del settore e protezione contro i crash di sistema.
    """
    def __init__(self, key_path="core/security/vault.key"):
        self.vault = SecureVault(key_path=key_path)
        self.db = DatabaseAziendale()
        
        # Dizionario esteso per includere i termini dei file reali
        self.mappa_sinonimi = {
            'quantita': ['quantita', 'pezzi', 'qta', 'stock', 'unita', 'Quantita'],
            'valore': ['prezzo', 'importo', 'lordo', 'valore', 'costo', 'ammontare', 'Costo_Unitario'],
            'rischio': ['rischio', 'impatto', 'criticità', 'priorità', 'Rischio_Logistico'],
            'stato': ['stato', 'condizione', 'status', 'pagamento', 'disponibilita', 'Stato_Qualita']
        }

    def _auto_rilevamento_settore(self, colonne):
        """Analizza le intestazioni per capire se è Logistica, Finance o Relazioni."""
        colonne_lower = [str(c).lower() for c in colonne]
        
        if any(term in colonne_lower for term in ['fattura', 'iban', 'lordo', 'costo_unitario']):
            return "FINANCE", AssetDiValore
        if any(term in colonne_lower for term in ['bolla', 'ddt', 'magazzino', 'quantita', 'sku', 'ubicazione']):
            return "LOGISTICS", AssetDiMercato
        if any(term in colonne_lower for term in ['cliente', 'fornitore', 'crm', 'fornitore_origine']):
            return "RELATIONS", AssetDiRelazione
        
        return "GENERAL", AssetStrategico

    def _estrai_dato(self, row, categoria_chiave, default=0):
        """Cerca il dato usando i sinonimi definiti sopra."""
        for sinonimo in self.mappa_sinonimi.get(categoria_chiave, []):
            val = row.get(sinonimo)
            if val is not None:
                return val
        return default

    def elabora_csv(self, file_path, company_id):
        # PROTEZIONE CRITICA: Inizializziamo sempre come lista vuota per evitare NoneType
        asset_list = [] 
        
        if not os.path.exists(file_path):
            print(f"❌ Errore: File {file_path} non trovato.")
            return asset_list

        try:
            # Lettura con gestione errori
            df = pd.read_csv(file_path)
            
            # Rilevamento automatico del reparto
            settore_nome, ClasseAsset = self._auto_rilevamento_settore(df.columns)
            self.db.registra_caricamento(company_id, f"Ingestione {settore_nome}", os.path.basename(file_path))

            for _, row in df.iterrows():
                # Creiamo il dizionario base con i dati certi
                dati_riga = row.to_dict()
                
                # Integriamo i campi fondamentali per RGD-Alpha
                dati_riga['id_asset'] = row.get('ID_Movimento', row.get('id', row.get('ID')))
                dati_riga['nome'] = row.get('Descrizione_Asset', row.get('nome', 'Asset_Generico'))
                dati_riga['rischio'] = float(self._estrai_dato(row, 'rischio', 5.0))
                dati_riga['company_id'] = company_id
                dati_riga['data'] = row.get('Data_Registrazione', row.get('data', datetime.now().strftime("%Y-%m-%d")))

                try:
                    # Inizializzazione della classe (grazie a **kwargs in entities.py accetta tutto)
                    nuovo_asset = ClasseAsset(**dati_riga)
                    
                    # Genera i KPI interni se il metodo esiste
                    if hasattr(nuovo_asset, 'genera_kpi_strategici'):
                        nuovo_asset.genera_kpi_strategici()
                    
                    asset_list.append(nuovo_asset)
                except Exception as e:
                    print(f"⚠️ Salto riga per errore formato: {e}")

        except Exception as e:
            print(f"❌ Errore durante l'elaborazione del file: {e}")
        
        # Restituisce sempre la lista (piena o vuota), garantendo stabilità ad app.py
        return asset_list