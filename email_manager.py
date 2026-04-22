import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Definiamo i permessi
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def autentica_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v3', credentials=creds)

def leggi_mail(service):
    # Cerca le mail non lette
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        oggetto = next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject')
        
        if "Richiedi Accreditamento" in oggetto:
            print("Trovata richiesta di Accreditamento!")
            # Qui chiameremo la funzione di invio risposta automatica
        elif "Hai bisogno di un adeguamento?" in oggetto:
            print("Trovata richiesta di Adeguamento!")
            # Qui chiameremo la funzione di log
            if __name__ == '__main__':
    service = autentica_gmail()
    leggi_mail(service)
    print("Controllo mail completato.")