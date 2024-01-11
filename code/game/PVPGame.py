from Game import Game
from time import perf_counter
import random
from const import TIME_OPTIONS, MIN_RANK, MAX_RANK
import chess


class PVPGame(Game):
    waiting_list: dict[str, list[list[str]]] = {
        key: [[] for _ in range(6)] for key in TIME_OPTIONS
    }

    @classmethod
    async def start(cls, sid: str, data: dict[str, str], seed=None, type=None) -> None:
        if not await cls.validate_data(sid, data):
            return
        rank = cls.calculate_rank(data["rank"])
        time = data["time"]
        index = cls.calculate_index(rank)

        if sid in Game.sid_to_id:
            await Game.emit_error("Started Matching", sid)
            return

        await cls.process_matching(sid, time, rank, index)

    @classmethod
    async def validate_data(cls, sid: str, data: dict[str, str]) -> bool:
        if "rank" not in data or "time" not in data:
            await Game.emit_error("Missing fields", sid)
            return False

        if not cls.check_int(data, "rank", MIN_RANK, MAX_RANK):
            await Game.emit_error("Invalid rank", sid)
            return False

        if not cls.check_options(data, "time", TIME_OPTIONS):
            await Game.emit_error("Invalid clocktime", sid)
            return False

        return True

    @staticmethod
    def check_int(data, key, inf, sup):
        try:
            v = int(data[key])
            return inf <= v <= sup
        except (ValueError, TypeError):
            return False

    @staticmethod
    def check_options(data, key, options):
        try:
            value = int(data[key])
            return value in options
        except (ValueError, TypeError, KeyError):
            return False

    @staticmethod
    def calculate_rank(rank):
        return round(max(min(int(rank), 100), 0) / 10) * 10

    @staticmethod
    def calculate_index(rank):
        return (10 - (rank // 10)) % 6 if rank // 10 > 5 else (rank // 10) % 6

    @classmethod
    async def process_matching(cls, sid, time, rank, index):
        if (
            len(cls.waiting_list[time][index]) > 0
            and cls.waiting_list[time][index][0]["rank"] == 100 - rank
        ):
            #match trovato
            await cls.setup_game_with_existing_player(sid, time, rank, index)
        else:
            await cls.add_player_to_waiting_list(sid, time, rank, index)

    @classmethod
    async def setup_game_with_existing_player(cls, sid, time, rank, index):
        session = await Game.sio.get_session(sid)
        found_guest = None
        for waiting in cls.waiting_list[time][index]:
            if abs(waiting["elo"] - session["elo"]) < 100:
                found_guest = waiting
                break
        if found_guest is None:
            await cls.add_player_to_waiting_list(sid, time, rank, index)
            return
        first = random.randint(0, 1)
        players = [sid, found_guest["sid"]] if first else [found_guest["sid"], sid]
        game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
        cls.games[game_id] = cls(players, rank if first else 100 - rank, time)
        cls.waiting_list[time][index].remove(found_guest)
        cls.sid_to_id[players[0]] = game_id
        cls.sid_to_id[players[1]] = game_id
        current = await Game.sio.get_session(players[0])
        opponent = await Game.sio.get_session(players[1])
        usernames = [obj["username"] for obj in [current, opponent]]
        elos = [obj["elo"] for obj in [current, opponent]]
        await Game.sio.emit(
            "config",
            {
                "fen": cls.games[game_id].fen,
                "id": game_id,
                "color": "white",
                "elo": elos,
                "username": usernames[1],
            },
            room=players[0],
        )
        await Game.sio.emit(
            "config",
            {
                "fen": cls.games[game_id].fen,
                "id": game_id,
                "color": "black",
                "elo": elos,
                "username": usernames[0],
            },
            room=players[1],
        )

    @classmethod
    async def add_player_to_waiting_list(cls, sid, time, rank, index):
        session = await Game.sio.get_session(sid)
        cls.waiting_list[time][index].append(
            {"sid": sid, "rank": rank, "elo": session["elo"]}
        )
        # serve per eliminarlo dalla entry
        Game.sid_to_id[sid] = {"time": time, "index": index}

    def __init__(self, players: [str], rank: [], timer):
        super().__init__(players, rank, timer)
        self.timer = 1
        self.isTimed = timer != -1

    def swap(self):
        self.popped = False
        self.turn = (self.turn + 1) % 2

    def is_player_turn(self, sid):
        return self.current.sid == sid

    async def disconnect(self, sid: str, send_to_disconnected: bool = True, outcome: chess.Outcome = None) -> None:
        await self.update_win_database(self.opponent(sid).sid, False if outcome is None else outcome.winner)
        if send_to_disconnected:
            await Game.sio.emit("end", {"winner": False if outcome is None else outcome.winner}, room=sid)
        await Game.sio.emit("end", {"winner": True if outcome is None else outcome.winner}, room=self.opponent(sid).sid)
        # await Game.sio.disconnect(sid=self.opponent(sid).sid)
        if sid not in Game.sid_to_id:
            return
        elif Game.sid_to_id[sid] in Game.games:
            if self.opponent(sid).sid in Game.sid_to_id:
                del Game.sid_to_id[self.opponent(sid).sid]
            del Game.games[Game.sid_to_id[sid]]
            del Game.sid_to_id[sid]

    async def pop(self, sid: str) -> None:
        if sid not in Game.sid_to_id:
            await Game.emit_error("Missing id", sid)
            return
        if not await self.game_found(sid, Game.sid_to_id[sid]):
            return
        if not self.is_player_turn(sid):
            await Game.emit_error("It's not your turn", sid, None)
            return
        if self.popped:
            await Game.emit_error("You have already popped", sid, None)
            return
        if self.board.fullmove_number == 1:
            await Game.emit_error("No moves to undo", sid, None)
        else:
            self.board.pop()
            self.board.pop()
            await Game.sio.emit(
                "pop",
                {"time": self.get_times()},
                room=[player.sid for player in self.players],
            )
            self.popped = True

    async def move(self, sid: str, data: dict[str, str]) -> None:
        if sid not in Game.sid_to_id:
            await Game.emit_error("No games found", sid)
            return
        if "san" not in data:
            await Game.emit_error("Missing fields", sid)
            return
        if data["san"] is None:
            await Game.emit_error("Encountered None value", sid, None)
            return
        if not self.is_player_turn(sid):
            await Game.emit_error("It's not your turn", sid, None)
            return
        if not self.current.has_time():
            return
        try:
            uci_move = self.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await Game.emit_error("Invalid move", sid, None)
            return
        if chess.Move.from_uci(uci_move) not in self.board.legal_moves:
            await Game.emit_error("Invalid move", sid, None)
            return
        uci_move = self.board.parse_uci(self.board.parse_san(data["san"]).uci())
        san_move = self.board.san(uci_move)
        self.board.push_uci(uci_move.uci())
        outcome = self.board.outcome()
        if outcome is not None:
            await Game.sio.emit(
                "move",
                {"san": san_move, "time": self.get_times()},
                room=self.current.sid,
            )
            await Game.sio.emit(
                "move", {"san": san_move, "time": self.get_times()}, room=self.next.sid
            )
            elos = await self.update_win_database(sid, outcome.winner)
            await Game.sio.emit(
                "end",
                {
                    "winner": True if outcome.winner is not None else outcome.winner,
                    "elo": elos[self.turn],
                },
                room=self.current.sid,
            )
            await Game.sio.emit(
                "end",
                {
                    "winner": False if outcome.winner is not None else outcome.winner,
                    "elo": elos[1 - self.turn],
                },
                room=self.next.sid,
            )
            await self.disconnect(self.next.sid)
            return
        self.popped = False
        await Game.sio.emit("ack", {"time": self.get_times()}, room=self.current.sid)
        self.swap()
        self.current.latest_timestamp = perf_counter()
        await Game.sio.emit(
            "move", {"san": san_move, "time": self.get_times()}, room=self.current.sid
        )
