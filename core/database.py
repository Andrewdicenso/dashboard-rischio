import os
import logging
import sqlite3
from typing import Optional

import bcrypt
import pandas as pd

from core.secure_vault import SecureVault

logger = logging.getLogger("RGD-Alpha.Database")


class DatabaseAziendale:
    """Persistenza aziendale con crittografia, multi-tenant e KPI centralizzati."""

    def __init__(self, db_folder: str = "data/db", db_name: str = "azienda.db"):
        try:
            os.makedirs(db_folder, exist_ok=True)
            self.db_path = os.path.join(db_folder, db_name)
            self.vault = SecureVault()
            self.crea_tabelle()
            logger.info(f"🛡️ Database RGD-Alpha pronto: {self.db_path}")
        except Exception as exc:
            logger.critical(f"❌ Fallimento database: {exc}")
            raise

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def crea_tabelle(self):
        """Crea o aggiorna lo schema principale del database."""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS utenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        ruolo TEXT NOT NULL,
                        azienda TEXT,
                        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS asset_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        company_id TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        tipo TEXT,
                        rischio REAL NOT NULL,
                        momentum TEXT,
                        volatilita REAL,
                        valore_extra REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS storico_kpi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        company_id TEXT NOT NULL,
                        kpi_nome TEXT NOT NULL,
                        valore REAL NOT NULL,
                        data_rilevazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS log_caricamenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        azienda TEXT,
                        contesto TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        nome_file TEXT,
                        FOREIGN KEY (user_id) REFERENCES utenti(id)
                    )
                    """
                )

                conn.commit()
        except Exception as exc:
            logger.error(f"❌ Errore creazione schema: {exc}")

    def crea_utente(self, email: str, password: str, ruolo: str = "user", azienda: Optional[str] = None):
        """Crea un nuovo utente con password hashata e azienda opzionale."""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                email_enc = self.vault.encrypt_data(email)
                password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                cursor.execute(
                    "INSERT INTO utenti (email, password_hash, ruolo, azienda) VALUES (?, ?, ?, ?)",
                    (email_enc, password_hash, ruolo, None),
                )
                user_id = cursor.lastrowid

                if azienda is None:
                    azienda = f"AZ-{user_id}"
                azienda_enc = self.vault.encrypt_data(azienda)

                cursor.execute("UPDATE utenti SET azienda = ? WHERE id = ?", (azienda_enc, user_id))
                conn.commit()
                return user_id
        except Exception as exc:
            logger.error(f"❌ Errore creazione utente: {exc}")
            return None

    def get_utente_by_email(self, email: str):
        """Recupera un utente tramite email, decriptando i campi sensibili."""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute("SELECT id, email, password_hash, ruolo, azienda FROM utenti")
                rows = cursor.fetchall()

            for row in rows:
                try:
                    email_dec = self.vault.decrypt_data(row[1])
                    if isinstance(email_dec, bytes):
                        email_dec = email_dec.decode("utf-8")

                    if email_dec.lower() == email.lower():
                        azienda_dec = self.vault.decrypt_data(row[4]) if row[4] else None
                        if isinstance(azienda_dec, bytes):
                            azienda_dec = azienda_dec.decode("utf-8")

                        return {
                            "id": row[0],
                            "email": email_dec,
                            "password_hash": row[2],
                            "ruolo": row[3],
                            "azienda": azienda_dec,
                        }
                except Exception:
                    continue
            return None
        except Exception as exc:
            logger.error(f"❌ Errore recupero utente by email: {exc}")
            return None

    def get_utente_by_id(self, user_id: int):
        """Recupera e decripta un utente tramite il suo ID."""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "SELECT id, email, password_hash, ruolo, azienda FROM utenti WHERE id = ?",
                    (user_id,),
                )
                row = cursor.fetchone()

            if not row:
                return None

            email_dec = self.vault.decrypt_data(row[1])
            if isinstance(email_dec, bytes):
                email_dec = email_dec.decode("utf-8")

            azienda_dec = self.vault.decrypt_data(row[4]) if row[4] else None
            if isinstance(azienda_dec, bytes):
                azienda_dec = azienda_dec.decode("utf-8")

            return {
                "id": row[0],
                "email": email_dec,
                "password_hash": row[2],
                "ruolo": row[3],
                "azienda": azienda_dec,
            }
        except Exception:
            return None

    def get_azienda_per_utente(self, user_id: int):
        utente = self.get_utente_by_id(user_id)
        return utente.get("azienda") if utente else None

    def salva_asset(self, user_id: int, nome_asset: str, rischio: float, **kwargs):
        """Salva un asset con valori crittografati per l'azienda e il nome."""
        try:
            utente = self.get_utente_by_id(user_id)
            if not utente or not utente.get("azienda"):
                raise ValueError("Utente o Azienda non validi.")

            company_id_secure = self.vault.encrypt_data(str(utente["azienda"]))
            nome_secure = self.vault.encrypt_data(str(nome_asset))

            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO asset_logs (
                        user_id, company_id, nome, tipo, rischio, momentum, volatilita, valore_extra
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        company_id_secure,
                        nome_secure,
                        kwargs.get("tipo", "GenericAsset"),
                        rischio,
                        kwargs.get("momentum", 0.0),
                        kwargs.get("volatilita", 0.0),
                        kwargs.get("valore_extra", 0.0),
                    ),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"❌ Errore salvataggio asset {nome_asset}: {exc}")

    def recupera_asset_per_utente(self, user_id: int):
        """Recupera gli asset di un utente, decriptando i nomi."""
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query("SELECT * FROM asset_logs WHERE user_id = ?", conn, params=(user_id,))

            if df.empty:
                return df

            df["nome"] = df["nome"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            return df
        except Exception as exc:
            logger.error(f"❌ Errore recupero asset: {exc}")
            return pd.DataFrame()

    def recupera_asset_per_azienda(self, company_id: str):
        """Recupera gli asset di un'azienda tramite il valore di company_id."""
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM asset_logs WHERE company_id = ? ORDER BY timestamp DESC",
                    conn,
                    params=(self.vault.encrypt_data(str(company_id)),),
                )

            if df.empty:
                return df

            df["nome"] = df["nome"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            return df
        except Exception as exc:
            logger.error(f"❌ Errore recupero asset per azienda: {exc}")
            return pd.DataFrame()

    def calcola_e_salva_kpi_correnti(self, user_id: int):
        """Calcola KPI aziendali e li salva nello storico."""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT rischio, volatilita FROM asset_logs
                    WHERE id IN (
                        SELECT MAX(id) FROM asset_logs WHERE user_id = ? GROUP BY nome
                    )
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()

            if not rows:
                return {"rischio_medio": 0.0, "solidita": 100.0, "impatto_30gg": 0.0}

            tot_rischio = sum(r[0] for r in rows)
            tot_volatilita = sum(r[1] if r[1] else 0.0 for r in rows)
            conteggio = len(rows)

            rischio_medio = round(tot_rischio / conteggio, 2)
            solidita = round(max(0.0, min(100.0, 100.0 - (rischio_medio * 9.5))), 1)
            impatto_30gg = round((tot_volatilita / conteggio) * rischio_medio * 1.5, 2)

            self.salva_kpi(user_id, "Rischio Medio", rischio_medio)
            self.salva_kpi(user_id, "Solidità Operativa", solidita)
            self.salva_kpi(user_id, "Impatto 30gg", impatto_30gg)

            return {
                "rischio_medio": rischio_medio,
                "solidita": solidita,
                "impatto_30gg": impatto_30gg,
            }
        except Exception as exc:
            logger.error(f"❌ Errore nel calcolo centralizzato dei KPI: {exc}")
            return {"rischio_medio": 5.0, "solidita": 50.0, "impatto_30gg": 5.0}

    def salva_kpi(self, user_id: int, kpi_nome: str, valore: float):
        try:
            azienda = self.get_azienda_per_utente(user_id)
            if azienda is None:
                raise ValueError("Nessuna azienda associata all'utente.")

            company_id_secure = self.vault.encrypt_data(str(azienda))
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO storico_kpi (user_id, company_id, kpi_nome, valore) VALUES (?, ?, ?, ?)",
                    (user_id, company_id_secure, kpi_nome, valore),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"Errore salvataggio KPI {kpi_nome}: {exc}")

    def recupera_kpi_per_utente(self, user_id: int):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM storico_kpi WHERE user_id = ? ORDER BY data_rilevazione DESC",
                    conn,
                    params=(user_id,),
                )

            if df.empty:
                return df

            df["company_id"] = df["company_id"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            return df
        except Exception as exc:
            logger.error(f"Errore recupero KPI per utente: {exc}")
            return pd.DataFrame()

    def supervisione_admin_metriche_globali(self):
        """Riepilogo aggregato per l'amministratore."""
        try:
            with self._get_conn() as conn:
                df_clienti = pd.read_sql_query("SELECT id, email, azienda, ruolo FROM utenti WHERE ruolo != 'admin'", conn)
                df_logs = pd.read_sql_query("SELECT user_id, rischio, volatilita FROM asset_logs", conn)
                df_uploads = pd.read_sql_query("SELECT user_id, COUNT(id) as totale_caricamenti FROM log_caricamenti GROUP BY user_id", conn)

            if df_clienti.empty:
                return pd.DataFrame(columns=["User ID", "Email Cliente", "Azienda", "Asset Attivi", "Rischio Medio", "File Caricati"])

            df_clienti["email"] = df_clienti["email"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            df_clienti["azienda"] = df_clienti["azienda"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")

            riepilogo = []
            for _, row in df_clienti.iterrows():
                u_id = row["id"]
                logs_utente = df_logs[df_logs["user_id"] == u_id]
                uploads_utente = df_uploads[df_uploads["user_id"] == u_id]

                asset_attivi = len(logs_utente)
                rischio_medio = round(logs_utente["rischio"].mean(), 2) if asset_attivi > 0 else 0.0
                file_caricati = int(uploads_utente["totale_caricamenti"].iloc[0]) if not uploads_utente.empty else 0

                riepilogo.append(
                    {
                        "User ID": u_id,
                        "Email Cliente": row["email"],
                        "Azienda": row["azienda"],
                        "Asset Attivi": asset_attivi,
                        "Rischio Medio": rischio_medio,
                        "File Caricati": file_caricati,
                    }
                )

            return pd.DataFrame(riepilogo)
        except Exception as exc:
            logger.error(f"❌ Errore durante la supervisione globale dell'Admin: {exc}")
            return pd.DataFrame()

    def registra_caricamento(self, user_id: int, contesto: str, nome_file: str):
        try:
            azienda = self.get_azienda_per_utente(user_id)
            if azienda is None:
                raise ValueError("Nessuna azienda associata all'utente.")

            azienda_sec = self.vault.encrypt_data(str(azienda))
            file_sec = self.vault.encrypt_data(str(nome_file))

            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO log_caricamenti (user_id, azienda, contesto, nome_file) VALUES (?, ?, ?, ?)",
                    (user_id, azienda_sec, contesto, file_sec),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"Errore log admin: {exc}")

    def recupera_log_caricamenti_per_utente(self, user_id: int):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM log_caricamenti WHERE user_id = ? ORDER BY timestamp DESC",
                    conn,
                    params=(user_id,),
                )

            if df.empty:
                return df

            df["azienda"] = df["azienda"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            df["nome_file"] = df["nome_file"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            return df
        except Exception as exc:
            logger.error(f"Errore recupero log caricamenti per utente: {exc}")
            return pd.DataFrame()

    def recupera_log_caricamenti_admin(self):
        try:
            with self._get_conn() as conn:
                df = pd.read_sql_query("SELECT * FROM log_caricamenti ORDER BY timestamp DESC", conn)

            if df.empty:
                return df

            df["azienda"] = df["azienda"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            df["nome_file"] = df["nome_file"].apply(lambda x: self.vault.decrypt_data(x).decode("utf-8") if x else "N/D")
            return df
        except Exception as exc:
            logger.error(f"Errore recupero log caricamenti admin: {exc}")
            return pd.DataFrame()

