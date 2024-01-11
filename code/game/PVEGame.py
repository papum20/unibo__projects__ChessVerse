import chess
from chess.engine import Limit, popen_uci
from Game import Game
from const import (
    MIN_RANK,
    MAX_RANK,
    MIN_DEPTH,
    MAX_DEPTH,
    MIN_TIME,
    MAX_TIME,
    MODE_RANKED_PT_DIFF,
)
from time import perf_counter
from const import GameType
from datetime import datetime, date

def calculate_result(outcome: chess.Outcome):
    if outcome is None or outcome.winner is False:
        return "loss"
    elif outcome.winner:
        return "win"
    else:
        return "draw"


class PVEGame(Game):
    __slots__ = ["bot", "depth", "type"]

    def __init__(
        self,
        player: str,
        rank: int | None,
        depth: int,
        time: int,
        seed: int | None = None,
        type: int | None = None,
    ) -> None:
        super().__init__([player], rank, time, seed)
        self.bot = None
        self.depth = depth
        self.type = type

    @staticmethod
    def get_new_ranked(cur_ranked: int, outcome: chess.Outcome) -> int:
        new_rank = None
        if outcome is None:
            new_rank = cur_ranked + MODE_RANKED_PT_DIFF[2]
        elif outcome.winner is None:
            new_rank = cur_ranked + MODE_RANKED_PT_DIFF[1]
        elif outcome.winner:
            new_rank = cur_ranked + MODE_RANKED_PT_DIFF[0]
        else:
            new_rank = cur_ranked + MODE_RANKED_PT_DIFF[2]
        return min(max(new_rank, 0), 100)

    @classmethod
    async def start(cls, sid: str, data: dict[str, str], seed=None, type=None) -> None:
        if not await PVEGame.validate_data(data, sid):
            return
        if sid not in Game.sid_to_id:
            await PVEGame.initialize_game(sid, data, seed, type)
        else:
            await Game.emit_error("SID already used", sid)

    @classmethod
    async def validate_data(cls, data, sid):
        required_fields = ["rank", "depth", "time"]
        if not all(field in data for field in required_fields):
            await Game.emit_error("Missing fields", sid)
            return False
        for field, (min_val, max_val, display_name) in {
            "rank": (MIN_RANK, MAX_RANK, "rank"),
            "depth": (MIN_DEPTH, MAX_DEPTH, "bot strength"),
            "time": (MIN_TIME, MAX_TIME, "clocktime"),
        }.items():
            if not cls.check_int(data, field, min_val, max_val):
                await Game.emit_error(f"Invalid {display_name}", sid)
                return False

        return True

    @staticmethod
    def check_int(data, key, inf, sup):
        try:
            v = int(data[key])
            return inf <= v <= sup
        except (ValueError, TypeError):
            return False

    @classmethod
    async def initialize_game(cls, sid, data, seed, type):
        Game.sid_to_id[sid] = sid  # solo in PVE;
        rank = -1
        if seed is not None:
            Game.games[sid] = PVEGame(sid, None, 1, -1, seed, type)
        else:
            await cls.setup_game_without_seed(sid, data, type)
        await Game.games[sid].instantiate_bot()
        await Game.sio.emit(
            "config", {"fen": Game.games[sid].fen, "rank": rank}, room=sid
        )

    @classmethod
    async def setup_game_without_seed(cls, sid, data, type):
        if type == GameType.RANKED:
            session_id = await Game.get_session_id(sid)
            rank = Game.get_user_field(session_id, "score_ranked")
            if rank is not None:
                rank = rank[0]
            else:
                rank = 0
            print(f"score_ranked = {rank}")
            Game.games[sid] = PVEGame(sid, rank, 1, -1, None, type)
        else:
            Game.games[sid] = PVEGame(
                sid,
                int(data["rank"]),
                int(data["depth"]),
                int(data["time"]),
                None,
                type,
            )

    @classmethod
    def current_week_and_year(cls):
        # Get the current date
        current_date = datetime.now()

        # Extract the current week number and year
        week_number = current_date.isocalendar()[1]
        year = current_date.year

        # Format as WWYYYY
        return f"{week_number:02d}{year}"

    @classmethod
    def current_day_month_year(cls):
        # Get the current date
        current_date = datetime.now()

        # Extract the day, month, and year
        day = current_date.day
        month = current_date.month
        year = current_date.year

        # Format as DDMMYYYY
        return f"{day:02d}{month:02d}{year}"

    async def disconnect_daily(self, sid: str, outcome: chess.Outcome) -> None:
        # get user information based on the sessionId
        current_username = await Game.get_username(sid)
        attempts = PVEGame.get_attempts(current_username)
        date = PVEGame.current_day_month_year()
        if attempts == 0:
            Game.execute_query(
                "INSERT INTO backend_dailyleaderboard (username, moves_count, challenge_date, result, attempts) VALUES (%s, %s, %s, %s, %s)",
                (
                    current_username,
                    self.current.move_count,
                    date,
                    calculate_result(outcome),
                    attempts + 1,
                ),
            )
        else:
            Game.execute_query(
                """
                UPDATE backend_dailyleaderboard
                SET moves_count = %s, attempts = attempts + 1, result = %s
                WHERE username = %s AND challenge_date = %s
                """,
                (
                    self.current.move_count,
                    calculate_result(outcome),
                    current_username,
                    date,
                ),
            )

    async def disconnect_weekly(self, sid: str, outcome: chess.Outcome) -> None:
        # Insert into weekly leaderboard
        current_username = await Game.get_username(sid)
        weekno = PVEGame.current_week_and_year()
        # check if the current user has already played the weekly challenge
        result = Game.execute_query(
            "SELECT moves_count, challenge_date FROM backend_weeklyleaderboard WHERE username = %s AND challenge_date = %s",
            (current_username, weekno),
        )
        if result is None or len(result) == 0:
            Game.execute_query(
                "INSERT INTO backend_weeklyleaderboard (username, moves_count, challenge_date, result) VALUES (%s, %s, %s, %s)",
                (
                    current_username,
                    self.current.move_count,
                    weekno,
                    calculate_result(outcome),
                ),
            )
        else:
            Game.execute_query(
                """
                UPDATE backend_weeklyleaderboard
                SET moves_count = %s, result = %s
                WHERE username = %s AND challenge_date = %s
                """,
                (self.current.move_count, calculate_result(outcome), current_username, weekno),
            )

    async def disconnect_ranked(self, sid: str, outcome: chess.Outcome):
        session_id = await Game.get_session_id(sid)
        if session_id is not None:
            score_ranked = PVEGame.get_user_field(session_id, "score_ranked")
            if score_ranked is not None:
                score_ranked = score_ranked[0]
            else:
                score_ranked = 0
            new_ranked = PVEGame.get_new_ranked(score_ranked, outcome)
            PVEGame.set_user_field(session_id, "score_ranked", new_ranked)

    async def disconnect(self, sid: str, outcome: chess.Outcome = None) -> None:
        if not outcome:
            outcome = self.board.outcome()
        print(f"mi sto disconnetendo {sid}")
        if self.type == GameType.DAILY:
            await self.disconnect_daily(sid, outcome)
        elif self.type == GameType.WEEKLY:
            await self.disconnect_weekly(sid, outcome)
        elif self.type == GameType.RANKED:
            await self.disconnect_ranked(sid, outcome)
        await self.bot.quit()
        if sid in Game.games:
            del Game.games[sid]
        if sid in Game.sid_to_id:
            del Game.sid_to_id[sid]

    async def instantiate_bot(self) -> None:
        self.bot = (await popen_uci("./stockfish"))[1]

    @classmethod
    def get_attempts(cls, username: str):
        result = Game.execute_query(
            "SELECT attempts FROM backend_dailyleaderboard WHERE username = %s AND challenge_date = %s",
            (username, PVEGame.current_day_month_year()),
        )
        print(result, username, date.today())
        return 0 if result is None or len(result) <= 0 else result[0][0]

    async def move(self, sid: str, data: dict[str, str]) -> None:
        if "san" not in data:
            await Game.emit_error("Missing fields", sid, None)
            return
        if data["san"] is None:
            await Game.emit_error("Encountered None value", sid, None)
            return
        if not self.current.has_time(True):
            return
        try:
            uci_move = self.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await Game.emit_error("Invalid move", sid, None)
            return
        self.current.move_count += 1
        self.board.push_uci(uci_move)
        outcome = self.board.outcome()
        if outcome is not None:
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
        await Game.sio.emit(
            "move", {"san": san_bot_move, "time": self.get_times()}, room=sid
        )

    async def pop(self, sid: str) -> None:
        if self.popped:
            await Game.emit_error("You have already popped", sid, None)
        elif self.board.fullmove_number == 1:
            await Game.emit_error("No moves to undo", sid, None)
        else:
            self.board.pop()
            self.board.pop()
            self.popped = True
            await Game.sio.emit("pop", {"time": self.get_times()}, room=sid)
