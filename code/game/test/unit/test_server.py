import unittest
from unittest import TestCase, IsolatedAsyncioTestCase, mock
from unittest.mock import AsyncMock, MagicMock, PropertyMock
import datetime

import sys
import socketio

sys.path.append("../..")
from server import GameHandler
from Game import Game
from PVEGame import PVEGame
from PVPGame import PVPGame
from Player import Player
from const import GameType


class TestSid2Game(TestCase):
    def setUp(self):
        self.sid = 'test_sid'
        self.server = GameHandler()

    def test_game_id_is_not_a_string(self):
        Game.sid_to_id[self.sid] = 10
        self.assertIsNone(GameHandler.sid2game(self.sid))

    def test_with_invalid_key(self):
        Game.sid_to_id[self.sid] = 'test_id'
        self.assertIsNone(GameHandler.sid2game(self.sid))

    def test_with_valid_key(self):
        Game.sid_to_id[self.sid] = 'test_id'
        Game.games['id'] = 'test_game'
        self.assertIsNone(GameHandler.sid2game(self.sid), 'test_game')


class TestOnConnect(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

    async def test_emits_correct_msg(self):
        await self.server.on_connect(self.sid, None)
        Game.sio.emit.assert_called_once_with("connected", room=self.sid)


class TestOnDisconnect(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    """
    async def test_if_id_is_dict_instance(self):
        Game.sid_to_id[self.sid] = {'key': self.sid}
        await self.server.on_disconnect(self.sid)
        ...
    """

    async def test_id_is_not_dict_instance(self):
        await self.server.on_disconnect(self.sid)
        self.game.disconnect.assert_called_once_with(self.sid)


class TestOnStart(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    async def test_invalid_type(self):
        await self.server.on_start(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid type", "fatal": True}, room=self.sid
        )

    @mock.patch("Game.Game.login")
    async def test_session_id(self, mock_login):
        await self.server.on_start(self.sid, {"session_id": self.sid})
        mock_login.assert_called_once_with(self.sid, self.sid)

    @mock.patch("PVEGame.PVEGame.start")
    async def test_gametype_pve(self, mock_pve_start):
        data = {"type": GameType.PVE}
        await self.server.on_start(self.sid, data)
        mock_pve_start.assert_called_once_with(self.sid, data)

    @mock.patch("PVPGame.PVPGame.start")
    async def test_gametype_pvp(self, mock_pvp_start):
        data = {"type": GameType.PVP}
        await self.server.on_start(self.sid, data)
        mock_pvp_start.assert_called_once_with(self.sid, data)

    @mock.patch("PVEGame.PVEGame.start")
    @mock.patch("server.GameHandler.daily_seed", return_value=0)
    async def test_gametype_daily(self, mock_daily_seed, mock_daily_start):
        data = {"type": GameType.DAILY}
        await self.server.on_start(self.sid, data)
        mock_daily_start.assert_called_once_with(
            self.sid, data, seed=0, type=GameType.DAILY
        )

    @mock.patch("PVEGame.PVEGame.start")
    @mock.patch("server.GameHandler.weekly_seed", return_value=0)
    async def test_gametype_weekly(self, mock_weekly_seed, mock_weekly_start):
        data = {"type": GameType.WEEKLY}
        await self.server.on_start(self.sid, data)
        mock_weekly_start.assert_called_once_with(
            self.sid, data, seed=0, type=GameType.WEEKLY
        )

    @mock.patch("PVEGame.PVEGame.start")
    async def test_gametype_ranked(self, mock_start):
        data = {"type": GameType.RANKED}
        await self.server.on_start(self.sid, data)
        mock_start.assert_called_once_with(
            self.sid, data, seed=None, type=GameType.RANKED
        )

    async def test_error(self):
        await self.server.on_start(self.sid, {"type": None})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid type", "fatal": True}, room=self.sid
        )


class TestOnMove(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    async def test_invalid_type(self):
        await self.server.on_move(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid type", "fatal": True}, room=self.sid
        )

    """
    @mock.patch('server.GameHandler.sid2game')
    async def test_sid2game_is_called(self, mock_sid2game):
        await self.server.on_move(self.sid, {'type': 'some_data'})
        mock_sid2game.assert_called_once_with(self.sid)
    """

    @mock.patch("server.GameHandler.sid2game", return_value=None)
    async def test_game_not_found(self, mock_sid2game):
        await self.server.on_move(self.sid, {"type": "some_data"})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.sid
        )


class TestOnResign(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    @mock.patch("server.GameHandler.on_disconnect")
    async def test_method_calls_correctly(self, mock_on_disconnect):
        await self.server.on_resign(self.sid, None)
        mock_on_disconnect.assert_called_once_with(self.sid)


class TestOnPop(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    async def test_invalid_type(self):
        await self.server.on_pop(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid type", "fatal": True}, room=self.sid
        )

    @mock.patch("server.GameHandler.sid2game", return_value=None)
    async def test_game_not_found(self, mock_sid2game):
        await self.server.on_pop(self.sid, {"type": "some_data"})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.sid
        )


class TestDailySeed(unittest.TestCase):
    @mock.patch("datetime.date")
    def test_daily_seed(self, mock_date):
        mock_date_obj = MagicMock()
        mock_date_obj.year = 2023
        mock_date_obj.month = 12
        mock_date_obj.day = 17
        mock_date.today.return_value = mock_date_obj
        expected_seed = 2023 * 10000 + 12 * 100 + 17
        self.assertEqual(expected_seed, GameHandler.daily_seed())


class TestWeeklySeed(unittest.TestCase):
    @mock.patch("datetime.date")
    def test_weekly_seed(self, mock_date):
        mock_date_obj = MagicMock()
        mock_date_obj.isocalendar.return_value = (2023, 50, 1)
        mock_date_obj.year = 2023
        mock_date.today.return_value = mock_date_obj
        expected_seed = 2023 * 100 + 50
        self.assertEqual(expected_seed, GameHandler.weekly_seed())


class TestUpdateGames(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    @mock.patch("server.GameHandler.update_current_player")
    async def test_method_updates_players(self, mock_update_current_player):
        await self.server.update_games()
        mock_update_current_player.assert_awaited()


class TestUpdateCurrentPlayer(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()
        self.player = Player(sid=self.sid, color=True, time=3000)
        type(self.game).players = PropertyMock(
            return_value=[self.player]
        )

    @mock.patch("server.GameHandler.check_player")
    async def test_method_checks_player_timeout(self, mock_check_player):
        await self.server.update_current_player(self.game)
        mock_check_player.assert_awaited()


class TestCheckPlayer(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()
        self.player = Player(sid=self.sid, color=True, time=3000)
        type(self.game).players = PropertyMock(
            return_value=[self.player]
        )

    @mock.patch("server.GameHandler.calculate_remaining_time", return_value=3000)
    @mock.patch("server.GameHandler.handle_timeout")
    async def test_method_behaviour_with_remaining_time(self, mock_timeout, mock_calc_remaining_time):
        await self.server.check_player(self.player, self.game)
        mock_calc_remaining_time.assert_called_once_with(self.player, False)
        mock_timeout.assert_not_called()

    @mock.patch("server.GameHandler.calculate_remaining_time", return_value=0)
    @mock.patch("server.GameHandler.handle_timeout")
    async def test_method_behaviour_on_timeout(self, mock_timeout, mock_calc_remaining_time):
        await self.server.check_player(self.player, self.game)
        mock_calc_remaining_time.assert_called_once_with(self.player, False)
        mock_timeout.assert_called_once()


class TestHandleTimeOut(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()
        self.player = Player(sid=self.sid, color=True, time=3000)
        type(self.game).players = PropertyMock(
            return_value=[self.player]
        )
        type(self.game).board = PropertyMock()

    @mock.patch("chess.Board.has_insufficient_material", return_value=True)
    async def test_method_emits_correctly(self, mock_board_has_insufficient_material):
        await self.server.handle_timeout(self.player, self.game)
        self.mock_emit.assert_called_once_with("end", {'winner': None}, room=self.sid)


if __name__ == "__main__":
    unittest.main()
