import unittest
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest import mock
from unittest.mock import AsyncMock, PropertyMock, call

import sys
import random
import chess
import socketio

sys.path.append("../..")
from Game import Game, expected_score, update_rating, calc_k
from PVPGame import PVPGame
from server import GameHandler
from const import DEFAULT_ELO
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = "/".join(project_root.split("/")[:-1])
os.chdir(target_dir)

class TestLogin(IsolatedAsyncioTestCase):
    @mock.patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.sid = "test_sid"
        self.opponent_sid = "test_opponent_sid"
        self.players = ["player1", "player2"]
        self.rank = 1
        self.time = 100
        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit
        Game.sio.save_session = AsyncMock()
        self.server = GameHandler()

        self.data = {"rank": 1, "time": 600, "session_id": "a"*16}

    @mock.patch("Game.Game.execute_query", return_value=None)
    async def test_login_not_found(self, mock_query):
        await self.server.on_start(self.sid, self.data)
        Game.sio.save_session.assert_called_once_with(
            self.sid, {"elo": DEFAULT_ELO, "session_id": "a"*16, "username": "Guest"}
        )

    @mock.patch("Game.Game.execute_query", return_value=[(10, "a")])
    async def test_login_found(self, mock_query):
        await self.server.on_start(self.sid, self.data)
        Game.sio.save_session.assert_called_once_with(
            self.sid, {"elo": 10, "session_id": "a"*16, "username": "a"}
        )

class TestDisconnect(IsolatedAsyncioTestCase):
    @mock.patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.sid = "test_sid"
        self.opponent_sid = "test_opponent_sid"
        self.players = ["player1", "player2"]
        self.rank = 1
        self.time = 100
        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit
        Game.sio.disconnect = AsyncMock()

        # Game instantiation
        Game.sid_to_id[self.sid] = self.sid
        self.game = Game.games[self.sid] = PVPGame(self.players, self.rank, self.time)

    @mock.patch("Game.Game.execute_query")
    @mock.patch("Game.Game.opponent")
    async def test_update_win_database_correct(
        self, mock_opponent, mock_query
    ):
        type(mock_opponent.return_value).sid = PropertyMock(
            return_value=self.opponent_sid
        )
        dc = AsyncMock()
        dc.return_value = {"session_id": "a"*16, "elo": 10}
        Game.sio.get_session = dc
        await self.game.disconnect(self.sid)

        calls = [call('UPDATE backend_registeredusers SET GamesWon = GamesWon + 1 WHERE session_id = %s', ("a"*16,)),
                 call('UPDATE backend_registeredusers SET GamesLost = GamesLost + 1 WHERE session_id = %s', ("a"*16,)),
                 call('UPDATE backend_registeredusers SET EloReallyBadChess = -20.0 WHERE session_id = %s', ("a"*16,)),
                 call('UPDATE backend_registeredusers SET EloReallyBadChess = 40.0 WHERE session_id = %s', ("a"*16,))]

        mock_query.assert_has_calls(calls)

    @mock.patch("Game.Game.execute_query")
    @mock.patch("Game.Game.opponent")
    async def test_update_win_database_correct(
        self, mock_opponent, mock_query
    ):
        type(mock_opponent.return_value).sid = PropertyMock(
            return_value=self.opponent_sid
        )
        dc = AsyncMock()
        dc.return_value = None
        Game.sio.get_session = dc
        await self.game.disconnect(self.sid)
        mock_query.assert_not_called()


class TestExpectedScore(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3

    def test_method_returns_correctly(self):
        correct_result = 1.0 / (1 + 10 ** ((self.rating_b - self.rating_a) / 400))
        self.assertEqual(expected_score(self.rating_a, self.rating_b), correct_result)


class TestUpdateRating(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3
        self.risultato = 15

    @mock.patch("Game.expected_score", return_value=10)
    @mock.patch("Game.calc_k", return_value=17.5)
    def test_method_returns_correctly(self, mock_calc_k, mock_expected_score):
        correct_result = (
            self.rating_a + 17.5 * (15 - 10),
            self.rating_b + 17.5 * (1 - 15 - 10),
        )
        self.assertEqual(
            update_rating(self.rating_a, self.rating_b, self.risultato), correct_result
        )


class TestCalculateK(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3

    def test_method_returns_correctly(self):
        correct_result = round(60 - 0.0167 * (self.rating_a + self.rating_b) / 2)
        self.assertEqual(correct_result, calc_k(self.rating_a, self.rating_b))
