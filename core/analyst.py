import pandas as pd

class AnalistaRischio:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def calcola_trend(self, nome_asset):
        """Analizza l'evoluzione del rischio nel tempo per un asset specifico."""
        query = f"SELECT rischio, data_inserimento FROM asset WHERE nome = '{nome_asset}' ORDER BY data_inserimento ASC"
        df = pd.read_sql_query(query, self.db_conn)
        
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