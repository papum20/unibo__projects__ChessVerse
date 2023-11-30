import unittest
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import json

sys.path.append("../../")
import chess
# from server import (
    # handle_connect,
    # handle_disconnect,
    # handle_start,
    # handle_move,
    # handle_resign,
    # handle_pop,
# )

import PVEGame
import chess.engine

"""
sono da testare GamePVE, handle_connect, handle_disconnect, handle_start, handle_move, handle_resign, handle_pop


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


class TestChessSocketIO(IsolatedAsyncioTestCase):

    # simple connection
    @mock.patch("server.print")
    async def test_handle_connect(self, mock_print):
        sid = "test_sid"
        environ = {}
        # Mocking the socketio emit function
        await handle_connect(sid, environ)
        mock_print.assert_called_with("connect ", sid)
        await handle_disconnect(sid)
        mock_print.assert_called_with("disconnect ", sid)

    # simple disconnection
    @mock.patch("server.pveGames")
    async def test_handle_disconnect(self, mock_dict):
        sid = "test_sid"
        mock_dict.keys.return_value = {"myid", "hello"}
        await handle_disconnect(sid)
        mock_dict.__delitem__.assert_not_called()

    # simple start
    # @mock.patch("server.sio.emit")
    # async def test_handle_invalid_start(self, mock_emit):
    #     sid = "test_sid"
    #     data = {}
    #     await handle_start(sid, data)
    #     mock_emit.assert_called_with("error", {"cause": "Missing fields"}, room=sid)

    # si puo' iniziare la partita anche senza connect
    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_valid_start(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank":10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_emit.assert_called_with("config", {"fen": chess.STARTING_FEN}, room=sid)

    # @mock.patch("server.sio.emit")
    # # bad initialization data
    # async def test_handle_invalid_start(self, mock_emit):
    #     sid = "test_sid"
    #     data = {"rank": -100, "depth": -100, "time": -1000}
    #     await handle_start(sid, data)
    #     await handle_move(sid, {"san": "e4"})
    #     mock_emit.assert_called_with('error', {'cause': 'Game not found', 'fatal': True}, room=sid)

    @mock.patch("server.pveGames")
    @mock.patch("server.sio.emit")
    async def test_handle_resign_invalid(self, mock_emit, mock_dict):
        sid = "test_sid"
        mock_dict.return_value = {}
        await handle_resign(sid, {})
        mock_emit.assert_called_with('error', {'cause': 'Game not found', 'fatal': True}, room=sid)

    @mock.patch("server.pveGames")
    @mock.patch("server.sio.emit")
    @mock.patch("server.handle_disconnect")
    async def test_handle_resign_valid(self, mock_disconnect, mock_emit, mock_dict):
        sid = "test_sid"
        mock_dict.return_value = {"test_sid": "val"}
        mock_dict.__contains__.return_value = True
        await handle_resign(sid, {})
        mock_disconnect.assert_called()

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_empty_move(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 0, "depth": 0, "time": 0}
        await handle_start(sid, data)
        await handle_move(sid, {})
        mock_emit.assert_called_with('error', {'cause': 'Game not found', 'fatal': True}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_move_timeout(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 0, "depth": 0, "time": 0}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "hello"})
        mock_emit.assert_called_with('error', {'cause': 'Invalid move'}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_invalid_move(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "hello"})
        mock_emit.assert_called_with("error", {"cause": "Invalid move"}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_invalid_uci_move(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "e1e2"})
        mock_emit.assert_called_with("error", {"cause": "Invalid move"}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_valid_uci_move(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "e2e4"})
        # mock_emit.assert_called_with("error", {"cause": "Invalid move"}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_invalid_san_move(self, mock_emit, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "e2"})
        mock_emit.assert_called_with("error", {"cause": "Invalid move"}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_valid_san_move(self, mock_play, mock_gen_start_fen):
        sid = "test_sid"
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("e7e5", mock_play)
        # mock_move = MagicMock()
        # mock_move.uci.return_value = "e7e5"  # Define the return value for uci() method
        # mock_play.return_value = mock.MagicMock(move=mock_move)
        await handle_move(sid, {"san": "e4"})

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_checkmate_move(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("h3h1", mock_play)
        await handle_move(sid, {"san": "Ke1"})
        mock_emit.assert_called_with("end", {"winner": False}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_checkmate_move2(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "4k3/2Q5/3RBB2/7P/8/2P5/PPP1PPP1/RN2K1N1 w Q - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("h3h1", mock_play)
        await handle_move(sid, {"san": "Rd8"})
        mock_emit.assert_called_with("end", {"winner": True}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_stalemate(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "nrk4n/ppp1pppp/8/8/3b4/1q1b3r/8/2K5 w - - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("h3h1", mock_play)
        await handle_move(sid, {"san": "Kd2"})
        mock_emit.assert_called_with("end", {"winner": None}, room=sid)

    @mock.patch("server.sio.emit")
    async def test_handle_empty_move(self, mock_emit):
        sid = "test_sid"
        await handle_move(sid, {"san": "e2e4"})
        # Assertion to check if sio.emit was called with the expected arguments
        mock_emit.assert_called_with('error', {'cause': 'Game not found', 'fatal': True}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_enpassant(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("e7e5", mock_play)
        await handle_move(sid, {"san": "f5"})
        mock_bot_move("d7e6", mock_play)
        await handle_move(sid, {"san": "fxe6"})

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_promotion(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/ppPp2pp/8/8/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("e8d8", mock_play)
        await handle_move(sid, {"san": "cxd8=R+"})

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    @mock.patch.object(chess.engine.UciProtocol, "play")
    async def test_handle_castling(self, mock_play, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/2N5/PPNPBPP1/1B1QP2P/R3K2R w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        mock_bot_move("h7h6", mock_play)
        await handle_move(sid, {"san": "O-O"})

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_valid_pop(self, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "e4"})
        await handle_pop(sid, {})
        await handle_move(sid, {"san": "e4"})
        await handle_pop(sid, {})
        mock_emit.assert_called_with("pop", {}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_unsufficient_pop(self, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_pop(sid, {})
        mock_emit.assert_called_with("error", {"cause": "No moves to undo"}, room=sid)

    @mock.patch("Game.confighandler.gen_start_fen")
    @mock.patch("server.sio.emit")
    async def test_handle_repetitive_pop(self, mock_emit, mock_gen_start_fen):
        sid = "test"
        mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        data = {"rank": 10, "depth": 10, "time": 100}
        await handle_start(sid, data)
        await handle_move(sid, {"san": "e4"})
        await handle_move(sid, {"san": "f4"})
        await handle_pop(sid, {})
        await handle_pop(sid, {})
        mock_emit.assert_called_with("error", {"cause": "You have already popped"}, room=sid)

    # @mock.patch("server.sio.emit")
    # async def test_handle_move_no_game(self, mock_emit):
    #     sid = "test_sid"
    #     await handle_move(sid, {"san": "e2e4"})
    #
    #     # Assertion to check if sio.emit was called with the expected arguments
    #     mock_emit.assert_called_with("error", {"cause": "Game not found"}, room=sid)


if __name__ == "__main__":
    unittest.main()
