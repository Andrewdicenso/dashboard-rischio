# core/analyst.py
import pandas as pd
import sqlite3
import logging

logger = logging.getLogger("RGD-Alpha.Analyst")

class AnalistaRischio:
    """
    Modulo di Intelligence: trasforma lo storico in proiezioni di scalabilità.
    """
    def __init__(self, db_path="data/db/azienda.db"):
        self.db_path = db_path

    def calcola_trend_predittivo(self, nome_asset, company_id) -> dict:
        """
        Analizza l'evoluzione temporale e predice la direzione del rischio aziendale.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Query ottimizzata per scalabilità (filtra per azienda e asset)
                query = """
                    SELECT rischio, data_inserimento 
                    FROM asset 
                    WHERE nome = ? AND company_id = ? 
                    ORDER BY data_inserimento DESC LIMIT 5
                """
                df = pd.read_sql_query(query, conn, params=(nome_asset, company_id))
            
            if df.empty or len(df) < 2:
                logger.info(f"Storico insufficiente per {nome_asset}.")
                return {"status": "Inizializzazione", "trend": "STABILE", "delta": 0}
            
            # Calcolo variazione (ultimo vs precedente)
            ultimo = float(df['rischio'].iloc[0])
            precedente = float(df['rischio'].iloc[1])
            delta = ultimo - precedente
            
            # Logica di diagnosi predittiva
            predizione = {
                "valore_attuale": round(ultimo, 2),
                "variazione": round(delta, 2),
                "direzione": "PEGGIORAMENTO" if delta > 0.1 else "MIGLIORAMENTO" if delta < -0.1 else "STABILE"
            }

            # Suggerimento per l'imprenditore (Logica Scalabile)
            if delta > 1.0:
                predizione["azione"] = "URGENTE: Espansione rischio non controllata. Intervenire subito."
            elif delta > 0:
                predizione["azione"] = "Monitorare: tendenza al rialzo nel breve periodo."
            else:
                predizione["azione"] = "Operazione efficiente: scalabilità sicura."

            return predizione

        except Exception as e:
            logger.error(f"Errore critico Analyst su {nome_asset}: {e}")
            return {"status": "Errore", "messaggio": str(e)}