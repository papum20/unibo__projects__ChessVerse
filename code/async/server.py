#!/usr/bin/env python

import asyncio
import os
import json
import threading

import socketio
import aiohttp
from time import perf_counter

import chess
import chess.engine

from PVEGame import PVEGame

class PVEGameNamespace(socketio.AsyncNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pveGames = {}
        thread = threading.Thread(target=self.cleaner_thread)
        thread.start()

    async def on_connect(self, sid, _):
        await self.emit("connected", room=sid)
        print("connect ", sid)

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
        if sid in self.pveGames.keys():
            del self.pveGames[sid]

    async def on_start(self, sid, data):
        def check_int(key, min, max):
            try:
                v = int(data[key])
                return min <= v <= max
            except (ValueError, TypeError) as e:
                return False

        if "rank" not in data or "depth" not in data or "time" not in data:
            await self.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
            return
        if not check_int("rank", 0, 100):
            await self.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_int("depth", 1, 20):
            await self.emit("error", {"cause": "Invalid bot strength", "fatal": True}, room=sid)
            return
        if not check_int("time", 1, 3000):
            await self.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return
        self.pveGames[sid] = PVEGame(sid, data["rank"], data["depth"], data["time"])
        await self.pveGames[sid].initialize_bot()
        await self.emit("config", {"fen": self.pveGames[sid].fen}, room=sid)

    async def on_move(self, sid, data):
        print("move ", sid, data)
        if sid not in self.pveGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        game = self.pveGames[sid]
        if "san" not in data:
            await self.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if not game.current.has_time():
            return
        try:
            uci_move = game.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await self.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
            await self.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        game.board.push_uci(uci_move)
        outcome = game.board.outcome()
        if outcome is not None:
            await self.emit("end", {"winner": outcome.winner}, room=sid)
            await self.on_disconnect(sid)
            return
        start = perf_counter()
        bot_move = (await game.bot.play(game.board, chess.engine.Limit(depth=game.depth))).move
        game.board.push_uci(bot_move.uci())
        outcome = game.board.outcome()
        latest_move = game.board.pop()
        san_bot_move = game.board.san(bot_move)
        game.board.push(latest_move)
        if outcome is not None:
            await self.emit("move", {"san": san_bot_move}, room=sid)
            await self.emit("end", {"winner": outcome.winner}, room=sid)
            await self.on_disconnect(sid)
            return
        game.popped = False
        end = perf_counter()
        game.current.add_time(end - start)
        game.current.first_move = False
        await self.emit("move", {"san": san_bot_move}, room=sid)

    async def on_resign(self, sid, _):
        print("resign", sid)
        if sid not in self.pveGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await self.on_disconnect(sid)

    async def on_pop(self, sid, _):
        print("pop", sid)
        if sid not in self.pveGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        game = self.pveGames[sid]
        if game.popped:
            await self.emit("error", {"cause": "You have already popped"}, room=sid)
        elif game.board.fullmove_number == 1:
            await self.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            game.board.pop()
            game.board.pop()
            await self.emit("pop", {}, room=sid)
            game.popped = True

    def cleaner_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def cleaner():
            while True:
                await asyncio.sleep(1)

                for sid in list(self.pveGames.keys()):
                    if sid not in self.pveGames:
                        continue

                    for player in self.pveGames[sid].players:
                        if not player.has_time():
                            print("gotcha ", sid)
                            await self.emit("timeout", {}, room=sid)
                            await self.on_disconnect(sid)
                            await self.disconnect(sid)

        loop.run_until_complete(cleaner())

async def main():
    env = os.environ.get("ENVIROMENT", "development")
    if env == "development":
        from dotenv import load_dotenv
        env_file = f".env.{env}"
        load_dotenv(dotenv_path=env_file)
    sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
    app = aiohttp.web.Application()
    sio.attach(app)

    game_namespace = PVEGameNamespace(os.environ.get("WSS_NAMESPACE"))
    sio.register_namespace(game_namespace)

    app.router.add_get(os.environ.get("WSS_NAMESPACE"), sio.handle_request)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    host = os.environ.get("WSS_DOMAIN")
    port = 8766

    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()
    print(f"Listening on {host}:{port}")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
