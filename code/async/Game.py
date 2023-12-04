import chess
import confighandler
import Player
import os
from socketio import AsyncServer
from abc import ABC, abstractmethod
from const import TIME_OPTIONS


class Game(ABC):
    sio = None
    games = {}
    sid_to_id: dict[str, str] = {}
    waiting_list: dict[str, list[list[str]]] = {key: [[] for _ in range(6)] for key in TIME_OPTIONS}
    __slots__ = ["fen", "board", "players", "turn", "popped"]

    def __init__(self, sids: [], rank: int, time: int) -> None:
        if confighandler.get_configs() is None:
            confighandler.load_configs(os.path.join(os.path.dirname(__file__), 'configs.csv'))
        self.fen = confighandler.gen_start_fen(rank)
        self.board = chess.Board(self.fen)
        self.players = []
        for i, sid in enumerate(sids):
            self.players.append(Player.Player(sid, not bool(i), time))
        self.turn = 0
        self.popped = False

    @property
    def current(self) -> Player:
        return self.players[self.turn]

    @property
    def next(self) -> Player:
        return self.players[1 - self.turn]

    def opponent(self, sid: str) -> Player:
        return self.players[1 - self.players.index(sid)]

    @abstractmethod
    async def disconnect(self, sid: str) -> None:
        pass

    @classmethod
    @abstractmethod
    async def start(cls, sid: str) -> None:
        pass

    @abstractmethod
    async def move(self, sid: str, data: dict[str, str]) -> None:
        pass

    @abstractmethod
    async def pop(self, sid: str) -> None:
        pass

    @classmethod
    def set_sio(cls, sio: AsyncServer) -> None:
        if cls.sio is not None and isinstance(sio, AsyncServer):
            cls.sio = sio

    async def game_found(self, sid: str, game_id: str):
        if game_id not in self.games:
            await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True
