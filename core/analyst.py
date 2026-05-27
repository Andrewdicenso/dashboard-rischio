import pandas as pd
import sqlite3
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger("RGD-Alpha.Analyst")

class AnalistaRischio:
    """
    Modulo di Intelligence Predittiva: implementa Regressione Lineare e 
    analisi della Volatilità Storica per la prevenzione dei rischi.
    """
    def __init__(self, db_path="data/db/azienda.db"):
        self.db_path = db_path
        self.soglia_critica = 7.0 
        self.soglia_warning = 5.0

    def _calcola_proiezione_lineare(self, serie_rischio):
        """
        Utilizza i minimi quadrati per calcolare la pendenza (slope) del trend.
        Permette di prevedere se il rischio salirà o scenderà nel lungo periodo.
        """
        n = len(serie_rischio)
        x = np.arange(n)
        y = serie_rischio
        # Calcolo pendenza (m) della retta y = mx + c
        if n < 2: return 0
        m = (n * np.sum(x*y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x)**2))
        return m

    def calcola_trend_predittivo(self, nome_asset, company_id) -> dict:
        """
        Analisi Ingegneristica: Sincronizzata con schema 'asset_logs'.
        Calcola Momentum, Volatilità e Proiezione Futura.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # SINCRONIZZAZIONE: Usa 'asset_logs' e 'timestamp'
                query = """
                    SELECT rischio, timestamp 
                    FROM asset_logs 
                    WHERE nome = ? AND company_id = ? 
                    ORDER BY timestamp DESC LIMIT 15
                """
                df = pd.read_sql_query(query, conn, params=(nome_asset, company_id))
            
            # Controllo integrità per evitare crash 'valore_attuale'
            if df.empty or len(df) < 2:
                return {
                    "status": "Inizializzazione",
                    "valore_attuale": df['rischio'].iloc[0] if not df.empty else 0.0,
                    "valutazione_strategica": "RACCOLTA DATI",
                    "azione": "Dati insufficienti per proiezione statistica."
                }
            
            # Ordine cronologico per analisi serie temporale
            rischi = df['rischio'].values[::-1]
            ultimo = rischi[-1]
            precedente = rischi[-2]
            
            # 1. Indicatori di Velocità
            delta = ultimo - precedente
            pendenza = self._calcola_proiezione_lineare(rischi)
            
            # 2. Analisi Volatilità (Deviazione Standard)
            volatilita = np.std(rischi)
            
            # 3. Momentum (Variazione percentuale)
            momentum_perc = ((ultimo - rischi[0]) / rischi[0] * 100) if rischi[0] != 0 else 0

            predizione = {
                "status": "Successo",
                "valore_attuale": round(ultimo, 2),
                "delta_immediato": round(delta, 2),
                "momentum_percentuale": f"{momentum_perc:+.2f}%",
                "indice_volatilita": round(volatilita, 2),
                "pendenza_trend": round(pendenza, 3),
                "alert_critico": ultimo > self.soglia_critica
            }

            # --- LOGICA DI INTELLIGENCE PREDITTIVA ---
            if pendenza > 0.3 or (ultimo > self.soglia_critica and delta > 0):
                predizione["valutazione_strategica"] = "INSTABILITÀ ACCELERATA"
                predizione["azione"] = "CRITICO: Trend in forte crescita. Richiesto intervento preventivo immediato."
            elif pendenza < -0.1 and ultimo < self.soglia_warning:
                predizione["valutazione_strategica"] = "RECUPERO STRUTTURALE"
                predizione["azione"] = "EFFICIENTE: L'asset sta riducendo il rischio in modo costante."
            elif volatilita > 1.2:
                predizione["valutazione_strategica"] = "VOLATILITÀ ELEVATA"
                predizione["azione"] = "ATTENZIONE: Comportamento imprevedibile. Aumentare frequenza monitoraggio."
            else:
                predizione["valutazione_strategica"] = "STABILITÀ OPERATIVA"
                predizione["azione"] = "MANTENIMENTO: Trend stabile e in linea con i target."

            return predizione

        except Exception as e:
            logger.error(f"❌ Errore Analista su {nome_asset}: {e}")
            return {
                "status": "Errore", 
                "valore_attuale": 0.0, 
                "valutazione_strategica": "FALLIMENTO CALCOLO",
                "azione": "Verificare connessione database."
            }