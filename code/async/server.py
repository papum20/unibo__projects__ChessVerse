#!/usr/bin/env python
import asyncio
import os
import threading
import socketio
import aiohttp
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

    async def game_found(self, sid):
        if sid not in self.pveGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True

    async def on_connect(self, sid, _):
        print("connect ", sid)
        await sio.emit("connected", room=sid)

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
        if sid in self.pveGames.keys():
            await self.pveGames[sid].bot.quit()
            del self.pveGames[sid]

    async def on_start(self, sid, data):
        def check_int(key, min, max):
            try:
                v = int(data[key])
                return min <= v <= max
            except (ValueError, TypeError):
                return False

        # Check for data validity
        if "rank" not in data or "depth" not in data or "time" not in data:
            await sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
            return
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await self.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_int("depth", MIN_DEPTH, MAX_DEPTH):
            await self.emit("error", {"cause": "Invalid bot strength", "fatal": True}, room=sid)
            return
        if not check_int("time", MIN_TIME, MAX_TIME):
            await self.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return

        self.pveGames[sid] = PVEGame(sid, data["rank"], data["depth"], data["time"])
        await self.pveGames[sid].initialize_bot()
        await sio.emit("config", {"fen": self.pveGames[sid].fen}, room=sid)

    async def on_move(self, sid, data):
        print("move ", sid, data)
        if sid not in self.pveGames:
            await sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        game = self.pveGames[sid]

        if "san" not in data:
            await sio.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if not game.current.has_time():
            return
        try:
            uci_move = game.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
            await sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        game.board.push_uci(uci_move)
        outcome = game.board.outcome()
        if outcome is not None:
            await sio.emit("end", {"winner": outcome.winner}, room=sid)
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
            await sio.emit("move", {"san": san_bot_move}, room=sid)
            await sio.emit("end", {"winner": outcome.winner}, room=sid)
            await self.on_disconnect(sid)
            return
        game.popped = False
        end = perf_counter()
        game.current.add_time(end - start)
        game.current.first_move = False
        await sio.emit("move", {"san": san_bot_move}, room=sid)

    async def on_resign(self, sid, _):
        print("resign", sid)
        if sid not in self.pveGames:
            await sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        await self.on_disconnect(sid)

    async def on_pop(self, sid, _):
        print("pop", sid)
        if sid not in self.pveGames:
            await sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return
        game = self.pveGames[sid]
        if game.popped:
            await sio.emit("error", {"cause": "You have already popped"}, room=sid)
        elif game.board.fullmove_number == 1:
            await sio.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            game.board.pop()
            game.board.pop()
            await sio.emit("pop", {}, room=sid)
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
                            await sio.emit("timeout", {}, room=sid)
                            await self.on_disconnect(sid)
                            await self.disconnect(sid)

        loop.run_until_complete(cleaner())



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

    handler = PVEGameHandler()
    
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
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", port)

    await site.start()
    print(f"Listening on 0.0.0.0:{port}")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
