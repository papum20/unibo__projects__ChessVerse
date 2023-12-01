## Eventi
- Tutti gli eventi sono universali, e valgono siano per multiplayer e singleplayer:
  - `pop`
  - `move`
  - `connect`
  - `disconnect`
  - `start`

## Analisi di eventi e le differenze tra PVP e PVE con esempi di corpo del json (salvare il campo id e poi inviare nei json per fare le operazioni di pop, disconnect, resign, move)

## Start request (frontend event: start)
```json
//start pvp
{
  "rank": 70,
  "time": 300,
  "type": 0
}
//start pve
{
  "rank": 70,
  "time": 300,
  "depth": 1,
  "type": 1
}
```
## Start response (frontend event: config)
```json
// risposta (se un altro giocatore ha mandato la richiesta con lo stesso tempo e rank complementario)
//pvp
{
  "fen": 'nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1',
  "id": "aaaaaaaaaaaaaaaa"
}
//pve
{
  "fen": 'nrk4n/ppp1pppp/8/8/8/1q1bb2r/3K4/8 w - - 0 1'
}
```
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