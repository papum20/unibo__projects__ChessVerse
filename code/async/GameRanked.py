from const import MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME

from Game import Game
from PVEGame import PVEGame

from database.users import get_user_rank
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
			rank = get_user_rank(sid, "ranked")

			Game.sid_to_id[sid] = sid # solo in PVE; ?
			Game.games[sid] = GameRanked(sid, rank, int(data["depth"]), int(data["time"]))
			
			await Game.games[sid].instantiate_bot()
			await Game.sio.emit("config",
					   {
						   "fen": Game.games[sid].fen,
						   "rank": rank,
						},
					   room=sid)
