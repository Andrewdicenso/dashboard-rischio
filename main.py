from core.entities import AssetDiMercato, AssetDiRelazione
from core.engine import DataGateway
from core.database import DatabaseAziendale
from core.notifier import Sentinella
from core.analyst import AnalistaRischio
import os

# --- CONFIGURAZIONE ---
MIA_AZIENDA = "AZIENDA_001"
# Percorsi definiti in modo centralizzato per coerenza con la struttura VS Code
DB_PATH = "data/db/azienda.db"
LOG_PATH = "data/logs/report_critico.txt"

# 1. Inizializzazione
# Passiamo i percorsi specifici al database e alla sentinella
db = DatabaseAziendale(db_folder="data/db", db_name="azienda.db")
sentinella = Sentinella(log_dir="data/logs", filename="report_critico.txt")
analista = AnalistaRischio(db.conn)

# Ecosistema
ecosistema = [
    AssetDiMercato(101, "Fornitore Acciaio", 0.9, 2),
    AssetDiMercato(102, "Trasporti Rapidi", 0.4, 6)
]

# 2. Analisi e Salvataggio
print(f"--- ANALISI STRATEGICA PER {MIA_AZIENDA} ---")
for asset in ecosistema:
    db.salva_asset(asset, MIA_AZIENDA)

# 3. Interrogazione
rischi_storici = db.estrai_asset_a_rischio(MIA_AZIENDA, 5)
for nome, rischio in rischi_storici:
    print(f"ATTENZIONE: {nome} ha rischio {rischio} per {MIA_AZIENDA}.")

# 4. Sentinella
sentinella.genera_report(rischi_storici)
print(f"Report generato in: {LOG_PATH}")