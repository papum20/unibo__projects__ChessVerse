import Game
import json
from const import EventType, AckType


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