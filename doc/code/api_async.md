# Async

(docs co-authored by copilot)  

## Eventi
- Tutti gli eventi sono universali, e valgono siano per multiplayer e singleplayer:
  - `pop`
  - `move`
  - `connect`
  - `disconnect`
  - `start`

## Analisi di eventi e le differenze tra PVP e PVE con esempi di corpo del json (salvare il campo id e poi inviare nei json per fare le operazioni di pop, disconnect, resign, move)

## Start Request (frontend event: start)

This event is triggered when a player wants to start a new game. The request body should contain the following fields:  
- `rank`: The player's rank. This should be an integer between `MIN_RANK` and `MAX_RANK`. Only for modes `PVE`, `PVP`.  
- `time`: The amount of time for the game. This should be an integer between `MIN_TIME` and `MAX_TIME`.  
- `depth`: (Only for PVE games) The difficulty level of the bot. This should be an integer between `MIN_DEPTH` and `MAX_DEPTH`.  
- `type`: The type of game. `0` for PVP (Player versus Player), `1` for PVE (Player versus Environment), `2` for Ranked (PvE).  
- `mode`: (Optional) The game mode. Can be either "ranked" or "reallyBadChess". If omitted, defaults to "reallyBadChess".  

Example of a PVP start request:

```json
{
  "rank": 70,
  "time": 300,
  "type": 0,
  "mode": "ranked"
}
```

Example of a PVE start request:

```json
{
  "rank": 70,
  "time": 300,
  "depth": 1,
  "type": 1,
  "mode": "reallyBadChess"
}
```

## Start Response (frontend event: config)

The server responds with a `config` event. The response contains the initial game configuration.  
- `fen`: The initial position of the game in Forsyth-Edwards Notation (FEN).  
- `id`: (Only for PVP games) The game ID.  
- `rank`: the player's rank (in the game mode for which a request was made)  

Example of a PVP start response:

```json
{
  "fen": 'nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1',
  "id": "aaaaaaaaaaaaaaaa",
}
```

Example of a PVE start response:
```json
{
  "fen": 'nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1',
}
```

Example of a Ranked start response:
```json
{
  "fen": 'nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1',
  "rank": 10,
}
```

If there's an error (e.g., missing fields, invalid values, the SID is already in use, or an invalid game mode is specified), the server responds with an `error` event. The response contains a `cause` field with a description of the error and a `fatal` field indicating whether the error is fatal. If `fatal` is `True`, the client should not attempt to recover from the error.

## Move request (frontend event: move)
```json
//move pvp
{
  "san": "e4",
  "id":  "aaaaaaaaaaaaaaa",
  "type": 0
}
//move pve
{
  "san": "e4",
  "type": 1
}
```
## Move response (frontend event: move, end)
```json
// risposta (se un altro giocatore ha mandato la richiesta con lo stesso tempo e rank complementario)
//pvp no outcome 'move'
{
  "san": "e4",
  "id": "aaaaaaaaaaaaaaaa"
}
//pvp with outcome 'end'
{
  "winner": true
}
//pve no outcome 'move'
{
  "san": "e4",
}
//pve with outcome 'end'
{
  "winner": true
}
```
## Disconnect request (frontend event: disconnect)
```json
// risposta (se un altro giocatore ha mandato la richiesta con lo stesso tempo e rank complementario)
//pvp no outcome 'disconnecte'
{
  "id": "aaaaaaaaaaaaaaaa"
}
//pve 
{
}
```
## Disconnect response (frontend event: disconnected)
```json
{
}
```
## Pop request (frontend event: disconnected)
```json
//pvp
{
  "type": 0,
  "id": "aaaaaaaaaaa"
}
//pve
{
  "type":1
}
```
## Pop response (frontend event: move)
```json
//pvp
{
}

//pve
{
}
```