import { useState, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import Spinner from 'react-bootstrap/Spinner';
import { toast } from "react-toastify";
import {PVE, PVP} from "../const/const.js";


function Board(props) {
  const [game, setGame] = useState(null);
  const [moveSan, setMoveSan] = useState(null);
  const [moveFrom, setMoveFrom] = useState("");
  const [moveTo, setMoveTo] = useState(null);
  const [showPromotionDialog, setShowPromotionDialog] = useState(false);
  const [moveSquares] = useState({});
  const [optionSquares, setOptionSquares] = useState({});
  const [oppMoveSan, setOppMoveSan] = useState("");
  const [awaitingOppMove, setAwaitingOppMove] = useState(false);
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
    const makeOppMove = async () => {
      if (oppMoveSan) {
        const updatedGame = new Chess();
        updatedGame.load(game.fen()); // Carica la posizione attuale della scacchiera

        const move = updatedGame.move(oppMoveSan);
        if (move) {
          // Ritarda l'esecuzione per un breve periodo per visualizzare l'animazione
          await new Promise(resolve => setTimeout(resolve, 300));

          safeGameMutate((game) => {
            game.move(move.san, { sloppy: true });
          });

          setOppMoveSan(null);
        }
      }
    };

    makeOppMove();
  }, [oppMoveSan]);

  async function onSquareClick(square) {
    if (awaitingOppMove) return;
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
    if(props.startFen){
      const newGame = new Chess();
          newGame.load(props.startFen);
          setGame(newGame);
    }
  },[props.startFen])

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
      /*
      if(props.mode===PVE || props.color==="white")
        props.startWhite;
      else
        props.startBlack;
*/
      props.socket.emit("move", {san: moveSan, type: props.mode, id: props.roomId});
      props.stopTimer();
      setMoveSan(null);
      setAwaitingOppMove(true);
    }
  },[moveSan])

const [getPop, setGetPop] = useState(false);

  useEffect(()=>{
    props.socket?.on("move", (res) =>{
      setOppMoveSan(res.san);
      setAwaitingOppMove(false);
      props.startTimer();
/*
      if(props.color==="white")
        props.startBlack;
      else
        props.startWhite;
*/

      //props.setWhiteTimer(res.time[0]);
      //props.setBlackTimer(res.time[1] ?? -1);
      //props.setTurn(0);
     // props.setTimerOn(true);
      console.log("prendo la mossa e setto il timer ON")
    });
    props.socket?.on("end", (res) =>{
      if (res.winner)
        props.setVictory(true);
      else
        props.setShowGameOver(true);
      props.socket.disconnect();
      // TODO 
      // else if (winner.winner === false){
      //   props.setShowGameOver(true);
      // }
      // else {
      //   props.setShowTie(true);
      // }
    
    })

    props.socket?.on("timeout", (_data) =>{
        props.setShowGameOver(true);
    })
    
    props.socket?.on("pop", () => {
      setGetPop(prevValue => !prevValue);
    })
    props.socket?.on("error", (error) =>{
      toast.error(error.cause, {className: "toast-message"});
      if(error.fatal){
        props.setSocket(undefined);
        props.socket?.off("pop");
        props.socket?.off("timeout");
        props.socket?.off("move");
        props.socket?.off("end");
        props.socket?.off("config");
        props.navigator(`../`, { relative: "path" });
      }
    })
  },[])

  useEffect(()=>{
      if(!!game){
        game.undo();
        game.undo();
        setPosition(game.fen());
        setMoveSan(null);
        setOppMoveSan(null);
       
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
    <>
      {props.mode===PVP ?
        <div data-testid="Loading">

          <div style={{display: "flex", justifyContent: "center", marginTop: "10vh"}} >
            <h1 style={{fontWeight:"bold", marginBottom: "20px"}}>waiting for a player</h1>
          </div>

          <div style={{display: "flex", justifyContent: "center", marginTop: "10px"}}>
            <Spinner  animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        
        </div>
        
        
    :
      <div data-testid="Loading">
        <div style={{display: "flex", justifyContent: "center", marginTop: "10vh"}} >
          <Spinner  animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      </div>
    }

    </>
    
    
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
        boardOrientation={props.mode===PVE ? "white" : props.color}
      />
    </div>
  }
    </>
  );
}

export default Board;
