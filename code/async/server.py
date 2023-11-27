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


class PVEGameNamespace(socketio.AsyncNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pveGames = {}
        thread = threading.Thread(target=self.cleaner_thread)
        thread.start()

    async def game_found(self, sid):
        if sid not in self.pveGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True

    async def on_connect(self, sid, _):
        await self.emit("connected", room=sid)
        print("connect ", sid)

    async def on_disconnect(self, sid):
        print("disconnect ", sid)
        if sid in self.pveGames.keys():
            await pveGames[sid].bot.quit()
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
            await self.emit("error", {"cause": "Missing fields", "fatal": True}, room=sid)
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
        await self.emit("config", {"fen": self.pveGames[sid].fen}, room=sid)

    async def on_move(self, sid, data):
        print("move ", sid, data)
        if not self.game_found(sid):
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
        if not self.game_found(sid):
            return
        await self.on_disconnect(sid)

    async def on_pop(self, sid, _):
        print("pop", sid)
        if not self.game_found(sid):
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


class PVPGameNamespace(socketio.AsyncNamespace):
    """
    problemi: dobbiamo tenere conto sia del rank dato che il tempo, si puo' fare un dizionario di dizionari, il rank sara' approssimato al decimo piu' vicino
    se ci sono due player che hanno aspettato un limite massimo di tempo, ma hanno impostato lo stesso tempo, sara' fatta una media dei 2 ranks e usata il tempo impostato, si puo' fare che ogni volta entra un utente, controllo il timestamp di quello che sta piu' in tempo in attesa, se hanno lo stesso rank, allora li metto insieme, se no ed e' passato piu' di tot minuti, faccio la media
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.MAX_WAITING_TIME = 60
        self.pvpGames = {}
        self.connected_clients = {key: [] for key in TIME_OPTIONS}
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

    # bisogna che ho l'id del gioco
    async def game_found(self, sid, data):
        if data["id"] not in self.pvpGames:
            await self.emit("error", {"cause": "Game not found", "fatal": True}, room=sid)
            return False
        return True

    async def on_connect(self, sid, _):
        await self.emit("connected", room=sid)
        print("connect ", sid)

    async def on_disconnect(self, data):
        id = data["id"]
        print("disconnect ",id)
        if id in self.pvpGames:
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
        if not check_int("rank", MIN_RANK, MAX_RANK):
            await self.emit("error", {"cause": "Invalid rank", "fatal": True}, room=sid)
            return
        if not check_options("time", TIME_OPTIONS):
            await self.emit("error", {"cause": "Invalid clocktime", "fatal": True}, room=sid)
            return
        # se non loggato, se loggato devo pure vedere il database
        time = data["time"]
        rank = round(max(min(int(data["rank"]), 100), 0)/10)*10
        index = (10 - (rank // 10)) % 6 if rank // 10 > 5 else (rank // 10) % 6
        if (len(self.connected_clients[time][index]) > 0 and self.connected_clients[time][index][0]["rank"] == 100-rank):
            first = random.randint(0, 1)
            players = (
                [sid, self.connected_clients[time][index].pop(0)["sid"]]
                if first
                else [self.connected_clients[time][index].pop(0)["sid"], sid]
            )
            game_id = "".join(random.choice("0123456789abcdef") for _ in range(16))
            self.pvpGames[game_id] = PVPGame(players, rank if first else 100-rank, data["time"])
            await self.emit("config", {"fen": self.pvpGames[game_id].fen, "id": game_id}, room=players)
        else:
            self.connected_clients[time][index].append({"sid": sid, "rank": rank})

    async def on_move(self, sid, data):
        print("move ", sid, data)
        if not self.game_found(sid, data):
            return
        id = data["id"]
        game = self.pvpGames[id]
        if "san" not in data:
            await self.emit("error", {"cause": "Missing fields"}, room=sid)
            return
        if not game.is_player.turn or not game.current.has_time():
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
            await self.emit("end", {"winner": outcome.winner}, room=[player.sid for player in game.players])
            await self.on_disconnect(id)
            return
        game.popped = False
        game.current.first_move = False
        game.swap()
        await self.emit("move", {"san": data["san"]}, room=game.opponent.sid)

    async def on_resign(self, sid, data):
        print("resign", sid)
        if not self.game_found(sid, data):
            return
        await self.on_disconnect(sid, data)

    async def on_pop(self, sid, data):
        print("pop", sid)
        id = data["id"]
        if not self.game_found(id):
            return
        game = self.pvpGames[id]
        if game.popped:
            await self.emit("error", {"cause": "You have already popped"}, room=sid)
        elif game.board.fullmove_number == 1:
            await self.emit("error", {"cause": "No moves to undo"}, room=sid)
        else:
            game.board.pop()
            game.board.pop()
            await self.emit("pop", {}, room=[player.sid for player in game.players])
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

                    for player in self.pveGames[sid].players:
                        if not player.has_time():
                            print("gotcha ", sid)
                            await self.emit("timeout", {}, room=sid)
                            await self.on_disconnect(sid)
                            await self.disconnect(sid)

        loop.run_until_complete(cleaner())

async def main():
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "development":
        from dotenv import load_dotenv
        env_file = f".env.{env}"
        load_dotenv(dotenv_path=env_file)
    sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
    app = aiohttp.web.Application()
    sio.attach(app)

    single_game_namespace = PVEGameNamespace(os.environ.get("WSS_NAMESPACE"))
    sio.register_namespace(single_game_namespace)

    multiplayer_game_namespace = PVPGameNamespace(os.environ.get("MULTIPLAYER_NAMESPACE"))
    sio.register_namespace(multiplayer_game_namespace)

    app.router.add_get(os.environ.get("WSS_NAMESPACE"), sio.handle_request)
    app.router.add_get(os.environ.get("MULTIPLAYER_NAMESPACE"), sio.handle_request)

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
