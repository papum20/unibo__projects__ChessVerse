#!/usr/bin/env python

import asyncio
import random
import json
import csv
import threading

import socketio
import aiohttp
from time import perf_counter

import chess
import chess.engine

from PVEGame import PVEGame

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = aiohttp.web.Application()
sio.attach(app)


pveGames = {}


async def handle_connect(sid, environ):
    print("connect ", sid)

async def handle_disconnect(sid):
    print("disconnect ", sid)
    if sid in pveGames.keys():
        del pveGames[sid]


async def handle_start(sid, data):
    print("start ", sid, data)
    if not "rank" in data or not "depth" in data or not "time" in data:
        await sio.emit("error", {"cause": "Missing fields"}, room=sid)
        return
    pveGames[sid] = PVEGame(sid, data["rank"], data["depth"], data["time"])
    await pveGames[sid].initialize_bot()
    await sio.emit("config", {"fen": pveGames[sid].fen}, room=sid)


async def handle_move(sid, data):
    print("move ", sid, data)
    if not sid in pveGames:
        await sio.emit("error", {"cause": "Game not found"}, room=sid)
        return
    game = pveGames[sid]
    if "san" not in data:
        await sio.emit("error", {"cause": "Missing fields"}, room=sid)
        return
    if not game.current.has_time():
        return
    uci_move = game.board.parse_san(data["san"]).uci()
    if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
        await sio.emit("error", {"cause": "Invalid move"}, room=sid)
        return
    game.board.push_uci(uci_move)
    outcome = game.board.outcome()
    if not outcome is None:
        await sio.emit("end", {"winner": outcome.winner}, room=sid)
        await handle_disconnect(sid)
        await sio.disconnect(sid)
        return
    inizio = perf_counter()
    bot_move = (await game.bot.play(game.board, chess.engine.Limit(depth=game.depth))).move
    game.board.push_uci(bot_move.uci())
    outcome = game.board.outcome()
    latest_move = game.board.pop()
    san_bot_move = game.board.san(bot_move)
    game.board.push(latest_move)
    if outcome is not None:
        print(outcome)
        await sio.emit("move", {"san": san_bot_move}, room=sid)
        await sio.emit("end", {"winner": outcome.winner}, room=sid)
        await handle_disconnect(sid)
        await sio.disconnect(sid)
        return
    game.popped = False
    fine = perf_counter()
    game.current.add_time(fine - inizio)
    game.current.first_move = False
    await sio.emit("move", {"san": san_bot_move}, room=sid)


async def handle_resign(sid, data):
    print("resign", sid)
    if not sid in pveGames:
        await sio.emit("error", {"cause": "Game not found"}, room=sid)
        return
    await handle_disconnect(sid)
    await sio.disconnect(sid)


async def handle_pop(sid, data):
    print("pop", sid)
    if not sid in pveGames:
        await sio.emit("error", {"cause": "Game not found"}, room=sid)
        return
    game = pveGames[sid]
    if game.popped:
        await sio.emit("error", {"cause": "You have already popped"}, room=sid)
    elif game.board.fullmove_number == 1:
        await sio.emit("error", {"cause": "No moves to undo"}, room=sid)
    else:
        game.board.pop()
        game.board.pop()
        await sio.emit("pop", {}, room=sid)
        game.popped = True


sio.on("connect", handle_connect)
sio.on("disconnect", handle_disconnect)
sio.on("resign", handle_resign)
sio.on("pop", handle_pop)
sio.on("move", handle_move)
sio.on("start", handle_start)


def cleaner_thread(games, sio):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def cleaner():
        while True:
            await asyncio.sleep(1)  # Adjust the sleep interval as needed

            for sid in list(games.keys()):
                if sid not in games:
                    continue

                for player in games[sid].players:
                    if not player.has_time():
                        print("gotcha ", sid)
                        await sio.emit("timeout", {}, room=sid)
                        await handle_disconnect(sid)
                        await sio.disconnect(sid)

    loop.run_until_complete(cleaner())


async def main():
    print("starting...")
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, 'localhost', 8766)
    thread = threading.Thread(target=cleaner_thread, args=(pveGames, sio))
    thread.start()
    await site.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
