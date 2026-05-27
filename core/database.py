import sqlite3
import datetime
import os
import logging
import pandas as pd
from core.secure_vault import SecureVault

logger = logging.getLogger("RGD-Alpha.Database")

class DatabaseAziendale:
    """
    Architettura di Persistenza Enterprise Criptata RGD-ALPHA.
    Sincronizzato con SecureVault per la cifratura dei dati a riposo.
    """
    def __init__(self, db_folder="data/db", db_name="azienda.db"):
        try:
            os.makedirs(db_folder, exist_ok=True)
            self.db_path = os.path.join(db_folder, db_name)
            
            # Inizializzazione Vault (Auto-configurato con vault.key)
            self.vault = SecureVault()
            
            self.crea_tabelle()
            logger.info(f"🛡️ Database RGD-Alpha (SECURE MODE) pronto: {self.db_path}")
        except Exception as e:
            logger.critical(f"❌ Fallimento critico database: {e}")
            raise

    # 🔥 FUNZIONE AGGIUNTA QUI (POSIZIONE CORRETTA)
    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def crea_tabelle(self):
        """Inizializza lo schema garantendo l'integrità dei dati criptati."""
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.cursor()
                
                # 1. Tabella Asset Logs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS asset_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        tipo TEXT, 
                        rischio REAL NOT NULL,
                        momentum TEXT,
                        volatilita REAL,
                        valore_extra REAL, 
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 2. Tabella Storico KPI
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS storico_kpi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id TEXT NOT NULL,
                        kpi_nome TEXT NOT NULL,
                        valore REAL NOT NULL,
                        data_rilevazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 3. Log Caricamenti
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS log_caricamenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        azienda TEXT,
                        contesto TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        nome_file TEXT
                    )
                """)

                # 4. Tabella Utenti (NUOVA)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS utenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        ruolo TEXT NOT NULL,
                        azienda TEXT,
                        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
        except Exception as e:
            logger.error(f"❌ Errore creazione schema: {e}")
            raise

    # ------------------------------
    #   FUNZIONI UTENTI (NUOVE)
    # ------------------------------

    def crea_utente(self, email, password_hash, ruolo, azienda):
        try:
            email_enc = self.vault.encrypt_data(email)
            azienda_enc = self.vault.encrypt_data(azienda)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO utenti (email, password_hash, ruolo, azienda)
                    VALUES (?, ?, ?, ?)
                """, (email_enc, password_hash, ruolo, azienda_enc))
        except Exception as e:
            logger.error(f"Errore creazione utente: {e}")
            raise

    def get_utente_by_email(self, email):
        try:
            email_enc = self.vault.encrypt_data(email)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, email, password_hash, ruolo, azienda
                    FROM utenti WHERE email = ?
                """, (email_enc,))
                row = cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "email": self.vault.decrypt_data(row[1]),
                "password_hash": row[2],
                "ruolo": row[3],
                "azienda": self.vault.decrypt_data(row[4])
            }
        except Exception as e:
            logger.error(f"Errore recupero utente: {e}")
            return None

    def get_tutti_gli_utenti(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM utenti", conn)

            if df.empty:
                return df

            df["email"] = df["email"].apply(self.vault.decrypt_data)
            df["azienda"] = df["azienda"].apply(self.vault.decrypt_data)

            return df
        except Exception as e:
            logger.error(f"Errore recupero utenti: {e}")
            return pd.DataFrame()

    # ------------------------------
    #   FUNZIONI ESISTENTI
    # ------------------------------

    def salva_asset(self, company_id, nome_asset, rischio, **kwargs):
        try:
            company_id_secure = self.vault.encrypt_data(str(company_id))
            nome_secure = self.vault.encrypt_data(str(nome_asset))
            
            tipo_asset = kwargs.get('tipo', 'GenericAsset')
            momentum = kwargs.get('momentum', 'Stabile')
            volatilita = kwargs.get('volatilita', 0.0)
            valore_extra = kwargs.get('valore_extra', 0.0)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO asset_logs (company_id, nome, tipo, rischio, momentum, volatilita, valore_extra)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (company_id_secure, nome_secure, tipo_asset, 
                      rischio, momentum, volatilita, valore_extra))
        except Exception as e:
            logger.error(f"❌ Errore salvataggio asset {nome_asset}: {e}")

    def recupera_asset_per_azienda(self, company_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query('SELECT * FROM asset_logs', conn)
                
            if df.empty:
                return df

            df['company_id'] = df['company_id'].apply(self.vault.decrypt_data)
            df_filtrato = df[df['company_id'] == company_id].copy()
            
            if not df_filtrato.empty:
                df_filtrato['nome'] = df_filtrato['nome'].apply(self.vault.decrypt_data)
            
            return df_filtrato
        except Exception as e:
            logger.error(f"Errore recupero asset storico: {e}")
            return pd.DataFrame()

    def recupera_attivita_globale(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query('SELECT id, company_id, nome, rischio, timestamp FROM asset_logs ORDER BY id DESC', conn)
            
            if not df.empty:
                df['company_id'] = df['company_id'].apply(self.vault.decrypt_data)
                df['nome'] = df['nome'].apply(self.vault.decrypt_data)
                
            return df
        except Exception as e:
            logger.error(f"Errore recupero log globali: {e}")
            return pd.DataFrame()

    def registra_caricamento(self, azienda, contesto, nome_file):
        try:
            azienda_sec = self.vault.encrypt_data(str(azienda))
            file_sec = self.vault.encrypt_data(str(nome_file))
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO log_caricamenti (azienda, contesto, nome_file) VALUES (?, ?, ?)",
                            (azienda_sec, contesto, file_sec))
        except Exception as e: 
            logger.error(f"Errore log admin: {e}")

