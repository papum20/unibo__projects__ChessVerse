import unittest
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, patch, call
import sys
import os
import socketio
import chess
import chess.engine
from random import choice
from ...PVEGame import PVEGame
from ...PVPGame import PVPGame
from ...server import GameHandler
from ...const import GameType

sys.path.append("../../")

"""
sono da testare GamePVE, on_connect, on_disconnect, on_start, on_move, on_resign, on_pop


on_connect: -> che si riesca a trovare il socket
on_disconect: -> che non si riesca a trovare il socket
on_start: -> venga inizializzata la partita
on_mmove: -> venga fatta la mossa, con test di mosse varie
on_resign: -> venga fatta la sconfitta
on_pop: -> venga fatta pop e non consecutivi.
e' possibile fare mock delle mosse di stockfish e della generazione inziale della board
l'ordine dei patch e' al contrario

module.func1
module.func2
test(func2, fun1)
"""

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = "/".join(project_root.split("/")[:-1])
os.chdir(target_dir)


def mock_bot_move(move: str, to_mock: MagicMock):
    mock_move = MagicMock()
    mock_move.uci.return_value = move  # Define the return value for uci() method
    to_mock.return_value = mock.MagicMock(move=mock_move)


class TestChessSocketIO(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.game_handler = GameHandler(self.sio)
        mock_emit = AsyncMock()
        self.sio.emit = mock_emit
        self.pvp = "".join(choice("0123456789abcdef") for _ in range(16))
        self.pve = "".join(choice("0123456789abcdef") for _ in range(16))
        self.pvp1 = "".join(choice("0123456789abcdef") for _ in range(16))

    async def test_on_connect(self):
        sid = "test_sid"
        await self.game_handler.on_connect(sid, None)
        self.sio.emit.assert_called_once_with("connected", room=sid)

    """
    async def test_on_disconnect(self):
        await self.game_handler.on_disconnect(self.pve, {"type": GameType.PVE})
        self.sio.emit.assert_not_called()
        await self.game_handler.on_disconnect(self.pvp, {"type": GameType.PVP})
        self.sio.emit.assert_called_with("error", {"cause": "Invalid type", "fatal": True}, room=self.pvp)

    async def test_on_bad_disconnect(self):
        await self.game_handler.on_disconnect(self.pve, {})
        self.sio.emit.assert_called_with("error", {"cause": "Invalid type", "fatal": True}, room=self.pve)
        await self.game_handler.on_disconnect(self.pvp, {})
        self.sio.emit.assert_called_with("error", {"cause": "Invalid type", "fatal": True}, room=self.pvp)
    """

    async def test_on_start_invalid_type(self):
        sid = "test_sid"
        invalid_data = {"rank": 70, "depth": 1, "time": 3000}
        await self.game_handler.on_start(sid, invalid_data)
        self.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid type", "fatal": True}, room=sid
        )

    async def test_on_start_PVE(self):
        sid = "test_sid"
        data = {"rank": 70, "depth": 1, "time": 3000, "type": GameType.PVE}
        await self.game_handler.on_start(sid, data)
        PVEGame.start.assert_called_once_with(sid, data)

    async def test_on_start_PVP(self):
        sid = "test_sid"
        data = {"rank": 70, "depth": 1, "time": 3000, "type": GameType.PVP}
        await self.game_handler.on_start(sid, data)
        PVPGame.start.assert_called_once_with(sid, data)

    """
    @patch('random.choice', return_value="a")
    @patch("Game.confighandler.gen_start_fen")
    async def test_on_valid_start(self, mock_gen_start_fen, _):
        mock_gen_start_fen.return_value = chess.STARTING_FEN
        await self.game_handler.on_start(self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE})
        self.sio.emit.assert_called_with("config", {"fen": chess.STARTING_FEN}, room=self.pve)
        await self.game_handler.on_start(self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP})
        await self.game_handler.on_start(self.pvp, {"rank": 30, "time": 300, "type": GameType.PVP})
        self.sio.emit.assert_called_with("error", {"cause": "Started Matching", "fatal": True}, room=self.pvp)
        await self.game_handler.on_start(self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE})
        self.sio.emit.assert_called_with("error", {"cause": "Started Matching", "fatal": True}, room=self.pve)
        await self.game_handler.on_start(self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP})
        self.sio.emit.assert_called_with("config", {"fen": chess.STARTING_FEN, "id": "a" * 16},
                                         room=[self.pvp, self.pvp1])

    # bad initialization data
    async def test_on_invalid_start(self):
        data = {"rank": -100, "depth": -100, "time": -1000, "type": GameType.PVE}
        await self.game_handler.on_start(self.pve, data)
        self.sio.emit.assert_called_with('error', {'cause': 'Invalid rank', 'fatal': True}, room=self.pve)
        data["type"] = GameType.PVP
        await self.game_handler.on_start(self.pvp, data)
        self.sio.emit.assert_called_with('error', {'cause': 'Invalid rank', 'fatal': True}, room=self.pvp)
        data["type"] = GameType.PVE
        data["rank"] = 10
        await self.game_handler.on_start(self.pve, data)
        self.sio.emit.assert_called_with('error', {"cause": "Invalid bot strength", "fatal": True}, room=self.pve)
        data["depth"] = 10
        data["type"] = GameType.PVE
        await self.game_handler.on_start(self.pve, data)
        self.sio.emit.assert_called_with('error', {"cause": "Invalid clocktime", "fatal": True}, room=self.pve)
        data["type"] = GameType.PVP
        await self.game_handler.on_start(self.pvp, data)
        self.sio.emit.assert_called_with('error', {'cause': "Invalid clocktime", 'fatal': True}, room=self.pvp)
    """

    async def test_on_resign_game_not_found(self):
        ...

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    async def test_on_resign(self, _, __, ___):
        await self.game_handler.on_resign(self.pve, {"type": GameType.PVE})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pve
        )
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_resign(self.pve, {"type": GameType.PVE})
        self.sio.emit.assert_called_with("disconnected", room=self.pve)

        # resign p1
        await self.game_handler.on_resign(self.pvp, {"type": GameType.PVP})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Missing id", "fatal": True}, room=self.pvp
        )
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_resign(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16}
        )
        self.sio.emit.assert_any_call(
            "end", {"winner": False}, room=[self.pvp1, self.pvp]
        )
        # resign player
        await self.game_handler.on_resign(self.pvp, {"type": GameType.PVP})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Missing id", "fatal": True}, room=self.pvp
        )
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_resign(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16}
        )
        self.sio.emit.assert_any_call(
            "end", {"winner": True}, room=[self.pvp1, self.pvp]
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    async def test_on_empty_move(self, _, __, ___):
        # empty test
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Missing fields"}, room=self.pve
        )

        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Missing fields"}, room=self.pvp1
        )

        # empty value test
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": None})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Encountered None value"}, room=self.pve
        )

        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": None}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Encountered None value"}, room=self.pvp1
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    async def test_on_none_move(self, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": None})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Encountered None value"}, room=self.pve
        )

        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": None}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Encountered None value"}, room=self.pvp1
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    async def test_on_invalid_move(self, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(
            self.pve, {"type": GameType.PVE, "san": "hello"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Invalid move"}, room=self.pve
        )

        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "hello"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Invalid move"}, room=self.pvp1
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_valid_uci_move(self, mock_play, _, __, ___):
        mock_bot_move("e7e5", mock_play)
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        # subsequent move
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e2e3"})
        mock_bot_move("h7h5", mock_play)
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e4"})

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e2e4"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "e2e3"}
        )
        self.sio.emit.assert_called_with("move", {"san": "e3"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e7e5"}
        )
        self.sio.emit.assert_called_with("move", {"san": "e5"}, room=self.pvp1)
        # mossa successiva
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        self.sio.emit.assert_called_with("move", {"san": "e4"}, room=self.pvp)

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_invalid_uci_move(self, mock_play, _, __, ___):
        mock_bot_move("e7e5", mock_play)
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e2"})
        self.sio.emit.assert_called_with(
            "error", {"cause": "Invalid move"}, room=self.pve
        )
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "e2"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Invalid move"}, room=self.pvp1
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_checkmate(self, mock_play, _, __, ___):
        mock_bot_move("h3h1", mock_play)
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "Ke1"})
        self.sio.emit.assert_has_calls(
            [call("end", {"winner": False}, room=self.pve)], any_order=True
        )
        self.sio.emit.assert_any_call("end", {"winner": False}, room=self.pve)

        # subsequent move
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e2e3"})
        mock_bot_move("h7h5", mock_play)
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pve
        )

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with("move", {"san": "Ke1"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Rh1"}
        )
        self.sio.emit.assert_any_call(
            "end", {"winner": False}, room=[self.pvp1, self.pvp]
        )
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pvp
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="4k3/2Q5/3RBB2/7P/8/2P5/PPP1PPP1/RN2K1N1 w Q - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_checkmate_move2(self, mock_play, _, __, ___):
        mock_bot_move("h3h1", mock_play)
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "Rd8"})
        self.sio.emit.assert_any_call("end", {"winner": True}, room=self.pve)
        # subsequent move
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e2e3"})
        mock_bot_move("h7h5", mock_play)
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pve
        )

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Rd8"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "Rd8"}
        )
        self.sio.emit.assert_any_call(
            "end", {"winner": True}, room=[self.pvp1, self.pvp]
        )
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pvp
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="nrk4n/ppp1pppp/8/8/3b4/1q1b3r/8/2K5 w - - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_stalemate(self, mock_play, _, __, ___):
        mock_bot_move("h3h1", mock_play)
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "Kd2"})
        self.sio.emit.assert_any_call("end", {"winner": None}, room=self.pve)

        # subsequent move
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e2e3"})
        mock_bot_move("h7h5", mock_play)
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pve
        )

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "Kd2"}
        )
        self.sio.emit.assert_called_with("move", {"san": "Kd2"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "h3h1"}
        )
        self.sio.emit.assert_any_call(
            "end", {"winner": None}, room=[self.pvp1, self.pvp]
        )
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "Game not found", "fatal": True}, room=self.pvp
        )

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_enpassant(self, mock_play, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        mock_bot_move("e7e5", mock_play)
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "f5"})
        mock_bot_move("d7e6", mock_play)
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "fxe6"})

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "f5"}
        )
        self.sio.emit.assert_called_with("move", {"san": "f5"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e7e5"}
        )
        self.sio.emit.assert_called_with("move", {"san": "e5"}, room=self.pvp1)
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "fxe6"}
        )
        self.sio.emit.assert_called_with("move", {"san": "fxe6"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "d7e6"}
        )
        self.sio.emit.assert_called_with("move", {"san": "dxe6"}, room=self.pvp1)

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="rnbqkbnr/ppPp2pp/8/8/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_promotion(self, mock_play, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        mock_bot_move("e8d8", mock_play)
        await self.game_handler.on_move(
            self.pve, {"type": GameType.PVE, "san": "cxd8=R+"}
        )

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "cxd8=R+"}
        )
        self.sio.emit.assert_called_with("move", {"san": "cxd8=R+"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e8d8"}
        )
        self.sio.emit.assert_called_with("move", {"san": "Kxd8"}, room=self.pvp1)

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch(
        "Game.confighandler.gen_start_fen",
        return_value="rnbqkbnr/pppppppp/8/8/2N5/PPNPBPP1/1B1QP2P/R3K2R w KQkq - 0 1",
    )
    @patch.object(chess.engine.UciProtocol, "play")
    async def test_on_castling(self, mock_play, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        mock_bot_move("h7h6", mock_play)
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "O-O"})

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "Ke1"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "O-O"}
        )
        self.sio.emit.assert_called_with("move", {"san": "O-O"}, room=self.pvp)
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "h7h6"}
        )
        self.sio.emit.assert_called_with("move", {"san": "h6"}, room=self.pvp1)

    @patch("random.randint", return_value=1)
    @patch("random.choice", return_value="a")
    @patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    async def test_on_pop(self, _, __, ___):
        await self.game_handler.on_start(
            self.pve, {"rank": 70, "depth": 1, "time": 300, "type": GameType.PVE}
        )
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e4"})
        await self.game_handler.on_pop(self.pve, {"type": GameType.PVE})
        await self.game_handler.on_move(self.pve, {"type": GameType.PVE, "san": "e4"})
        await self.game_handler.on_pop(self.pve, {"type": GameType.PVE})
        self.sio.emit.assert_called_with("pop", {}, room=self.pve)

        # pvp testing
        await self.game_handler.on_start(
            self.pvp, {"rank": 70, "time": 300, "type": GameType.PVP}
        )
        await self.game_handler.on_start(
            self.pvp1, {"rank": 30, "time": 300, "type": GameType.PVP}
        )

        # pvp1 dovrebbe esssere il primo
        # testing for sending message not in turn
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        self.sio.emit.assert_called_with(
            "error", {"cause": "It's not your turn"}, room=self.pvp
        )
        # testing moves
        await self.game_handler.on_move(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16, "san": "e4"}
        )
        await self.game_handler.on_move(
            self.pvp, {"type": GameType.PVP, "id": "a" * 16, "san": "h7h6"}
        )
        await self.game_handler.on_pop(
            self.pvp1, {"type": GameType.PVP, "id": "a" * 16}
        )
        self.sio.emit.assert_any_call("pop", {}, room=[self.pvp1, self.pvp])

    # @mock.patch("Game.configonr.gen_start_fen")
    # @mock.patch("server.sio.emit")
    # async def test_on_unsufficient_pop(self, mock_emit, mock_gen_start_fen):
    #     sid = "test"
    #     mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    #     data = {"rank": 10, "depth": 10, "time": 100}
    #     await on_start(sid, data)
    #     await on_pop(sid, {})
    #     mock_emit.assert_called_with("error", {"cause": "No moves to undo"}, room=sid)
    #
    # @mock.patch("Game.configonr.gen_start_fen")
    # @mock.patch("server.sio.emit")
    # async def test_on_repetitive_pop(self, mock_emit, mock_gen_start_fen):
    #     sid = "test"
    #     mock_gen_start_fen.return_value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    #     data = {"rank": 10, "depth": 10, "time": 100}
    #     await on_start(sid, data)
    #     await on_move(sid, {"san": "e4"})
    #     await on_move(sid, {"san": "f4"})
    #     await on_pop(sid, {})
    #     await on_pop(sid, {})
    #     mock_emit.assert_called_with("error", {"cause": "You have already popped"}, room=sid)


if __name__ == "__main__":
    unittest.main()
