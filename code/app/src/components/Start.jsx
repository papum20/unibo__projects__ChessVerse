import { useNavigate, Link } from "react-router-dom";
import PropTypes from "prop-types";
import { Button, Typography, Slider  } from "@mui/material";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import ChessBoardImg from "../assets/background2.jpg";
import ImageScacchi from "../assets/logo.png";
import ImageSinglePlayer from "../assets/singleplayer-removebg-preview.png";
import ImageMultiPlayer from "../assets/multiplayer-removebg-preview.png";
import { Image, Nav, Modal, Form, CloseButton } from "react-bootstrap";
import { useState, useEffect } from "react";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import {MAX_BOT_DIFF, MAX_GAME_IMB, MAX_GAME_TIME, MIN_BOT_DIFF, MIN_GAME_IMB, MIN_GAME_TIME, PVP, PVE, TIME_OPTIONS} from "../const/const.js";
import { io } from "socket.io-client";


function Start({
                   mode, setMode,
                   gameImb, setGameImb,
                   botDiff, setBotDiff,
                   gameTime, setGameTime,
                   socket, setSocket,
                   setIsLoadingGame,
                   data,
                   setStartFen,
                   setRoomId,
                   setColor
               })
{
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

    const navigator = useNavigate();
    const [showOptions, setShowOptions] = useState(false);
    const [showModal, setShowModal] = useState(false);

  
    
    async function handleSubmit (e) {
        e.preventDefault();
        if(botDiff === 0)
            setBotDiff(MIN_BOT_DIFF);
        setShowModal(false);
        setIsLoadingGame(true);
        const host = import.meta.env.VITE_ASYNC_HOST ?? "http://localhost:8080";
        const secure = import.meta.env.VITE_NODE_ENV == "production";
        const options = { transports: ["websocket"], secure}
        setSocket(io(host, options));
    }

    useEffect(() => {
        if (socket) {
            socket.connect();
            socket.on('connect', () => {
                socket.on("config", (data) => {
                    if(!data){
                      props.socket?.on("start", props.data);
                    }
                    else {
                        setStartFen(data.fen);
                        setColor(data.color);
                        setRoomId(data.id);
                        setIsLoadingGame(false);
                    }
                  })

                socket.emit('start', data);
                
            });
            navigator('./game', { relative: "path" });
        }
    }, [socket]);

    


    return (
        <div data-testid="startPage">

        <Modal  show={showModal} centered size="lg">
            <ThemeProvider theme={theme}>
                <Modal.Title  style={{display: "flex", justifyContent: "flex-end", backgroundColor: "#b6884e"}}>
                    <CloseButton style={{marginRight: "10px", marginTop: "5px"}} onClick={()=> setShowModal(false)}/>
                </Modal.Title>
                <Modal.Body style={{backgroundColor: "#b6884e"}}>
                    <Form onSubmit={async (e)=> await handleSubmit(e)} >
                        {mode===PVE &&
                            <>
                                <Typography id="botDifficult" gutterBottom
                                    style={{display:"flex", justifyContent: "center"}}
                                >
                                Bot Strength: {botDiff}
                                </Typography>
                                <Slider
                                    style={{width:"80%", marginLeft: "10%"}}
                                    value={botDiff}
                                    min={MIN_BOT_DIFF}
                                    step={1}
                                    max={MAX_BOT_DIFF}
                                    color="brown"
                                    onChange={(e) => { setBotDiff(Math.max(MIN_BOT_DIFF, Math.min(MAX_BOT_DIFF, e.target.value))); }}
                                    valueLabelDisplay="auto"
                                    aria-labelledby="botDifficult"
                                />
                            </>
                        }

                        <>
                            <Typography id="gameImbalance" gutterBottom
                                style={{display:"flex", justifyContent: "center"}}
                            >
                            Rank: {gameImb}
                            </Typography>
                            <Slider
                                style={{width:"80%", marginLeft: "10%"}}
                                value={gameImb}
                                min={MIN_GAME_IMB}
                                step={1}
                                max={MAX_GAME_IMB}
                                color="brown"
                                onChange={(e) => { setGameImb(Math.max(MIN_GAME_IMB, Math.min(MAX_GAME_IMB, e.target.value))); }}
                                valueLabelDisplay="auto"
                                aria-labelledby="gameImbalance"
                            />
                        </>
                        {mode===PVE ?
                        <>
                            <Typography id="gameTime" gutterBottom
                                style={{display:"flex", justifyContent: "center"}}
                            >
                            Clocktime: {gameTime} sec 
                            </Typography>
                            <Slider
                                style={{width:"80%", marginLeft: "10%"}}
                                value={gameTime}
                                min={MIN_GAME_TIME}
                                step={1}
                                max={MAX_GAME_TIME}
                                onChange={(e)=>{if(e.target.value < 0) setGameTime(MAX_GAME_IMB); else setGameTime(e.target.value);}}
                                color="brown"
                                valueLabelDisplay="auto"
                                aria-labelledby="gameTime"
                            />
                        </>
                        :
                        <div style={{marginTop: "20px", display: "flex", justifyContent: "center"}}>
                            <Form.Label style={{marginRight: "20px"}}>
                                Clocktime in minutes: 
                            </Form.Label>
                            {
                                TIME_OPTIONS.map((el,i) => 
                                <Form.Check
                                    key={i}
                                    inline
                                    // label={`${el%60}`}
                                    label={`${Math.floor(el/60)}`}
                                    type="radio"
                                    id={el}
                                    name="clocktime"
                                    onChange={()=> {setGameTime(el)}}
                                    defaultChecked={gameTime===el}
                                
                                />
                                )
                            }
                        </div>
                        }
                        <div style={{display: "flex", justifyContent: "flex-end"}}>
                            <Button size="large" color="brown" type="submit" variant="contained">start</Button>
                        </div>
                    </Form>
                </Modal.Body>
            </ThemeProvider>
        </Modal>

            <div style={{
                fontFamily: "Helvetica Neue",
                backgroundImage: `${!showOptions ? `url(${ChessBoardImg})` : "" }`,
                backgroundSize: "cover",
                backgroundAttachment: "fixed",
                backgroundRepeat: "no-repeat",
                backgroundColor: `${showOptions ? "#b99b69" : ""}`,
                width: "100vw",
                height: "100vh"
            }}>
                <ThemeProvider theme={theme}>
                <div style={{ paddingTop: "20vh"}}>
                    {!showOptions ?
                    <>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <Image
                              src={`${ImageScacchi}`}
                              alt="immagine di scacchi"
                              style={{
                                  width: "100px",
                                  height: "100px",
                                  opacity: 0.8,
                                  marginTop: "-5px"
                              }}
                            />
                            <span style={{color: "white", fontSize: "5rem"}}>ChessVerse</span>
                        </div>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <p style={{color: "white", fontSize: "3rem"}}>
                                Challenge yourself, Challenge the world
                            </p>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "40px"}}>
                            <Nav.Link as={Link} to="/login">
                                <Button
                                  color="brown"
                                  style={{fontSize: "1.5rem"}}
                                  variant="contained"
                                >
                                    Log In
                                </Button>
                            </Nav.Link>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Button
                              color="brown"
                              style={{fontSize: "1.5rem"}}
                              onClick={() => setShowOptions(true) }
                              variant="contained"
                            >
                                Play as guest
                            </Button>
                        </div>
                    </>
                    :
                    <>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <p style={{color: "white", fontSize: "5rem"}}>
                                Choose an option:
                            </p>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Button
                              color="brown"
                              onClick={() => {
                                  setMode(PVE);
                                  setShowModal(true);
                              }}
                              style={{fontSize: "1.5rem", borderRadius: "20px"}}
                              variant="contained"
                            >
                                <div style={{
                                    marginTop: "5px",
                                    marginBottom: "5px",
                                    marginRight: "30px",
                                    marginLeft: "30px"
                                }}>
                                    <Image
                                      src={`${ImageSinglePlayer}`}
                                      alt="immagine di scacchi SinglePlayer"
                                      style={{
                                          width: "30px",
                                          height: "30px",
                                          marginBottom: "5px",
                                          marginRight: "2px"
                                      }}
                                    />
                                    <span>Single Player</span>
                                </div>
                            </Button>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Button
                              
                              color="brown"
                              onClick={() => {
                                  setMode(PVP);
                                  setShowModal(true);
                              }}
                              style={{fontSize: "1.5rem", borderRadius: "20px"}}
                              variant="contained"
                            >
                                <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                    <Image
                                      src={`${ImageMultiPlayer}`}
                                      alt="immagine di scacchi multiplayer"
                                      style={{
                                          width: "50px",
                                          height: "30px",
                                          marginBottom: "2px",
                                          marginRight: "10px"
                                      }}
                                    />
                                    <span>MultiPlayer</span>
                                </div>
                            </Button>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Button
                              color="brown"
                              style={{fontSize: "1.5rem", borderRadius: "20px"}}
                              onClick={() => setShowOptions(false)}
                              variant="contained"
                            >
                                <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                    <HighlightOffIcon
                                      style={{marginRight: "10px", marginTop: "-3px"}}
                                      fontSize="large"
                                    />
                                    <span>Quit</span>
                                </div>
                            </Button>
                        </div>
                    </>
                    }
                </div>
                </ThemeProvider>
            </div>
                
        </div>
    )
}

Start.propTypes = {
    mode: PropTypes.number,
    setMode: PropTypes.func,
    gameImb: PropTypes.number,
    setGameImb: PropTypes.func,
    botDiff: PropTypes.number,
    setBotDiff: PropTypes.func,
    gameTime: PropTypes.number,
    setGameTime: PropTypes.func,
    socket: PropTypes.object,
    setSocket: PropTypes.func,
    setIsLoadingGame: PropTypes.func,
    data: PropTypes.object,
    setStartFen: PropTypes.func,
    setColor: PropTypes.func,
    setRoomId: PropTypes.func
}

export default Start;
