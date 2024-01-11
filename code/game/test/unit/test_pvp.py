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

    @mock.patch("Game.Game.emit_error")
    async def test_missing_id(self, mock_emit_error):
        del Game.sid_to_id[self.sid]
        self.assertNotIn(self.sid, Game.sid_to_id)
        await self.game.pop(self.sid)
        mock_emit_error.assert_awaited_once_with("Missing id", self.sid)

    @mock.patch("PVPGame.PVPGame.game_found", return_value=False)
    async def test_game_not_found(self, mock_game_found):
        await self.game.pop(self.sid)
        Game.sio.emit.assert_not_called()

    @mock.patch("Game.Game.emit_error")
    @mock.patch("PVPGame.PVPGame.is_player_turn", return_value=False)
    async def test_wrong_turn(self, mock_is_player_turn, mock_emit_error):
        await self.game.pop(self.sid)
        mock_emit_error.assert_awaited_once_with("It's not your turn", self.sid, None)

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

    @mock.patch("Game.Game.emit_error")
    async def test_no_games_found(self, mock_emit_error):
        del Game.sid_to_id[self.sid]
        await self.game.move(self.sid, {})
        mock_emit_error.assert_awaited_once_with("No games found", self.sid)

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

    @mock.patch("PVPGame.PVPGame.calculate_index", return_value=15)
    @mock.patch("PVPGame.PVPGame.calculate_rank", return_value=0)
    @mock.patch("PVPGame.PVPGame.process_matching")
    async def test_call_to_process_matching(self, mock_process_matching, mock_calculate_rank, mock_calculate_index):
        del Game.sid_to_id[self.sid]
        self.assertNotIn(self.sid, Game.sid_to_id)
        await PVPGame.start(self.sid, self.data)
        mock_process_matching.assert_awaited_once_with(self.sid, 600, 0, 15)


class TestProcessMatching(IsolatedAsyncioTestCase):
    def setUp(self):
        self.sid = 'test_sid'
        self.time = 300
        self.rank = 5
        self.index = 0

    @mock.patch("PVPGame.PVPGame.add_player_to_waiting_list")
    async def test_no_match_found(self, mock_add_player_to_waiting_list):
        PVPGame.waiting_list[300, 0] = []
        await PVPGame.process_matching(self.sid, self.time, self.rank, self.index)
        mock_add_player_to_waiting_list.assert_awaited_once_with(self.sid, self.time, self.rank, self.index)

    @mock.patch("PVPGame.PVPGame.add_player_to_waiting_list")
    async def test_match_found(self, mock_add_player_to_waiting_list):
        PVPGame.waiting_list[300, 0] = [[{"rank": 95}]]
        await PVPGame.process_matching(self.sid, self.time, self.rank, self.index)
        mock_add_player_to_waiting_list.assert_awaited_once_with(self.sid, self.time, self.rank, self.index)


class TestSetupGameWithExistingPlayer(IsolatedAsyncioTestCase):
    @mock.patch("Game.confighandler.gen_start_fen", return_value=chess.STARTING_FEN)
    def setUp(self, mock_gen_start_fen):
        self.sid = "test_sid"
        self.opponent_sid = "test_opponent_sid"
        self.players = ["player1", "player2"]
        self.rank = 1
        self.time = 300
        self.index = 0
        Game.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.mock_emit = AsyncMock()
        Game.sio.emit = self.mock_emit

    @mock.patch("socketio.AsyncServer.get_session", return_value={"elo": 150})
    async def test_session_is_fetched(self, mock_get_session):
        await PVPGame.setup_game_with_existing_player(self.sid, self.time, self.rank, self.index)
        mock_get_session.assert_awaited_with(self.sid)


if __name__ == "__main__":
    unittest.main()
