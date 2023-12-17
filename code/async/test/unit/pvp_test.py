import unittest
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import json

sys.path.append("../../")
import chess
import chess.engine
from server import PVPGameNamespace

"""
sono da testare server


handle_connect: -> che si riesca a trovare il socket
handle_disconect: -> che non si riesca a trovare il socket
handle_start: -> venga inizializzata la partita
handle_mmove: -> venga fatta la mossa, con test di mosse varie
handle_resign: -> venga fatta la sconfitta
handle_pop: -> venga fatta pop e non consecutivi.
e' possibile fare mock delle mosse di stockfish e della generazione inziale della board
l'ordine dei patch e' al contrario

module.func1
module.func2
test(func2, fun1)
"""
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = "/".join(project_root.split("/")[:-1])
os.chdir(target_dir)


def mock_bot_move(move: str, tomock: MagicMock):
    mock_move = MagicMock()
    mock_move.uci.return_value = move  # Define the return value for uci() method
    tomock.return_value = mock.MagicMock(move=mock_move)


import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio

from server import PVPGameNamespace  # Replace with your actual namespace


class TestPVPGameNamespace(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.namespace = PVPGameNamespace("/test")  # Replace with your actual namespace

    async def test_on_connect(self):
        # Create an AsyncMock for 'emit'
        mock_emit = AsyncMock()
        self.namespace.emit = mock_emit

        # Simulate a client connection
        sid = "test"
        await self.namespace.on_connect(sid, None)

        # Assert that 'connected' event was emitted with the correct parameters
        mock_emit.assert_awaited_with("connected", room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    async def test_on_start(self, mock_gen_start_fen):
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        mock_emit = AsyncMock()
        self.namespace.emit = mock_emit
        player = "test1"
        player_data = {"rank": 10, "time": 600}
        opp = "test2"
        opp_data = {"rank": 90, "time": 600}

        await self.namespace.on_start(player, player_data)
        await self.namespace.on_start(opp, opp_data)

        mock_emit.assert_called_with("config", {"fen": chess.STARTING_FEN})

    # async def test_on_disconnect(self):

    # Add more test methods for other functionalities...


if __name__ == "__main__":
    unittest.main()
