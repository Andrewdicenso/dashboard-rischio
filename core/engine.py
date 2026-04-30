# core/engine.py
from core.secure_vault import SecureVault
from core.database import DatabaseAziendale
import logging
from datetime import datetime

# Configurazione logging avanzato per Audit Aziendale
logger = logging.getLogger("RGD-Alpha.Gateway.Enterprise")

class DataGateway:
    """
    Gateway Enterprise: Sistema di analisi, protezione e simulazione predittiva.
    """
    def __init__(self):
        try:
            # Percorso centralizzato secondo la nuova struttura
            self.vault = SecureVault(key_path="core/security/vault.key")
            self.db = DatabaseAziendale()
        except Exception as e:
            logger.critical(f"Errore critico avvio componenti core: {e}")
            raise
        
        # Pesi strategici: riflettono la sensibilità del business
        self.pesi_contesto = {
            "Magazzino": 1.2,
            "Fornitori": 1.5,
            "Performance Vendite": 1.0
        }

    def _archivia_asset(self, asset, rischio_pesato):
        """Salvataggio silenzioso nel DB per alimentare l'Analyst."""
        try:
            self.db.salva_asset(
                company_id=getattr(asset, 'company_id', 'SYSTEM_CORE'),
                nome_asset=getattr(asset, 'nome', 'Prodotto_Ignoto'),
                rischio=rischio_pesato
            )
        except Exception as e:
            logger.warning(f"Archiviazione fallita per asset {getattr(asset, 'nome', '?')}: {e}")

    def esegui_scan_strategico(self, lista_asset, contesto):
        """Analisi Estesa: calcola il rischio attuale e simula l'impatto futuro."""
        moltiplicatore = self.pesi_contesto.get(contesto, 1.0)
        report = []
        
        requisiti = {
            "Magazzino": {"col": "quantita", "base": 50, "impatto": "Liquidità"},
            "Fornitori": {"col": "stato", "base": "Attivo", "impatto": "Continuità"},
            "Performance Vendite": {"col": "volume", "base": 100, "impatto": "Crescita"}
        }

        # 1. VALIDAZIONE ANALITICA
        if contesto in requisiti:
            req = requisiti[contesto]
            if lista_asset and not hasattr(lista_asset[0], req["col"]):
                return [{"asset": "SISTEMA", "stato": "CONFIGURAZIONE SOSPESA", "rischio": 0, 
                         "segnalazioni": f"Dato '{req['col']}' mancante. Proiezione impossibile."}]

        # 2. MOTORE DI CALCOLO E ARCHIVIAZIONE
        soglie = {"Magazzino": 7.5, "Fornitori": 6.0, "Performance Vendite": 8.0}
        soglia = soglie.get(contesto, 7.0)

        for asset in lista_asset:
            rischio_base = getattr(asset, 'rischio', 0)
            rischio_pesato = rischio_base * moltiplicatore
            
            # SCALABILITÀ: Alimenta il DB per l'analisi predittiva futura
            self._archivia_asset(asset, rischio_pesato)
            
            proiezione_danni = (rischio_pesato * 1.5)
            
            dettagli_alert = []
            if contesto == "Magazzino" and hasattr(asset, 'quantita') and asset.quantita < requisiti["Magazzino"]["base"]:
                dettagli_alert.append("Scorte scarse: rischio rottura stock. Impatto Liquidità: Alto.")
            
            if rischio_pesato > soglia:
                dettagli_alert.append(f"Rischio ({round(rischio_pesato, 2)}) sopra soglia.")
                dettagli_alert.append(f"Proiezione danno 30gg: livello {round(proiezione_danni, 1)}.")

            if dettagli_alert:
                report.append({
                    "asset": getattr(asset, 'nome', 'Prodotto'),
                    "stato": "CRITICO" if rischio_pesato > soglia else "ATTENZIONE",
                    "rischio": round(rischio_pesato, 2),
                    "proiezione_impatto": round(proiezione_danni, 2),
                    "segnalazioni": " ".join(dettagli_alert)
                })
        
        logger.info(f"Scan {contesto} completato. Generati {len(report)} alert.")
        return report

def salva_report_certificato(azienda, dati_report, vault):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        certificato = f"TS: {timestamp} | AZIENDA: {azienda} | DATA: {str(dati_report)}"
        return vault.encrypt_data(certificato)
    except Exception as e:
        logger.error(f"Errore certificazione: {e}")
        return None