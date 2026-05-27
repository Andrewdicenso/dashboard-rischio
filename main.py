import json
import logging
import random
from pathlib import Path

# --- IMPORT MODULI CORE ---
from consulente import ConsulenteAziendale
from core.entities import AssetDiMercato, AssetDiRelazione, AssetDiValore
from core.database import DatabaseAziendale
from core.notifier import Sentinella
from core.analyst import AnalistaRischio
from core.simulator import SimulatoreRischio

# Configurazione del sistema di logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RGD-Alpha.Main")

def genera_storico_simulato(db, asset, company_id, giorni=12):
    """
    MOTORE DI STRESS TEST: Simula dati storici per alimentare l'algoritmo predittivo.
    """
    logger.info(f"⚙️ Generazione storico simulato per: {asset.nome}")
    rischio_base = asset.rischio
    
    for i in range(giorni, 0, -1):
        fluttuazione = random.uniform(-0.5, 0.8) 
        rischio_simulato = max(1.0, min(10.0, rischio_base + fluttuazione))
        
        asset.rischio = rischio_simulato
        db.salva_asset(asset)
        
    asset.rischio = rischio_base

def avvia_sistema():
    """
    Coordina Database, Analista e Simulatore Proattivo.
    """
    COMPANY_ID = "AZ-TEST-01" 
    consulente = ConsulenteAziendale(COMPANY_ID)
    
    # 1. Caricamento Configurazione
    try:
        with open(consulente.file_config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ Configurazione non trovata per {COMPANY_ID}. Verificare il file JSON.")
        return

    # 2. Inizializzazione Professionale Componenti Core
    db_path = Path(config.get("db_path", "data/db/azienda.db"))
    log_path = Path(config.get("log_path", "data/logs/report_critico.txt"))

    # Inizializzazione oggetti secondo gerarchia ingegneristica
    db = DatabaseAziendale(db_folder=str(db_path.parent), db_name=db_path.name)
    # Nota: db.crea_tabelle() viene già chiamato internamente nel __init__ del database corretto sopra

    sentinella = Sentinella(log_dir=str(log_path.parent), filename=log_path.name)
    analista = AnalistaRischio(db_path=str(db_path))
    simulatore = SimulatoreRischio()

    # 3. Definizione Ecosistema Asset
    ecosistema = [
        AssetDiMercato(101, "Fornitore Acciaio", 6.8, COMPANY_ID),
        AssetDiMercato(102, "Trasporti Rapidi", 4.2, COMPANY_ID),
        AssetDiRelazione(201, "Cliente Gold Italia", 15000.0, 3.5, COMPANY_ID),
        AssetDiValore(301, "Server Farm Primaria", 5000.0, 0.0, 2.5, COMPANY_ID)
    ]
    
    print(f"\n🚀 --- INTELLIGENCE PROATTIVA RGD-ALPHA: {consulente.nome_azienda} ---")
    
    # 4. Fase di Popolamento
    for asset in ecosistema:
        genera_storico_simulato(db, asset, COMPANY_ID)
    
    print(f"✅ Analisi dei trend completata. Avvio elaborazione statistica...\n")

    # 5. Loop di Analisi e Simulazione
    for asset in ecosistema:
        db.salva_asset(asset) 
        report = analista.calcola_trend_predittivo(asset.nome, COMPANY_ID)
        
        print(f"[ANALISI ASSET: {asset.nome}]")
        
        if report.get("status") == "Inizializzazione":
            print(f"ℹ️ Dati storici in fase di consolidamento.")
        else:
            m_perc = report.get('momentum_percentuale', '0%')
            volat = report.get('indice_volatilita', 0)
            print(f"📊 Momentum: {m_perc} | Volatilità: {volat}")
            print(f"🧠 VALUTAZIONE: {report.get('valutazione_strategica')}")
            
            proiezione = simulatore.esegui_stress_test(
                valore_attuale=report['valore_attuale'],
                volatilita=volat
            )
            
            if proiezione:
                print(f"🔮 PROIEZIONE 30 GG: Probabilità Crisi: {proiezione['probabilita_crisi']}%")
                print(f"⏳ SOPRAVVIVENZA STIMATA: {proiezione['giorni_sopravvivenza_stimati']} giorni")
                
                if proiezione['probabilita_crisi'] > 40:
                    print(f"🔴 ALERT PROATTIVO: Rischio critico di instabilità imminente!")
            
            print(f"💡 AZIONE CONSIGLIATA: {report.get('azione')}")
            
            if report.get("alert_critico"):
                print(f"⚠️ STATO ATTUALE: Superata soglia critica ({report['valore_attuale']})")
        
        print("-" * 50)

    # 6. Reportistica Finale
    # Estraiamo i dati (ora il DB restituisce 3 valori: nome, rischio, timestamp)
    rischi_storici = db.estrai_asset_a_rischio(COMPANY_ID, 5)
    
    if rischi_storici:
        # Messaggio di log per conferma visiva nel terminale
        print(f"\n🛡️  Rilevate {len(rischi_storici)} criticità protette da cifratura.")
        
        # Sincronizzazione con il modulo sentinella
        # Passiamo i dati completi; assicurati che sentinella.py sia pronto a riceverli
        sentinella.genera_report(rischi_storici)
        
        print(f"✅ Analisi terminata. Report di sistema aggiornato: {log_path}")
    else:
        print("\n✅ Analisi completata: Nessun rischio critico rilevato nei dati cifrati.")

if __name__ == "__main__":
    try:
        avvia_sistema()
    except Exception as e:
        # Questo catturerà eventuali altri errori di 'unpacking' rimasti
        logger.critical(f"💥 Errore fatale irreversibile: {e}")