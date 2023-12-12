from typing import List
import chess
import Player
import confighandler
from abc import ABC, abstractmethod
from const import TIME_OPTIONS


class Game(ABC):
	sio = None
	games = {}
	sid_to_id: dict[str, str] = {}
	waiting_list: dict[str, list[list[str]]] = {key: [[] for _ in range(6)] for key in TIME_OPTIONS}
	cursor = None
	conn = None
	__slots__ = ["fen", "board", "players", "turn", "popped"]

	def __init__(self, sids:List, rank: int, time: int, fen:str|None=None) -> None:
		"""
		Initialize a new Game instance.

		Args:
			sids (list): A list of session IDs for the players.
			rank (int): The rank of the game.
			time (int): The time limit for the game.
			fen (str, optional): The initial board setup in Forsyth-Edwards Notation. 
								 If not provided, a starting position will be generated based on the rank.

		Returns:
			None
		"""
		self.fen = fen if fen else confighandler.gen_start_fen(rank)	# generate if not given
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
	async def login(cls, sid: str) -> None:
		session_id = "abc"
		Game.cursor.execute("SELECT EloReallyBadChess FROM backend_registeredusers WHERE session_id = %s", (session_id,))
		user_info = Game.cursor.fetchone()
		if user_info is not None:
			print(f"logged user:{user_info}")
			#prendo le informazioni dal database e le salvo in session
			await Game.sio.save_session(sid, {'elo': user_info[0], 'session_id': session_id})
		else:
			await Game.sio.save_session(sid, {'elo': 1000, 'session_id': None})

	async def update_win_database(self, sid: str) -> None:
		session = await Game.sio.get_session(sid)
		if session["session_id"] is not None:
			Game.cursor.execute("UPDATE backend_registeredusers SET GamesWon = GamesWon + 1 WHERE session_id = %s",
								(session["session_id"],))
			Game.cursor.execute(
				"UPDATE backend_registeredusers SET EloReallyBadChess = EloReallyBadChess  + 30 WHERE session_id = %s",
				(session["session_id"],))
		session = await Game.sio.get_session(self.opponent(sid).sid)
		if session["session_id"] is not None:
			Game.cursor.execute("UPDATE backend_registeredusers SET GamesLost = GamesLost + 1 WHERE session_id = %s",
								(session["session_id"],))
			Game.cursor.execute(
				"UPDATE backend_registeredusers SET EloReallyBadChess = EloReallyBadChess  - 30 WHERE session_id = %s",
				(session["session_id"],))
		Game.conn.commit()

	async def game_found(self, sid: str, game_id: str):
		if game_id not in self.games:
			await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
			return False
		return True

	def get_times(self):
		return [player.remaining_time for player in self.players]