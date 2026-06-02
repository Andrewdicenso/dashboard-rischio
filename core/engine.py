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

    py
    def _genera_consiglio_azione(self, rischio, settore):
        """Genera un consiglio pratico basato su rischio e settore rilevato."""
        if rischio > 8:
            if settore == "LOGISTICS":
                return "🚨 CRITICO: Avviare liquidazione immediata o svendita stock per liberare spazio e capitale."
            if settore == "FINANCE":
                return "🚨 CRITICO: Rischio perdita totale valore. Valutare accantonamento o revisione immediata contratti."
            return "🚨 CRITICO: Azione d'emergenza richiesta entro 48 ore."
        
        elif rischio > 5:
            if settore == "LOGISTICS":
                return "⚠️ ATTENZIONE: Pianificare promozione 'Bundle' o rotazione fisica verso zone di prelievo rapido."
            if settore == "RELATIONS":
                return "⚠️ ATTENZIONE: Contattare il fornitore per rinegoziare i tempi o cercare alternativa secondaria."
            return "⚠️ ATTENZIONE: Monitoraggio intensivo richiesto per i prossimi 7 giorni."
        
        else:
            return "✅ OTTIMALE: Mantenere le attuali politiche di riordino. Nessuna azione richiesta."

    def esegui_scan_strategico(self, lista_asset, contesto, fattore_stress=1.0):
        # ... (mantieni la logica esistente di rilevamento settore) ...
        config_settore = analizza_e_configura_motore(colonne)
        settore_rilevato = config_settore.get("settore", "GENERAL")
        
        report = []
        for asset in lista_asset:
            # ... (mantieni il calcolo del rischio_pesato) ...
            rischio_pesato = round(rischio_base * moltiplicatore_finale, 2)
            
            # --- NUOVA LOGICA: GENERAZIONE CONSIGLIO ---
            consiglio = self._genera_consiglio_azione(rischio_pesato, settore_rilevato)
            
            report.append({
                "asset": nome_asset,
                "stato": "CRITICO" if rischio_pesato > 7 else "ATTENZIONE" if rischio_pesato > 5 else "OTTIMALE",
                "rischio": rischio_pesato,
                "proiezione_impatto": proiezione_30gg,
                "consiglio_strategico": consiglio, # <--- IL VALORE AGGIUNTO
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