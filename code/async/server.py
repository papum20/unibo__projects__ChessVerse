#!/usr/bin/env python
import asyncio
import os
import ssl
import threading
import socketio
import aiohttp
from time import perf_counter
import chess
import chess.engine
from PVEGame import PVEGame
from PVPGame import PVPGame
from Player import Player
import random
from const import MIN_RANK, MAX_RANK, MIN_DEPTH, MAX_DEPTH, MIN_TIME, MAX_TIME, TIME_OPTIONS, GameType
active_clients = []
class GameHandler:
    def __init__(self, sio):
        self.sio = sio
        self.pve_handler = PVEGameHandler(sio)
        self.pvp_handler = PVPGameHandler(sio)

    async def on_connect(self, sid):
        print("connect ", sid)
        await self.sio.emit("connected", room=sid)

    async def on_disconnect(self, sid, data):
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await self.pve_handler.on_disconnect(sid)
        elif("id" in data and data["type"] == GameType.PVP):
            await self.pvp_handler.on_disconnect(sid, data["id"])
        else:
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_start(self, sid, data):
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await self.pve_handler.on_start(sid, data)
        elif(data["type"] == GameType.PVP):
            await self.pvp_handler.on_start(sid, data)
        else:
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_move(self, sid, data):
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await self.pve_handler.on_move(sid, data)
        elif(data["type"] == GameType.PVP):
            await self.pvp_handler.on_move(sid, data)
        else:
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_resign(self, sid, data):
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await self.pve_handler.on_resign(sid, data)
        elif(data["type"] == GameType.PVP):
            await self.pvp_handler.on_resign(sid, data)
        else:
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

    async def on_pop(self, sid, data):
        if("type" not in data.keys()):
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)
        elif(data["type"] == GameType.PVE):
            await self.pve_handler.on_pop(sid, data)
        elif(data["type"] == GameType.PVP):
            await self.pvp_handler.on_pop(sid, data)
        else:
            await self.sio.emit("error", {"cause": "Invalid type", "fatal": True}, room=sid)

class PVPGameHandler:
    def __init__(self, sio):
        self.pvpGames = {}
        self.connected_clients = {key: [[] for _ in range(5)] for key in TIME_OPTIONS}
        self.sio = sio
        """
        array con 5 indici, che rappresentano le code dei ranks complementari, 10-90, 20-80, 30-70, 40-60, 50-50
        in un certo istante di tempo sara' uno tra i due stati complementari rappresentati, (implementato automaticamente
        la coda con priorita' (gli elementi piu' vecchi sono in fondo alla lista), e implementato il meccanismo della ricerca
        quando il timer scatta, e.g. vado a cercare gli elementi agli indici successivi

        priorita' dei match:
        1) quelli che hanno passato piu' del tempo massimo di attesa -> cercare quelli piu' compatibili
        2) quelli piu' compatibili
        """
        thread = threading.Thread(target=self.cleaner_thread)
        thread.start()

    async def game_found(self, sid, id):
        if id not in self.pvpGames:
            await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True

    async def on_disconnect(self, sid, id):
        print("disconnect", sid, id)
        if id in self.pvpGames:
            active_clients.remove(self.pvpGames[id].players[0].sid)
            active_clients.remove(self.pvpGames[id].players[1].sid)
            self.sio.emit("disconnected", room=[player.sid for player in self.pvpGames[id].players])
            del self.pvpGames[id]

    async def on_start(self, sid, data):
        def check_int(key, min, max):
            try:
                v = int(data[key])
                return min <= v <= max
            except (ValueError, TypeError):
                return False

        def check_options(key, options):
            try:
                value = int(data[key])
                return value in options
            except (ValueError, TypeError, KeyError):
                return False

        # Check for data validity
        if "rank" not in data or "time" not in data:
            await self.sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
            return
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await self.sio.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_options("time", TIME_OPTIONS):
            await self.sio.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return

        # se non loggato, se loggato devo pure vedere il database
        time = data["time"]
        rank = round(max(min(int(data["rank"]), 100), 0)/10)*10
        # vedere se ci sta il complementare
        index = (10 - (rank // 10)) % 6 if rank // 10 > 5 else (rank // 10) % 6
        if sid in active_clients:
            await self.sio.emit("error", {"cause": "Started Matching", "fatal": True}, room=sid)
        elif (len(self.connected_clients[time][index]) > 0 and self.connected_clients[time][index][0]["rank"] == 100-rank):
            first = random.randint(0, 1)
            players = (
                [sid, self.connected_clients[time][index].pop(0)["sid"]]
                if first
                else [self.connected_clients[time][index].pop(0)["sid"], sid]
            )
            game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
            self.pvpGames[game_id] = PVPGame(players, rank if first else 100-rank, data["time"])
            active_clients.append(sid)
            await self.sio.emit("config", {"fen": self.pvpGames[game_id].fen, "id": game_id}, room=players)
        else:
            self.connected_clients[time][index].append({"sid": sid, "rank": rank})
            active_clients.append(sid)


    async def on_move(self, sid, data):
        print("move", sid, data)
        if not await self.game_found(sid, data["id"]):
            return
        id = data["id"]
        game = self.pvpGames[id]
        if "san" not in data:
            await self.sio.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if data["san"] is None:
            await self.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
            return
        if not game.is_player_turn(sid):
            await self.sio.emit("error", {"cause": "It's not your turn"}, room=sid)
            return
        if not game.current.has_time():
            await self.sio.emit("error", {"cause": "Timeout"}, room=sid)
            return
        try:
            uci_move = game.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await self.sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
            await self.sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        uci_move = game.board.parse_uci(game.board.parse_san(data["san"]).uci())
        san_move = game.board.san(uci_move)
        game.board.push_uci(uci_move.uci())
        outcome = game.board.outcome()
        print(game.board.outcome)
        if outcome is not None:
            await self.sio.emit("move", {"san": san_move}, room=game.current.sid)
            await self.sio.emit("end", {"winner": outcome.winner}, room=[player.sid for player in game.players])
            await self.on_disconnect(sid, id)
            return
        game.popped = False
        game.current.first_move = False
        game.swap()
        await self.sio.emit("move", {"san": san_move}, room=game.current.sid)


    async def on_resign(self, sid, data):
        print("resign", sid)
        if "id" not in data.keys():
            await self.sio.emit("error", {"cause": "Missing id", "fatal": True}, room=sid)
        elif not await self.game_found(sid, data["id"]):
            return
        else:
            id = data["id"]
            await self.sio.emit("end", {"winner": self.pvpGames[id].opponent(sid).color}, room=[player.sid for player in self.pvpGames[id].players])
            await self.on_disconnect(sid, id)


    async def on_pop(self, sid, data):
        print("pop", sid)
        if "id" not in data.keys():
            await self.sio.emit("error", {"cause": "Missing id", "fatal": True}, room=sid)
        id = data["id"]
        if not await self.game_found(sid, data["id"]):
            return
        game = self.pvpGames[id]
        if game.popped:
            await self.sio.emit("error", {"cause": "You have already popped"}, room=sid)
        elif game.board.fullmove_number == 1:
            await self.sio.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            game.board.pop()
            game.board.pop()
            await self.sio.emit("pop", {}, room=[player.sid for player in game.players])
            game.popped = True


    def cleaner_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def cleaner():
            while True:
                await asyncio.sleep(1)

                for id in list(self.pvpGames.keys()):
                    if id not in self.pvpGames:
                        continue

                    for player in self.pvpGames[id].players:
                        if not player.has_time():
                            print("gotcha ", player.sid)
                            await self.sio.emit("timeout", {}, room=player.sid)
                            await self.on_disconnect(player.sid, id)

        loop.run_until_complete(cleaner())

class PVEGameHandler:
    def __init__(self, sio):
        self.pveGames = {}
        self.sio = sio
        thread = threading.Thread(target=self.cleaner_thread)
        thread.start()

    async def game_found(self, sid):
        if sid not in self.pveGames:
            await self.sio.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True

    async def on_connect(self, sid, _):
        print("connect ", sid)
        await self.sio.emit("connected", room=sid)

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
        if sid in self.pveGames.keys():
            await self.pveGames[sid].bot.quit()
            del self.pveGames[sid]
            active_clients.remove(sid)
            await self.sio.emit("disconnected", room=sid)

    async def on_start(self, sid, data):
        def check_int(key, min, max):
            try:
                v = int(data[key])
                return min <= v <= max
            except (ValueError, TypeError):
                return False
        # Check for data validity
        if "rank" not in data or "depth" not in data or "time" not in data:
            await self.sio.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
            return
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await self.sio.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_int("depth", MIN_DEPTH, MAX_DEPTH):
            await self.sio.emit("error", {"cause": "Invalid bot strength", "fatal": True}, room=sid)
            return
        if not check_int("time", MIN_TIME, MAX_TIME):
            await self.sio.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return
        if sid not in active_clients:
            self.pveGames[sid] = PVEGame(sid, int(data["rank"]), int(data["depth"]), int(data["time"]))
            active_clients.append(sid)
            await self.pveGames[sid].initialize_bot()
            await self.sio.emit("config", {"fen": self.pveGames[sid].fen}, room=sid)
        else:
            await self.sio.emit("error", {"cause": "Started Matching", "fatal": True}, room=sid)

    async def on_move(self, sid, data):
        print("move", sid, data)
        if not await self.game_found(sid):
            return
        game = self.pveGames[sid]

        if "san" not in data:
            await self.sio.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if data["san"] is None:
            await self.sio.emit("error", {"cause": "Encountered None value"}, room=sid)
            return
        if not game.current.has_time():
            return
        try:
            uci_move = game.board.parse_san(data["san"]).uci()
        except (chess.InvalidMoveError, chess.IllegalMoveError):
            await self.sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
            await self.sio.emit("error", {"cause": "Invalid move"}, room=sid)
            return
        game.board.push_uci(uci_move)
        outcome = game.board.outcome()
        if outcome is not None:
            await self.sio.emit("end", {"winner": outcome.winner}, room=sid)
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
            await self.sio.emit("move", {"san": san_bot_move}, room=sid)
            await self.sio.emit("end", {"winner": outcome.winner}, room=sid)
            await self.on_disconnect(sid)
            return
        game.popped = False
        end = perf_counter()
        game.current.add_time(end - start)
        game.current.first_move = False
        await self.sio.emit("move", {"san": san_bot_move}, room=sid)

    async def on_resign(self, sid, _):
        print("resign", sid)
        if not await self.game_found(sid):
            return
        await self.on_disconnect(sid)

    async def on_pop(self, sid, _):
        print("pop", sid)
        if not await self.game_found(sid):
            return
        game = self.pveGames[sid]
        if game.popped:
            await self.sio.emit("error", {"cause": "You have already popped"}, room=sid)
        elif game.board.fullmove_number == 1:
            await self.sio.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            game.board.pop()
            game.board.pop()
            await self.sio.emit("pop", {}, room=sid)
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
                            await self.sio.emit("timeout", {}, room=sid)
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

    handler = GameHandler(sio)
    
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
