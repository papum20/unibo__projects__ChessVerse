import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# scrivo sul mio locale le cose
from ..code.async. import server

# Use functions/classes from other_script.py
other_script.some_function()

from server import (
    handle_start,
    handle_move,
    handle_resign,
    handle_pop,
    EventType,
    AckType,
    GameType,
)

class TestSocketServer(unittest.IsolatedAsyncioTestCase):
    async def test_handle_start_valid_data(self):
        # Prepare test data
        sid = "sample_sid"
        data = {"rank": 1200, "depth": 3, "time": 5}

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_start(sid, data, sio=mocked_sio)

        # Assertions on mocked functions being called
        mocked_sio.emit.assert_called_with(EventType.CONFIG.value, {"fen": "your_expected_fen"}, room=sid)

    # Add similar test methods for other handle_* functions

if __name__ == '__main__':
    unittest.main()
