import logging
from core.database import DatabaseAziendale

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("RGD-Alpha.Main")
def genera_storico_simulato(db, user_id, asset, giorni=12):
    """
    MOTORE DI STRESS TEST: Simula dati storici per alimentare l'algoritmo predittivo.
    Sincronizzato con la firma corretta di db.salva_asset.
    """
    logger.info(f"⚙️ Generazione storico simulato per: {asset.nome}")
    rischio_base = asset.rischio
    
    # Determina il tipo di asset basandosi sulla classe dell'oggetto
    tipo_asset = asset.__class__.__name__
    
    for i in range(giorni, 0, -1):
        fluttuazione = random.uniform(-0.5, 0.8) 
        rischio_simulato = max(1.0, min(10.0, rischio_base + fluttuazione))
        
        # Salva nel database rispettando la firma esatta di database.py
        db.salva_asset(
            user_id=user_id,
            nome_asset=asset.nome,
            rischio=rischio_simulato,
            tipo=tipo_asset,
            momentum="Simulazione",
            volatilita=abs(fluttuazione)
        )
        
    asset.rischio = riesgo_base

def avvia_sistema():
    """
    Coordina Database, Analista e Simulatore Proattivo in ambiente multi-tenant.
    """
    # 1. Configurazione Iniziale e Ambiente di Test
    EMAIL_TESTER = "tester@rgdalpha.com"
    PASSWORD_TESTER = "RgdAlpha2026!"
    COMPANY_ID_DEFAULT = "AZ-TEST-01"
    
    consulente = ConsulenteAziendale(COMPANY_ID_DEFAULT)
    
    # Caricamento Configurazione File
    try:
        with open(consulente.file_config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.warning(f"⚠️ Configurazione non trovata per {COMPANY_ID_DEFAULT}. Utilizzo impostazioni di fallback.")
        config = {}

    db_path = Path(config.get("db_path", "data/db/azienda.db"))
    log_path = Path(config.get("log_path", "data/logs/report_critico.txt"))

    # Inizializzazione Database
    db = DatabaseAziendale(db_folder=str(db_path.parent), db_name=db_path.name)

    # 2. Garantire l'esistenza di un utente per il vincolo di Foreign Key
    utente_tester = db.get_utente_by_email(EMAIL_TESTER)
    if not utente_tester:
        logger.info(f"🌱 Creazione utente di test multi-tenant: {EMAIL_TESTER}")
        user_id = db.crea_utente(email=EMAIL_TESTER, password=PASSWORD_TESTER, ruolo="user", azienda=COMPANY_ID_DEFAULT)
        utente_tester = db.get_utente_by_id(user_id)
    else:
        user_id = utente_tester["id"]

    azienda_reale = utente_tester["azienda"]

    # Inizializzazione Componenti Core rimanenti
    sentinella = Sentinella(log_dir=str(log_path.parent), filename=log_path.name)
    analista = AnalistaRischio(db_path=str(db_path))
    simulatore = SimulatoreRischio()

    # 3. Definizione Ecosistema Asset (Legati all'identità protetta)
    ecosistema = [
        AssetDiMercato(101, "Fornitore Acciaio", 6.8, azienda_reale),
        AssetDiMercato(102, "Trasporti Rapidi", 4.2, azienda_reale),
        AssetDiRelazione(201, "Cliente Gold Italia", 15000.0, 3.5, azienda_reale),
        AssetDiValore(301, "Server Farm Primaria", 5000.0, 0.0, 2.5, azienda_reale)
    ]
    
    print(f"\n🚀 --- INTELLIGENCE PROATTIVA RGD-ALPHA: {azienda_reale} ---")
    
    # 4. Fase di Popolamento Storico
    for asset in ecosistema:
        genera_storico_simulato(db, user_id, asset)
    
    print(f"✅ Analisi dei trend completata. Avvio elaborazione statistica...\n")

    # 5. Loop di Analisi, Persistenza Corrente e Simulazione
    for asset in ecosistema:
        tipo_asset = asset.__class__.__name__
        
        # Salvataggio dello stato attuale dell'asset
        db.salva_asset(
            user_id=user_id,
            nome_asset=asset.nome,
            rischio=asset.rischio,
            tipo=tipo_asset
        )
        
        report = analista.calcola_trend_predittivo(asset.nome, azienda_reale)
        
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
                print(f"🔮 PROIEZIONE 30 GG: Probabilità Crisis: {proiezione['probabilita_crisi']}%")
                print(f"⏳ SOPRAVVIVENZA STIMATA: {proiezione['giorni_sopravvivenza_stimati']} giorni")
                
                if proiezione['probabilita_crisi'] > 40:
                    print(f"🔴 ALERT PROATTIVO: Rischio critico di instabilità imminente!")
            
            print(f"💡 AZIONE CONSIGLIATA: {report.get('azione')}")
            
            if report.get("alert_critico"):
                print(f"⚠️ STATO ATTUALE: Superata soglia critica ({report['valore_attuale']})")
        
        print("-" * 50)

    # 6. Elaborazione ed Esecuzione Centralizzata KPI via Database
    print("\n📊 --- AGGREGAZIONE STRATEGICA KPI (SQL CORE) ---")
    kpi_finali = db.calcola_e_salva_kpi_correnti(user_id)
    print(f"🎯 Rischio Medio Aziendale: {kpi_finali['rischio_medio']}/10")
    print(f"💎 Solidità Operativa: {kpi_finali['solidita']}%")
    print(f"📉 Impatto Finanziario Stimato (30gg): {kpi_finali['impatto_30gg']}")
    print("--------------------------------------------------")

    # 7. Reportistica Finale ed Estrazione Dati via Dataframe (Pandas)
    df_storico = db.recupera_asset_per_utente(user_id)
    
    if not df_storico.empty:
        # Filtriamo gli elementi ad alto rischio per la Sentinella (es. rischio > 5.0)
        df_critici = df_storico[df_storico["rischio"] > 5.0]
        rischi_storici = df_critici[["nome", "rischio", "timestamp"]].values.tolist()
        
        if rischi_storici:
            print(f"\n🛡️  Rilevate {len(rischi_storici)} criticità protette da cifratura nel database.")
            # Invio dei dati convertiti in lista alla Sentinella per la scrittura su file log
            sentinella.genera_report(rischi_storici)
            print(f"✅ Analisi terminata. Report di sistema aggiornato: {log_path}")
        else:
            print("\n✅ Analisi completata: Nessun rischio critico superiore alla soglia rilevato nei dati cifrati.")
    else:
        print("\n✅ Analisi completata: Archivio vuoto, nessuna attività rilevata.")

if __name__ == "__main__":
    try:
        avvia_sistema()
    except Exception as e:
        logger.critical(f"💥 Errore fatale irreversibile nel motore principale: {e}")


def avvia_sistema():
    """
    Entry point di test e diagnostica.
    Non avvia Streamlit.
    Non modifica logiche critiche.
    Serve solo per verificare che il database e i moduli core rispondano.
    """
    logger.info("🚀 Avvio diagnostica RGD-Alpha")

    # 1. Inizializzazione database
    try:
        db = DatabaseAziendale()
        logger.info("🗄️ Database inizializzato correttamente.")
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione database: {e}")
        return

    # 2. Verifica admin
    try:
        admin = db.get_utente_by_email("admin@rgandja.com")
        if admin:
            logger.info("👤 Admin rilevato correttamente nel database.")
        else:
            logger.warning("⚠️ Admin NON trovato. Verrà ricreato automaticamente al prossimo avvio.")
    except Exception as e:
        logger.error(f"❌ Errore verifica admin: {e}")

    logger.info("✅ Diagnostica completata. Il sistema è operativo.")


if __name__ == "__main__":
    avvia_sistema()

