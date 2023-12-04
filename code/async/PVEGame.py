import chess
from chess.engine import Limit, popen_uci
from Game import Game
from const import MIN_RANK, MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME
from time import perf_counter


class PVEGame(Game):
    __slots__ = ["bot", "depth"]

    @classmethod
    async def start(cls, sid: str, data: dict[str, str]) -> None:
        def check_int(key, inf, sup):
            try:
                v = int(data[key])
                return inf <= v <= sup
            except (ValueError, TypeError):
                return False
        if "rank" not in data or "depth" not in data or "time" not in data:
            await Game.sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
            return
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await Game.sio.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_int("depth", MIN_DEPTH, MAX_DEPTH):
            await Game.sio.emit("error", {"cause": "Invalid bot strength", "fatal": True}, room=sid)
            return
        if not check_int("time", MIN_TIME, MAX_TIME):
            await Game.sio.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return
        if sid not in Game.sid_to_id:
            Game.sid_to_id[sid] = sid # solo in PVE;
            Game.games[sid] = PVEGame(sid, int(data["rank"]), int(data["depth"]), int(data["time"]))
            await Game.games[sid].instanciate_bot()
            await Game.sio.emit("config", {"fen": Game.games[sid].fen}, room=sid)
        else:
            await Game.sio.emit("error", {"cause": "SID already used", "fatal": True}, room=sid)

    def __init__(self, player: str, rank: int, depth: int, time: int) -> None:
        super().__init__([player], rank, time)
        self.bot = None
        self.depth = depth

    async def disconnect(self, sid: str) -> None:
        await self.bot.quit()
        del Game.games[sid]
        del Game.sid_to_id[sid]

    async def instanciate_bot(self) -> None:
        self.bot = (await popen_uci("./stockfish"))[1]

    async def move(self, sid: str, data: dict[str, str]) -> None:
        if "san" not in data:
            await Game.sio.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if data["san"] is None:
            await Game.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
            return
        if not self.current.has_time():
            return
        try:
            uci_move = self.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await Game.sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        self.board.push_uci(uci_move)
        outcome = self.board.outcome()
        if outcome is not None:
            await Game.sio.emit("move", {"san": san_bot_move}, room=sid)
            await Game.sio.emit("end", {"winner": outcome.winner}, room=sid)
            await self.disconnect(sid)
            return
        start = perf_counter()
        bot_move = (await self.bot.play(self.board, Limit(depth=self.depth))).move
        san_bot_move = self.board.san(bot_move)
        self.board.push_uci(bot_move.uci())
        outcome = self.board.outcome()
        if outcome is not None:
            await Game.sio.emit("move", {"san": san_bot_move}, room=sid)
            await Game.sio.emit("end", {"winner": outcome.winner}, room=sid)
            await self.disconnect(sid)
            return
        self.popped = False
        end = perf_counter()
        self.current.add_time(end - start)
        self.current.first_move = False
        await Game.sio.emit("move", {"san": san_bot_move}, room=sid)

    async def pop(self, sid: str) -> None:
        if self.popped:
            await Game.sio.emit("error", {"cause": "You have already popped"}, room=sid)
        elif self.board.fullmove_number == 1:
            await Game.sio.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            self.board.pop()
            self.board.pop()
            self.popped = True
            await Game.sio.emit("pop", {}, room=sid)