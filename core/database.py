import sqlite3
import datetime
import os

class DatabaseAziendale:
    def __init__(self, db_folder="data", db_name="azienda.db"):
        # Assicura che la cartella 'data' esista
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, db_name)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.crea_tabella()

    def crea_tabella(self):
        cursor = self.conn.cursor()
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
        # Assumendo che asset.nome sia già criptato come bytes se gestito da SecureVault
        # e che asset.analisi_strategica() restituisca un valore numerico o descrittivo coerente
        cursor.execute('''
            INSERT INTO asset (company_id, nome, rischio, data_inserimento)
            VALUES (?, ?, ?, ?)
        ''', (company_id, asset.nome, asset.analisi_strategica(), data))
        self.conn.commit()
        print(f"DEBUG: Asset salvato per azienda {company_id}.")

    def estrai_asset_a_rischio(self, company_id, soglia=5):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT nome, rischio FROM asset 
            WHERE company_id = ? AND rischio >= ?
            ORDER BY data_inserimento DESC
        ''', (company_id, soglia))
        return cursor.fetchall()