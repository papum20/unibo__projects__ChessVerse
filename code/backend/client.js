import { Chess, BLACK, WHITE } from 'chess.js'

let board = null
const game = new Chess()
const whiteSquareGrey = '#a9a9a9'
const blackSquareGrey = '#696969'

function removeGreySquares () {
  $('#myBoard .square-55d63').css('background', '')
}

function greySquare (square) {
  const $square = $('#myBoard .square-' + square)

  let background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }

  $square.css('background', background)
}

function onDragStart (source, piece) {
  // do not pick up pieces if the game is over
  if (game.isGameOver()) return false

  // or if it's not that side's turn
  if ((game.turn() === WHITE && piece.search(/^b/) !== -1) ||
      (game.turn() === BLACK && piece.search(/^w/) !== -1)) {
    return false
  }
}

function onDrop (source, target) {
  removeGreySquares()

  // see if the move is legal
  const lastMove = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (lastMove === null) return 'snapback'
  else move(lastMove.after)
}

function onMouseoverSquare (square, piece) {
  // get list of possible moves for this square
  const moves = game.moves({
    square: square,
    verbose: true
  })

  // exit if there are no moves available for this square
  if (moves.length === 0) return

  // highlight the square they moused over
  greySquare(square)

  // highlight the possible squares for this piece
  for (let i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
}

function onMouseoutSquare (square, piece) {
  removeGreySquares()
}

function onSnapEnd () {
  board.position(game.fen())
}

const config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare,
  onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)


// codice riguardante al websocket

const ACKType = {
    OK : 0,
    NOK : 1,
    UNKNOWN_ACTION : 2,
    WRONG_CONFIG : 3,
    NOT_IMPLEMENTED : 4,
    GAME_NOT_FOUND : 5,
    WRONG_TURN : 6
};

const EventType = {
    ERROR : -1,
    RESIGN : 0,
    MOVE : 1,
    POP : 2,
    ACK : 3,
    CONFIG : 4,
    END : 5,
    SELECT: 6,
    START : 999,
};


let ws;
let lastMove;
let color;
let ready = true; //questa variabile serve per non mandare troppe richieste al server
//viene settato a false non appena si manda una richiesta e false quando si riceve una risposta

const startGame = (typeOfGame, depth, rank) => {
    ws = new WebSocket('ws://localhost:8766');
    const msg = {
        event : EventType.START,
        data : {
            type : typeOfGame,
            depth : Math.max(Math.min(depth, 20), 1),
            rank : Math.max(Math.min(rank, 100), 0)
        },
    };

    ws.onopen = (event) => {
        ws.send(JSON.stringify(msg));
    };
}

const move = (mv) => {
    const uci = mv;
    lastMove = uci;
    ws.send(JSON.stringify({
        event: EventType.MOVE,
        data: {
            value: uci
        }
    }));
    ready = false;
}


const resign = () => {
    ws.send(JSON.stringify({
        event: EventType.RESIGN,
        data: {
            id: gameId,
            type: gameType
        }
    }));
    ready = false;
}


const pop = () => {
    ws.send(JSON.stringify({
        event: EventType.POP,
        data: {
            id: gameId,
            type: gameType
        }
    }));
    ready = false;
}

const handleConfig = (msg) => {
    //inizializzare chessboard con fen, color ricevuti, salvando gameId e gameType
    const fen = msg.data.fen;
    const color = msg.data.color;
    const gameId = msg.data.id;
    config.position = fen;
}

const handleMove = (msg) => {
    const opponentMove = msg.data.value;
    ready = true;
    game.move(opponentMove) // chess.js
    board.move(opponentMove) // chessboard.js
}

const handlePop = (msg) => {
    //fai due pop delle ultime due mosse memorizzate sia su board che su chess.js
    ready = true;
}

const handleEnd = (msg) => {
    //mostrare l'interfaccia del risultato del gioco
    ws.close();
}


const handleError = (msg) => {
    //mostrare l'errore
    ws.close();
}

const handleACK = (msg) => {
    if(msg.data.value !== ACKType.OK){
        //operazione rifiutata, si puo' fare altra mossa
        ready = true;
    }
    else if(lastMove.event === EventType.MOVE){
        //fai push in chess.js e metti la mossa sulla board grafica
    }
    else if(lastMove.event === EventType.POP){
        //fai due pop in chess.js e togli due mosse dalla board grafica

    }
    else{
        //errore
        ws.close();
    }
}

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    switch (msg.type) {
        case EventType.MOVE:
            handleMove(msg);
            break;
        case EventType.POP:
            handlePop(msg);
            break;
        case EventType.ACK:
            handleACK(msg);
            break;
        case EventType.CONFIG:
            handleConfig(msg);
            break;
        case EventType.END:
            handleEnd(msg);
            break;
        case EventType.ERROR:
            handleError(msg);
            break;
        default:
            ws.close()
            break;
    }
}
