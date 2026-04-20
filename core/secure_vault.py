from cryptography.fernet import Fernet

class SecureVault:
    def __init__(self):
        # Generiamo una chiave segreta. 
        # NOTA: In produzione, questa chiave andrà salvata in un luogo sicuro!
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_data(self, data: str) -> bytes:
        # Cripta il dato (trasforma testo in codice illeggibile)
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        # Decripta il dato (torna leggibile solo per chi ha la chiave)
        return self.cipher.decrypt(encrypted_data).decode()