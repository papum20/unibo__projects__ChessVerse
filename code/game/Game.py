from typing import Optional
import chess
import Player
import confighandler
from abc import ABC, abstractmethod
from const import TIME_OPTIONS, DEFAULT_ELO
from const import FIELDS


def expected_score(rating_A, rating_B):
    return 1.0 / (1 + 10 ** ((rating_B - rating_A) / 400))


def update_rating(rating_A, rating_B, risultato):
    expected_a = expected_score(rating_A, rating_B)
    expected_b = expected_score(rating_B, rating_A)
    K = calc_K(rating_A, rating_B)
    new_rating_a = rating_A + K * (risultato - expected_a)
    new_rating_b = rating_B + K * (1 - risultato - expected_b)
    return new_rating_a, new_rating_b


def calc_K(rating_A, rating_B):
    # Assumo che il rating Elo sia compreso tra 0 e 3000
    # Assumo che il valore di K sia compreso tra 10 e 60
    # Uso una formula lineare per interpolare il valore di K
    # K = 60 - 0.0167 * (rating_A + rating_B) / 2
    # Arrotondo il valore di K al numero intero piÃ¹ vicino
    return round(60 - 0.0167 * (rating_A + rating_B) / 2)


class Game(ABC):
    sio = None
    games = {}
    sid_to_id: dict[str, str] = {}
    waiting_list: dict[str, list[list[str]]] = {
        key: [[] for _ in range(6)] for key in TIME_OPTIONS
    }
    conn = None
    __slots__ = ["fen", "board", "players", "turn", "popped"]
    
    def __init__(self, sids: [], rank: int|None, time: int, seed: int | None = None) -> None:
        self.fen = confighandler.gen_start_fen(rank, seed)
        self.board = chess.Board(self.fen)
        self.players = []
        for i, sid in enumerate(sids):
            self.players.append(Player.Player(sid, not bool(i), time))
        self.turn = 0
        self.popped = False

    @property
    def current(self) -> Player:
        return self.players[self.turn]

    @property
    def next(self) -> Player:
        return self.players[1 - self.turn]

    def opponent(self, sid: str) -> Player:
        return self.players[1 - self.players.index(sid)]

    @abstractmethod
    async def disconnect(self, sid: str) -> None:
        pass

    @classmethod
    @abstractmethod
    async def start(cls, sid: str) -> None:
        pass

    @abstractmethod
    async def move(self, sid: str, data: dict[str, str]) -> None:
        pass

    @abstractmethod
    async def pop(self, sid: str) -> None:
        pass

    @classmethod
    async def get_username(cls, sid):
        session = await Game.sio.get_session(sid)
        return session["username"]
    
    @classmethod
    async def get_session_id(cls, sid):
        session = await Game.sio.get_session(sid)
        return session["session_id"]
    
    @classmethod
    async def get_session_field(cls, sid, field):
        session = await Game.sio.get_session(sid)
        return session[field]
    
    @classmethod
    def execute_query(cls, query, params=None):
        with Game.conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                Game.conn.commit()
                return None
    
    @classmethod
    def set_user_field(cls, session_id: str, field: str, new_value: int) -> bool:
        """
		:param session_id: session id field
		:param rank_type: game type, form const.RANKS
		:param new_rank: new_rank
		:return: True if success, False otherwise
		"""

        if field not in FIELDS:
            # print("[err][db] Invalid rank type")
            return 0

        if session_id is None:
            # print("[err][db] Invalid session id")
            return 0

        Game.execute_query(
            f"""
			UPDATE backend_registeredusers 
			SET {field} = %(new_value)s
			WHERE session_id = %(session_id)s
			""",
            {
                'new_value': new_value,
                'session_id': session_id
            }
        )

        print(f"[db] set rank to:{new_value}")
        return True
    
    @classmethod
    def get_user_field(cls, session_id: str, field: str) -> int:
        """
		:param session_id: session id field
		"""

        if session_id is None:
            # print("[err][db] Invalid session id")
            return 0
        field = Game.execute_query(
            f"""
			SELECT {field}
			FROM backend_registeredusers
			WHERE session_id = %s
			""",
            (session_id,)
        )
        return field[0] if field is not None and len(field) > 0 else None


    @classmethod
    async def login(cls, session_id: str, sid: str) -> None:
        print(f"faccio login {session_id, sid}")
        users_info = Game.execute_query("SELECT EloReallyBadChess, Username FROM backend_registeredusers WHERE session_id = %s",(session_id,))
        if len(users_info) > 0:
            user_info = users_info[0]
            await Game.sio.save_session(
                sid,
                {
                    "elo": user_info[0],
                    "session_id": session_id,
                    "username": user_info[1],
                },
            )
        else:
            await Game.sio.save_session(
                sid, {"elo": DEFAULT_ELO, "session_id": session_id, "username": "Guest"}
            )

    async def update_win_database(self, sid: str, outcome: bool | None) -> None:
        current = await Game.sio.get_session(sid)
        opponent = await Game.sio.get_session(self.opponent(sid).sid)
        if current["session_id"] is not None:
            field = "GamesWon" if outcome is not None else "GamesDrawn"
            Game.execute_query(
                f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
                (current["session_id"],)
            )
        if opponent["session_id"] is not None:
            field = "GamesLost" if outcome is not None else "GamesDrawn"
            Game.execute_query(
                f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
                (opponent["session_id"],)
            )
        new_elos = [None, None]
        if current["session_id"] is not None and opponent["session_id"] is not None:
            result = 1 if outcome is True else 0.5 if outcome is None else 0
            new_elos = update_rating(current["elo"], opponent["elo"], result)
            Game.execute_query(
                f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[0]} WHERE session_id = %s",
                (current["session_id"],)
            )
            Game.execute_query(
                f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[1]} WHERE session_id = %s",
                (opponent["session_id"],)
            )
        return new_elos


    async def game_found(self, sid: str, game_id: str):
        if game_id not in self.games:
            await self.sio.emit(
                "error", {"cause": "Game not found", "fatal": True}, room=sid
            )
            return False
        return True

    def get_times(self):
        return [player.remaining_time for player in self.players if player.is_timed]
