#!/usr/bin/env python
import asyncio
import os
import socketio
import aiohttp
<<<<<<< HEAD
from PVEGame import PVEGame
from PVPGame import PVPGame
from Game import Game
from const import GameType
import ssl
import mysql.connector
=======
from time import perf_counter
import chess
import chess.engine
from PVEGame import PVEGame
from const import MIN_RANK, MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME, TIME_OPTIONS


class PVEGameHandler:
    def __init__(self):
        self.pveGames = {}
        thread = threading.Thread(target=self.cleaner_thread)
        thread.start()
>>>>>>> dev-login

active_clients = {}

<<<<<<< HEAD

class GameHandler:
    def __init__(self):
        pass
    @classmethod
    def sid2game(cls, sid):
        if isinstance(Game.sid_to_id[sid], str):
            try:
                return Game.games[Game.sid_to_id[sid]]
            except KeyError:
                return None
        return None

    async def on_connect(self, sid, environ, auth):
        # cookie_header = environ.get('HTTP_COOKIE', '')
        # session_id = None
        #
        # for cookie in cookie_header.split(';'):
        #     key, value = map(str.strip, cookie.split('=', 1))
        #     if key == 'sessionId':
        #         session_id = value
        await Game.login(sid)
        await Game.sio.emit("connected", room=sid)
=======
    async def on_connect(self, sid, _):
        print("connect ", sid)
        await sio.emit("connected", room=sid)
>>>>>>> dev-login

    async def on_disconnect(self, sid):
        if sid in Game.sid_to_id:
            game_id = Game.sid_to_id[sid]
            if isinstance(game_id, dict):
                Game.waiting_list[game_id["time"]][game_id["index"]] = [waiting for waiting in Game.waiting_list[game_id["time"]][game_id["index"]] if waiting["sid"] != sid]
                del Game.sid_to_id[sid]
            else:
                if game_id in Game.games:
                    await Game.games[game_id].disconnect(sid)

    async def on_start(self, sid, data):
        if("type" not in data.keys()):
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif data["type"] == GameType.PVE:
            await PVEGame.start(sid, data)
        elif data["type"] == GameType.PVP:
            await PVPGame.start(sid, data)
        else:
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_move(self, sid, data):
        if "type" not in data.keys():
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await game.move(sid, data)

    async def on_resign(self, sid, data):
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await game.disconnect(sid)

    async def on_pop(self, sid, data):
        if "type" not in data.keys():
            await Game.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
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
                        await self.on_disconnect(player.sid)



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

<<<<<<< HEAD
    conn = mysql.connector.connect(
        host=os.environ.get("DATABASE_HOST"),
        user=os.environ.get("DATABASE_USER"),
        password=os.environ.get("DATABASE_PASSWORD"),
        database=os.environ.get("DATABASE_NAME"),
        port=3306
    )
    cursor = conn.cursor()

    handler = GameHandler()
    Game.sio = sio
    Game.cursor = cursor
    Game.conn = conn
=======
    handler = PVEGameHandler()
>>>>>>> dev-login
    
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
        ssl_context.load_cert_chain(certfile="/run/secrets/ssl_certificate.crt", keyfile="/run/secrets/ssl_priv_key.key")
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", port, ssl_context=ssl_context)

    await site.start()
    print(f"Listening on 0.0.0.0:{port}")

    cleaner_task = asyncio.create_task(handler.cleaner())

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())