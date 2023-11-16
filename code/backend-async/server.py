#!/usr/bin/env python

import asyncio
import random
import json
import csv

import socketio
import aiohttp
from enum import IntEnum, StrEnum, Flag
from time import perf_counter

import chess
import chess.engine
from Player import Player
from PVEGame import PVEGame


sio = socketio.AsyncServer(cors_allowed_origins="*")
app = aiohttp.web.Application()
sio.attach(app)

class EventType(StrEnum):
    ERROR = "error"
    RESIGN = "resign"
    MOVE = "move"
    POP = "pop"
    ACK = "ack"
    CONFIG = "config"
    END = "end"
    START = "start"


class AckType(IntEnum):
    OK = 0
    NOK = 1
    UNKNOWN_ACTION = 2
    WRONG_CONFIG = 3
    NOT_IMPLEMENTED = 4
    GAME_NOT_FOUND = 5
    WRONG_TURN = 6


class GameType(Flag):
    PVP = False
    PVE = True


class RowType(StrEnum):
    BACK = "back"
    FRONT = "front"


connected_clients = {-1: [], 5: [], 10: [], 15: []}
pvpGames = {}
pveGames = {}
lock = asyncio.Lock()


async def matchmaker(msg, websocket):
    global connected_clients
    try:
        if msg["data"]["type"] == GameType.PVP:
            async with lock:
                time = msg["data"]["time"]
                if time in c.botDiff:
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
        print(msg)
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

pveGames = {}

async def handle_connect(sid, environ):
    print("connect ", sid)
    # TODO aggiungere giocatore alla lista dei giocatori connessi
    await sio.emit("my response", {"data": "Connected", "count": 0}, room=sid)

async def handle_disconnect(sid):
    print("disconnect ", sid)
    del pveGames[sid]

async def handle_start(sid, data):
    print("start ", sid, data)
    if not "rank" in data or not "depth" in data or not "time" in data:
        await sio.emit("my response", {"data": "error", "count": 0}, room=sid)
        return
    pveGames[sid] = PVEGame(sid, data["rank"], data["depth"], data["time"])
    await pveGames[sid].initialize_bot()
    await sio.emit("config", pvGames[sid].current.get_config_msg(), room=sid)

class EventType(StrEnum):
    ERROR = "error"
    RESIGN = "resign"
    MOVE = "move"
    POP = "pop"
    ACK = "ack"
    CONFIG = "config"
    END = "end"
    START = "start"


sio.on("connect", handle_connect)
sio.on("disconnect", handle_disconnect)
sio.on("resign", handle_resign)
sio.on("pop", handle_pop)
sio.on("move", handle_move)
sio.on("start", handle_start)


async def main():
    print("starting...")
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, 'localhost', 8766)
    await site.start()
    while True:
        await asyncio.sleep(1)
       
    # async with serve(receive_message, "localhost", 8766):
    #     await asyncio.Future()


asyncio.run(main())
