import chess
from chess.engine import Limit, popen_uci
from Game import Game
from const import MIN_RANK, MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME
from time import perf_counter
from ranks import dailyRank, weeklyRank, sessionId

class PVEGame(Game):
    __slots__ = ["bot", "depth"]
    cursor = None
    conn = None
    
    def __init__(self, player: str, rank: int, depth: int, time: int, seed: int|None = None, type: int|None = None) -> None:
        super().__init__([player], rank, time, seed)
        self.bot = None
        self.depth = depth
        self.type = type

    @classmethod
    async def start(cls, sid: str, data: dict[str, str], seed = None, type = None) -> None:
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
            if seed is not None:
                if type == 2:
                    Game.games[sid] = PVEGame(sid, dailyRank, 1, -1, seed, type)
                else:
                    Game.games[sid] = PVEGame(sid, weeklyRank, 1, -1, seed, type)
            else:
                Game.games[sid] = PVEGame(sid, int(data["rank"]), int(data["depth"]), int(data["time"]), seed)
            await Game.games[sid].instantiate_bot()
            await Game.sio.emit("config", {"fen": Game.games[sid].fen}, room=sid)
        else:
            await Game.sio.emit("error", {"cause": "SID already used", "fatal": True}, room=sid)

    async def disconnect(self, sid: str) -> None:
        await self.bot.quit()
        if sid in Game.games:
            del Game.games[sid]
        if sid in Game.sid_to_id:
            del Game.sid_to_id[sid]

    async def instantiate_bot(self) -> None:
        self.bot = (await popen_uci("./stockfish"))[1]
    
    def get_current_user():
        Game.cursor.execute("SELECT username FROM backend_registeredusers WHERE session_id = %s", (sessionId,))
        return Game.cursor.fetchone()[0]
    
    def get_attempts(username):
        Game.cursor.execute("SELECT attempts FROM backend_dailyleaderboard WHERE username = %s AND challenge_date = %s", (username, date.today()))
        result = Game.cursor.fetchone()
        if result is None:
            attempts = 0
        else:
            attempts = Game.cursor.fetchone()[0]
        return attempts

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
            #Player wins
            if self.type == 2:
                #get user information based on the sessionId
                current_username = get_current_user(sessionId)
                attempts = get_attempts(current_username) 
                if attempts == 0:
                    Game.cursor.execute("INSERT INTO backend_dailyleaderboard (username,  moves_count, challenge_date, result, attempts) VALUES (%s, %s, %s, %s)", (current_username, self.current.move_count, date.today(), 'win', attempts+1))
                else:
                        Game.cursor.execute("""
                        UPDATE backend_dailyleaderboard
                        SET moves_count = %s, attempts = attempts + 1, result = 'win'
                        WHERE username = %s AND challenge_date = %s
                    """, (self.current.move_count, current_username, date.today()))
            elif self.type == 3:
                #Insert into weekly leaderboard
                current_username = get_current_user(sessionId)
                start_of_week = date.today() - timedelta(days=date.today().weekday())
                end_of_week = start_of_week + timedelta(days=6)
                #check if the current user has already played the weekly challenge
                Game.cursor.execute("SELECT moves_count, challenge_date FROM backend_weeklyleaderboard WHERE username = %s", (current_username,))
                result = Game.cursor.fetchone()
                if result is None:
                    Game.cursor.execute("INSERT INTO backend_weeklyleaderboard (username,  moves_count, challenge_date, result) VALUES (%s, %s, %s, %s)", (current_username, self.current.move_count, date.today(), 'win'))
                else:
                    #check if the current user has obtained a better result
                    if self.current.move_count < result[0] or ((result[1] >= start_of_week and result[1] <= end_of_week) == False):
                        Game.cursor.execute("""
                        UPDATE backend_weeklyleaderboard
                        SET moves_count = %s, result = 'win'
                        WHERE username = %s AND challenge_date = %s
                    """, (self.current.move_count, current_username, date.today()))
                
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
            #Bot wins
            if self.type == 2:
                #get user information based on the sessionId
                current_username = get_current_user(sessionId)
                attempts = get_attempts(current_username) 
                if attempts == 0:
                    Game.cursor.execute("INSERT INTO backend_dailyleaderboard (username,  moves_count, challenge_date, result, attempts) VALUES (%s, %s, %s, %s)", (current_username, self.current.move_count, date.today(), 'loss', attempts+1))
                else:
                        Game.cursor.execute("""
                        UPDATE backend_dailyleaderboard
                        SET moves_count = %s, attempts = attempts + 1, result = 'loss'
                        WHERE username = %s AND challenge_date = %s
                    """, (self.current.move_count, current_username, date.today()))
            elif self.type == 3:
                #Insert into weekly leaderboard
                current_username = get_current_user(sessionId)
                start_of_week = date.today() - timedelta(days=date.today().weekday())
                end_of_week = start_of_week + timedelta(days=6)
                #check if the current user has already played the weekly challenge
                Game.cursor.execute("SELECT moves_count, challenge_date FROM backend_weeklyleaderboard WHERE username = %s", (current_username,))
                result = Game.cursor.fetchone()
                if result is None:
                    Game.cursor.execute("INSERT INTO backend_weeklyleaderboard (username,  moves_count, challenge_date, result) VALUES (%s, %s, %s, %s)", (current_username, self.current.move_count, date.today(), 'loss'))
                else:
                        Game.cursor.execute("""
                        UPDATE backend_weeklyleaderboard
                        SET moves_count = %s, result = 'loss'
                        WHERE username = %s AND challenge_date = %s
                    """, (self.current.move_count, current_username, date.today()))
                    
                    
                
            await self.disconnect(sid)
            return
        self.popped = False
        end = perf_counter()
        self.current.add_time(end - start)
        await Game.sio.emit("move", {"san": san_bot_move, "time": self.get_times()}, room=sid)

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



