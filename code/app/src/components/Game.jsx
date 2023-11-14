import ImageScacchi from "../assets/logo.png";
import { Image, Row, Col, Card, Modal, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import { Chessboard } from "react-chessboard";
import { useEffect, useState } from "react";
import { Chess } from 'chess.js';
import {createTheme,ThemeProvider} from '@mui/material/styles';
import { Button  } from "@mui/material";
import {Gear, Clock, ExclamationDiamond} from 'react-bootstrap-icons';
import "./Game.css";


function Game (props) {

    const [moves, setMoves] = useState(["5a", "2b", "7f", "8g","5a", "2b", "7f", "8g","5a", "2b", "7f", "8g","5a", "2b", "7f", "8g",]);
    const [botMessages, setBotMessages] = useState(["ciao", "pippo", "pluto", "paperino","ciao", "pippo", "pluto", "paperino","ciao", "pippo", "pluto", "paperino",]);

    const [game, setGame] = useState(new Chess());

    function makeAMove(move) {
        const gameCopy = { ...game };
        const result = gameCopy.move(move);
        setGame(gameCopy);
        return result; // null if the move was illegal, the move object if the move was legal
      }

      function makeRandomMove() {
        const possibleMoves = game.moves();
        if (game.game_over() || game.in_draw() || possibleMoves.length === 0)
          return; // exit if the game is over
        const randomIndex = Math.floor(Math.random() * possibleMoves.length);
        makeAMove(possibleMoves[randomIndex]);
      }

      function onDrop(sourceSquare, targetSquare) {
        const move = makeAMove({
          from: sourceSquare,
          to: targetSquare,
          promotion: "q", // always promote to a queen for example simplicity
        });
    
        // illegal move
        if (move === null) return false;
        setTimeout(makeRandomMove, 200);
        return true;
      }

      const theme = createTheme({
        palette: {
          brown: {
            main: '#795548',
            light: '#543b32',
            dark: '#543b32',
            contrastText: '#fff',
          },
        },
      });

    const [showModalMenu, setShowModalMenu] = useState(false);
    const [showGameOver, setShowGameOver] = useState(false);

    const [time, setTime] = useState(props.gameTime || 1);

    useEffect(() => {
        const timerInterval = setInterval(() => {
          setTime((prevTime) => prevTime - 1);
        }, 1000);
    
        return () => clearInterval(timerInterval);
      }, []);

    useEffect(()=>{
        if(time <= 0){
            setShowGameOver(true);
        }
    },[time])

    return (
        <>

            <Modal show={showGameOver} centered dialogClassName="my-modal">
                <Modal.Body style={{backgroundColor: "#b6884e"}}>
                    <div style={{display: "flex", justifyContent: "center", fontSize: "1.7rem"}}>
                        <span style={{fontWeight: "bold", marginRight: "10px"}}>Game Over</span>
                        <ExclamationDiamond size={40} color="red" />
                    </div>
                    { time <=0 &&
                            <div style={{display: "flex", justifyContent: "center", fontSize: "1.3rem", marginTop: "20px"}}>
                                <p>The time has run out</p>
                            </div>
                        }
                    
                    <div style={{display: "flex", justifyContent: "space-around", marginTop: "20px", marginBottom: "15px"}}>
                        <ThemeProvider theme={theme}>
                            <Nav.Link as={Link} to="/" style={{display: "flex", justifyContent: "center"}}>
                                <Button style={{fontSize: "1.2rem"}} size="large" color="brown"  variant="contained">Return to the menu</Button>
                            </Nav.Link>
                        </ThemeProvider>
                    </div>
                </Modal.Body>
            </Modal>

            <Modal show={showModalMenu} centered dialogClassName="my-modal">
                <Modal.Body style={{backgroundColor: "#b6884e", fontSize: "1.5rem"}}>
                    <div style={{display: "flex", justifyContent: "center"}}>
                        <p>Are you sure you want to go back</p>
                    </div>
                    <div style={{display: "flex", justifyContent: "center"}}>
                        <p>to the main menu?</p>
                    </div>
                    <div style={{display: "flex", justifyContent: "space-around", marginTop: "20px", marginBottom: "15px"}}>
                        <ThemeProvider theme={theme}>
                            <Button style={{fontSize: "1.2rem"}} size="large" color="brown" onClick={()=>setShowModalMenu(false)} variant="contained">No</Button>
                            <Nav.Link as={Link} to="/">
                                <Button style={{fontSize: "1.2rem"}} size="large" color="brown"  variant="contained">Yes</Button>
                            </Nav.Link>
                        </ThemeProvider>
                    </div>
                </Modal.Body>
            </Modal>

            <div style={{backgroundColor: "#b99b69", width: "100vw", height: "100vh"}}>
                <ThemeProvider theme={theme}>
                <div style={{paddingTop: "10px", paddingLeft: "10px"}}>
                    <Row>
                        <Col>
                            <Image src={`${ImageScacchi}`} style={{width: "50px", height: "50px", opacity: 0.8, marginTop: "-30px"}} alt="immagine di scacchi" />
                            <span style={{color: "white", fontSize: "2.5rem"}}>ChessVerse</span>
                        </Col>
                        <Col style={{display: "flex", justifyContent: "flex-end", marginRight: "40px"}}>
                            <Button  color="brown" onClick={()=>setShowModalMenu(true)}   style={{fontSize: "1.5rem"}}  variant="contained" ><Gear  size={30} /></Button>
                        </Col>
                    </Row>
                    
                </div>
                <Row style={{marginTop: "5vh"}}>
                    <Col xs={3}>
                        <Card style={{marginLeft: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: "3rem"}}>Storico Mosse</p>
                            </Card.Title>
                            <Card.Body style={{overflow: "auto", height: "500px", marginLeft: "20px", marginBottom: "20px"}}>
                                {moves.map((el,i) => 
                                    <Card style={{marginTop: "10px", marginBottom: "10px", backgroundColor: "#9f7a48"}} key={i}>
                                        <Card.Body>
                                            <p>{el}</p>
                                        </Card.Body>
                                    </Card>
                                )
                                }
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col xs={6}>
                        <div style={{marginLeft: "5vw", marginRight: "5vw"}}>
                            <div style={{marginBottom: "30px", display: "flex", justifyContent: "center"}}>
                                <Clock size={30}/>
                                <p style={{marginLeft: "10px"}}>{time}</p>
                            </div>
                            <Chessboard id="BasicBoard" position={game.fen()} onPieceDrop={onDrop} />
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "20px"}}>
                            <Button color="brown"   style={{fontSize: "1.5rem"}}  variant="contained" >Undo</Button>
                        </div>
                        
                    </Col>
                    <Col xs={3}>
                        <Card style={{marginRight: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: "3rem"}}>Chat</p>
                            </Card.Title>
                            <Card.Body style={{overflow: "auto", height: "500px", marginLeft: "20px", marginBottom: "20px"}}>
                                {botMessages.map((el,i) => 
                                    <Card style={{marginTop: "10px", marginBottom: "10px", backgroundColor: "#9f7a48"}} key={i}>
                                        <Card.Body>
                                            <p>{el}</p>
                                        </Card.Body>
                                    </Card>
                                )
                                }
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
                </ThemeProvider>
            </div>
        </>
    )
}

export default Game;