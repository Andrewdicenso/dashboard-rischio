import sys
import logging
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.secure_vault import SecureVault
from core.database import DatabaseAziendale
from core.engine_settori import analizza_e_configura_motore

logger = logging.getLogger("RGD-Alpha.Gateway.Enterprise")


class DataGateway:
    def __init__(self):
        self.vault = SecureVault(key_path="core/security/vault.key")
        self.db = DatabaseAziendale()
        self.pesi_contesto = {
            "Magazzino": 1.2,
            "Fornitori": 1.5,
            "Performance Vendite": 1.0,
            "UNIVERSAL": 1.0,
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
                user_id = getattr(asset, "user_id", 1)
                nome_asset = getattr(asset, "nome", "Prodotto_Ignoto")
                tipo = getattr(asset, "tipo", "GenericAsset")
                momentum = getattr(asset, "momentum", "Stabile")
                volatilita = getattr(asset, "volatilita", 0.0)

            self.db.salva_asset(
                user_id=user_id,
                nome_asset=nome_asset,
                rischio=rischio_pesato,
                tipo=tipo,
                momentum=momentum,
                volatilita=volatilita,
            )
        except Exception as e:
            nome_log = asset.get("nome", "?") if isinstance(asset, dict) else getattr(asset, "nome", "?")
            logger.warning(f"Archiviazione fallita per asset {nome_log}: {e}")

    def _genera_consiglio_azione(self, rischio, settore):
        if rischio > 8:
            if settore == "LOGISTICS":
                return "🚨 CRITICO: Avviare liquidazione immediata o svendita stock per liberare spazio e capitale."
            if settore == "FINANCE":
                return "🚨 CRITICO: Rischio perdita totale valore. Valutare accantonamento o revisione immediata contratti."
            return "🚨 CRITICO: Azione d'emergenza richiesta entro 48 ore."
        if rischio > 5:
            if settore == "LOGISTICS":
                return "⚠️ ATTENZIONE: Pianificare promozione 'Bundle' o rotazione fisica verso zone di prelievo rapido."
            if settore == "RELATIONS":
                return "⚠️ ATTENZIONE: Contattare il fornitore per rinegoziare i tempi o cercare alternativa secondaria."
            return "⚠️ ATTENZIONE: Monitoraggio intensivo richiesto per i prossimi 7 giorni."
        return "✅ OTTIMALE: Mantenere le attuali politiche di riordino. Nessuna azione richiesta."

    def esegui_scan_strategico(self, lista_asset, contesto, fattore_stress=1.0):
        colonne = []
        if lista_asset:
            primo_asset = lista_asset[0]
            if isinstance(primo_asset, dict):
                colonne = list(primo_asset.keys())
                if "dati_extra" in primo_asset and isinstance(primo_asset["dati_extra"], dict):
                    colonne.extend(primo_asset["dati_extra"].keys())
            else:
                colonne = list(vars(primo_asset).keys())
                if hasattr(primo_asset, "dati_extra") and isinstance(primo_asset.dati_extra, dict):
                    colonne.extend(primo_asset.dati_extra.keys())

        print("\n" + "=" * 50)
        print(f"🔍 [DIAGNOSI RGD-ALPHA] Asset analizzati: {len(lista_asset)}")
        print(f"📋 Tutte le chiavi rilevate (incluse extra): {colonne}")
        if lista_asset:
            sample = lista_asset[0]
            extra_sample = sample.get("dati_extra", {}) if isinstance(sample, dict) else getattr(sample, "dati_extra", {})
            print(f"📄 Esempio dati extra primo asset: {extra_sample}")
        print("=" * 50 + "\n")

        config_settore = analizza_e_configura_motore(colonne)
        soglia_critica = config_settore["soglia"]
        moltiplicatore_settore = config_settore["moltiplicatore"]
        moltiplicatore_contesto = self.pesi_contesto.get(contesto, 1.0)
        moltiplicatore_finale = moltiplicatore_settore * moltiplicatore_contesto
        settore_rilevato = config_settore.get("settore", "GENERALE")

        report = []
        for asset in lista_asset:
            if isinstance(asset, dict):
                nome_asset = asset.get("nome", "Prodotto")
                rischio_base = asset.get("rischio", 0.0)
            else:
                nome_asset = getattr(asset, "nome", "Prodotto")
                rischio_base = getattr(asset, "rischio", 0.0)

            rischio_pesato = round(rischio_base * moltiplicatore_finale, 2)
            consiglio = self._genera_consiglio_azione(rischio_pesato, settore_rilevato)
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

            self._archivia_asset(asset, rischio_pesato)

            report.append(
                {
                    "asset": nome_asset,
                    "stato": stato_salute,
                    "rischio": rischio_pesato,
                    "proiezione_impatto": proiezione_30gg,
                    "proiezione_90gg": proiezione_90gg,
                    "consiglio_strategico": consiglio,
                    "alert": "🚨 STRESS TEST ATTIVO" if fattore_stress > 1.0 else "Nessuna anomalia",
                    "dettagli_alert": dettagli_alert,
                }
            )

        return report


def salva_report_certificato(azienda, dati_report, vault):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        certificato = f"TS: {timestamp} | AZIENDA: {azienda} | VERIFIED BY RGD-ALPHA"
        return vault.encrypt_data(certificato)
    except Exception:
        return None
