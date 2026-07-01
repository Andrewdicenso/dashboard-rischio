<<<<<<< HEAD
# FILE: core/engine.py
=======
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
import sys
import logging
from pathlib import Path
from datetime import datetime

# ==============================================================================
<<<<<<< HEAD
# RISOLUZIONE DINAMICA DEL PATH PER STREAMLIT (Evita ModuleNotFoundError)
=======
# RISOLUZIONE DINAMICA DEL PATH PER STREAMLIT
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.secure_vault import SecureVault
from core.database import DatabaseAziendale
<<<<<<< HEAD
from experimental_modules.engine_settori import analizza_e_configura_motore
=======
from core.experimental_modules.engine_settori import analizza_e_configura_motore
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707

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
<<<<<<< HEAD
        """Salvataggio nel DB adattivo per supportare sia Oggetti che Dizionari."""
        try:
            # Riconoscimento robusto della tipologia di struttura dati passata
=======
        try:
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
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

<<<<<<< HEAD
            # Esecuzione persistenza atomica sul database allineata con il modulo aziendale
=======
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
            self.db.salva_asset(
                user_id=user_id,
                nome_asset=nome_asset,
                rischio=rischio_pesato,
                tipo=tipo,
                momentum=momentum,
                volatilita=volatilita
            )
        except Exception as e:
<<<<<<< HEAD
            # Evitiamo crash critici se un singolo asset è corrotto durante lo storicizzazione
            nome_log = asset.get('nome', '?') if isinstance(asset, dict) else getattr(asset, 'nome', '?')
            logger.warning(f"Archiviazione fallita per asset {nome_log}: {e}")

    def esegui_scan_strategico(self, lista_asset, contesto):
        """
        Analisi Avanzata RGD-ALPHA: Integra il riconoscimento automatico del settore
        con proiezioni predittive a 30 e 90 giorni supportando input ibridi.
        """
        colonne = []
        if lista_asset:
            primo_asset = lista_asset[0]
            # Estrazione sicura delle chiavi a seconda del formato (Dizionario o Oggetto)
            if isinstance(primo_asset, dict):
                colonne = list(primo_asset.keys())
                if "dati_extra" in primo_asset and isinstance(primo_asset["dati_extra"], dict):
                    colonne.extend(primo_asset["dati_extra"].keys())
            else:
                colonne = list(vars(primo_asset).keys())
                if hasattr(primo_asset, 'dati_extra') and isinstance(primo_asset.dati_extra, dict):
                    colonne.extend(primo_asset.dati_extra.keys())
        
        # --- LOG DI DIAGNOSI PER IL TERMINALE ---
        print("\n" + "="*50)
        print(f"🔍 [DIAGNOSI RGD-ALPHA] Asset analizzati: {len(lista_asset)}")
        print(f"📋 Tutte le chiavi rilevate (incluse extra): {colonne}")
        if lista_asset:
            sample = lista_asset[0]
            extra_sample = sample.get('dati_extra', {}) if isinstance(sample, dict) else getattr(sample, 'dati_extra', {})
            print(f"📄 Esempio dati extra primo asset: {extra_sample}")
        print("="*50 + "\n")
=======
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
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
        
        else:
            return "✅ OTTIMALE: Mantenere le attuali politiche di riordino. Nessuna azione richiesta."

    def esegui_scan_strategico(self, lista_asset, contesto, fattore_stress=1.0):
        # ... (mantieni la logica esistente di rilevamento settore) ...
        config_settore = analizza_e_configura_motore(colonne)
<<<<<<< HEAD
        
        # Parametri dinamici estrapolati dal modulo settori
        soglia_critica = config_settore["soglia"]
        moltiplicatore_settore = config_settore["moltiplicatore"]
        moltiplicatore_contesto = self.pesi_contesto.get(contesto, 1.0)
        
        moltiplicatore_finale = moltiplicatore_settore * moltiplicatore_contesto
        
        report = []
        for asset in lista_asset:
            # Estrazione valori adattiva
            if isinstance(asset, dict):
                nome_asset = asset.get("nome", "Prodotto")
                rischio_base = asset.get("rischio", 0.0)
            else:
                nome_asset = getattr(asset, 'nome', 'Prodotto')
                rischio_base = getattr(asset, 'rischio', 0.0)
                
=======
        settore_rilevato = config_settore.get("settore", "GENERAL")
        
        report = []
        for asset in lista_asset:
            # ... (mantieni il calcolo del rischio_pesato) ...
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
            rischio_pesato = round(rischio_base * moltiplicatore_finale, 2)
            
            # --- NUOVA LOGICA: GENERAZIONE CONSIGLIO ---
            consiglio = self._genera_consiglio_azione(rischio_pesato, settore_rilevato)
            
<<<<<<< HEAD
            # --- MOTORE PREDITTIVO AUTOMATICO ---
            proiezione_30gg = round(rischio_pesato * 1.25, 2)
            proiezione_90gg = round(rischio_pesato * 1.5, 2)
            
            dettagli_alert = []
            if rischio_pesato > soglia_critica:
                dettagli_alert.append(f"⚠️ [{config_settore['settore']}] Rischio Critico: {rischio_pesato}.")
                dettagli_alert.append(f"PIANO AZIONE: {config_settore['consiglio']}")
            
            stato_salute = "CRITICO" if rischio_pesato > soglia_critica else "OTTIMALE"
            if 5.0 < rischio_pesato <= soglia_critica:
                stato_salute = "ATTENZIONE"
                dettagli_alert.append("Trend in crescita: monitoraggio consigliato.")

            # Struttura dati finale per la visualizzazione nella War Room
            report.append({
                "asset": nome_asset,
                "stato": stato_salute,
=======
            report.append({
                "asset": nome_asset,
                "stato": "CRITICO" if rischio_pesato > 7 else "ATTENZIONE" if rischio_pesato > 5 else "OTTIMALE",
>>>>>>> bcab1954171fcee24d307cf15bb8f449159e2707
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