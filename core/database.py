import sqlite3
import datetime
import os
import logging
import pandas as pd

logger = logging.getLogger("RGD-Alpha.Database")

class DatabaseAziendale:
    def __init__(self, db_folder="data/db", db_name="azienda.db"):
        try:
            os.makedirs(db_folder, exist_ok=True)
            self.db_path = os.path.join(db_folder, db_name)
            self._inizializza_db()
            logger.info(f"🛡️ Database RGD-Alpha pronto: {self.db_path}")
        except Exception as e:
            logger.critical(f"❌ Fallimento critico database: {e}")
            raise

    def _inizializza_db(self):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cursor = conn.cursor()
            # Tabella Asset (Multi-tenant)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT,
                    nome TEXT,
                    rischio REAL,
                    data_inserimento TIMESTAMP
                )
            ''')
            # Tabella Richieste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS richieste (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_azienda TEXT,
                    email TEXT,
                    stato TEXT DEFAULT 'in_attesa',
                    data_richiesta TIMESTAMP
                )
            ''')
            # Log Caricamenti (Admin View)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_caricamenti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    azienda TEXT,
                    contesto TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    nome_file TEXT
                )
            """)
            # Storico KPI (Predittivo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storico_kpi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    azienda TEXT,
                    kpi_nome TEXT,
                    valore REAL,
                    data_rilevazione DATE DEFAULT CURRENT_DATE
                )
            """)
            conn.commit()

    def registra_caricamento(self, azienda, contesto, nome_file):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO log_caricamenti (azienda, contesto, nome_file) VALUES (?, ?, ?)",
                            (azienda, contesto, nome_file))
        except Exception as e: logger.error(f"Errore log admin: {e}")

    def salva_asset(self, asset_obj, company_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO asset (company_id, nome, rischio, data_inserimento)
                    VALUES (?, ?, ?, ?)
                ''', (company_id, asset_obj.nome, asset_obj.rischio, datetime.datetime.now()))
        except Exception as e:
            logger.error(f"❌ Errore salvataggio asset {asset_obj.nome}: {e}")

    def salva_nuova_richiesta(self, nome_azienda, email):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('INSERT INTO richieste (nome_azienda, email, data_richiesta) VALUES (?, ?, ?)',
                            (nome_azienda, email, datetime.datetime.now()))
        except Exception as e: logger.error(f"Errore richiesta: {e}")

    def estrai_asset_a_rischio(self, company_id, soglia=5):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT nome, rischio FROM asset WHERE company_id = ? AND rischio >= ? ORDER BY data_inserimento DESC',
                               (company_id, soglia))
                return cursor.fetchall()
        except Exception as e: return []

    def recupera_attivita_globale(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query("SELECT * FROM log_caricamenti ORDER BY timestamp DESC", conn)
        except Exception as e: return pd.DataFrame()