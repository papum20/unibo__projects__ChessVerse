import unittest
from unittest import TestCase
from unittest import mock

import sys

import chess

sys.path.append("../..")
from PVPGame import PVPGame


class TestInitialization(TestCase):
    @mock.patch('Game.confighandler.gen_start_fen', return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.players = ['player1', 'player2']
        self.rank = 1
        self.depth = 5
        self.time = 100
        self.instance = PVPGame(self.players, self.rank, self.time)

    def test_player_init(self):
        self.assertEqual(self.instance.players, self.players)

    def test_fen_init(self):
        self.assertEqual(self.instance.fen, chess.STARTING_FEN)


if __name__ == '__main__':
    unittest.main()
