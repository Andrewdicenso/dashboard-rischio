import json
import os
from consulente import ConsulenteAziendale
from core.entities import AssetDiMercato
from core.database import DatabaseAziendale
from core.notifier import Sentinella
from core.analyst import AnalistaRischio

def avvia_sistema():
    # 1. Caricamento Identità Aziendale
    COMPANY_ID = "AZIENDA_001"
    consulente = ConsulenteAziendale(COMPANY_ID)
    
    with open(consulente.file_config, 'r') as f:
        config = json.load(f)
    
    # 2. Inizializzazione Componenti (Percorsi allineati 2026)
    db = DatabaseAziendale(
        db_folder=os.path.dirname(config.get("db_path", "data/db/azienda.db")), 
        db_name=os.path.basename(config.get("db_path", "azienda.db"))
    )
    sentinella = Sentinella(
        log_dir=os.path.dirname(config.get("log_path", "data/logs/report_critico.txt")), 
        filename=os.path.basename(config.get("log_path", "report_critico.txt"))
    )
    
    # 3. Ecosistema dinamico
    ecosistema = [
        AssetDiMercato(101, "Fornitore Acciaio", 0.9, 2, company_id=COMPANY_ID),
        AssetDiMercato(102, "Trasporti Rapidi", 0.4, 6, company_id=COMPANY_ID)
    ]
    
    print(f"\n🚀 --- ANALISI RGD-ALPHA AVVIATA PER: {consulente.nome_azienda} ---")
    
    # 4. Elaborazione e Persistenza
    for asset in ecosistema:
        db.salva_asset(asset, COMPANY_ID)
        
    # Estrazione Rischi
    rischi_storici = db.estrai_asset_a_rischio(COMPANY_ID, 5)
    
    if rischi_storici:
        for nome, rischio in rischi_storici:
            print(f"⚠️ ALLERTA: {nome} | Livello Rischio: {rischio}")
        
        # 5. Notifica e Chiusura
        sentinella.genera_report(rischi_storici)
        print(f"✅ Analisi completata. Report generato in {sentinella.log_path}")
    else:
        print("✅ Nessun rischio critico rilevato.")

if __name__ == "__main__":
    avvia_sistema()