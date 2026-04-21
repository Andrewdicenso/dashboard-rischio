from core.entities import AssetDiMercato, AssetDiRelazione
from core.engine import DataGateway
from core.database import DatabaseAziendale
from core.notifier import Sentinella
from core.analyst import AnalistaRischio
import os

# --- CONFIGURAZIONE ---
MIA_AZIENDA = "AZIENDA_001"
# Assicuriamo che la cartella data esista per i report
os.makedirs("data/logs", exist_ok=True)

# 1. Inizializzazione
db = DatabaseAziendale()
sentinella = Sentinella()
analista = AnalistaRischio(db.conn)

# Ecosistema
ecosistema = [
    AssetDiMercato(101, "Fornitore Acciaio", 0.9, 2),
    AssetDiMercato(102, "Trasporti Rapidi", 0.4, 6)
]

# 2. Analisi e Salvataggio
print(f"--- ANALISI STRATEGICA PER {MIA_AZIENDA} ---")
for asset in ecosistema:
    # Assumiamo che db.salva_asset gestisca internamente i percorsi
    db.salva_asset(asset, MIA_AZIENDA)

# 3. Interrogazione
rischi_storici = db.estrai_asset_a_rischio(MIA_AZIENDA, 5)
for nome, rischio in rischi_storici:
    print(f"ATTENZIONE: {nome} ha rischio {rischio} per {MIA_AZIENDA}.")

# 4. Sentinella (Assicuriamoci che il report vada in data/logs)
report_path = os.path.join("data/logs", "report_critico.txt")
sentinella.genera_report(rischi_storici, output_file=report_path)
print(f"Report generato in: {report_path}")