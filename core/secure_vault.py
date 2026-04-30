from cryptography.fernet import Fernet, InvalidToken
import os
import logging

# Logger dedicato per la sicurezza
logger = logging.getLogger("RGD-Alpha.Vault")

class SecureVault:
    """
    Vault aziendale scalabile: gestisce la cifratura dei dati
    con protezione contro la corruzione e gestione automatica dei percorsi.
    """
    def __init__(self, key_path="core/security/vault.key"):
        # Puntiamo alla nuova cartella di sicurezza per scalabilità
        self.key_path = key_path
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        """Carica la chiave esistente o ne genera una nuova creando le cartelle necessarie."""
        try:
            # Creazione dinamica della cartella se non esiste (fondamentale per nuovi server)
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
            
            if os.path.exists(self.key_path):
                with open(self.key_path, "rb") as key_file:
                    return key_file.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_path, "wb") as key_file:
                    key_file.write(key)
                logger.info(f"Nuova chiave di sicurezza generata in: {self.key_path}")
                return key
        except Exception as e:
            logger.critical(f"FALLIMENTO CRITICO: Impossibile gestire la chiave di cifratura: {e}")
            raise

    def encrypt_data(self, data: str) -> bytes:
        """Trasforma stringhe in dati cifrati pronti per il database."""
        try:
            return self.cipher.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Errore durante la cifratura: {e}")
            raise

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decifra i dati e verifica l'integrità del token."""
        try:
            return self.cipher.decrypt(encrypted_data).decode('utf-8')
        except InvalidToken:
            logger.error("ERRORE SICUREZZA: Chiave non valida o dati compromessi.")
            raise
        except Exception as e:
            logger.error(f"Errore generico decifratura: {e}")
            raise