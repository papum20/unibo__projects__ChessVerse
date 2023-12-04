from Game import Game
import json
import random
from const import TIME_OPTIONS, MIN_RANK, MAX_RANK
import chess


class PVPGame(Game):
	waiting_list: dict[str, list[list[str]]] = {key: [[] for _ in range(6)] for key in TIME_OPTIONS}

	def __init__(self, players: [str], rank: [], timer):
		super().__init__(players, rank, timer)
		self.timer = 1
		self.isTimed = timer != -1

	def swap(self):
		self.popped = False
		self.turn = (self.turn + 1) % 2

	def is_player_turn(self, sid):
		return self.current.sid == sid

	async def disconnect(self, sid: str) -> None:
		await Game.sio.emit("end", {"winner": True}, room=self.opponent(sid).sid)
		await Game.sio.emit("disconnected", room=self.opponent(sid).sid)
		if self.opponent(sid).sid in Game.sid_to_id:
			del Game.sid_to_id[self.opponent(sid).sid]

	async def pop(self, sid: str) -> None:
		if sid not in Game.sid_to_id:
			await self.sio.emit("error", {"cause": "Missing id", "fatal": True}, room=sid)
		if not await self.game_found(sid, Game.sid_to_id[sid]):
			return
		if not self.is_player_turn(sid):
			await Game.sio.emit("error", {"cause": "It's not your turn"}, room=sid)
			return
		if self.popped:
			await Game.sio.emit("error", {"cause": "You have already popped"}, room=sid)
		elif self.board.fullmove_number == 1:
			await Game.sio.emit("error", {"cause": "No moves to undo"}, room=sid)
		else:
			self.board.pop()
			self.board.pop()
			await Game.sio.emit("pop", {}, room=[player.sid for player in self.players])
			self.popped = True

	async def move(self, sid: str, data: dict[str, str]) -> None:
		if sid not in Game.sid_to_id:
			await Game.sio.emit("error", {"cause": "No games founded"}, room=sid)
		if "san" not in data:
			await Game.sio.emit("error", {"cause": "Missing fields"}, room=sid)
			return
		if data["san"] is None:
			await Game.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
			return
		if not self.is_player_turn(sid):
			await Game.sio.emit("error", {"cause": "It's not your turn"}, room=sid)
			return
		if not self.current.has_time():
			return
		try:
			uci_move = self.board.parse_san(data["san"]).uci()
		except (chess.InvalidMoveError, chess.IllegalMoveError):
			await Game.sio.emit("error", {"cause": "Invalid move"}, room=sid)
			return
		if chess.Move.from_uci(uci_move) not in self.board.legal_moves:
			await Game.sio.emit("error", {"cause": "Invalid move"}, room=sid)
			return
		uci_move = self.board.parse_uci(self.board.parse_san(data["san"]).uci())
		san_move = self.board.san(uci_move)
		self.board.push_uci(uci_move.uci())
		outcome = self.board.outcome()
		if outcome is not None:
			await Game.sio.emit("move", {"san": san_move}, room=self.current.sid)
			await Game.sio.emit("end", {"winner": outcome.winner}, room=[player.sid for player in self.players])
			await Game.disconnect(self.current.sid)
			await Game.on_disconnect(self.next.sid)
			return
		self.popped = False
		self.current.first_move = False
		self.swap()
		await Game.sio.emit("move", {"san": san_move}, room=self.current.sid)

	@classmethod
	async def start(cls, sid: str, data: dict[str, str]) -> None:
		def check_int(key, inf, sup):
			try:
				v = int(data[key])
				return inf <= v <= sup
			except (ValueError, TypeError):
				return False

		def check_options(key, options):
			try:
				value = int(data[key])
				return value in options
			except (ValueError, TypeError, KeyError):
				return False

		# Check for data validity
		if "rank" not in data or "time" not in data:
			await Game.sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
			return
		if not check_int("rank", MIN_RANK, MAX_RANK):
			await Game.sio.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
			return
		if not check_options("time", TIME_OPTIONS):
			await Game.sio.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
			return

		# se non loggato, se loggato devo pure vedere il database
		time = data["time"]
		rank = round(max(min(int(data["rank"]), 100), 0) / 10) * 10
		# vedere se ci sta il complementare
		index = (10 - (rank // 10)) % 6 if rank // 10 > 5 else (rank // 10) % 6
		if sid in Game.sid_to_id:
			await Game.sio.emit("error", {"cause": "Started Matching", "fatal": True}, room=sid)
		elif (len(cls.waiting_list[time][index]) > 0 and cls.waiting_list[time][index][0][
			"rank"] == 100 - rank):
			first = random.randint(0, 1)
			players = (
				[sid, cls.waiting_list[time][index].pop(0)["sid"]]
				if first
				else [cls.waiting_list[time][index].pop(0)["sid"], sid]
			)
			game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
			Game.games[game_id] = cls(players, rank if first else 100 - rank, data["time"])
			Game.sid_to_id[sid] = game_id
			Game.sid_to_id[players[1] if first else players[0]] = game_id
			await Game.sio.emit("config", {"fen": Game.games[game_id].fen, "id": game_id, "color": "white"}, room=players[0])
			await Game.sio.emit("config", {"fen": Game.games[game_id].fen, "id": game_id, "color": "black"}, room=players[1])
			#togliere l'id dal frontend
		else:
			cls.waiting_list[time][index].append({"sid": sid, "rank": rank})
			# serve per eliminarlo dalla entry
			Game.sid_to_id[sid] = {"time": time, "index": index}