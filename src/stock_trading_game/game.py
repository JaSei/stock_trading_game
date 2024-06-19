from .player import Player

class Game:
    def __init__(self, players: list[Player]) -> None:
        self.players = players 
        self.turn = 1
