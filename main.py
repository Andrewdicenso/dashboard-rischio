from core.entities import AssetDiMercato, AssetDiRelazione
from core.engine import DataGateway
from core.database import DatabaseAziendale
from core.notifier import Sentinella
from core.analyst import AnalistaRischio

# Identificativo dell'azienda che sta usando il software
MIA_AZIENDA = "AZIENDA_001"

# 1. Inizializzazione
db = DatabaseAziendale()
sentinella = Sentinella()
analista = AnalistaRischio(db.conn)

# Ecosistema
ecosistema = [
    AssetDiMercato(101, "Fornitore Acciaio", 0.9, 2),
    AssetDiMercato(102, "Trasporti Rapidi", 0.4, 6)
]

# 2. Analisi e Salvataggio (Passiamo sempre MIA_AZIENDA)
print(f"--- ANALISI STRATEGICA PER {MIA_AZIENDA} ---")
for asset in ecosistema:
    db.salva_asset(asset, MIA_AZIENDA)

# 3. Interrogazione (Passiamo sempre MIA_AZIENDA)
rischi_storici = db.estrai_asset_a_rischio(MIA_AZIENDA, 5)
for nome, rischio in rischi_storici:
    print(f"ATTENZIONE: {nome} ha rischio {rischio} per {MIA_AZIENDA}.")

# 4. Sentinella
sentinella.genera_report(rischi_storici)