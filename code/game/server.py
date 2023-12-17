#!/usr/bin/env python
import random
import asyncio
import os
import aiohttp
from PVEGame import PVEGame
from PVPGame import PVPGame
from Game import Game
from GameRanked import GameRanked
from const import GameType
from time import perf_counter
import ssl
import mysql.connector
import schedule
import time
import datetime
from ranks import dailyRank, weeklyRank

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

    async def on_connect(self, sid, environ):
        #print("connect", sid)
        await Game.sio.emit("connected", room=sid)

    async def on_disconnect(self, sid):
        print("disconnect", sid)
        if sid in Game.sid_to_id:
            game_id = Game.sid_to_id[sid]
            if isinstance(game_id, dict):
                Game.waiting_list[game_id["time"]][game_id["index"]] = [
                    waiting
                    for waiting in Game.waiting_list[game_id["time"]][game_id["index"]]
                    if waiting["sid"] != sid
                ]
                del Game.sid_to_id[sid]
            else:
                if game_id in Game.games:
                    await Game.games[game_id].disconnect(sid)
    
    def daily_seed():
        # Otteniamo la data corrente
        today = datetime.date.today()
        # Estraiamo anno, mese e giorno
        year = today.year
        month = today.month
        day = today.day
        # Combiniamo anno, mese e giorno per creare il seed
        seed = year * 10000 + month * 100 + day
        return seed
    
    def weekly_seed():
        # Otteniamo la data corrente
        today = datetime.date.today()
        # Otteniamo il numero della settimana e l'anno
        week_number = today.isocalendar()[1]
        year = today.year
        # Combiniamo anno e numero della settimana per creare il seed
        seed = year * 100 + week_number
        return seed

    async def on_start(self, sid, data): 
        daily_seed = GameHandler.daily_seed()
        weekly_seed = GameHandler.weekly_seed()
        print("start", data["type"])
        if "session_id" in data.keys():
            await Game.login(data["session_id"], sid)
        if "type" not in data.keys():
            await Game.sio.emit(
                "error", {"cause": "Invalid type", "fatal": True}, room=sid
            )
        elif data["type"] == GameType.PVE:
            await PVEGame.start(sid, data)
        elif data["type"] == GameType.PVP:
            await PVPGame.start(sid, data)
        #add new GameTypes Daily and Wekkly challenges
        elif data["type"] == GameType.DAILY:
            await PVEGame.start(sid, data, seed = daily_seed, type = GameType.DAILY)
        elif data["type"] == GameType.WEEKLY:
            await PVEGame.start(sid, data, seed = weekly_seed, type = GameType.WEEKLY)
        elif data["type"] == GameType.RANKED:
            await GameRanked.start(sid, data)
        #add new GameTypes Daily and Wekkly challenges
        else:
            await Game.sio.emit(
                "error", {"cause": "Invalid type", "fatal": True}, room=sid
            )

    async def on_move(self, sid, data):
        print("move", sid)
        if "type" not in data.keys():
            await Game.sio.emit(
                "error", {"cause": "Invalid type", "fatal": True}, room=sid
            )
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit(
                "error", {"cause": "Game not found", "fatal": True}, room=sid
            )
            return
        await game.move(sid, data)

    async def on_resign(self, sid, data):
        print("resign", sid)
        await self.on_disconnect(sid)

    async def on_pop(self, sid, data):
        print("pop", sid)
        if "type" not in data.keys():
            await Game.sio.emit(
                "error", {"cause": "Invalid type", "fatal": True}, room=sid
            )
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.sio.emit(
                "error", {"cause": "Game not found", "fatal": True}, room=sid
            )
            return
        await game.pop(sid)

    async def cleaner(self):
        while True:
            await asyncio.sleep(1)
            for id in list(Game.games.keys()):
                if id not in Game.games:
                    continue
                for player in Game.games[id].players:
                    if player.is_timed:
                        player_time = player.remaining_time - (
                            perf_counter() - player.latest_timestamp
                        )
                        if player_time <= 0:
                            await Game.sio.emit("timeout", {}, room=player.sid)
                            if type(Game.games[id]).__name__ == "PVPGame":
                                await Game.games[id].disconnect(player.sid, False)
                            else:
                                await Game.games[id].disconnect(player.sid)

async def main():
    env = os.environ.get("ENV", "development")
    if env == "development":
        from dotenv import load_dotenv
        env_file = f".env.{env}"
        load_dotenv(dotenv_path=env_file)

    global sio
    sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
    app = aiohttp.web.Application()
    sio.attach(app)

    conn = mysql.connector.connect(
        host=os.environ.get("DATABASE_HOST"),
        user=os.environ.get("DATABASE_USER"),
        password=os.environ.get("DATABASE_PASSWORD"),
        database=os.environ.get("DATABASE_NAME"),
        port=os.environ.get("DATABASE_PORT"),
    )
    cursor = conn.cursor()

    handler = GameHandler()
    Game.sio = sio
    Game.conn = conn

    # Aggiorna le chiamate a handler
    sio.on("connect", handler.on_connect)
    sio.on("disconnect", handler.on_disconnect)
    sio.on("start", handler.on_start)
    sio.on("move", handler.on_move)
    sio.on("resign", handler.on_resign)
    sio.on("pop", handler.on_pop)

    
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    port = os.environ.get("PORT", 8080)
    ssl_context = None
    if os.environ.get("ENV") == "production":
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile="/run/secrets/game_cert",
            keyfile="/run/secrets/game_priv",
        )
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", port, ssl_context=ssl_context)

    await site.start()
    print(f"Listening on 0.0.0.0:{port}")
    asyncio.create_task(handler.cleaner())

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())