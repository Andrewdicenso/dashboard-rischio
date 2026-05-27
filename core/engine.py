# core/engine.py
from core.secure_vault import SecureVault
from core.database import DatabaseAziendale
import logging
from datetime import datetime
from experimental_modules.engine_settori import analizza_e_configura_motore

# Configurazione logging avanzato per Audit Aziendale
logger = logging.getLogger("RGD-Alpha.Gateway.Enterprise")

class DataGateway:
    """
    Gateway Enterprise: Sistema di analisi, protezione e simulazione predittiva.
    Gestisce il flusso dati tra l'ingestione e l'archiviazione storica.
    """
    def __init__(self):
        try:
            # Percorso centralizzato: garantisce l'avvio indipendentemente dal punto di esecuzione
            self.vault = SecureVault(key_path="core/security/vault.key")
            self.db = DatabaseAziendale()
        except Exception as e:
            logger.critical(f"Errore critico avvio componenti core: {e}")
            raise
        
        # Pesi strategici: riflettono la sensibilità del business
        self.pesi_contesto = {
            "Magazzino": 1.2,
            "Fornitori": 1.5,
            "Performance Vendite": 1.0,
            "UNIVERSAL": 1.0  # Allineamento con la Dashboard principale
        }

    def _archivia_asset(self, asset, rischio_pesato):
        """Salvataggio nel DB per alimentare l'Analisi Storica e Predittiva."""
        try:
            self.db.salva_asset(
                company_id=getattr(asset, 'company_id', 'SYSTEM_CORE'),
                nome_asset=getattr(asset, 'nome', 'Prodotto_Ignoto'),
                rischio=rischio_pesato
            )
        except Exception as e:
            logger.warning(f"Archiviazione fallita per asset {getattr(asset, 'nome', '?')}: {e}")

    def esegui_scan_strategico(self, lista_asset, contesto):
        """
        Analisi Avanzata RGD-ALPHA: Integra il riconoscimento automatico del settore
        con proiezioni predittive a 30 e 90 giorni.
        """
        # 1. Identificazione automatica del settore e configurazione dinamica
        # Estraiamo le chiavi principali e quelle annidate dentro dati_extra
        colonne = []
        if lista_asset:
            # Estrae gli attributi esterni dall'oggetto (nome, rischio, company_id, ecc.)
            colonne = list(vars(lista_asset[0]).keys())
            
            # Se l'oggetto contiene il dizionario dati_extra, estrae anche le chiavi interne (scadenza, lotto)
            if hasattr(lista_asset[0], 'dati_extra') and isinstance(lista_asset[0].dati_extra, dict):
                colonne.extend(lista_asset[0].dati_extra.keys())
        
        # --- LOG DI DIAGNOSI PER IL TERMINALE ---
        print("\n" + "="*50)
        print(f"🔍 [DIAGNOSI RGD-ALPHA] Asset analizzati: {len(lista_asset)}")
        print(f"📋 Tutte le chiavi rilevate (incluse extra): {colonne}")
        if lista_asset:
            print(f"📄 Esempio dati extra primo asset: {getattr(lista_asset[0], 'dati_extra', {})}")
        print("="*50 + "\n")
        
        config_settore = analizza_e_configura_motore(colonne)
        
        # 2. Parametri dinamici dal modulo settori
        soglia_critica = config_settore["soglia"]
        moltiplicatore_settore = config_settore["moltiplicatore"]
        moltiplicatore_contesto = self.pesi_contesto.get(contesto, 1.0)
        
        # Moltiplicatore finale combinato
        moltiplicatore_finale = moltiplicatore_settore * moltiplicatore_contesto
        
        report = []
        for asset in lista_asset:
            rischio_base = getattr(asset, 'rischio', 0)
            rischio_pesato = round(rischio_base * moltiplicatore_finale, 2)
            
            # --- ALIMENTAZIONE DATABASE ---
            self._archivia_asset(asset, rischio_pesato)
            
            # --- MOTORE PREDITTIVO (Evoluzione 2026) ---
            proiezione_30gg = round(rischio_pesato * 1.25, 2)
            proiezione_90gg = round(rischio_pesato * 1.5, 2)
            
            dettagli_alert = []
            
            # Logica di segnalazione basata sul settore e rischio
            if rischio_pesato > soglia_critica:
                dettagli_alert.append(f"⚠️ [{config_settore['settore']}] Rischio Critico: {rischio_pesato}.")
                dettagli_alert.append(f"PIANO AZIONE: {config_settore['consiglio']}")
            
            # Definizione stato salute
            stato_salute = "CRITICO" if rischio_pesato > soglia_critica else "OTTIMALE"
            if 5.0 < rischio_pesato <= soglia_critica:
                stato_salute = "ATTENZIONE"
                dettagli_alert.append("Trend in crescita: monitoraggio consigliato.")

            # Costruzione record per la War Room
            report.append({
                "asset": getattr(asset, 'nome', 'Prodotto'),
                "stato": stato_salute,
                "rischio": rischio_pesato,
                "proiezione_impatto": proiezione_30gg,
                "trend_90gg": proiezione_90gg,
                "settore_rilevato": config_settore["descrizione"],
                "segnalazioni": " ".join(dettagli_alert) if dettagli_alert else "Parametri stabili."
            })
        
        logger.info(f"Scan {contesto} completato ({config_settore['settore']}). Asset: {len(report)}")
        return report

def salva_report_certificato(azienda, dati_report, vault):
    """Genera un blob cifrato del report per il download sicuro."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        certificato = f"TS: {timestamp} | AZIENDA: {azienda} | ASSETS_RECAP: {len(dati_report)} | STATUS: VERIFIED"
        return vault.encrypt_data(certificato)
    except Exception as e:
        logger.error(f"Errore generazione certificato cifrato: {e}")
        return None