import pandas as pd

class AnalistaRischio:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def calcola_trend(self, nome_asset):
        """Analizza l'evoluzione del rischio nel tempo per un asset specifico."""
        # Correzione sicurezza: uso dei parametri (?) invece della concatenazione di stringhe
        query = "SELECT rischio, data_inserimento FROM asset WHERE nome = ? ORDER BY data_inserimento ASC"
        
        # Passiamo il parametro come una tupla
        df = pd.read_sql_query(query, self.db_conn, params=(nome_asset,))
        
        if len(df) < 2:
            return "Dati insufficienti per analisi trend"
        
        # Calcoliamo la differenza tra l'ultimo e il penultimo valore
        ultimo = df['rischio'].iloc[-1]
        precedente = df['rischio'].iloc[-2]
        
        if ultimo > precedente:
            return f"IN AUMENTO (da {precedente} a {ultimo})"
        elif ultimo < precedente:
            return f"IN DIMINUZIONE (da {precedente} a {ultimo})"
        else:
            return "STABILE"