import ImageScacchi from "../assets/logo.png";
import { Image, Row, Col, Card, Modal, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useRef, useEffect, useState, useLayoutEffect } from "react";
import Board from "./Board.jsx";
import { createTheme,ThemeProvider } from '@mui/material/styles';
import { Button  } from "@mui/material";
import {Gear, Clock, ExclamationDiamond} from 'react-bootstrap-icons';
import "../styles/Game.css";
import useWindowDimensions from "./useWindowDimensions.jsx";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import {PVE} from "../const/Const.js";
import ImageBlackTime from "../assets/blackTime.png";
import ImageWhiteTime from "../assets/whiteTime.png";
//import { useTimer } from 'react-timer-hook';

function Game({
                  gameTime,
                  isLoadingGame, setIsLoadingGame,
                  socket, setSocket,
                  data,
                  mode,
                  startFen,
                  color,
                  roomId
              })
{
    const { width, height } = useWindowDimensions();
    const [fontSize, setFontSize] = useState("20px");

    useLayoutEffect(()=>{
        if(width < 440)
            setFontSize("18px");
        else if((width > 440) && (width < 540))
            setFontSize("22px");
        else
            setFontSize("26px");
    },[width]);

    const navigator = useNavigate();
    const [moves, setMoves] = useState([]);
    const [botMessages, setBotMessages] = useState(["ciao", "pippo", "pluto", "paperino", "ciao", "peppecasa", "pippo", "pluto", "paperino", "ciao", "pippo", "pluto", "paperino"]);
    const [showModalMenu, setShowModalMenu] = useState(false);
    const [showGameOver, setShowGameOver] = useState(false);
    const [showVictory, setVictory] = useState(false);
    const movesRef = useRef(null);

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
/*
    const expiryTimestamp = new Date();
    expiryTimestamp.setSeconds(expiryTimestamp.getSeconds() + (gameTime || 1));
    const {
        totalSecondsWhite,
        startWhite,
        pauseWhite,
      } = useTimer({expiryTimestamp, onExpire: () =>  pauseBlack});
    
      const {
        totalSecondsBlack,
        startBlack,
        pauseBlack,
      } = useTimer({expiryTimestamp, onExpire: () =>  pauseWhite});
    
      useEffect(()=>{console.log(totalSecondsWhite)},[totalSecondsWhite])


    const [blackTimer, setBlackTimer] = useState(gameTime || 1);
    const [whiteTimer, setWhiteTimer] = useState(gameTime || 1);

    const [timerOn, setTimerOn] = useState(false);
    const [turn, setTurn] = useState(0);
    */
    /*
        swapTurn:
            1) da al giocatore quanto e' passato dall'ultimo decremento
            2) cambia indice del turno
            3) fa partire il timer del nuovo turno
            ogni volta che questo timer scade (1000ms ma si possono anche fare 100 e far vedere i decimi di secondo) decrementa il timer del turno corrente

    ogni 1000ms decrementi quello il timer del turno corrente
    e quando cambi turno fai stop e resume cosi

    */
/*
    const [startTimer, setStartTimer] = useState(false);

    useEffect(()=>{
        if(!startTimer)
            setStartTimer(!startTimer)

    },[timerOn])

    useEffect(()=>{
        (() => {
            // if (timerOn){
                if(turn===0) setWhiteTimer(prevValue => prevValue - 0.1)
                else setBlackTimer(prevValue => prevValue - 0.1)
            // }
        }, 100);

    },[startTimer])


    useEffect(()=>{console.log("timerON ", timerOn)},[timerOn])


*/
    
const [timer, setTimer] = useState(gameTime || 1);
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
    if (timer === 0) {
        stopTimer();
    }
}, [timer])


    function handleMenu(){
        socket.emit("resign", {type: mode, id: roomId});
        setSocket(undefined);
    }

    function handleUndo (){
        socket.emit("pop", {type: mode, id: roomId});
    }

    useEffect(()=>{
        movesRef.current.scrollTo({
            top: movesRef.current.scrollHeight,
            behavior: "smooth",
        });
        
    },[moves]);

    //questo useEffect serve a fare in modo che se refreshi game ti fa tornare al menu
    useEffect(()=>{
        if (socket === undefined || socket === null) {
            navigator(`../`, { relative: "path" });
        }
    }, [socket])

    return (
        <div data-testid="game">
            <Modal
              show={showGameOver}
              centered
              dialogClassName="my-modal"
            >
                <div style={{border: "4px solid red"}}>
                    <Modal.Body style={{backgroundColor: "#b6884e"}}>
                        <div style={{display: "flex", justifyContent: "center", fontSize: `${fontSize}`}}>
                            <span style={{fontWeight: "bold", marginRight: "10px"}}>Game Over</span>
                            <ExclamationDiamond size={40} color="red" />
                        </div>
                        { /*
                        ((color === "white" && totalSecondsWhite <= 0) || (color === "black" && totalSecondsBlack <= 0)) &&
                          <div style={{
                              display: "flex",
                              justifyContent: "center",
                              fontSize: `${fontSize}`,
                              marginTop: "20px"
                          }}>
                              <p>The time has run out</p>
                          </div>
                        */}
                        {timer <= 0 &&
                          <div style={{
                              display: "flex",
                              justifyContent: "center",
                              fontSize: `${fontSize}`,
                              marginTop: "20px"
                          }}>
                              <p>The time has run out</p>
                          </div>
                        }

                        <div style={{display: "flex", justifyContent: "space-around", marginTop: "20px", marginBottom: "15px"}}>
                            <ThemeProvider theme={theme}>
                                <Nav.Link
                                  as={Link}
                                  to="/"
                                  style={{display: "flex", justifyContent: "center"}}
                                >
                                    <Button
                                      style={{fontSize: "1.2rem"}}
                                      size="large"
                                      color="brown"
                                      onClick={() => {socket.emit("resign", {type: mode, id: roomId}); 
                                                        setSocket(undefined);
                                                    }}
                                      variant="contained"
                                    >
                                        Return to menu
                                    </Button>
                                </Nav.Link>
                            </ThemeProvider>
                        </div>
                    </Modal.Body>
                </div>
            </Modal>

            <Modal
              show={showVictory}
              centered
              dialogClassName="my-modal"
            >
                <div style={{border: "4px solid green"}}>
                    <Modal.Body style={{backgroundColor: "#b6884e"}}>
                        <div style={{display: "flex", justifyContent: "center", fontSize: `${fontSize}`}}>
                            <span style={{fontWeight: "bold", marginRight: "10px"}}>You won!</span>
                            <ExclamationDiamond size={40} color="green" />
                        </div>
                        
                        <div style={{display: "flex", justifyContent: "space-around", marginTop: "20px", marginBottom: "15px"}}>
                            <ThemeProvider theme={theme}>
                                <Nav.Link
                                  as={Link}
                                  to="/"
                                  style={{display: "flex", justifyContent: "center"}}
                                >
                                    <Button
                                      style={{fontSize: "1.2rem"}}
                                      size="large"
                                      color="brown"
                                      onClick={() => {setSocket(undefined); }}
                                      variant="contained"
                                    >
                                        Return to menu
                                    </Button>
                                </Nav.Link>
                            </ThemeProvider>
                        </div>
                    </Modal.Body>
                </div>
            </Modal>

            <Modal
              show={showModalMenu}
              centered
              dialogClassName="my-modal"
            >
                <Modal.Body style={{backgroundColor: "#b6884e", fontSize: `${fontSize}`}}>
                    <div style={{display: "flex", justifyContent: "center"}}>
                        <p>Are you sure you want to go back</p>
                    </div>
                    <div style={{display: "flex", justifyContent: "center"}}>
                        <p>to the main menu?</p>
                    </div>
                    <div style={{display: "flex", justifyContent: "space-around", marginTop: "20px", marginBottom: "15px"}}>
                        <ThemeProvider theme={theme}>
                            <Button
                              style={{fontSize: "1.2rem"}}
                              size="large"
                              color="brown"
                              onClick={()=> setShowModalMenu(false)}
                              variant="contained"
                            >
                                No
                            </Button>
                            <Nav.Link as={Link} to="/">
                                <Button
                                  style={{fontSize: "1.2rem"}}
                                  size="large"
                                  color="brown"
                                  onClick={(e)=> {
                                      e.stopPropagation();
                                      handleMenu();
                                  }}
                                  variant="contained"
                                >
                                    Yes
                                </Button>
                            </Nav.Link>
                        </ThemeProvider>
                    </div>
                </Modal.Body>
            </Modal>

            <div style={{backgroundColor: "#b99b69", width: "100vw", height: "100vh", overflow: "auto", overflowX: "hidden"}}>
                <ThemeProvider theme={theme}>
                <div style={{paddingTop: "10px", paddingLeft: "10px"}}>
                    <Row>
                        <Col>
                            <Row style={{marginBottom: "20px"}}>
                                <Col style={{display:"flex", justifyContent:"flex-end"}}>
                                    <div style={{marginTop: "20px", display: "flex", justifyContent: "center"}}>
                                        <Clock size={30}/>
                                        <p style={{marginLeft: "10px"}}>{timer}</p>
                                    </div>
                                </Col>
                                    {/*
                                <Col style={{marginTop: "20px", display:"flex", justifyContent: `${mode === PVE ? "flex-end" : "space-around"}`, marginLeft: `${mode === PVE ? "0px" : "20px"}` }}>
                                    
                                        mode===PVE ?
                                            <div style={{ display: "flex", justifyContent: "center"}}>
                                                <Clock size={30}/>
                                                <p style={{marginLeft: "10px"}}>{Math.floor(totalSecondsWhite)}</p>  
                                            </div>
                                            :
                                            <>
                                                <div>
                                                    <Image src={`${ImageWhiteTime}`} alt="clock black" style={{maxWidth: "30px", marginTop: "-3px"}}/>
                                                    <span style={{marginLeft: "10px"}}>{Math.floor(totalSecondsWhite)}</span>  
                                                </div>
                                                <div>
                                                    <Image src={`${ImageBlackTime}`} alt="clock whithe" style={{maxWidth: "30px", marginTop: "-3px"}}/>
                                                    <span style={{marginLeft: "10px"}}>{Math.floor(totalSecondsBlack)}</span>  
                                                </div>
                                            </>
                                
                                </Col>*/}
                                <Col style={{display:"flex", justifyContent:"flex-end", marginRight: "-200px"}}>
                                    <Image src={`${ImageScacchi}`} style={{width: "50px", height: "50px", opacity: 0.8}} alt="immagine di scacchi" />
                                        <span style={{color: "white", fontSize: "2.7rem"}}>ChessVerse</span>
                                </Col>
                            </Row>
                        </Col>
                        <Col style={{display: "flex", justifyContent: "flex-end", marginRight: "40px"}}>
                            <Button
                              color="brown"
                              onClick={()=> setShowModalMenu(true)}
                              style={{fontSize: "1.5rem"}}
                              variant="contained"
                            >
                                <Gear size={30} />
                            </Button>
                        </Col>
                    </Row>
                </div>
                <Row>
                    <Col>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div>
                                <Board
                                  navigator={navigator}
                                  setVictory={setVictory}
                                  width={width}
                                  height={height}
                                  setShowGameOver={setShowGameOver}
                                  setMoves={setMoves}
                                  data={data}
                                  isLoadingGame={isLoadingGame}
                                  setIsLoadingGame={setIsLoadingGame}
                                  socket={socket}
                                  setSocket={setSocket}
                                  mode={mode}
                                  startFen={startFen}
                                  color={color}
                                 // startWhite={startWhite}
                                  //startBlack={startBlack}
                                  //pauseWhite={pauseWhite}
                                  //pauseBlack={pauseBlack}
                                  startTimer={startTimer}
                                  stopTimer={stopTimer}
                                  roomId={roomId}
                                />
                            </div>
                        </div>
                    </Col>
                    <Col style={{maxWidth:"50vw"}}>
                    <Row>
                    <Col>
                    <Card style={{marginLeft: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: `${fontSize}`, marginTop: "5px"}}>
                                    Moves History
                                </p>
                            </Card.Title>
                            <Card.Body ref={movesRef} style={{overflow: "auto", height: `calc(${height}px / 2)`, marginLeft: "20px", marginBottom: "20px", overflowY:"auto"}}>
                                <Row>
                                    <Col>
                                    {moves.map((el,i) => {
                                        if(i % 2 === 0) {
                                            return (
                                            <Card style={{marginBottom: "10px", backgroundColor: "#9f7a48", border: `3px solid white`, display: "flex", alignItems: "center" }} key={i}>
                                                <span style={{paddingTop: "5px", paddingBottom: "5px"}}>{el}</span>
                                            </Card>
                                            )
                                        }
                                    })}
                                    </Col>
                                    <Col>
                                    {moves.map((el,i) => {
                                        if(i % 2 === 1){
                                            return (
                                              <Card style={{
                                                  marginBottom: "10px",
                                                  backgroundColor: "#9f7a48",
                                                  border: `3px solid black`,
                                                  display: "flex",
                                                  alignItems: "center"
                                              }} key={i}
                                              >
                                                  <span style={{paddingTop: "5px", paddingBottom: "5px"}}>
                                                      {el}
                                                  </span>
                                              </Card>
                                            )
                                        }
                                    })}
                                    </Col>
                                </Row>
                                <Row>
                                    <div style={{paddingTop: "20px"}}>
                                        <Button disabled={moves.length === 0} color="brown" style={{width: "100%", fontSize: `${fontSize}`}} onClick={handleUndo}  variant="contained" >Undo</Button>
                                    </div>
                                </Row>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col>
                        <Card style={{marginRight: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: `${fontSize}`, marginTop: "5px"}}>
                                    Chat
                                </p>
                            </Card.Title>
                            <Card.Body style={{overflow: "auto", height: `calc(${height}px / 2)`, marginLeft: "20px", marginBottom: "20px", overflowY: "auto"}}>
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
                    </Col>
                </Row>
                </ThemeProvider>
            </div>
        </div>
    )
}

Game.propTypes = {
    gameTime: PropTypes.number,
    isLoadingGame: PropTypes.bool,
    setIsLoadingGame: PropTypes.func,
    socket: PropTypes.object,
    setSocket: PropTypes.func,
    mode: PropTypes.number,
    data: PropTypes.object,
    startFen: PropTypes.string,
    color: PropTypes.string,
    roomId: PropTypes.string
}

export default Game;