# FILE: experimental_modules/engine_settori.py
# SCOPO: Mappatura silente dei settori senza interferire con RGD-Alpha

SETTORI_CONFIG = {
    "PRIMARIO_ALIMENTARE": {
        "keywords": ["scadenza", "lotto", "haccp", "temperatura", "fresco"],
        "analisi_tipo": "Breve Termine / Deperibilità"
    },
    "SECONDARIO_MANIFATTURA": {
        "keywords": ["taglia", "colore", "materia prima", "produzione", "stock"],
        "analisi_tipo": "Medio Termine / Ciclo Produttivo"
    },
    "TERZIARIO_LOGISTICA": {
        "keywords": ["bolla", "ddt", "targa", "consegna", "ritardo"],
        "analisi_tipo": "Statistica di Flusso / Lead Time"
    }
}

def identifica_settore_da_file(lista_colonne):
    """
    Tenta di identificare il settore basandosi sui nomi delle colonne.
    Se non trova nulla di certo, restituisce 'GENERALE'.
    """
    for settore, config in SETTORI_CONFIG.items():
        if any(key in str(lista_colonne).lower() for key in config["keywords"]):
            return settore
    return "GENERALE"