import logging

logger = logging.getLogger("RGD-Alpha.Entities")

class AssetStrategico:
    """
    Classe Base: Ogni risorsa aziendale deve avere un'appartenenza societaria (company_id).
    """
    def __init__(self, id: int, nome: str, rischio: float, company_id: str = "GENERIC_CORP"):
        self.id = id
        self.nome = nome
        self.rischio = rischio
        self.company_id = company_id # Fondamentale per la scalabilità multi-aziendale

class AssetDiMercato:
    def __init__(self, id_asset, nome, valore, impatto, company_id=None):
        self.id_asset = id_asset
        self.nome = nome
        self.valore = valore
        self.impatto = impatto
        self.company_id = company_id
        # Il rischio viene calcolato dinamicamente
        self.rischio = round(valore * impatto, 2)
    """
    Partner e Fornitori. Valutazione basata su affidabilità.
    """
    def __init__(self, id: int, nome: str, affidabilita: float, rischio: float, company_id: str = "GENERIC_CORP"):
        super().__init__(id, nome, rischio, company_id)
        self.affidabilita = affidabilita
        self.stato = "Attivo" # Valore di default per engine.py

    def analisi_strategica(self) -> str:
        if self.affidabilita > 0.8 and self.rischio < 3:
            return "Partner Strategico: Punto fermo da tutelare."
        elif self.affidabilita < 0.5:
            return "Partner Critico: Instabilità elevata, rischio operativo."
        return "Partner Standard: Collaborazione regolare."

class AssetDiRelazione(AssetStrategico):
    """
    Clienti: Valutazione basata su Life Time Value (LTV).
    """
    def __init__(self, id: int, nome: str, ltv: float, rischio: float, company_id: str = "GENERIC_CORP"):
        super().__init__(id, nome, rischio, company_id)
        self.ltv = ltv

    def analisi_strategica(self) -> str:
        if self.ltv > 5000:
            return "Cliente Premium: Alto impatto sul fatturato."
        elif self.rischio > 7:
            return "Cliente a rischio: Verificare regolarità pagamenti."
        return "Cliente Standard."

class AssetDiValore(AssetStrategico):
    """
    Risorse Fisiche e Prodotti: Compatibile con i requisiti dello Scan Strategico.
    """
    def __init__(self, id: int, nome: str, costo: float, prezzo: float, rischio: float, company_id: str = "GENERIC_CORP"):
        super().__init__(id, nome, rischio, company_id)
        self.costo = costo
        self.prezzo = prezzo
        
        # Attributi dinamici richiesti dall'Engine
        self.quantita = 0.0
        self.volume = 0.0
        self.stato = "Disponibile"

    def verifica_integrita_dati(self, contesto):
        """Controlla se mancano parametri vitali per l'analisi engine."""
        messaggi = []
        if contesto == "Magazzino" and (self.quantita is None or self.quantita == 0):
            messaggi.append("Attenzione: Quantità stock non rilevata o zero.")
        return messaggi

    def calcola_margine(self) -> float:
        return self.prezzo - self.costo

    def genera_alert(self, soglia: float = 7.0) -> dict:
        if self.rischio > soglia:
            return {
                "stato": "CRITICO",
                "messaggio": f"L'asset '{self.nome}' richiede intervento immediato."
            }
        return {"stato": "OK", "messaggio": "Parametri nella norma."}