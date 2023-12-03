#!/usr/bin/env python
import asyncio
import os
import ssl
import socketio
import aiohttp
from PVEGame import PVEGame
from PVPGame import PVPGame
from Game import Game
from const import GameType
import threading

active_clients = {}
class GameHandler:
    def __init__(self, sio):
        self.sio = sio
        self.games = {}
        self.loop = asyncio.new_event_loop()
        self.cleaner_thread = threading.Thread(target=self.cleaner)
        self.cleaner_thread.start()


    @classmethod
    def sid2game(cls, sid):
        try:
            print(f"{sid=}")
            print(f"{Game.sid_to_id=}")
            print(f"{Game.sid_to_id[sid]=}")
            print(f"{Game.games=}")
            print(f"{Game.games[Game.sid_to_id[sid]]=}")
            return Game.games[Game.sid_to_id[sid]]
        except KeyError:
            return None


    async def on_connect(self, sid, _):
        print("connect ", sid)
        await self.sio.emit("connected", room=sid)

    async def on_disconnect(self, sid):
        print("disconnect", sid)
        if sid in active_clients:
            id = active_clients[sid]
            if isinstance(id, dict):
                self.pvp_handler.connected_clients[id["time"]][id["index"]].pop(0)
            else:
                game_id = active_clients[sid]
                await Game.games[game_id].disconnect(sid)
            del active_clients[sid]

    async def on_start(self, sid, data):
        print("start", sid)
        if("type" not in data.keys()):
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await PVEGame.start(sid, data)
        elif(data["type"] == GameType.PVP):
            await PVPGame.start(sid, data)
        else:
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_move(self, sid, data):
        print("move", sid)
        if("type" not in data.keys()):
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await game.move(sid, data)

    async def on_resign(self, sid, data):
        print("resign", sid)
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await game.disconnect(sid)

    async def on_pop(self, sid, data):
        print("pop", sid)
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await game.pop(sid)

    async def cleaner(self):
        while True:
            await asyncio.sleep(1)

            for id in list(Game.games.keys()):
                if id not in Game.games:
                    continue

                for player in Game.games[id].players:
                    if not player.has_time():
                        await Game.sio.emit("timeout", {}, room=player.sid)
                        await Game.games[id].disconnect(player.sid)


async def cleaner():
    while True:
        await asyncio.sleep(1)

        for id in list(Game.games.keys()):
            if id not in Game.games:
                continue

            for player in Game.games[id].players:
                if not player.has_time():
                    await Game.sio.emit("timeout", {}, room=player.sid)
                    await Game.games[id].disconnect(player.sid)

async def main():
    env = os.environ.get("ENV", "development")
    if env == "development":
        from dotenv import load_dotenv
        env_file = f".env.{env}"
        load_dotenv(dotenv_path=env_file)

    global sio
    sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
    app = aiohttp.web.Application()
    sio.attach(app)

    handler = GameHandler(sio)
    Game.sio = sio
    
    # Aggiorna le chiamate a handler
    sio.on('connect', handler.on_connect)
    sio.on('disconnect', handler.on_disconnect)
    sio.on('start', handler.on_start)
    sio.on('move', handler.on_move)
    sio.on('resign', handler.on_resign)
    sio.on('pop', handler.on_pop)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    port = os.environ.get("PORT", 8080)
    ssl_context = None
    if os.environ.get("ENV") == "production":
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile="/run/secrets/certificate.crt", keyfile="/run/secrets/private.key")
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", port, ssl_context=ssl_context)

    await site.start()
    print(f"Listening on 0.0.0.0:{port}")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
