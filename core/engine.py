import sys
import logging
from pathlib import Path
from datetime import datetime

# ==============================================================================
# RISOLUZIONE DINAMICA DEL PATH PER STREAMLIT
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.secure_vault import SecureVault
from core.database import DatabaseAziendale
from core.experimental_modules.engine_settori import analizza_e_configura_motore

logger = logging.getLogger("RGD-Alpha.Gateway.Enterprise")

class DataGateway:
    def __init__(self):
        try:
            self.vault = SecureVault(key_path="core/security/vault.key")
            self.db = DatabaseAziendale()
        except Exception as e:
            logger.critical(f"Errore critico avvio componenti core: {e}")
            raise
        
        self.pesi_contesto = {
            "Magazzino": 1.2,
            "Fornitori": 1.5,
            "Performance Vendite": 1.0,
            "UNIVERSAL": 1.0
        }

    def _archivia_asset(self, asset, rischio_pesato):
        try:
            if isinstance(asset, dict):
                user_id = asset.get("user_id", 1)
                nome_asset = asset.get("nome", "Prodotto_Ignoto")
                tipo = asset.get("tipo", "GenericAsset")
                momentum = asset.get("momentum", "Stabile")
                volatilita = asset.get("volatilita", 0.0)
            else:
                user_id = getattr(asset, 'user_id', 1)
                nome_asset = getattr(asset, 'nome', 'Prodotto_Ignoto')
                tipo = getattr(asset, 'tipo', 'GenericAsset')
                momentum = getattr(asset, 'momentum', 'Stabile')
                volatilita = getattr(asset, 'volatilita', 0.0)

            self.db.salva_asset(
                user_id=user_id,
                nome_asset=nome_asset,
                rischio=rischio_pesato,
                tipo=tipo,
                momentum=momentum,
                volatilita=volatilita
            )
        except Exception as e:
            logger.warning(f"Archiviazione fallita: {e}")

    def esegui_scan_strategico(self, lista_asset, contesto, fattore_stress=1.0):
        """
        Analisi Avanzata RGD-ALPHA con WHAT-IF ANALYSIS.
        """
        colonne = []
        if lista_asset:
            primo_asset = lista_asset[0]
            if isinstance(primo_asset, dict):
                colonne = list(primo_asset.keys())
            else:
                colonne = list(vars(primo_asset).keys())
        
        config_settore = analizza_e_configura_motore(colonne)
        soglia_critica = config_settore["soglia"]
        
        # LOGICA WHAT-IF: Il moltiplicatore finale include lo stress test
        moltiplicatore_finale = config_settore["moltiplicatore"] * self.pesi_contesto.get(contesto, 1.0) * fattore_stress
        
        report = []
        for asset in lista_asset:
            nome_asset = asset.nome if not isinstance(asset, dict) else asset.get("nome", "Prodotto")
            rischio_base = asset.rischio if not isinstance(asset, dict) else asset.get("rischio", 0.0)
                
            rischio_pesato = round(rischio_base * moltiplicatore_finale, 2)
            self._archivia_asset(asset, rischio_pesato)
            
            proiezione_30gg = round(rischio_pesato * 1.25, 2)
            
            # Definizione stato
            stato_salute = "CRITICO" if rischio_pesato > soglia_critica else "OTTIMALE"
            if 5.0 < rischio_pesato <= soglia_critica:
                stato_salute = "ATTENZIONE"

            report.append({
                "asset": nome_asset,
                "stato": stato_salute,
                "rischio": rischio_pesato,
                "proiezione_impatto": proiezione_30gg,
                "alert": "🚨 STRESS TEST ATTIVO" if fattore_stress > 1.0 else "Nessuna anomalia"
            })
        return report

def salva_report_certificato(azienda, dati_report, vault):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        certificato = f"TS: {timestamp} | AZIENDA: {azienda} | VERIFIED BY RGD-ALPHA"
        return vault.encrypt_data(certificato)
    except:
        return None