from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import chess
from chess import Outcome
from mysql.connector import MySQLConnection
from socketio import AsyncServer

from const import TIME_OPTIONS

import confighandler
from database.users import set_user_rank
from Player import Player


class Game(ABC):
	sio: Optional[AsyncServer] = None
	games = {}
	sid_to_id: dict[str, str] = {}
	waiting_list: dict[str, list[list[str]]] = {key: [[] for _ in range(6)] for key in TIME_OPTIONS}
	cursor = None
	conn: Optional[MySQLConnection] = None
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
		"""
		Tipically called on disconnect;
		tipically removes some saved data,
		and updates db.
		"""
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

	async def database_update_win(self, sid: str, rank:str="EloReallyBadChess", diffs:Tuple[int,int]=(30,-30)) -> None:
		
		# update current player
		session = await Game.sio.get_session(sid)
		if session["session_id"] is not None:
			Game.cursor.execute("UPDATE backend_registeredusers SET GamesWon = GamesWon + 1 WHERE session_id = %s",
								(session["session_id"],))
			set_user_rank(session["session_id"], rank, diffs[0])

		# update opponent
		session = await Game.sio.get_session(self.opponent(sid).sid)
		if session["session_id"] is not None:
			Game.cursor.execute("UPDATE backend_registeredusers SET GamesLost = GamesLost + 1 WHERE session_id = %s",
								(session["session_id"],))
			set_user_rank(session["session_id"], rank, diffs[1])

		Game.conn.commit()

	async def game_found(self, sid: str, game_id: str):
		if game_id not in self.games:
			await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
			return False
		return True

	def get_times(self):
		return [player.remaining_time for player in self.players]



	# standard responses
	
	@staticmethod
	async def emit_win(sid:str, outcome:Outcome) -> None:
		if outcome is not None:
			await Game.sio.emit("end", {
					"winner": outcome.winner
				}, room=sid)
	
	
	
	# standard handlers for events

	async def handle_win(self, sid:str) -> bool:
		"""
		Checks if the game has ended and if so emits the win event.
		:return: True if the game has ended, False otherwise
		"""
		outcome = self.board.outcome()
		if outcome is not None:
			await Game.emit_win(sid, outcome)
			await self.disconnect(sid)
			return True
		return False