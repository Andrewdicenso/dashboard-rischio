class AssetStrategico:
    def __init__(self, id: int, nome: str, rischio: int):
        self.id = id
        self.nome = nome
        self.rischio = rischio

class AssetDiMercato(AssetStrategico):
    def __init__(self, id: int, nome: str, affidabilita: float, rischio: int):
        super().__init__(id, nome, rischio)
        self.affidabilita = affidabilita

    def analisi_strategica(self) -> str:
        if self.affidabilita > 0.8 and self.rischio < 3:
            return "Partner Strategico: Da blindare"
        elif self.affidabilita < 0.5:
            return "Partner Critico: Cercare alternative"
        return "Partner Standard"

class AssetDiRelazione(AssetStrategico):
    def __init__(self, id: int, nome: str, ltv: float, rischio: int):
        super().__init__(id, nome, rischio)
        self.ltv = ltv

    def analisi_strategica(self) -> str:
        if self.ltv > 5000:
            return "Cliente Premium: Alto valore"
        elif self.rischio > 7:
            return "Cliente a rischio insolvenza"
        return "Cliente Standard"

# Ho aggiunto questa classe che mancava nell'IngestorStrategico
class AssetDiValore(AssetStrategico):
    def __init__(self, id: int, nome: bytes, costo: float, prezzo: float, rischio: int):
        # Il nome è passato come bytes perché arriva criptato da SecureVault
        super().__init__(id, nome, rischio)
        self.costo = costo
        self.prezzo = prezzo