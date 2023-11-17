import ImageScacchi from "../assets/logo.png";
import { Image, Row, Col, Card, Modal, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import { Chessboard } from "react-chessboard";
import { useEffect, useState } from "react";
import Board from "./Board.jsx";
import {createTheme,ThemeProvider} from '@mui/material/styles';
import { Button  } from "@mui/material";
import {Gear, Clock, ExclamationDiamond} from 'react-bootstrap-icons';
import "./Game.css";
import io from 'socket.io-client';
import useWindowDimensions from "./useWindowDimensions.jsx";

function Game (props) {

    const { width } = useWindowDimensions();

    const [moves, setMoves] = useState(["5a", "2b", "7f", "8g","5a", "2b", "7f", "8g","5a", "2b", "7f", "8g","5a", "2b", "7f", "8g",]);
    const [botMessages, setBotMessages] = useState(["ciao", "pippo", "pluto", "paperino","ciao", "pippo", "pluto", "paperino","ciao", "pippo", "pluto", "paperino",]);

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



    //inizio
    class EventType {
        static ERROR = new EventType(-1);
        static RESIGN = new EventType(0);
        static MOVE = new EventType(1);
        static POP = new EventType(2);
        static ACK = new EventType(3);
        static CONFIG = new EventType(4);
        static END = new EventType(5);
        static START = new EventType(999);
        #val

        constructor(val) {
            this.#val = val;
        }

        get value() {
            return this.#val;
        }

        toString() {
            return this.#val;
        }
    }


    const [timer, setTimer] = useState(props.gameTime || 1);
    const [timerId, setTimerId] = useState(null);

    const startTimer = () => {
        const newTimerId = setInterval(() => {
          setTimer((prevTime) => prevTime - 1);
        }, 1000);
        setTimerId(newTimerId);
      };

    const stopTimer = () => {
        clearInterval(timerId);
        setTimerId(null);
    };

    const resumeTimer = () => {
        if (timerId === null) {
          startTimer();
        }
      };

    useEffect(() => {

        startTimer();
    
        return () => clearInterval(timerId);
      }, []);

    useEffect(()=>{
        if(timer === 1){
            setShowGameOver(true);
            stopTimer();
            setTimer (0);
        }
    },[timer])

   

    const handleMessage = (msg) => {
        switch (msg.data) {
            case EventType.MOVE.value:
            handleMove();
            break;
          case EventType.POP.value:
            handlePop();
            break;
          case EventType.ACK.value:
            handleAck();
            break;
          case EventType.CONFIG.value:
            handleConfig();
            break;
          case EventType.END.value:
            handleEnd();
            break;
          default:
            handleError();
            break;
        }
   }

    function handlePop() {
        /* Pops twice */
        console.log("sono pop")
    }

     function handleAck() {
     /* ... */
        console.log("sono ack")
     }

    function handleConfig() {
    /* ... */
       console.log("sono config")
    }

    function handleEnd() {
    /* ... */
       console.log("sono end")
    }

    function handleError() {
    /* ... */
       console.log("sono error")
    }

    function handleMove(){
        console.log("sono move")
    }


  

    
    function handleMenu(){
        props.setSocket(undefined);
        props.socket.emit("resign", {});
    }

    function handleUndo (){
        props.socket.emit("pop", {});
    }

    return (
        <>

            <Modal  show={showGameOver} centered dialogClassName="my-modal">
                <div style={{border: "4px solid red"}}>
                    <Modal.Body style={{backgroundColor: "#b6884e"}}>
                        <div style={{display: "flex", justifyContent: "center", fontSize: "1.7rem"}}>
                            <span style={{fontWeight: "bold", marginRight: "10px"}}>Game Over</span>
                            <ExclamationDiamond size={40} color="red" />
                        </div>
                        { timer <=0 &&
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
                </div>
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
                                <Button style={{fontSize: "1.2rem"}} size="large" color="brown" onClick={(e)=>{ e.stopPropagation(); handleMenu();}}  variant="contained">Yes</Button>
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
                <Row >
                    <Col xs={3} sm={3} lg={3}>
                        <Card style={{marginLeft: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: "3rem"}}>Storico Mosse</p>
                            </Card.Title>
                            <Card.Body style={{overflow: "auto", height: `calc(${width}px / 4)`, marginLeft: "20px", marginBottom: "20px"}}>
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
                    <Col xs={6} sm={6} lg={6}>
                        <div style={{marginLeft: "5vw", marginRight: "5vw"}}>
                            <div style={{marginBottom: "30px", display: "flex", justifyContent: "center"}}>
                                <Clock size={30}/>
                                <p style={{marginLeft: "10px"}}>{timer}</p>
                            </div>
                            <div style={{display: "flex", justifyContent: "center"}}>
                            <Board isLoadingGame={props.isLoadingGame} setIsLoadingGame={props.setIsLoadingGame} width={width} socket={props.socket}/>
                            </div>
                            <div style={{display: "flex", justifyContent: "center", paddingTop: "30px"}}>
                                <Button color="brown"   style={{fontSize: "1.5rem"}} onClick={handleUndo}  variant="contained" >Undo</Button>
                            </div>
                        </div>
                        
                        
                    </Col>
                    <Col xs={3} sm={3} lg={3}>
                        <Card style={{marginRight: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: "3rem"}}>Chat</p>
                            </Card.Title>
                            <Card.Body style={{overflow: "auto", height: `calc(${width}px / 4)`, marginLeft: "20px", marginBottom: "20px"}}>
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