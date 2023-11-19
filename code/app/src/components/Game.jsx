import ImageScacchi from "../assets/logo.png";
import { Image, Row, Col, Card, Modal, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useEffect, useState, useLayoutEffect } from "react";
import Board from "./Board.jsx";
import { createTheme,ThemeProvider } from '@mui/material/styles';
import { Button  } from "@mui/material";
import {Gear, Clock, ExclamationDiamond} from 'react-bootstrap-icons';
import "./Game.css";
import useWindowDimensions from "./useWindowDimensions.jsx";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";

function Game({
                  gameTime,
                  botDiff,
                  isLoadingGame, setIsLoadingGame,
                  socket, setSocket,
                  data,
                  gameImb,
                  isSinglePlayer
              })
{
    const { width } = useWindowDimensions();
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
        setSocket(undefined);
        socket.emit("resign", {});
    }

    function handleUndo (){
        socket.emit("pop", {});
    }

    //questo useEffect serve a fare in modo che se refreshi game ti fa tornare al menu
    useEffect(() => {
        if (socket === undefined) {
            navigator(`../`, {relative: "path"});
        }
    }, [socket])

    return (
        <>
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
                                      onClick={() => setSocket(undefined)}
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
                                      onClick={() => setSocket(undefined)}
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

            <div style={{backgroundColor: "#b99b69", width: "100vw", height: "100vh"}}>
                <ThemeProvider theme={theme}>
                <div style={{paddingTop: "10px", paddingLeft: "10px"}}>
                    <Row>
                        <Col>
                            <Image
                              src={`${ImageScacchi}`}
                              alt="immagine di scacchi"
                              style={{
                                  width: "50px",
                                  height: "50px",
                                  opacity: 0.8,
                                  marginTop: "-30px"
                              }}
                            />
                            <span style={{color: "white", fontSize: "2.5rem"}}>
                                ChessVerse
                            </span>
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
                <Row style={{marginTop: "4vh"}}>
                    <Col xs={3} sm={3} lg={3}>
                        <Card style={{marginLeft: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}> 
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: `${fontSize}`, marginTop: "5px"}}>
                                    Moves History
                                </p>
                            </Card.Title>
                            <Card.Body
                              style={{
                                  overflow: "auto",
                                  height: `calc(${width}px / 4)`,
                                  marginLeft: "20px",
                                  marginBottom: "20px"
                              }}
                            >
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
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col xs={6} sm={6} lg={6}>
                        <div style={{marginBottom: "30px", display: "flex", justifyContent: "center"}}>
                            <Clock size={30}/>
                            <p style={{marginLeft: "10px"}}>{timer}</p>
                        </div>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div >
                                <Board
                                  setVictory={setVictory}
                                  startTimer={startTimer}
                                  setShowGameOver={setShowGameOver}
                                  setMoves={setMoves}
                                  data={data}
                                  isLoadingGame={isLoadingGame}
                                  setIsLoadingGame={setIsLoadingGame}
                                  width={width}
                                  socket={socket}
                                />
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", paddingTop: "30px"}}>
                            <Button
                              color="brown"
                              style={{fontSize: `${fontSize}`}}
                              onClick={handleUndo}
                              variant="contained"
                            >
                                Undo
                            </Button>
                        </div>
                    </Col>
                    <Col xs={3} sm={3} lg={3}>
                        <Card style={{marginRight: "30px", backgroundColor: "#b6884e", marginTop: "120px"}}>
                            <Card.Title style={{display: 'flex', justifyContent: "center"}}>
                                <p style={{fontWeight: "bold", fontSize: `${fontSize}`, marginTop: "5px"}}>
                                    Chat
                                </p>
                            </Card.Title>
                            <Card.Body style={{
                                overflow: "auto",
                                height: `calc(${width}px / 4)`,
                                marginLeft: "20px",
                                marginBottom: "20px"
                            }}>
                                {botMessages.map((el, i) =>
                                  <Card
                                    style={{
                                        marginTop: "10px",
                                        marginBottom: "10px",
                                        backgroundColor: "#9f7a48"
                                    }}
                                    key={i}
                                  >
                                      <Card.Body>
                                          <p>{el}</p>
                                      </Card.Body>
                                  </Card>
                                )}
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
                </ThemeProvider>
            </div>
        </>
    )
}

Game.propTypes = {
    gameTime: PropTypes.number,
    botDiff: PropTypes.number,
    isLoadingGame: PropTypes.bool,
    setIsLoadingGame: PropTypes.func,
    socket: PropTypes.object,
    setSocket: PropTypes.func,
    gameImb: PropTypes.number,
    isSinglePlayer: PropTypes.bool,
    data: PropTypes.object,
}

export default Game;