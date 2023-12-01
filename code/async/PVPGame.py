import Game
import json
from const import EventType, AckType


class PVPGame(Game.Game):
	def __init__(self, players, rank, timer):
		super().__init__(players, rank, timer)
		self.isTimed = timer != -1

	def swap(self):
		self.popped = False
		self.turn = (self.turn + 1) % 2

	def is_player_turn(self, sid):
		return self.current.sid == sid

