import sqlite3
import datetime

class DatabaseAziendale:
    def __init__(self, db_name="azienda.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.crea_tabella()

    def crea_tabella(self):
        cursor = self.conn.cursor()
        # Aggiunta la colonna company_id per isolare i dati delle aziende
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset (
                id INTEGER PRIMARY KEY,
                company_id TEXT,
                nome TEXT,
                rischio REAL,
                data_inserimento TIMESTAMP
            )
        ''')
        self.conn.commit()

    def salva_asset(self, asset, company_id):
        cursor = self.conn.cursor()
        data = datetime.datetime.now()
        # Salviamo l'asset associato al company_id specifico
        cursor.execute('''
            INSERT INTO asset (company_id, nome, rischio, data_inserimento)
            VALUES (?, ?, ?, ?)
        ''', (company_id, asset.nome, asset.analisi_strategica(), data))
        self.conn.commit()
        print(f"DEBUG: Asset '{asset.nome}' salvato per azienda {company_id} con data {data}.")

    def estrai_asset_a_rischio(self, company_id, soglia=5):
        cursor = self.conn.cursor()
        # Estraiamo solo gli asset appartenenti a quella specifica azienda
        cursor.execute('''
            SELECT nome, rischio FROM asset 
            WHERE company_id = ? AND rischio >= ?
            ORDER BY data_inserimento DESC
        ''', (company_id, soglia))
        return cursor.fetchall()