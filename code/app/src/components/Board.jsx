import { useState, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import Spinner from 'react-bootstrap/Spinner';
import { toast } from "react-toastify";


function Board(props) {
  const [game, setGame] = useState(null);
  const [moveSan, setMoveSan] = useState(null);
  const [moveFrom, setMoveFrom] = useState("");
  const [moveTo, setMoveTo] = useState(null);
  const [showPromotionDialog, setShowPromotionDialog] = useState(false);
  const [moveSquares] = useState({});
  const [optionSquares, setOptionSquares] = useState({});
  const [botMoveSan, setBotMoveSan] = useState("");
  const [awaitingBotMove, setAwaitingBotMove] = useState(false);
  const [firstMove, setFirstMove] = useState(true);
  const [position, setPosition] = useState("");
  
  function safeGameMutate(modify) {
    setGame((g) => {
      const update = { ...g };
      modify(update);
      return update;
    });
  }

  function getMoveOptions(square) {
    const moves = game.moves({
      square,
      verbose: true,
    });
    if (moves.length === 0) {
      setOptionSquares({});
      return false;
    }

    const newSquares = {};
    moves.map((move) => {
      newSquares[move.to] = {
        background:
          game.get(move.to) &&
          game.get(move.to).color !== game.get(square).color
            ? "radial-gradient(circle, rgba(0,0,0,.1) 85%, transparent 85%)"
            : "radial-gradient(circle, rgba(0,0,0,.1) 25%, transparent 25%)",
        borderRadius: "50%",
      };
      return move;
    });
    newSquares[square] = {
      background: "rgba(255, 255, 0, 0.4)",
    };
    setOptionSquares(newSquares);
    return true;
  }

  
  useEffect(() => {
    const makeBotMove = async () => {
      if (botMoveSan) {
        const updatedGame = new Chess();
        updatedGame.load(game.fen()); // Carica la posizione attuale della scacchiera

        const move = updatedGame.move(botMoveSan);
        if (move) {
          // Ritarda l'esecuzione per un breve periodo per visualizzare l'animazione
          await new Promise(resolve => setTimeout(resolve, 300));

          safeGameMutate((game) => {
            game.move(move.san, { sloppy: true });
          });

          setBotMoveSan(null);
        }
      }
    };

    makeBotMove();
  }, [botMoveSan]);

  async function onSquareClick(square) {
    if (awaitingBotMove) return;
    // from square
    if (!moveFrom) {
      const hasMoveOptions = getMoveOptions(square);
      if (hasMoveOptions) setMoveFrom(square);
      return;
    }

    // to square
    if (!moveTo) {
      // check if valid move before showing dialog
      const moves = game.moves({
        square: moveFrom,
        verbose: true,
      });
      const foundMove = moves.find(
        (m) => m.from === moveFrom && m.to === square
      );
      // not a valid move
      if (!foundMove) {
        // check if clicked on new piece
        const hasMoveOptions = getMoveOptions(square);
        // if new piece, setMoveFrom, otherwise clear moveFrom
        setMoveFrom(hasMoveOptions ? square : "");
        return;
      }

      // valid move
      setMoveTo(square);

      // if promotion move
      if (
        (foundMove.color === "w" &&
          foundMove.piece === "p" &&
          square[1] === "8") ||
        (foundMove.color === "b" &&
          foundMove.piece === "p" &&
          square[1] === "1")
      ) {
        setShowPromotionDialog(true);
        return;
      }
      
      // is normal move
      const gameCopy = { ...game };
      // const gameCopy = async;
      const move = gameCopy.move({
        from: moveFrom,
        to: square,
        promotion: "q",
      });
      setMoveSan(move.san);

      // if invalid, setMoveFrom and getMoveOptions
      if (move === null) {
        const hasMoveOptions = getMoveOptions(square);
        if (hasMoveOptions) setMoveFrom(square);
        return;
      }
      setGame(gameCopy);

      resetMove();
    }
  }

  async function onPromotionPieceSelect(piece) {
    // if no piece passed then user has cancelled dialog, don't make move and reset
    if (piece) {
      const gameCopy = { ...game };
      const move = gameCopy.move({
        from: moveFrom,
        to: moveTo,
        promotion: piece[1].toLowerCase() ?? "q",
      });
      setMoveSan(move.san);
      setGame(gameCopy);
    }

    setShowPromotionDialog(false);
    resetMove();
    return true;
  }

  function resetMove() {
    setMoveFrom("");
    setMoveTo(null);
    setOptionSquares({});
  }
  
  

  useEffect(()=>{
    let failedCnt = 0;
    if(props.socket){
      props.socket?.on("config", async (data) => {
        if (!data && failedCnt > 6){
          props.setSocket(undefined);
          toast.error("comunicazione col server fallita", {className: "toast-message"});
        }
        else if (!data){
          failedCnt++; 
          await new Promise((resolve) => setTimeout(resolve, 300));
          props.socket?.emit("start", props.data);
        } 
        else {
          const newGame = new Chess();
          newGame.load(data.fen);
          setGame(newGame);
          failedCnt = 0;
        }
        
      })
    }
  },[props.socket])

  useEffect(()=>{

    async function wait (){
      await new Promise((resolve) => setTimeout(resolve, 600));
      props.setIsLoadingGame(false);

    } 
    if(!!game){
      wait();
    }
    

  },[game])

  useEffect(()=>{
    if(!!moveSan){
      if(firstMove){
        setFirstMove(false);
        props.startTimer();
      }
      props.socket.emit("move", {san: moveSan});
      setMoveSan(null);
      setAwaitingBotMove(true);
    }
  },[moveSan])

const [getPop, setGetPop] = useState(false);

useEffect(() => {
	if (props.socket) {
	  props.socket.addEventListener('message', (event) => {
		const message = JSON.parse(event.data);
		if (message.type === 'move') {
		  setBotMoveSan(message.data.san);
		  setAwaitingBotMove(false);
		} else if (message.type === 'end') {
		  if (message.data.winner)
			props.setVictory(true);
		  else
			props.setShowGameOver(true);
		} else if (message.type === 'timeout') {
		  props.setShowGameOver(true);
		} else if (message.type === 'pop') {
		  setGetPop(prevValue => !prevValue);
		} else if (message.type === 'error') {
		  toast.error(message.data.cause, {className: "toast-message"});
		  if(message.data.fatal){
			props.setSocket(undefined);
			props.navigator(`../`, { relative: "path" });
		  }
		}
	  });
  
	  return () => {
		props.socket.removeEventListener('message');
	  };
	}
  }, []);

  useEffect(()=>{
      if(!!game){
        game.undo();
        game.undo();
        setPosition(game.fen());
        setMoveSan(null);
        setBotMoveSan(null);
       
      }
      
  },[getPop])


  useEffect(()=>{
    if(game){
      props.setMoves(game.history());
    }
  },[game, getPop])


  useEffect(()=>{
    if (game){
      setPosition(game.fen());
    }
  },[game])

  return (
    <>
    {props.isLoadingGame ? 
    <div style={{display: "flex", justifyContent: "center", marginTop: "10vh"}} data-testid="Loading">
      <Spinner  animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
    
  : 
    <div data-testid="chessboard">
      <Chessboard 
        id="ClickToMove"
        animationDuration={300}
        arePiecesDraggable={false}
        position={position}
        onSquareClick={async (square)=>await onSquareClick(square)}
        onPromotionPieceSelect={async (piece) => await onPromotionPieceSelect(piece)}
        customBoardStyle={{
          borderRadius: "4px",
          boxShadow: "0 2px 10px rgba(0, 0, 0, 0.5)",
        }}
        customSquareStyles={{
          ...moveSquares,
          ...optionSquares,
        }}
        promotionToSquare={moveTo}
        showPromotionDialog={showPromotionDialog}
        boardWidth={`${props.width/2 >(props.height-180) ? (props.height-180) : (props.width/2)}`}
      />
    </div>
  }
    </>
  );
}

export default Board;
