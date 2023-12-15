from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import chess
from chess import Outcome
from mysql.connector import MySQLConnection
from socketio import AsyncServer

from const import DEFAULT_ELO, TIME_OPTIONS
from ranks import sessionId

import confighandler
from database.users import DatabaseHandlerUsers
from Player import Player


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

	sio: Optional[AsyncServer] = None
	games = {}
	sid_to_id: dict[str, str] = {}
	waiting_list: dict[str, list[list[str]]] = {key: [[] for _ in range(6)] for key in TIME_OPTIONS}
	cursor = None
	conn: Optional[MySQLConnection] = None
	__slots__ = ["fen", "board", "players", "turn", "popped"]

	databaseHandler_users: Optional[DatabaseHandlerUsers] =  DatabaseHandlerUsers()


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

	def _deletePlayers(self, sid):
		"""
		delete players (on disconnect).
		"""
		
		for player in self.players:
			if player.sid in Game.sid_to_id:
				del Game.sid_to_id[player.sid]

		#if self.opponent(sid).sid in Game.sid_to_id:
		#	del Game.sid_to_id[self.opponent(sid).sid]

		del Game.games[Game.sid_to_id[sid]]
		del Game.sid_to_id[sid]
		if len(self.players) > 1 and self.opponent(sid).sid in Game.sid_to_id:
			del Game.sid_to_id[self.opponent(sid).sid]


	async def update_win_database(self, sid: str, outcome: bool|None) -> None:
		current = await Game.sio.get_session(sid)
		opponent = await Game.sio.get_session(self.opponent(sid).sid)
		if current["session_id"] is not None:
			field = "GamesWon" if outcome is not None else "GamesDrawn"
			Game.cursor.execute(f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
									(current["session_id"],))
		if opponent["session_id"] is not None:
			field = "GamesLost" if outcome is not None else "GamesLost"
			Game.cursor.execute(f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
								(opponent["session_id"],))
		new_elos = [None, None]
		if current["session_id"] is not None and opponent["session_id"] is not None:
			result = 1 if outcome is True else 0.5 if outcome is None else 0
			new_elos = update_rating(current["elo"], opponent["elo"], result)
			Game.cursor.execute(
				f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[0]} WHERE session_id = %s",
				(current["session_id"],))
			Game.cursor.execute(
				f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[1]} WHERE session_id = %s",
				(opponent["session_id"],))
		Game.conn.commit()
		return new_elos


	def _deletePlayers(self, sid):
		"""
		delete players (on disconnect).
		"""

		for player in self.players:
			if player.sid in Game.sid_to_id:
				del Game.sid_to_id[player.sid]

		del Game.games[Game.sid_to_id[sid]]
		if len(self.players) > 1 and self.opponent(sid).sid in Game.sid_to_id:
			del Game.sid_to_id[self.opponent(sid).sid]


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
	async def login(cls, session_id: str, sid: str) -> None:

		Game.cursor.execute("SELECT EloReallyBadChess FROM backend_registeredusers WHERE session_id = %s", (session_id,))
		user_info = Game.cursor.fetchone()
		if user_info is not None:
			print(f"logged user:{user_info}")
			#prendo le informazioni dal database e le salvo in session
			await Game.sio.save_session(sid, {'elo': user_info[0], 'session_id': session_id, 'username': user_info[1]})
		else:
			await Game.sio.save_session(sid, {'elo': 1000, 'session_id': None})


	async def database_update_win(self, sid: str, outcome: bool|None, rank:str="EloReallyBadChess", diffs:Tuple[int,int,int]=(30,0,-30)):

		"""
		Updates the database with the result of the game.
		:param sid: the session id of the player
		:param rank: the name of the rank field in the given mode
		:param diffs: a tuple containing, in order, for the current player, the points to sum in case of win, draw and loss
		:return: None
		note: default values is provided for compatibility with previous version
		"""
		
		# update current player
		session = await Game.sio.get_session(sid)
		current = await Game.sio.get_session(sid)
		opponent = await Game.sio.get_session(self.opponent(sid).sid)
		
		if session["session_id"] is not None:
			field = "GamesWon" if outcome is not None else "GamesDrawn"
			Game.cursor.execute(f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
								(session["session_id"],))
			Game.databaseHandler_users.set_user_rank(session["session_id"], rank, diffs[0])

		# update opponent
		session = await Game.sio.get_session(self.opponent(sid).sid)
		if session["session_id"] is not None:
			field = "GamesDrawn" if outcome is not None else "GamesLost"
			Game.cursor.execute(f"UPDATE backend_registeredusers SET {field} = {field} + 1 WHERE session_id = %s",
								(session["session_id"],))
			Game.databaseHandler_users.set_user_rank(session["session_id"], rank, diffs[1])

		# ??
		new_elos = [None, None]
		if current["session_id"] is not None and opponent["session_id"] is not None:
			result = 1 if outcome is True else 0.5 if outcome is None else 0
			new_elos = update_rating(current["elo"], opponent["elo"], result)
			Game.cursor.execute(
				f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[0]} WHERE session_id = %s",
				(current["session_id"],))
			Game.cursor.execute(
				f"UPDATE backend_registeredusers SET EloReallyBadChess = {new_elos[1]} WHERE session_id = %s",
				(opponent["session_id"],))

		Game.conn.commit()
		return new_elos


	async def game_found(self, sid: str, game_id: str):
		if game_id not in self.games:
			await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
			return False
		return True

	def get_times(self):
		return [player.remaining_time for player in self.players if player.is_timed]



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
	

	# setters

	def set_cursor(self, cursor):
		Game.cursor = cursor
		self.databaseHandler_users.cursor = cursor

	def set_connector(self, connector):
		Game.conn = connector
		self.databaseHandler_users.connector = connector
