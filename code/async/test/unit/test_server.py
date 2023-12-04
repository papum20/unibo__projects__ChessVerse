import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock


class TestOnConnect(IsolatedAsyncioTestCase):
    sio = None

    @classmethod
    def setUpClass(cls):
        cls.sid = 'test_sid'
        cls.sio = MagicMock()
        cls.sio.emit = AsyncMock()
        cls.game_handler = GameHandler(sio=cls.sio)

    async def test_called_with_correct_arguments(self):
        await self.game_handler.on_connect(self.sid, None)
        self.sio.emit.assert_called_once_with('connected', room=self.sid)


class TestOnDisconnect(IsolatedAsyncioTestCase):
    ...


class TestOnStart(IsolatedAsyncioTestCase):
    ...


class TestOnMove(IsolatedAsyncioTestCase):
    ...


class TestOnResign(IsolatedAsyncioTestCase):
    ...


class TestOnPop(IsolatedAsyncioTestCase):
    ...


class TestCleaner(IsolatedAsyncioTestCase):
    ...


if __name__ == '__main__':
    unittest.main()
