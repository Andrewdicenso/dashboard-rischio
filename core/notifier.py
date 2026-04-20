import datetime

class Sentinella:
    def __init__(self, file_log="report_critico.txt"):
        self.file_log = file_log

    def genera_report(self, asset_critici):
        """Scrive un report formattato su file se trova criticità."""
        if not asset_critici:
            return

        with open(self.file_log, "a") as f:
            f.write(f"\n--- REPORT CRITICO: {datetime.datetime.now()} ---\n")
            for nome, rischio in asset_critici:
                f.write(f"ALLERTA: L'asset '{nome}' presenta un rischio critico di {rischio}.\n")
        print(f"SENTINELLA: Report generato in {self.file_log}")