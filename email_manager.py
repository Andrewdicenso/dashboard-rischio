import os
import pickle
import base64
import time
import json
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
# Importiamo il database
from core.database import DatabaseAziendale
# Importiamo il nuovo connettore proattivo
from connectors.connector_manager import SFTPConnector

# Inizializziamo il database
db = DatabaseAziendale()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def autentica_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def invia_risposta(service, destinatario, oggetto_originale, corpo_richiesta):
    message = EmailMessage()
    risposta = f"Gentile utente,\n\nconfermiamo di aver ricevuto la Sua richiesta: '{oggetto_originale}'.\n\nDati ricevuti:\n{corpo_richiesta}\n\nIl nostro team di supporto la prenderà in carico a breve.\n\nCordiali saluti,\nRGandja Co-Pilota"
    message.set_content(risposta)
    message['To'] = destinatario
    message['From'] = 'me'
    message['Subject'] = f"Re: {oggetto_originale}"
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
    print(f"Risposta inviata a {destinatario}")

def leggi_mail(service):
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    
    if not messages:
        return

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        
        payload = msg['payload']
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        headers = msg['payload']['headers']
        oggetto = next((h['value'] for h in headers if h['name'] == 'Subject'), "Senza Oggetto")
        mittente = next((h['value'] for h in headers if h['name'] == 'From'), "Sconosciuto")
        
        if "Richiedi Accreditamento" in oggetto:
            print(f"Trovata richiesta da {mittente}.")
            nome_azienda = "Sconosciuto"
            if "Azienda:" in body:
                nome_azienda = body.split("Azienda:")[1].split("|")[0].strip()
            
            db.salva_nuova_richiesta(nome_azienda, mittente)
            
            invia_risposta(service, mittente, oggetto, body)
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
        
        elif "Hai bisogno di un adeguamento?" in oggetto:
            print(f"Trovata richiesta di Adeguamento da {mittente}!")
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == '__main__':
    print("Avvio Co-Pilota RGandja in modalità monitoraggio...")
    try:
        service = autentica_gmail()
        
        # Caricamento sicuro delle credenziali e lista file da config.json
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                sftp_conf = config['sftp']
                files_conf = config['files_to_sync']
        except FileNotFoundError:
            print("Errore: Il file 'config.json' non è stato trovato.")
            exit()
        
        # Inizializzazione connettore con la nuova logica flessibile
        sftp_manager = SFTPConnector(
            host=sftp_conf['host'],
            username=sftp_conf['username'],
            password=sftp_conf['password'],
            files_to_sync=files_conf
        )
        
        while True:
            # 1. Sincronizzazione proattiva dati
            print("Esecuzione sincronizzazione dati...")
            sftp_manager.sync_dati()
            
            # 2. Controllo Email
            leggi_mail(service)
            
            # 3. Attesa
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nMonitoraggio interrotto correttamente.")
    except Exception as e:
        print(f"\nErrore critico: {e}")