import chess
import confighandler
import Player
import os


class Game:
    __slots__ = ["fen", "board", "players", "turn", "popped"]

    def __init__(self, sids: [], rank: int, time: int):
        if confighandler.get_configs() is None:
            confighandler.load_configs(os.path.join(os.path.dirname(__file__), 'configs.csv'))
        self.fen = confighandler.gen_start_fen(rank)
        self.board = chess.Board(self.fen)
        self.players = []
        for i, sid in enumerate(sids):
            self.players.append(Player.Player(sid, not bool(i), time))
        self.turn = 0
        self.popped = False

    @property
    def current(self):
        return self.players[self.turn]
    
    @property
    def next(self):
        return self.players[1 - self.turn]

    def opponent(self, sid):
        return self.players[1-self.players.index(sid)]
