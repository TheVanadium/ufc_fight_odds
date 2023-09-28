DEFAULT_ELO: int = 1500

class Fighter():
    def __init__(self, name: str, region: str = "USA"):
        self.name: str = name
        self.wins: int = 0
        self.draws: int = 0
        self.losses: int = 0
        self.region: str = region

    fight_record: dict = {}

    def elo(self):
        return DEFAULT_ELO

    def experienced(self):
        return False

    def add_fight(self, opponent: str, result: str, location: str, date: str):
        pass
