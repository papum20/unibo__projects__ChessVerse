#!/usr/bin/env python

import asyncio
import threading
import os
import json
import chess
import chess.engine
import websockets
from aiohttp import web
from time import perf_counter

from PVEGame import PVEGame

websocket_dict = {}

async def handle_connect(websocket, _path=None):
	sid = id(websocket)
	print("connect ", sid)
	# Store the websocket instance in a global variable or an appropriate data structure
	websocket_dict[sid] = websocket

async def handle_disconnect(websocket, _path):
	sid = id(websocket)
	print("disconnect ", sid)

async def handle_start(websocket, data):
	sid = id(websocket)
	def check_int(key, min, max):
		return key in data and isinstance(data[key], int) and min <= data[key] <= max
	print("start ", sid, data)
	if "rank" not in data or "depth" not in data or "time" not in data:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Missing fields", "fatal": True}}))
		return
	if not check_int("rank", 0, 100):
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Invalid rank", "fatal": True}}))
		return
	if not check_int("depth", 1, 20):
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Invalid bot strength", "fatal": True}}))
		return
	if not check_int("time", 1, 3000):
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Invalid clocktime", "fatal": True}}))
		return
	pveGames[sid] = PVEGame(sid, data["rank"], data["depth"], data["time"])
	await pveGames[sid].initialize_bot()
	await websocket.send(json.dumps({"event": "config", "data": {"fen": pveGames[sid].fen}}))

async def handle_move(websocket, data):
	sid = id(websocket)
	print("move ", sid, data)
	if sid not in pveGames:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Game not found", "fatal": True}}))
		return
	game = pveGames[sid]
	if "san" not in data:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Missing fields"}}))
		return
	if not game.current.has_time():
		return
	try:
		uci_move = game.board.parse_san(data["san"]).uci()
	except (chess.InvalidMoveError, chess.IllegalMoveError):
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Invalid move"}}))
		return
	if chess.Move.from_uci(uci_move) not in game.board.legal_moves:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Invalid move"}}))
		return
	game.board.push_uci(uci_move)
	outcome = game.board.outcome()
	if outcome is not None:
		await websocket.send(json.dumps({"event": "end", "data": {"winner": outcome.winner}}))
		return
	start = perf_counter()
	bot_move = (await game.bot.play(game.board, chess.engine.Limit(time=game.time))).move
	game.board.push_uci(bot_move.uci())
	outcome = game.board.outcome()
	latest_move = game.board.pop()
	san_bot_move = game.board.san(bot_move)
	game.board.push(latest_move)
	if outcome is not None:
		print(outcome)
		await websocket.send(json.dumps({"event": "move", "data": {"san": san_bot_move}}))
		await websocket.send(json.dumps({"event": "end", "data": {"winner": outcome.winner}}))
		return
	game.popped = False
	end = perf_counter()
	game.current.add_time(end - start)
	game.current.first_move = False
	await websocket.send(json.dumps({"event": "move", "data": {"san": san_bot_move}}))

async def handle_resign(websocket, _data):
	sid = id(websocket)
	print("resign", sid)
	if sid not in pveGames:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Game not found", "fatal": True}}))
		return

async def handle_pop(websocket, _data):
	sid = id(websocket)
	print("pop", sid)
	if sid not in pveGames:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "Game not found", "fatal": True}}))
		return
	game = pveGames[sid]
	if game.popped:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "You have already popped"}}))
	elif game.board.fullmove_number == 1:
		await websocket.send(json.dumps({"event": "error", "data": {"cause": "No moves to undo"}}))
	else:
		game.board.pop()
		game.board.pop()
		await websocket.send(json.dumps({"event": "pop", "data": {}}))
		game.popped = True

pveGames = {}

async def cleaner(websocket_dict):
	while True:
		await asyncio.sleep(1)

		for sid, websocket in websocket_dict.items():
			for player in pveGames[sid].players:
				if not player.has_time():
					print("gotcha ", sid)
					await websocket.send(json.dumps({"event": "timeout", "data": {}}))
					await handle_disconnect(websocket, None)

async def main():
	app = web.Application()
	app.add_routes([web.get('/ws/{_path}', handle_connect),
					web.post('/ws/{_path}', handle_connect)])
	
	loop = asyncio.get_running_loop()
	loop.create_task(cleaner(websocket_dict))

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT")))
	await site.start()
	print(f"listening on 0.0.0.0:{os.environ.get('PORT')}")

	while True:
		await asyncio.sleep(1)

if __name__ == "__main__":
	asyncio.run(main())
