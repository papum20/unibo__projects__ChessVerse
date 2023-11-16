#!/usr/bin/env python

import asyncio
import random
import json
import csv

from websockets import serve
from websockets.exceptions import ConnectionClosedError
from enum import IntEnum, StrEnum
from time import perf_counter

import chess
import chess.engine

configs = {}


class EventType(IntEnum):
    ERROR = -1
    RESIGN = 0
    MOVE = 1
    POP = 2
    ACK = 3
    CONFIG = 4
    END = 5
    START = 999


class AckType(IntEnum):
    OK = 0
    NOK = 1
    UNKNOWN_ACTION = 2
    WRONG_CONFIG = 3
    NOT_IMPLEMENTED = 4
    GAME_NOT_FOUND = 5
    WRONG_TURN = 6


class GameType(IntEnum):
    PVP = 0
    PVE = 1


class RowType(StrEnum):
    BACK = "back"
    FRONT = "front"


class Player:
    def __init__(self, pid, websocket, color, time):
        self.id = pid
        self.ws = websocket
        self.color = color
        self.isTimed = time != -1
        if self.isTimed:
            self.remainingTime = time * 60
            self.latestTimeStamp = perf_counter()

    def update_time(self):
        if self.isTimed:
            self.remainingTime -= perf_counter() - self.latestTimeStamp
            self.latestTimeStamp = perf_counter()

    def has_time(self):
        return not self.isTimed or self.remainingTime > 0

    async def send(self, event_type: EventType, data: dict = None):
        msg = {"event": event_type}
        if data is not None:
            msg["data"] = data
        await self.ws.send(json.dumps(msg))

    async def send_config(self, fen, color, pid):
        await self.send(EventType.CONFIG, {"fen": fen, "color": color, "id": pid})

    async def send_ack(self, value: AckType, time: bool = False):
        data = {"value": value}
        if self.isTimed and time:
            self.update_time()
            data["time"] = self.remainingTime
        await self.send(EventType.ACK, data)

    async def send_end(self, won: bool):
        await self.send(EventType.END, {"value": int(won)})
        await self.ws.close()

    async def send_move(self, move: str, success: bool = True):
        await self.send(EventType.MOVE, {"value": move, "success": success})

    async def send_pop(self):
        await self.send(EventType.POP)


class Game:
    def __init__(self, p_socks: [], rank: int, key: str, time: int):
        self.fen = gen_start_fen(rank)
        self.board = chess.Board(self.fen)
        self.players = []
        for i, pSock in enumerate(p_socks):
            self.players.append(
                Player(
                    key + "".join(random.choice("0123456789abcdef") for _ in range(16)),
                    pSock,
                    i,
                    time,
                )
            )
        self.turn = 0
        self.popped = False
        self.key = key

    async def initialize_players(self):
        for player in self.players:
            await player.send_config(self.fen, player.color, player.id)

    def current(self):
        return self.players[self.turn]

    def opponent(self):
        return self.players[1 - self.turn]

    # @property
    # def current(self):
    #     return self.players[self.turn]
    
    # @property
    # def opponent(self):
    #     return self.players[1 - self.turn]


class PVPGame(Game):
    def __init__(self, players, rank, key, timer):
        super().__init__(players, rank, key, timer)
        self.isTimed = timer != -1

    def swap(self):
        self.popped = False
        self.turn = (self.turn + 1) % 2

    def is_players_turn(self, key):
        for i, player in enumerate(self.players):
            if player.id[16:] == key[16:]:
                return True
        return False

    async def end_game(self, winner: Player):
        loser = self.players[1 - winner.color]
        await winner.send_end(True)
        await loser.send_end(False)
        del pvpGames[self.key]

    async def recv_event(self, msg):
        if msg["event"] == EventType.RESIGN:
            await self.end_game(self.opponent())
            pass
        elif msg["event"] == EventType.MOVE:
            if not self.current().has_time():
                await self.end_game(self.opponent())
            else:
                while (
                        chess.Move.from_san(msg["data"]["value"])
                        not in self.board.legal_moves
                ):
                    await self.current().send_move(msg["data"]["value"], False)
                self.board.push_san(msg["data"]["value"])
                self.popped = False
                if self.board.outcome() is None:
                    await self.current().send_move(msg["data"]["value"])
                    await self.opponent().send_move(msg["data"]["value"])
                    self.swap()
                else:
                    await self.end_game(self.current())
        elif msg["event"] == EventType.POP:
            if not self.current().has_time():
                await self.current().send_end(False)
                await self.current().send_end(True)
            elif self.popped:
                await self.current().send_ack(AckType.OK, True)
            else:
                try:
                    m1 = self.board.pop()
                    try:
                        self.board.pop()
                    except IndexError:
                        self.board.push(m1)
                        raise IndexError
                except IndexError:
                    await self.current().send_ack(AckType.NOK, True)
                else:
                    await self.current().send_ack(AckType.OK, True)
                    await self.opponent().send_pop()
        else:
            await self.current().send_ack(AckType.UNKNOWN_ACTION)


class PVEGame(Game):
    def __init__(self, player, rank, key, depth):
        super().__init__([player], rank, key, -1)
        self.bot = None
        self.depth = depth

    async def initialize_bot(self):
        self.bot = (await chess.engine.popen_uci("./stockfish"))[1]

    async def end_game(self, winner: bool):
        await self.current().send_end(winner)
        del pveGames[self.key]

    async def recv_event(self, msg):
        if msg["event"] == EventType.RESIGN:
            await self.end_game(False)
            pass
        elif msg["event"] == EventType.MOVE:
            if not self.current().has_time():
                await self.end_game(False)
            else:
                while (
                        chess.Move.from_san(msg["data"]["value"])
                        not in self.board.legal_moves
                ):
                    await self.current().send_ack(AckType.NOK, True)
                self.board.push_san(msg["data"]["value"])
                self.popped = False
                if self.board.outcome() is None:
                    await self.current().send_ack(AckType.OK, True)
                    bot_move = (
                        await self.bot.play(
                            self.board, chess.engine.Limit(depth=self.depth)
                        )
                    ).move.san()
                    self.board.push_san(bot_move)
                    if self.board.outcome() is None:
                        await self.current().send_move(bot_move)
                    else:
                        await self.current().send_end(False)
                else:
                    await self.end_game(True)
        elif msg["event"] == EventType.POP:
            if not self.current().has_time():
                await self.current().send_end(False)
            elif self.popped:
                await self.current().send_ack(AckType.OK, True)
            else:
                try:
                    m1 = self.board.pop()
                    try:
                        self.board.pop()
                    except IndexError:
                        self.board.push(m1)
                        raise IndexError
                except IndexError:
                    await self.current().send_ack(AckType.NOK, True)
                else:
                    await self.current().send_ack(AckType.OK, True)
        else:
            await self.current().send_ack(AckType.UNKNOWN_ACTION)


def gen_start_fen(rank=50):
    rank = max(min(int(rank), 100), 0)

    def get_ref_ranks(ref_rank):
        return [ref_rank // 10 * 10, (ref_rank // 10 + (1 if ref_rank % 10 >= 5 else 0)) * 10]

    def gen_config(ranks, row_type):
        row_configs = [
            random.choice(configs[str(ranks[i])][row_type.value]) for i in range(len(ranks))
        ]
        return row_configs[0][:5] + row_configs[1][5:]

    wb = gen_config(get_ref_ranks(rank), RowType.BACK)
    wf = gen_config(get_ref_ranks(rank), RowType.FRONT)
    bb = gen_config(get_ref_ranks(100 - rank), RowType.BACK)
    bf = gen_config(get_ref_ranks(100 - rank), RowType.FRONT)
    castle = f"""{
        'Q' if wb[0] == 'r' else ''}{
        'K' if wb[7] == 'r' else ''}{
        'q' if bb[0] == 'r' else ''}{
        'k' if bb[7] == 'r' else ''}"""
    return f"{bb}/{bf}/8/8/8/8/{wf.upper()}/{wb.upper()} w {castle if len(castle) else '-'} - 0 1"


connected_clients = {-1: [], 5: [], 10: [], 15: []}
pvpGames = {}
pveGames = {}
lock = asyncio.Lock()


async def matchmaker(msg, websocket):
    global connected_clients
    try:
        if msg["data"]["type"] == 0:
            async with lock:
                time = msg["data"]["time"]
                if time in connected_clients:
                    connected_clients[time].append(websocket)
                else:
                    await websocket.send(json.dumps({"event": EventType.ERROR, "data": {"type": AckType.WRONG_CONFIG}}))
                if len(connected_clients[time]) == 2:
                    player = connected_clients[time][0]
                    connected_clients[time] = []
                    game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
                    players = (
                        [websocket, player]
                        if random.randint(0, 1)
                        else [player, websocket]
                    )
                    pvpGames[game_id] = PVPGame(players, msg["data"]["rank"], game_id, time)
                    await pvpGames[game_id].initialize_players()
        else:
            game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
            pveGames[game_id] = PVEGame(
                websocket, msg["data"]["rank"], game_id, msg["data"]["depth"]
            )
            await pveGames[game_id].initialize_players()
            await pveGames[game_id].initialize_bot()
    except ConnectionClosedError:
        async with lock:
            if websocket in connected_clients:
                del connected_clients[websocket]


async def receive_message(websocket):
    async for message in websocket:
        msg = json.loads(message)
        if msg["event"] == EventType.START:
            await matchmaker(msg, websocket)
        elif msg["data"]["type"] == GameType.PVP:
            game = pvpGames[msg["data"]["id"][:16]]
            if game is None:
                await websocket.send(
                    json.dumps(
                        {
                            "event": EventType.ERROR,
                            "data": {"value": AckType.GAME_NOT_FOUND},
                        }
                    )
                )
            elif not game.is_players_turn(msg["data"]["id"]):
                await websocket.send(
                    json.dumps(
                        {
                            "event": EventType.ERROR,
                            "data": {"value": AckType.WRONG_TURN},
                        }
                    )
                )
            else:
                await game.recv_event(msg)
        else:
            game = pveGames[msg["data"]["id"][:16]]
            if game is None:
                await websocket.send(
                    json.dumps(
                        {
                            "event": EventType.ERROR,
                            "data": {"value": AckType.GAME_NOT_FOUND},
                        }
                    )
                )
            else:
                await game.recv_event(msg)


async def main():
    async with serve(receive_message, "localhost", 8766):
        await asyncio.Future()


with open("configs.csv", newline="") as csvfile:
    rows = csv.reader(csvfile, delimiter=",", quotechar='"')
    for idx, (level, row) in enumerate(rows):
        if level in configs:
            configs[level]["front" if idx % 26 >= 13 else "back"].append(row)
        else:
            configs[level] = {"front": [], "back": [row]}


def test_configs():
    def gen_config(ranks, row_type):
        row_configs = [
            random.choice(configs[str(ranks[j])][row_type.value]) for j in range(len(ranks))
        ]
        return row_configs[0][:5] + row_configs[1][5:]

    errs = 0
    oks = 0
    for rank in range(0, 110, 10):
        for i in range(13):
            wb = gen_config([rank], RowType.BACK)
            wf = gen_config([rank], RowType.FRONT)
            bb = gen_config([100 - rank], RowType.BACK)
            bf = gen_config([100 - rank], RowType.FRONT)
            castle = f"""{
                'Q' if wb[0] == 'r' else ''}{
                'K' if wb[7] == 'r' else ''}{
                'q' if bb[0] == 'r' else ''}{
                'k' if bb[7] == 'r' else ''}"""
            fen = f"""{bb}/{bf}/8/8/8/8/{
                wf.upper()}/{wb.upper()} w {castle if len(castle) else "-"} - 0 1"""
            try:
                chess.Board(fen)
            except Exception as e:
                print(e)
                print(fen, "    ", rank, i)
                errs += 1
            else:
                oks += 1


asyncio.run(main())
