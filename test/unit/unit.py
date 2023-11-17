import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import json
sys.path.append("/code/async")
from server import (
    handle_start,
    handle_move,
    handle_resign,
    handle_pop,
    handle_connect,
    handle_disconnect,
    EventType,
    GameType,
    matchmaker,
    receive_message
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
    async def test_handle_move_valid_data(self):
        # Test handling move event with valid data
        sid = "sample_sid"
        data = {"san": "e4"}

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_move(sid, data)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior after a move

    async def test_handle_resign(self):
        # Test handling resign event
        sid = "sample_sid"
        data = {}  # No specific data for resign

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_resign(sid, data)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior after a resignation

    async def test_handle_pop(self):
        # Test handling pop event
        sid = "sample_sid"
        data = {}  # No specific data for pop

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_pop(sid, data)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior after a pop

    async def test_handle_connect(self):
        # Test handling connect event
        sid = "sample_sid"
        environ = {}  # Mocking the environ object

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_connect(sid, environ)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior on a connection

    async def test_handle_disconnect(self):
        # Test handling disconnect event
        sid = "sample_sid"

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_disconnect(sid)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior on a disconnection

    async def test_handle_start_valid_data(self):
        # Test handling start event with valid data
        sid = "sample_sid"
        data = {"rank": 1200, "depth": 3, "time": 5}

        # Prepare mocks
        mocked_sio = MagicMock()
        mocked_sio.emit = AsyncMock()

        # Call the function with test data and mocks
        await handle_start(sid, data)

        # Assertions on mocked functions being called
        # Add assertions for expected behavior after starting a async

    async def test_receive_message(self):
        # Test receiving a message and handling its content
        websocket = MagicMock()
        msg = {"event": "start", "data": {"type": GameType.PVP}}

        # Call the function with test data
        await receive_message(websocket, json.dumps(msg))

        # Assertions on the WebSocket behavior
        # Add assertions for how the message is processed

    async def test_matchmaker_pvp(self):
        # Test the matchmaker function for PvP games
        msg = {"data": {"type": GameType.PVP, "time": 5}}
        websocket_1 = MagicMock()
        websocket_2 = MagicMock()

        # Call the function with test data
        await matchmaker(msg, websocket_1)
        await matchmaker(msg, websocket_2)

        # Assertions on the matchmaking behavior
        # Add assertions for pairing players into a async

    async def test_matchmaker_pve(self):
        # Test the matchmaker function for PvE games
        msg = {"data": {"type": GameType.PVE, "rank": 1200, "depth": 3}}
        websocket = MagicMock()

        # Call the function with test data
        await matchmaker(msg, websocket)

        # Assertions on the matchmaking behavior
        # Add assertions for creating PvE games and initializing players

if __name__ == '__main__':
    unittest.main()
