# FILE: test_onboarding.py
# Scopo: Testare il modulo sperimentale senza toccare il core RGD-Alpha
from experimental_modules.engine_settori import identifica_settore_da_file

def esegui_test():
    # Esempi di intestazioni che potresti trovare in file di diversi clienti
    test_cases = {
        "Cliente Caseificio": ["Data", "ID_Asset", "Lotto", "Temperatura", "Valore", "Impatto"],
        "Cliente Abbigliamento": ["Codice_Prodotto", "Taglia", "Colore", "Prezzo", "Impatto"],
        "Cliente Trasporti": ["Data", "Targa_Mezzo", "DDT", "Destinazione", "Ritardo", "Impatto"],
        "Cliente Generico": ["ID", "Nome_Risorsa", "Grado_Rischio"]
    }

    print("=== AVVIO TEST MODULO SPERIMENTALE SETTORI ===")
    
    for nome_cliente, colonne in test_cases.items():
        settore = identifica_settore_da_file(colonne)
        print(f"\nAnalisi per: {nome_cliente}")
        print(f" > Colonne rilevate: {colonne}")
        print(f" > Risultato Mappatura: {settore}")

if __name__ == "__main__":
    esegui_test()