import unittest
from unittest import TestCase, IsolatedAsyncioTestCase, mock
from unittest.mock import AsyncMock
import datetime

import sys
import socketio

sys.path.append("../..")
from server import GameHandler
from Game import Game
from PVEGame import PVEGame
from PVPGame import PVPGame
from const import GameType


class TestSid2Game(TestCase):
    ...


class TestOnConnect(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

    async def test_emits_correct_msg(self):
        await self.server.on_connect(self.sid)
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
    async def test_gametype_daily(self, mock_daily_start):
        data = {"type": GameType.DAILY}
        await self.server.on_start(self.sid, data)
        mock_daily_start.assert_called_once_with(self.sid, data, 0, GameType.DAILY)

    @mock.patch("PVEGame.PVEGame.start")
    @mock.patch("server.GameHandler.weekly_seed", return_value=0)
    async def test_gametype_daily(self, mock_weekly_start):
        data = {"type": GameType.WEEKLY}
        await self.server.on_start(self.sid, data)
        mock_weekly_start.assert_called_once_with(self.sid, data, 0, GameType.WEEKLY)

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
    async def test_game_not_found(self):
        await self.server.on_move(self.sid, {"type": "some_data"})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.sid
        )

    """
    @mock.patch('server.GameHandler.sid2game')
    @mock.patch('Game.Game.move')
    async def test_correct_move(self, mock_move, mock_sid2game):
        await self.server.on_move(self.sid, {'type': 'some_data'})
        mock_move.assert_called_once_with(self.sid, {'type': 'some_data'})
    """


class TestOnResign(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = "test_sid"

        self.server = GameHandler()

        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        Game.sid_to_id[self.sid] = self.sid
        Game.games[self.sid] = self.game = AsyncMock()

    @mock.patch('server.GameHandler.on_disconnect')
    async def test_method_calls_correctly(self, mock_on_disconnect):
        await self.server.on_resign(self.sid)
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

    """
    @mock.patch('server.GameHandler.sid2game')
    @mock.patch('Game.Game.disconnect')
    async def test_pop(self, mock_move, mock_sid2game):
        await self.server.on_pop(self.sid, {'type': 'some_data'})
        mock_move.assert_called_once_with(self.sid, {'type': 'some_data'})
    """


class TestDailySeed(unittest.TestCase):
    @mock.patch('datetime.date.today', return_value=datetime.date(2023, 12, 17))
    def test_method_returns_correctly(self):
        expected_seed = 2023 * 10000 + 12 * 100 + 17
        self.assertEqual(expected_seed, GameHandler.daily_seed())


class TestWeeklySeed(unittest.TestCase):
    @mock.patch('datetime.date.today', return_value=datetime.date(2023, 12, 17))
    def test_method_returns_correctly(self):
        week_number = datetime.date(2023, 12, 17).isocalendar()[1]
        expected_seed = 2023 * 100 + week_number
        self.assertEqual(expected_seed, GameHandler.daily_seed())


class TestCleaner(IsolatedAsyncioTestCase):
    ...


if __name__ == "__main__":
    unittest.main()
