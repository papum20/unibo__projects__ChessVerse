import math
from typing import Optional, Tuple
import chess
from chess.engine import Limit, popen_uci
from Game import Game
from const import MIN_RANK, MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME, MODE_RANKED_PT_DIFF
from time import perf_counter
from const import GameType
from datetime import date, timedelta


class PVEGame(Game):
    __slots__ = ["bot", "depth", "type"]

    def __init__(
        self,
        player: str,
        rank: int,
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
    def get_new_ranked(cur_ranked:int, outcome:Optional[bool]) -> Tuple[int,int]:
        if outcome is None:
            return cur_ranked + MODE_RANKED_PT_DIFF[1]
        elif outcome:
            return cur_ranked + MODE_RANKED_PT_DIFF[0]
        else:
            return cur_ranked + MODE_RANKED_PT_DIFF[2]

    @classmethod
    async def start(cls, sid: str, data: dict[str, str], seed=None, type=None) -> None:
        def check_int(key, inf, sup):
            try:
                v = int(data[key])
                return inf <= v <= sup
            except (ValueError, TypeError):
                return False

        if "rank" not in data or "depth" not in data or "time" not in data:
            await Game.sio.emit(
                "error", {"cause": "Missing fields", "fatal": True}, room=sid
            )
            return
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await Game.sio.emit(
                "error", {"cause": "Invalid rank", "fatal": True}, room=sid
            )
            return
        if not check_int("depth", MIN_DEPTH, MAX_DEPTH):
            await Game.sio.emit(
                "error", {"cause": "Invalid bot strength", "fatal": True}, room=sid
            )
            return
        if not check_int("time", MIN_TIME, MAX_TIME):
            await Game.sio.emit(
                "error", {"cause": "Invalid clocktime", "fatal": True}, room=sid
            )
            return
        if sid not in Game.sid_to_id:
            Game.sid_to_id[sid] = sid  # solo in PVE;
            rank = -1
            if seed is not None:
                if type == GameType.DAILY:
                    Game.games[sid] = PVEGame(sid, None, 1, -1, seed, type)
                elif type == GameType.WEEKLY:
                    Game.games[sid] = PVEGame(sid, None, 1, -1, seed, type)
            else: # 1v1, freeplay, ranked
                if type == GameType.RANKED:
                    session_id = await Game.get_session_id(sid)
                    rank = Game.get_user_field(session_id, "score_ranked")
                    if rank is not None: 
                        rank = rank[0]
                    else:
                        rank = 0
                    print(f"score_ranked = {rank}")
                    Game.games[sid] = PVEGame(sid, rank, 1, -1, None, type)
                else :
                    Game.games[sid] = PVEGame(
                        sid, int(data["rank"]), int(data["depth"]), int(data["time"]), seed
                    )
            await Game.games[sid].instantiate_bot()
            await Game.sio.emit("config", {"fen": Game.games[sid].fen, "rank": rank}, room=sid)
        else:
            await Game.sio.emit(
                "error", {"cause": "SID already used", "fatal": True}, room=sid
            )

    async def disconnect_daily(self, sid: str, outcome: chess.Outcome) -> None:
        # get user information based on the sessionId
        current_username = await Game.get_username(sid)
        attempts = PVEGame.get_attempts(current_username)
        print(attempts)
        if attempts == 0:
            Game.execute_query(
                "INSERT INTO backend_dailyleaderboard (username, moves_count, challenge_date, result, attempts) VALUES (%s, %s, %s, %s, %s)",
                (
                    current_username,
                    self.current.move_count,
                    date.today(),
                    "loss" if (outcome is None or not outcome.winner) else "win" if outcome.winner else "draw",
                    attempts+1,
                )
            )
        else:
            Game.execute_query(
                """
                UPDATE backend_dailyleaderboard
                SET moves_count = %s, attempts = attempts + 1, result = %s
                WHERE username = %s AND challenge_date = %s
                """,
                (self.current.move_count, "loss" if (outcome is None or not outcome.winner) else "win" if outcome.winner else "draw", current_username, date.today(),)
            )

    async def disconnect_weekly(self, sid: str, outcome: chess.Outcome) -> None:
        # Insert into weekly leaderboard
        current_username = await Game.get_username(sid)
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        end_of_week = start_of_week + timedelta(days=6)
        # check if the current user has already played the weekly challenge
        result = Game.execute_query(
            "SELECT moves_count, challenge_date FROM backend_weeklyleaderboard WHERE username = %s",
            (current_username,)
        )
        if result is None or len(result) == 0:
            Game.execute_query(
                "INSERT INTO backend_weeklyleaderboard (username, moves_count, challenge_date, result) VALUES (%s, %s, %s, %s)",
                (
                    current_username,
                    self.current.move_count,
                    date.today(),
                    "loss" if (outcome is None or not outcome.winner) else "win" if outcome.winner else "draw",
                ),
            )
        else:
            Game.execute_query(
                """
                UPDATE backend_weeklyleaderboard
                SET moves_count = %s, result = %s
                WHERE username = %s AND challenge_date = %s
                """,
                (self.current.move_count, "loss" if (outcome is None or not outcome.winner) else "win" if outcome.winner else "draw", current_username, date.today()),
            )
    
    async def disconnect_ranked(self, sid: str, outcome: chess.Outcome):
        session_id = await Game.get_session_id(sid)
        print(session_id)
        if session_id is not None:
            score_ranked = PVEGame.get_user_field(session_id, "score_ranked")
            if score_ranked is not None:
                score_ranked = score_ranked[0]
            else:
                score_ranked = 0
            new_ranked = PVEGame.get_new_ranked(score_ranked, outcome)
            print(f"new_ranked = {new_ranked}")
            PVEGame.set_user_field(session_id, "score_ranked", new_ranked)


    async def disconnect(self, sid: str) -> None:
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
        result = Game.execute_query("SELECT attempts FROM backend_dailyleaderboard WHERE username = %s AND challenge_date = %s", (username, date.today()),)
        print(result, username, date.today())
        return 0 if result is None or len(result) <= 0 else result[0][0]

    async def move(self, sid: str, data: dict[str, str]) -> None:
        if "san" not in data:
            await Game.sio.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if data["san"] is None:
            await Game.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
            return
        if not self.current.has_time(True):
            return
        try:
            uci_move = self.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await Game.sio.emit("error", {"cause": "Invalid move"}, room=sid)
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
            await Game.sio.emit("error", {"cause": "You have already popped"}, room=sid)
        elif self.board.fullmove_number == 1:
            await Game.sio.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            self.board.pop()
            self.board.pop()
            self.popped = True
            await Game.sio.emit("pop", {"time": self.get_times()}, room=sid)
