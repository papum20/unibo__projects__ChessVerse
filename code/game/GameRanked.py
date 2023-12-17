import chess
from chess.engine import Limit
from time import perf_counter
from typing import List, Optional, Tuple

from const import MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME
from const.game_options import MODE_RANKED_K, MODE_RANKED_PT_DIFF

from Game import Game
from PVEGame import PVEGame

from utils.TypeChecker import TypeChecker


class GameRanked(PVEGame):
	__slots__ = ["bot", "depth"]



	def __init__(self, sid: str, rank: int, depth: int, time: int) -> None:
		super().__init__(sid, rank, depth, time)
		self.bot = None
		self.depth = depth


	@classmethod
	async def start(cls, sid: str, data: dict[str, str]) -> None:
			
		if "depth" not in data or "time" not in data:
			await Game.sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
			return
		if not TypeChecker.isIntInRange(data["depth"], MIN_DEPTH, MAX_DEPTH):
			await Game.sio.emit("error", {"cause": "Invalid bot strength", "fatal": True}, room=sid)
			return
		if not TypeChecker.isIntInRange(data["time"], MIN_TIME, MAX_TIME):
			await Game.sio.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
			return

		if sid in Game.sid_to_id:
			await Game.sio.emit("error", {"cause": "SID already used", "fatal": True}, room=sid)

		# finally create game
		else:
			session = await Game.get_session_from_sid(sid)
			rank = Game.databaseHandler_users.get_user_rank(session["session_id"], "score_ranked")

			Game.sid_to_id[sid] = sid # solo in PVE; ?
			Game.games[sid] = GameRanked(sid, rank, int(data["depth"]), int(data["time"]))
		
			await Game.games[sid].instantiate_bot()
			#print(f"fen e sid: {Game.games[sid].fen}, {sid}")
			await Game.sio.emit("config",
				{
					"fen": Game.games[sid].fen,
					"rank": rank,
				},
				room=sid
			)


	async def disconnect(self, sid: str) -> None:
		
		session = await Game.get_session_from_sid(sid)
		#print(session)
		await self.database_update_win(session["session_id"], self.board.outcome(), rank="score_ranked", get_new_elos=GameRanked.get_new_elos)
		rank_current = Game.databaseHandler_users.get_user_rank(session["session_id"], "score_ranked")

		await Game.sio.emit("end", 
			{
				"winner": self.board.outcome().winner if self.board.outcome() is not None else "draw",
				"new_rank": rank_current,
				
			}, room=sid)

		await self.bot.quit()
		
		[await Game.sio.disconnect(sid=player.sid) for player in self.players]
		
		# check what ?
		if sid not in Game.sid_to_id:
			return
		
		self._deletePlayers(sid)


	async def move_bot(self, sid: str) -> str:
		"""
		performs a move for the bot.
		:return: the move in SAN format
		"""

		bot_move = (await self.bot.play(self.board, Limit(depth=self.depth))).move
		bot_move_san = self.board.san(bot_move)
		self.board.push_uci(bot_move.uci())

		self.popped = False

		return bot_move_san


	async def move(self, sid: str, data: dict[str, str]) -> None:
		
		# input checks
		if "san" not in data:
			await Game.sio.emit("error", {"cause": "Missing fields"}, room=sid)
			return
		if data["san"] is None:
			await Game.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
			return
		if not self.current.has_time(True):
			return

		try:
			move_uci = self.board.parse_san(data["san"]).uci()
		except (chess.InvalidMoveError, chess.IllegalMoveError):
			await Game.sio.emit("error", {"cause": "Invalid move"}, room=sid)
			return
			
		# add (push) move to board
		self.board.push_uci(move_uci)
		if await self.handle_win(sid):
			return
		
		# bot move
		bot_time_start = perf_counter()	# count time, to reassign it later
		
		bot_move_san = await self.move_bot(sid)
		await Game.sio.emit("move", {
				"san": bot_move_san, "time": self.get_times()
			}, room=sid)

		if await self.handle_win(sid):
			return
		
		self.current.add_time( int(perf_counter() - bot_time_start) )	# add time back
		

	# const

	@staticmethod
	def get_botLevel_from_rank(rank:int):
		"""
		:param rank: user rank in ranked mode.
		:return the formula just gives a bot level for each K rank points.
		"""
		bot_level = int(rank / MODE_RANKED_K)
		return bot_level if bot_level <= MAX_RANK else MAX_RANK
		
	@staticmethod
	def get_new_elos(elo1:int, elo2:int, outcome:Optional[bool]) -> Tuple[int,int]:
		if outcome is None:
			return elo1 + MODE_RANKED_PT_DIFF[1], elo2 + MODE_RANKED_PT_DIFF[1]
		elif outcome:
			return elo1 + MODE_RANKED_PT_DIFF[0], elo2 + MODE_RANKED_PT_DIFF[2]
		else:
			return elo1 + MODE_RANKED_PT_DIFF[2], elo2 + MODE_RANKED_PT_DIFF[0]

