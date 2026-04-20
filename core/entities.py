class AssetStrategico:
    def __init__(self, id, nome, rischio):
        self.id = id
        self.nome = nome
        self.rischio = rischio

class AssetDiMercato(AssetStrategico):
    def __init__(self, id, nome, affidabilita, rischio):
        super().__init__(id, nome, rischio)
        self.affidabilita = affidabilita

    def analisi_strategica(self):
        if self.affidabilita > 0.8 and self.rischio < 3:
            return "Partner Strategico: Da blindare"
        elif self.affidabilita < 0.5:
            return "Partner Critico: Cercare alternative"
        return "Partner Standard"

class AssetDiRelazione(AssetStrategico):
    def __init__(self, id, nome, ltv, rischio):
        super().__init__(id, nome, rischio)
        self.ltv = ltv

    def analisi_strategica(self):
        if self.ltv > 5000:
            return "Cliente Premium: Alto valore"
        elif self.rischio > 7:
            return "Cliente a rischio insolvenza"
        return "Cliente Standard"