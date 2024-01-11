#!/usr/bin/env python
import asyncio
import os
import socketio
import aiohttp
from PVEGame import PVEGame
from PVPGame import PVPGame
from Game import Game
from const import GameType
from time import perf_counter
import chess
import datetime

errors = {"invalid_type": "Invalid type", "game_not_found": "Game not found"}


class GameHandler:
    @classmethod
    def sid2game(cls, sid):
        if isinstance(Game.sid_to_id[sid], str):
            try:
                return Game.games[Game.sid_to_id[sid]]
            except KeyError:
                return None
        return None

    async def on_connect(self, sid, _):
        print("connect", sid)
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

    @classmethod
    def daily_seed(cls):
        today = datetime.date.today()
        year = today.year
        month = today.month
        day = today.day
        seed = year * 10000 + month * 100 + day
        return seed

    @classmethod
    def weekly_seed(cls):
        # Otteniamo la data corrente
        today = datetime.date.today()
        # Otteniamo il numero della settimana e l'anno
        week_number = today.isocalendar()[1]
        year = today.year
        # Combiniamo anno e numero della settimana per creare il seed
        seed = year * 100 + week_number
        return seed

    async def on_start(self, sid, data):
        print("start", sid, data)
        if "session_id" in data.keys():
            await Game.login(data["session_id"], sid)
        if "type" not in data.keys() or data["type"] not in GameType:
            await Game.emit_error(errors["invalid_type"], sid)
        elif data["type"] == GameType.PVE:
            await PVEGame.start(sid, data)
        elif data["type"] == GameType.PVP:
            await PVPGame.start(sid, data)
        elif data["type"] == GameType.DAILY:
            await PVEGame.start(sid, data, seed=GameHandler.daily_seed(), type=GameType.DAILY)
        elif data["type"] == GameType.WEEKLY:
            await PVEGame.start(sid, data, seed=GameHandler.weekly_seed(), type=GameType.WEEKLY)
        elif data["type"] == GameType.RANKED:
            await PVEGame.start(sid, data, seed=None, type=GameType.RANKED)

    async def on_move(self, sid, data):
        print("move", sid)
        if "type" not in data.keys():
            await Game.emit_error(errors["invalid_type"], sid)
            return
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.emit_error(errors["game_not_found"], sid)
            return
        await game.move(sid, data)

    async def on_resign(self, sid, _):
        print("resign", sid)
        await self.on_disconnect(sid)

    async def on_pop(self, sid, data):
        print("pop", sid)
        if "type" not in data.keys():
            await Game.emit_error(errors["invalid_type"], sid)
            return
        game = GameHandler.sid2game(sid)
        if game is None:
            await Game.emit_error(errors["game_not_found"], sid)
            return
        await game.pop(sid)

    async def cleaner(self):
        while True:
            await asyncio.sleep(1)
            await self.update_games()

    async def update_games(self):
        for id in list(Game.games.keys()):
            if id not in Game.games:
                continue
            await self.update_current_player(Game.games[id])

    async def update_current_player(self, game):
        if game.current.is_timed:
            if type(game).__name__ == "PVPGame":
                await self.check_player(game.next, game)
            await self.check_player(game.current, game)

    async def check_player(self, player, game):
        player_time = self.calculate_remaining_time(player, player == game.current)
        print(player_time)
        if player_time <= 0:
            await self.handle_timeout(player, game)

    def calculate_remaining_time(self, player, current_turn):
        if current_turn:
            return player.remaining_time - (perf_counter() - player.latest_timestamp)
        else:
            return player.remaining_time

    async def handle_timeout(self, player, game):
        outcome = None
        if game.board.has_insufficient_material(not player.color):
            outcome = chess.Outcome(termination=chess.Termination(3), winner=None)
            await Game.sio.emit("end", {"winner": None}, room=player.sid)
        else:
            await Game.sio.emit("timeout", {}, room=player.sid)
        if type(game).__name__ == "PVPGame":
            await game.disconnect(player.sid, False, outcome)
        else:
            await game.disconnect(player.sid, outcome)


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

    handler = GameHandler()
    Game.sio = sio

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
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", port)

    await site.start()
    print(f"Listening on 0.0.0.0:{port}")
    asyncio.create_task(handler.cleaner())

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
