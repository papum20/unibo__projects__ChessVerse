import { useState, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import Spinner from 'react-bootstrap/Spinner';
import { toast } from "react-toastify";
import {PVE, PVP} from "../const/const.js";


function Board(props) {
 
  const [moveSan, setMoveSan] = useState(null);
  const [moveFrom, setMoveFrom] = useState("");
  const [moveTo, setMoveTo] = useState(null);
  const [showPromotionDialog, setShowPromotionDialog] = useState(false);
  const [moveSquares] = useState({});
  const [optionSquares, setOptionSquares] = useState({});
  const [oppMoveSan, setOppMoveSan] = useState("");
  const [awaitingOppMove, setAwaitingOppMove] = useState(false);
  const [position, setPosition] = useState("");

  
  function safeGameMutate(modify) {
    props.setGame((g) => {
      const update = { ...g };
      modify(update);
      return update;
    });
  }

  function getMoveOptions(square) {
    const moves = props.game.moves({
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
          props.game.get(move.to) &&
          props.game.get(move.to).color !== props.game.get(square).color
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
        updatedGame.load(props.game.fen()); // Carica la posizione attuale della scacchiera

        const move = updatedGame.move(oppMoveSan);
        if (move) {
          // Ritarda l'esecuzione per un breve periodo per visualizzare l'animazione
          await new Promise(resolve => setTimeout(resolve, 300));

          safeGameMutate((game) => {
            props.game.move(move.san, { sloppy: true });
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
      const moves = props.game.moves({
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
      const gameCopy = { ...props.game };
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
      props.setGame(gameCopy);

      resetMove();
    }
  }

  async function onPromotionPieceSelect(piece) {
    // if no piece passed then user has cancelled dialog, don't make move and reset
    if (piece) {
      const gameCopy = { ...props.game };
      const move = gameCopy.move({
        from: moveFrom,
        to: moveTo,
        promotion: piece[1].toLowerCase() ?? "q",
      });
      setMoveSan(move.san);
      props.setGame(gameCopy);
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
          props.setGame(newGame);
    }
  },[props.startFen])

  useEffect(()=>{
    async function wait (){
      await new Promise((resolve) => setTimeout(resolve, 600));
      props.setIsLoadingGame(false);
    } 
    if(!!props.game) wait(); 
  },[props.game]);

  useEffect(()=>{
    if (!moveSan) return;
    props.socket.emit("move", {san: moveSan, type: props.mode, id: props.roomId});
    props.setMoves(prevValue => [...prevValue, moveSan]);
    props.setTurn(prevValue => {return 1-prevValue;});
    setMoveSan(null);
    setAwaitingOppMove(true);
  },[moveSan]);

  const [getPop, setGetPop] = useState(false);

  useEffect(()=>{
    props.socket?.on("ack", (res) =>{
      props.updateTimers(res.time);
    });
    props.socket?.on("move", (res) =>{
      props.setMoves(prevValue => [...prevValue, res.san]);
      setOppMoveSan(res.san);
      setAwaitingOppMove(false);
      props.setTurn(prevValue => { return 1-prevValue;});
      props.updateTimers(res.time);
    });
    props.socket?.on("end", (res) =>{
      props.setShowEndGame(true);
      if (res.winner) props.setModalType("won");
      else if (res.winner === false) props.setModalType("gameover");
      else props.setModalType("tie");
      props.socket.disconnect();
    });

    props.socket?.on("timeout", (_data) =>{
        props.setShowEndGame(true);
        props.setModalType("gameover");
    });
    
    props.socket?.on("pop", () => {
      setGetPop(prevValue => !prevValue);
    });

    props.socket?.on("error", (error) =>{
      toast.error(error.cause, {className: "toast-message"});
      if(error.fatal){
        props.setSocket(null);
        props.socket?.off("pop");
        props.socket?.off("timeout");
        props.socket?.off("move");
        props.socket?.off("end");
        props.socket?.off("config");
        props.navigator(`../`, { relative: "path" });
      }
    })
  },[]);

  useEffect(()=>{
      if(!!props.game){
        props.game.undo();
        props.game.undo();
        setPosition(props.game.fen());
        setMoveSan(null);
        setOppMoveSan(null);
      }
  },[getPop]);




  useEffect(()=>{
    if (props.game){
      setPosition(props.game.fen());
      props.setTurn(0);
    }
  },[props.game]);

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
