import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def verifica_token():
    creds = Credentials(
        None,
        refresh_token=st.secrets["google_api"]["refresh_token"],
        client_id=st.secrets["google_api"]["client_id"],
        client_secret=st.secrets["google_api"]["client_secret"],
        token_uri=st.secrets["google_api"]["token_uri"]
    )

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    print("Connessione riuscita! Accesso a Gmail confermato.")

if __name__ == '__main__':
    verifica_token()
