import sqlite3
import datetime
import os
import logging
import pandas as pd
import bcrypt
from core.secure_vault import SecureVault

logger = logging.getLogger("RGD-Alpha.Database")


class DatabaseAziendale:

    """
    Architettura di Persistenza Enterprise Criptata RGD-ALPHA.
    Sincronizzato con SecureVault per la cifratura dei dati a riposo.
    Multi-tenant: 1 utente = 1 azienda, isolamento totale dei dati.
    Include funzioni analitiche avanzate per KPI e pannello Admin di supervisione.
    """

    def __init__(self, db_folder="data/db", db_name="azienda.db"):
        try:
            os.makedirs(db_folder, exist_ok=True)
            self.db_path = os.path.join(db_folder, db_name)


            # Inizializzazione Vault (Auto-configurato con vault.key)
            self.vault = SecureVault()


            self.vault = SecureVault()

            self.crea_tabelle()
            logger.info(f"🛡️ Database RGD-Alpha pronto: {self.db_path}")
        except Exception as e:
            logger.critical(f"❌ Fallimento database: {e}")
            raise


    # Connessione centralizzata

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    # =========================
    #   CREAZIONE TABELLE
    # =========================
    def crea_tabelle(self):
        """Inizializza lo schema garantendo l'integrità dei dati criptati e l'isolamento per utente."""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # 1. Tabella Utenti (MASTER)
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
                
                # 2. Tabella Asset Logs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS asset_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        company_id TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        tipo TEXT,
                        rischio REAL NOT NULL,
                        momentum TEXT,
                        volalita REAL,
                        valore_extra REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                """)

                # 3. Tabella Storico KPI
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS storico_kpi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        company_id TEXT NOT NULL,
                        kpi_nome TEXT NOT NULL,
                        valore REAL NOT NULL,
                        data_rilevazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                """)

                # 4. Log Caricamenti
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS log_caricamenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        azienda TEXT,
                        contesto TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        nome_file TEXT,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                """)

            conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Errore creazione schema: {e}")

# =========================================================
#   MODULO UTENTI / AUTENTICAZIONE (VERSIONE PULITA)
# =========================================================

def crea_utente(self, email, password, ruolo="user", azienda=None):
    """Crea un utente, gestisce la crittografia e l'assegnazione azienda."""
    try:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Crittografia e Hashing
            email_enc = self.vault.encrypt_data(email)
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # 2. Inserimento iniziale (senza azienda per generare l'ID)
            cursor.execute("""
                INSERT INTO utenti (email, password_hash, ruolo, azienda) 
                VALUES (?, ?, ?, ?)
            """, (email_enc, password_hash, ruolo, None))
            user_id = cursor.lastrowid

            # 3. Gestione Azienda (Se manca, usa l'ID generato)
            if azienda is None:
                azienda = f"AZ-{user_id}"
            azienda_enc = self.vault.encrypt_data(azienda)

            # 4. Aggiornamento finale con azienda criptata
            cursor.execute("UPDATE utenti SET azienda = ? WHERE id = ?", (azienda_enc, user_id))
            conn.commit()
            return user_id
    except Exception as e:
        logger.error(f"❌ Errore creazione utente: {e}")
        return None

def get_utente_by_email(self, email):
    """Recupera l'utente decriptando i dati per il confronto."""
    try:
        with self._get_conn() as conn:
            # Recuperiamo tutti gli utenti per confrontare l'email decriptata
            # Nota: Per database enormi si usa un hash deterministico come indice
            cursor = conn.execute("SELECT id, email, password_hash, ruolo, azienda FROM utenti")
            rows = cursor.fetchall()

        for row in rows:
            try:
                email_dec = self.vault.decrypt_data(row[1])
                if isinstance(email_dec, bytes): email_dec = email_dec.decode()
                
                if email_dec.lower() == email.lower():
                    azienda_dec = self.vault.decrypt_data(row[4]) if row[4] else None
                    if isinstance(azienda_dec, bytes): azienda_dec = azienda_dec.decode()
                    
                    return {
                        "id": row[0],
                        "email": email_dec,
                        "password_hash": row[2],
                        "ruolo": row[3],
                        "azienda": azienda_dec
                    }
            except:
                continue
        return None
    except Exception as e:
        logger.error(f"❌ Errore recupero utente by email: {e}")
        return None

def get_utente_by_id(self, user_id):
    """Recupera e decripta un utente tramite il suo ID."""
    try:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT id, email, password_hash, ruolo, azienda FROM utenti WHERE id = ?", (user_id,))
            row = cursor.fetchone()
        
        if not row: return None

        email_dec = self.vault.decrypt_data(row[1])
        if isinstance(email_dec, bytes): email_dec = email_dec.decode()
        
        azienda_dec = self.vault.decrypt_data(row[4]) if row[4] else None
        if isinstance(azienda_dec, bytes): azienda_dec = azienda_dec.decode()

        return {
            "id": row[0], "email": email_dec, "password_hash": row[2], 
            "ruolo": row[3], "azienda": azienda_dec
        }
    except Exception as e:
        return None

# =========================================================
#   MODULO ASSET / LOGICHE AZIENDALI
# =========================================================

def salva_asset(self, user_id, nome_asset, rischio, **kwargs):
    """Salva un log asset garantendo la protezione dei dati aziendali."""
    try:
        utente = self.get_utente_by_id(user_id)
        if not utente or not utente["azienda"]:
            raise ValueError("Utente o Azienda non validi.")

        # Criptiamo i dati identificativi
        company_id_secure = self.vault.encrypt_data(str(utente["azienda"]))
        nome_secure = self.vault.encrypt_data(str(nome_asset))

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO asset_logs (
                    user_id, company_id, nome, tipo, rischio, momentum, volatilita, valore_extra
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, company_id_secure, nome_secure,
                kwargs.get('tipo', 'GenericAsset'),
                rischio,
                kwargs.get('momentum', 0.0),
                kwargs.get('volatilita', 0.0),
                kwargs.get('valore_extra', 0.0)
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"❌ Errore salvataggio asset {nome_asset}: {e}")

def recupera_asset_per_utente(self, user_id):
    """Recupera la cronologia asset decriptando i nomi per la War Room."""
    try:
        with self._get_conn() as conn:
            df = pd.read_sql_query("SELECT * FROM asset_logs WHERE user_id = ?", conn, params=(user_id,))
        
        if df.empty: return df

        # Decriptiamo i nomi degli asset per la visualizzazione
        df['nome'] = df['nome'].apply(lambda x: self.vault.decrypt_data(x).decode() if x else "N/D")
        return df
    except Exception as e:
        logger.error(f"❌ Errore recupero asset: {e}")
        return pd.DataFrame()

# =========================================================
#   ADMIN / SUPERVISIONE GLOBALE
# =========================================================

def supervisione_admin_metriche_globali(self):
    """Vista Admin: decripta email e aziende per il monitoraggio."""
    try:
        with self._get_conn() as conn:
            df = pd.read_sql_query("SELECT email, ruolo, azienda, data_creazione FROM utenti", conn)
        
        if df.empty: return df

        df["email"] = df["email"].apply(lambda x: self.vault.decrypt_data(x).decode() if x else "N/D")
        df["azienda"] = df["azienda"].apply(lambda x: self.vault.decrypt_data(x).decode() if x else "N/D")
        return df
    except Exception as e:
        return pd.DataFrame()

    # ==========================================
    #   CALCOLO MATEMATICO CENTRALIZZATO KPI
    # ==========================================

    def calcola_e_salva_kpi_correnti(self, user_id: int):
        """
        Calcola istantaneamente i KPI strategici reali basandosi sugli ultimi log degli asset nel DB.
        Sfrutta SQL per la massima efficienza e memorizza il risultato nello storico_kpi.
        """
        try:
            azienda = self.get_azienda_per_utente(user_id)
            if not azienda:
                return None

            with self._get_conn() as conn:
                cursor = conn.cursor()
                # Seleziona l'ultimo record inserito per ciascun asset unico dell'utente
                cursor.execute("""
                    SELECT rischio, volatilita FROM asset_logs 
                    WHERE id IN (
                        SELECT MAX(id) FROM asset_logs WHERE user_id = ? GROUP BY nome
                    )
                """, (user_id,))
                rows = cursor.fetchall()

            if not rows:
                return {"rischio_medio": 0.0, "solidita": 100.0, "impatto_30gg": 0.0}

            tot_rischio = sum(r[0] for r in rows)
            tot_volatilità = sum(r[1] if r[1] else 0.0 for r in rows)
            conteggio = len(rows)

            # 1. Rischio Medio (Scala 1-10)
            rischio_medio = round(tot_rischio / conteggio, 2)
            
            # 2. Solidità Operativa (Inversa del rischio, espressa in percentuale)
            solidita = round(max(0.0, min(100.0, 100.0 - (rischio_medio * 9.5))), 1)
            
            # 3. Impatto Proiettato a 30gg (Derivato da volatilità complessiva e rischio attuale)
            impatto_30gg = round((tot_volatilità / conteggio) * rischio_medio * 1.5, 2)

            # Salvataggio persistente nella tabella storico_kpi per trend futuri
            self.salva_kpi(user_id, "Rischio Medio", rischio_medio)
            self.salva_kpi(user_id, "Solidità Operativa", solidita)
            self.salva_kpi(user_id, "Impatto 30gg", impatto_30gg)

            return {
                "rischio_medio": rischio_medio,
                "solidita": solidita,
                "impatto_30gg": impatto_30gg
            }
        except Exception as e:
            logger.error(f"❌ Errore nel calcolo centralizzato dei KPI: {e}")
            return {"rischio_medio": 5.0, "solidita": 50.0, "impatto_30gg": 5.0}

    # =========================
    #   KPI HISTORIC ACTIONS
    # =========================

    def salva_kpi(self, user_id: int, kpi_nome: str, valore: float):
        try:
            azienda = self.get_azienda_per_utente(user_id)
            if azienda is None:
                raise ValueError("Nessuna azienda associata all'utente.")

            company_id_secure = self.vault.encrypt_data(str(azienda))

            with self._get_conn() as conn:
                conn.execute("""
                    INSERT INTO storico_kpi (user_id, company_id, kpi_nome, valore)
                    VALUES (?, ?, ?, ?)
                """, (user_id, company_id_secure, kpi_nome, valore))
        except Exception as e:
            logger.error(f"Errore salvataggio KPI {kpi_nome}: {e}")

    def recupera_kpi_per_utente(self, user_id: int):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM storico_kpi WHERE user_id = ? ORDER BY data_rilevazione DESC",
                    conn,
                    params=(user_id,)
                )

            if df.empty:
                return df

            df['company_id'] = df['company_id'].apply(self.vault.decrypt_data)
            return df
        except Exception as e:
            logger.error(f"Errore recupero KPI per utente: {e}")
            return pd.DataFrame()

    # ==========================================
    #   SUPERVISIONE ADMIN (PANNELLO DI CONTROLLO)
    # ==========================================

    def supervisione_admin_metriche_globali(self):
        """
        Funzione esclusiva ADMIN: estrae un riepilogo aggregato ad alte prestazioni
        di tutte le aziende clienti registrate nel sistema per la dashboard di monitoraggio.
        """
        try:
            with self._get_conn() as conn:
                # Estraiamo l'elenco utenti escludendo l'admin stesso per monitorare i clienti
                df_clienti = pd.read_sql_query("SELECT id, email, azienda, ruolo FROM utenti WHERE ruolo != 'admin'", conn)
                df_logs = pd.read_sql_query("SELECT user_id, rischio, volatilita FROM asset_logs", conn)
                df_uploads = pd.read_sql_query("SELECT user_id, COUNT(id) as totale_caricamenti FROM log_caricamenti GROUP BY user_id", conn)

            if df_clienti.empty:
                return pd.DataFrame(columns=["User ID", "Email Cliente", "Azienda", "Asset Attivi", "Rischio Medio", "File Caricati"])

            # Decifratura dei dati sensibili degli utenti per la visualizzazione dell'Admin autorizzato
            df_clienti["email"] = df_clienti["email"].apply(self.vault.decrypt_data)
            df_clienti["azienda"] = df_clienti["azienda"].apply(self.vault.decrypt_data)

            Riepilogo = []
            for _, row in df_clienti.iterrows():
                u_id = row["id"]
                logs_utente = df_logs[df_logs["user_id"] == u_id]
                uploads_utente = df_uploads[df_uploads["user_id"] == u_id]
                
                asset_attivi = len(logs_utente)
                rischio_medio = round(logs_utente["rischio"].mean(), 2) if asset_attivi > 0 else 0.0
                file_caricati = int(uploads_utente["totale_caricamenti"].iloc[0]) if not uploads_utente.empty else 0

                Riepilogo.append({
                    "User ID": u_id,
                    "Email Cliente": row["email"],
                    "Azienda": row["azienda"],
                    "Asset Attivi": asset_attivi,
                    "Rischio Medio": rischio_medio,
                    "File Caricati": file_caricati
                })

            return pd.DataFrame(Riepilogo)
        except Exception as e:
            logger.error(f"❌ Errore durante la supervisione globale dell'Admin: {e}")
            return pd.DataFrame()

    # =========================
    #   LOG CARICAMENTI
    # =========================

    def registra_caricamento(self, user_id: int, contesto: str, nome_file: str):
        try:
            azienda = self.get_azienda_per_utente(user_id)
            if azienda is None:
                raise ValueError("Nessuna azienda associata all'utente.")

            azienda_sec = self.vault.encrypt_data(str(azienda))
            file_sec = self.vault.encrypt_data(str(nome_file))

            with self._get_conn() as conn:
                conn.execute("""
                    INSERT INTO log_caricamenti (user_id, azienda, contesto, nome_file)
                    VALUES (?, ?, ?, ?)
                """, (user_id, azienda_sec, contesto, file_sec))
        except Exception as e:
            logger.error(f"Errore log admin: {e}")

    def recupera_log_caricamenti_per_utente(self, user_id: int):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM log_caricamenti WHERE user_id = ? ORDER BY timestamp DESC",
                    conn,
                    params=(user_id,)
                )

            if df.empty:
                return df

            df["azienda"] = df["azienda"].apply(self.vault.decrypt_data)
            df["nome_file"] = df["nome_file"].apply(self.vault.decrypt_data)
            return df
        except Exception as e:
            logger.error(f"Errore recupero log caricamenti per utente: {e}")
            return pd.DataFrame()

    def recupera_log_caricamenti_admin(self):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM log_caricamenti ORDER BY timestamp DESC",
                    conn
                )

            if df.empty:
                return df

            df["azienda"] = df["azienda"].apply(self.vault.decrypt_data)
            df["nome_file"] = df["nome_file"].apply(self.vault.decrypt_data)
            return df
        except Exception as e:
            logger.error(f"Errore recupero log caricamenti admin: {e}")
            return pd.DataFrame()

    def recupera_log_caricamenti_admin(self):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query("SELECT * FROM log_caricamenti", conn)
                return df
        except: return pd.DataFrame()

    def registra_caricamento(self, user_id, contesto, nome_file):
        try:
            azienda = self.get_utente_by_id(user_id)["azienda"]
            with self._get_conn() as conn:
                conn.execute("INSERT INTO log_caricamenti (user_id, azienda, contesto, nome_file) VALUES (?, ?, ?, ?)", 
                             (user_id, azienda, contesto, nome_file))
                conn.commit()
        except: pass

    def salva_asset(self, user_id, nome_asset, rischio, **kwargs):
        try:
            azienda = self.get_utente_by_id(user_id)["azienda"]
            with self._get_conn() as conn:
                conn.execute("INSERT INTO asset_logs (user_id, company_id, nome, tipo, rischio, momentum, volatilita) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (user_id, azienda, nome_asset, kwargs.get('tipo'), rischio, kwargs.get('momentum'), kwargs.get('volatilita')))
                conn.commit()
        except: pass

    
    def calcola_e_salva_kpi_correnti(self, user_id):
        """Calcola i KPI reali basandosi sugli asset salvati nel database."""
        try:
            with self._get_conn() as conn:
                # Prendiamo la media del rischio degli ultimi asset caricati
                cursor = conn.execute("""
                    SELECT AVG(rischio) FROM asset_logs 
                    WHERE user_id = ? AND timestamp >= datetime('now', '-1 hour')
                """, (user_id,))
                rischio_medio = cursor.fetchone()[0]
            
            if rischio_medio is None:
                return {"solidita": 100, "impatto_30gg": "N/D", "rischio_medio": 0}

            # Formula della solidità: più il rischio è alto, più la solidità scende
            solidita = round(100 - (rischio_medio * 10), 1)
            solidita = max(min(solidita, 100), 0) # Mantiene tra 0 e 100
            
            impatto = "CRITICO" if rischio_medio > 7 else "ATTENZIONE" if rischio_medio > 4 else "STABILE"

            return {
                "solidita": solidita,
                "impatto_30gg": impatto,
                "rischio_medio": round(rischio_medio, 2)
            }
        except:
            return {"solidita": 0, "impatto_30gg": "ERRORE", "rischio_medio": 0}

