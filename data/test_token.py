from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

# Percorso del file token.json (nel tuo screenshot vedo 'token.pickle', 
# assicurati di usare il nome corretto che usi nel tuo script principale)
TOKEN_FILE = 'token.pickle' 

def verifica_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Errore: Il file {TOKEN_FILE} non esiste.")
        return

    # Carica il token (se è un pickle, usa Credentials.from_authorized_user_info o similare)
    # Nota: Se il tuo sistema usa pickle, potresti dover usare pickle.load
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes=['https://www.googleapis.com/auth/gmail.readonly'])

    if creds and creds.expired and creds.refresh_token:
        print("Il token è scaduto, provo ad aggiornarlo...")
        creds.refresh(Request())
        # Opzionale: risalva se necessario

    # Prova una chiamata reale
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    print("Connessione riuscita! Accesso a Gmail confermato.")

if __name__ == '__main__':
    verifica_token()