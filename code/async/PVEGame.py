import chess
import chess.engine

import Game

class PVEGame(Game.Game):
    def __init__(self, player, rank, depth, time):
        super().__init__([player], rank, time)
        self.bot = None
        self.depth = depth

    async def initialize_bot(self):
        self.bot = (await chess.engine.popen_uci("./stockfish"))[1]

    async def end_game(self, winner: bool):
        await self.current().send_end(winner)