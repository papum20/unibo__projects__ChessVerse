import chess
import chess.engine

import confighandler
import Player
import os

class Game:
    def __init__(self, sids: [], rank: int, time: int):
        if confighandler.get_configs() is None:
            confighandler.load_configs(os.path.join(os.path.dirname(__file__), 'configs.csv'))
        self.fen = confighandler.gen_start_fen(rank)
        self.board = chess.Board(self.fen)
        self.players = []
        for i, sid in enumerate(sids):
            self.players.append(Player.Player(sid, i, time))
        self.turn = 0
        self.popped = False

    @property
    def current(self):
        return self.players[self.turn]
    
    @property
    def opponent(self):
        return self.players[1 - self.turn]