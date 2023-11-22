import Game

class PVPGame(Game):
	def __init__(self, players, rank, key, timer):
		super().__init__(players, rank, key, timer)
		self.isTimed = timer != -1

	def swap(self):
		self.popped = False
		self.turn = (self.turn + 1) % 2

	def is_players_turn(self, key):
		for i, player in enumerate(self.players):
			if player.id[16:] == key[16:]:
				return True
		return False

	async def end_game(self, winner):
		loser = self.players[1 - winner.color]
		await websocket_dict[winner.id].send(json.dumps({"end": True}))
		await websocket_dict[loser.id].send(json.dumps({"end": False}))
		del pvpGames[self.key]
		
	async def recv_event(self, msg):
		if msg["event"] == EventType.RESIGN:
			await self.end_game(self.opponent())
			pass
		elif msg["event"] == EventType.MOVE:
			if not self.current().has_time():
				await self.end_game(self.opponent())
			else:
				while (
						chess.Move.from_san(msg["data"]["value"])
						not in self.board.legal_moves
				):
					await websocket_dict[self.current().id].send(json.dumps({"move": msg["data"]["value"], "valid": False}))
				self.board.push_san(msg["data"]["value"])
				self.popped = False
				if self.board.outcome() is None:
					await websocket_dict[self.current().id].send(json.dumps({"move": msg["data"]["value"]}))
					await websocket_dict[self.opponent().id].send(json.dumps({"move": msg["data"]["value"]}))
					self.swap()
				else:
					await self.end_game(self.current())

		elif msg["event"] == EventType.POP:
			if not self.current().has_time():
				await websocket_dict[self.current().id].send(json.dumps({"end": False}))
				await websocket_dict[self.opponent().id].send(json.dumps({"end": True}))
			elif self.popped:
				await websocket_dict[self.current().id].send(json.dumps({"ack": AckType.OK, "value": True}))
			else:
				try:
					m1 = self.board.pop()
					try:
						self.board.pop()
					except IndexError:
						self.board.push(m1)
						raise IndexError
				except IndexError:
					await websocket_dict[self.current().id].send(json.dumps({"ack": AckType.NOK, "value": True}))
				else:
					await websocket_dict[self.current().id].send(json.dumps({"ack": AckType.OK, "value": True}))
					await websocket_dict[self.opponent().id].send(json.dumps({"pop": True}))

		else:
			await websocket_dict[self.current().id].send(json.dumps({"ack": AckType.UNKNOWN_ACTION}))