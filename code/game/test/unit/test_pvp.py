import unittest
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest import mock
from unittest.mock import AsyncMock, PropertyMock

import sys
import chess
import socketio

sys.path.append("../..")
from PVPGame import PVPGame
from Game import Game


class TestInitialization(TestCase):
    @mock.patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.sid = "test_sid"
        self.players = ["player1", "player2"]
        self.rank = 1
        self.time = 100
        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        # Game instantiation
        Game.sid_to_id[self.sid] = self.sid
        self.game = Game.games[self.sid] = PVPGame(self.players, self.rank, self.time)

    def test_player_init(self):
        self.assertEqual(self.game.players, self.players)

    def test_fen_init(self):
        self.assertEqual(self.game.fen, chess.STARTING_FEN)


class TestSwap(TestCase):
    @mock.patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.sid = "test_sid"
        self.players = ["player1", "player2"]
        self.rank = 1
        self.time = 100
        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

        # Game instantiation
        Game.sid_to_id[self.sid] = self.sid
        self.game = Game.games[self.sid] = PVPGame(self.players, self.rank, self.time)

        self.game.turn = 0

    def test_popped_is_set_false(self):
        self.game.swap()
        self.assertFalse(self.game.popped)

    def test_turn_advance_from_0(self):
        self.game.swap()
        self.assertEqual(self.game.turn, 1)

    def test_turn_advance_from_1(self):
        self.game.turn = 1
        self.game.swap()
        self.assertEqual(self.game.turn, 0)


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

    @mock.patch("Game.Game.update_win_database")
    @mock.patch("Game.Game.opponent")
    async def test_update_win_database_is_called(
        self, mock_opponent, mock_update_win_db
    ):
        type(mock_opponent.return_value).sid = PropertyMock(
            return_value=self.opponent_sid
        )
        await self.game.disconnect(self.sid)
        mock_update_win_db.assert_awaited_once_with(self.opponent_sid, False)

    @mock.patch("Game.Game.update_win_database")
    @mock.patch("Game.Game.opponent")
    async def test_emit_end_msg(self, mock_opponent, mock_update_win_db):
        type(mock_opponent.return_value).sid = PropertyMock(
            return_value=self.opponent_sid
        )
        await self.game.disconnect(self.sid)
        Game.sio.emit.assert_any_call("end", {"winner": True}, room=self.opponent_sid)

    @mock.patch("Game.Game.update_win_database")
    @mock.patch("Game.Game.opponent")
    async def test_game_is_deleted(self, mock_opponent, mock_update_win_db):
        type(mock_opponent.return_value).sid = PropertyMock(
            return_value=self.opponent_sid
        )
        await self.game.disconnect(self.sid)
        self.assertNotIn(self.opponent_sid, Game.sid_to_id.keys())
        self.assertNotIn(self.opponent_sid, Game.games.keys())
        self.assertNotIn(self.sid, Game.sid_to_id.keys())
        self.assertNotIn(self.sid, Game.games.keys())


class TestPop(IsolatedAsyncioTestCase):
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

        # Game instantiation
        Game.sid_to_id[self.sid] = self.sid
        self.game = Game.games[self.sid] = PVPGame(self.players, self.rank, self.time)

    """
    async def test_missing_id(self):
        await self.game.pop(self.sid)
        Game.sio.emit.assert_any_await(
            "error",
            {"cause": "Missing id", "fatal": True},
            room=self.sid
        )
    """

    async def test_wrong_turn(self):
        await self.game.pop(self.sid)
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "It's not your turn"}, room=self.sid
        )

    @mock.patch("PVPGame.PVPGame.is_player_turn", return_value=True)
    async def test_already_popped(self, mock_is_player_turn):
        self.game.popped = True
        await self.game.pop(self.sid)
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "You have already popped"}, room=self.sid
        )

    @mock.patch("PVPGame.PVPGame.is_player_turn", return_value=True)
    async def test_no_moves_to_undo(self, mock_is_player_turn):
        self.game.board.fullmove_number = 1
        await self.game.pop(self.sid)
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "No moves to undo"}, room=self.sid
        )

    @mock.patch("PVPGame.PVPGame.is_player_turn", return_value=True)
    @mock.patch("PVPGame.PVPGame.get_times", return_value=[0, 1, 2])
    async def test_correct_pop(self, mock_get_times, mock_is_player_turn):
        self.game.board.push_uci("e2e4")
        self.game.board.push_uci("e7e5")
        await self.game.pop(self.sid)
        Game.sio.emit.assert_called_once_with(
            "pop", {"time": [0, 1, 2]}, room=self.game.players
        )
        self.assertTrue(self.game.popped)


class TestMove(IsolatedAsyncioTestCase):
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

        # Game instantiation
        Game.sid_to_id[self.sid] = self.sid
        self.game = Game.games[self.sid] = PVPGame(self.players, self.rank, self.time)
        self.game.current.sid = self.sid
        self.game.next.sid = self.opponent_sid

        self.data = {"san": "e2e4"}

    """
    async def test_no_games_found(self):
        del Game.sid_to_id[self.sid]
        await self.game.move(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error",
            {"cause": "No games found"},
            room=self.sid
        )
    """

    async def test_san_not_in_data(self):
        await self.game.move(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Missing fields", "fatal": True}, room=self.sid
        )

    async def test_san_value_is_none(self):
        await self.game.move(self.sid, {"san": None})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Encountered None value"}, room=self.sid
        )

    @mock.patch("PVPGame.PVPGame.is_player_turn", return_value=False)
    async def test_wrong_player_turn(self, mock_is_player_turn):
        await self.game.move(self.sid, self.data)
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "It's not your turn"}, room=self.sid
        )

    async def test_invalid_move(self):
        await self.game.move(self.sid, {"san": "invalid_move"})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid move"}, room=self.sid
        )

    @mock.patch("chess.Board.outcome")
    @mock.patch("Game.Game.update_win_database", return_value=[1000, 1200])
    @mock.patch("PVPGame.PVPGame.disconnect")
    @mock.patch("Game.Game.get_times", return_value=[1, 2, 3])
    async def test_move_with_outcome(
        self, mock_time, mock_disconnect, mock_update_win_db, mock_board_outcome
    ):
        type(mock_board_outcome.return_value).winner = PropertyMock(
            return_value=chess.WHITE
        )
        await self.game.move(self.sid, self.data)

        Game.sio.emit.assert_any_call(
            "move", {"san": "e4", "time": [1, 2, 3]}, room=self.sid
        )
        Game.sio.emit.assert_any_call(
            "move", {"san": "e4", "time": [1, 2, 3]}, room=self.opponent_sid
        )
        Game.sio.emit.assert_any_call(
            "end", {"winner": True, "elo": 1000}, room=self.sid
        )
        Game.sio.emit.assert_any_call(
            "end", {"winner": False, "elo": 1200}, room=self.opponent_sid
        )
        mock_disconnect.assert_called_once_with(self.opponent_sid)

    @mock.patch("PVPGame.PVPGame.swap")
    @mock.patch("Game.Game.get_times", return_value=[1, 2, 3])
    async def test_correct_move(self, mock_time, mock_swap):
        await self.game.move(self.sid, self.data)
        self.assertFalse(self.game.popped)
        mock_swap.assert_called_once()
        Game.sio.emit.assert_any_call(
            "move", {"san": "e4", "time": [1, 2, 3]}, room=self.sid
        )
        Game.sio.emit.assert_any_call("ack", {"time": [1, 2, 3]}, room=self.sid)


class TestStart(IsolatedAsyncioTestCase):
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

        self.data = {"rank": 1, "time": 600}

    async def test_missing_fields(self):
        await PVPGame.start(self.sid, {})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Missing fields", "fatal": True}, room=self.sid
        )

    async def test_invalid_rank(self):
        await PVPGame.start(self.sid, {"rank": -1, "time": 100})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid rank", "fatal": True}, room=self.sid
        )

    async def test_invalid_time(self):
        await PVPGame.start(self.sid, {"rank": 1, "time": -1})
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Invalid clocktime", "fatal": True}, room=self.sid
        )

    async def test_sid_already_present(self):
        Game.sid_to_id[self.sid] = self.sid
        await PVPGame.start(self.sid, self.data)
        Game.sio.emit.assert_called_once_with(
            "error", {"cause": "Started Matching", "fatal": True}, room=self.sid
        )

    ...


if __name__ == "__main__":
    unittest.main()
