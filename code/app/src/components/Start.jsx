import { useNavigate } from "react-router-dom";
import { Button, Typography, Slider  } from "@mui/material";
import {createTheme,ThemeProvider} from '@mui/material/styles';
import { Link } from "react-router-dom";
import ChessBoardImg from "../assets/background2.jpg";
import ImageScacchi from "../assets/logo.png";
import ImageSinglePlayer from "../assets/singleplayer-removebg-preview.png";
import ImageMultiPlayer from "../assets/multiplayer-removebg-preview.png";
import { Image, Nav, Modal, Form, FloatingLabel, CloseButton} from "react-bootstrap";
import { useState, useEffect } from "react";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import io from 'socket.io-client';



function Start(props){

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

    const [moveMod, setMoveMod] = useState(0);

    

    async function handleSubmit (e) {
        e.preventDefault();
        if(props.botDiff === 0)
            props.setBotDiff(1);
        setShowModal(false);
        props.setIsLoadingGame(true);
        props.setSocket(io("http://localhost:8766", {transports: ['websocket']}));
    }

    useEffect(()=>{
        if(props.socket){

            props.socket.connect();
            props.socket.on('connect_error', (error) => {
                console.error('Errore di connessione:', error);
            });
            
            props.socket.emit('start', props.data);
            // TODO ricevere config da server
            navigator(`./game`, { relative: "path" });
        }
    },[props.socket]);

    return (
        <>

        <Modal  show={showModal} centered size="lg">
            <ThemeProvider theme={theme}>
                <Modal.Title  style={{display: "flex", justifyContent: "flex-end", backgroundColor: "#b6884e"}}>
                    <CloseButton style={{marginRight: "10px", marginTop: "5px"}} onClick={()=> setShowModal(false)}/>
                </Modal.Title>
                <Modal.Body style={{backgroundColor: "#b6884e"}}>
                    <Form onSubmit={async (e)=> await handleSubmit(e)} >
                        {props.isSinglePlayer &&
                            <>
                                <Typography id="botDifficult" gutterBottom
                                    style={{display:"flex", justifyContent: "center"}}
                                >
                                Bot Strength: {props.botDiff}
                                </Typography>
                                <Slider
                                    style={{width:"80%", marginLeft: "10%"}}
                                    value={props.botDiff}
                                    min={1}
                                    step={1}
                                    max={20}
                                    color="brown"
                                    onChange={(e) => { props.setBotDiff(Math.max(1, Math.min(20, e.target.value))); }}
                                    valueLabelDisplay="auto"
                                    aria-labelledby="botDifficult"
                                />
                            </>
                        }

                        <>
                            <Typography id="gameImbalance" gutterBottom
                                style={{display:"flex", justifyContent: "center"}}
                            >
                            Rank: {props.gameImb}
                            </Typography>
                            <Slider
                                style={{width:"80%", marginLeft: "10%"}}
                                value={props.gameImb}
                                min={0}
                                step={1}
                                max={100}
                                color="brown"
                                onChange={(e) => { props.setGameImb(Math.max(0, Math.min(100, e.target.value))); }}
                                valueLabelDisplay="auto"
                                aria-labelledby="gameImbalance"
                            />
                        </>
                        <>
                            <Typography id="gameTime" gutterBottom
                                style={{display:"flex", justifyContent: "center"}}
                            >
                            Clocktime: {props.gameTime}
                            </Typography>
                            <Slider
                                style={{width:"80%", marginLeft: "10%"}}
                                value={props.gameTime}
                                min={1}
                                step={1}
                                max={3000}
                                onChange={(e)=>{if(e.target.value < 0) props.setGameTime(3000); else props.setGameTime(e.target.value);}}
                                color="brown"
                                valueLabelDisplay="auto"
                                aria-labelledby="gameTime"
                            />
                        </>
                        <div style={{display: "flex", justifyContent: "flex-end"}}>
                            <Button size="large" color="brown" type="submit" variant="contained">start</Button>
                        </div>
                    </Form>
                </Modal.Body>
            </ThemeProvider>
        </Modal>


            
            <div style={{fontFamily: "Helvetica Neue", backgroundImage: `${!showOptions ?  `url(${ChessBoardImg})` : "" }`, backgroundSize: "cover", backgroundAttachment: "fixed", backgroundRepeat: "no-repeat", backgroundColor: `${showOptions ? "#b99b69" : ""}`, width: "100vw", height: "100vh"}}> 
                <ThemeProvider theme={theme}>

                <div style={{ paddingTop: "20vh"}}>
                    {!showOptions ? 
                    <>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div>
                                <Image src={`${ImageScacchi}`} style={{width: "100px", height: "100px", opacity: 0.8, marginTop: "-60px"}} alt="immagine di scacchi" />
                                <span style={{color: "white", fontSize: "5rem"}}>ChessVerse</span>
                            </div>
                        </div>
                        
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div>
                                <p style={{color: "white", fontSize: "3rem"}}>Challenge yourself, Challenge the world</p>
                            </div>
                        </div>
                        
                        <div style={{display: "flex", justifyContent: "center", marginTop: "40px"}}>
                            <div>
                                <Nav.Link as={Link} to="/login">
                                    <Button color="brown" disabled={true}  style={{fontSize: "1.5rem"}}  variant="contained" >
                                    Log In
                                    </Button>
                                </Nav.Link>
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <div>
                                <Button color="brown"  style={{fontSize: "1.5rem"}} onClick={()=>{setShowOptions(true)}}  variant="contained" >
                                    Play as guest
                                </Button>
                            </div>
                        </div>
                    </>
                    : 
                    <>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div>
                                <p style={{color: "white", fontSize: "5rem"}}>Choose an option:</p>
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <div>
                                    <Button color="brown"  onClick={()=>{props.setIsSinglePlayer(true); setShowModal(true)}} style={{fontSize: "1.5rem", borderRadius: "20px"}}  variant="contained" >
                                        <div style={{marginTop: "5px", marginBottom: "5px", marginRight: "30px", marginLeft: "30px"}}>
                                            <Image src={`${ImageSinglePlayer}`} style={{width: "30px", height: "30px", marginBottom: "-5px", marginRight: "5px"}} alt="immagine di scacchi SinglePlayer" />
                                            <span>Single Player</span>
                                        </div> 
                                    </Button>     
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <div>
                                    <Button disabled color="brown" onClick={()=>{props.setIsSinglePlayer(false); setShowModal(true);}} style={{fontSize: "1.5rem", borderRadius: "20px"}}  variant="contained" >
                                        <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                            <Image src={`${ImageMultiPlayer}`} style={{width: "50px", height: "30px", marginBottom: "-5px", marginRight: "10px"}} alt="immagine di scacchi SinglePlayer" />
                                            <span>MultiPlayer</span>
                                        </div>  
                                    </Button>
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <div>
                                <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}} onClick={()=>setShowOptions(false)} variant="contained" >
                                    <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                        <HighlightOffIcon style={{marginRight: "10px", marginTop: "-3px"}} fontSize="large"/>
                                        <span>Quit</span>
                                    </div>
                                    
                                </Button>
                            </div>
                        </div>
                    </>
                    }
                </div>
                </ThemeProvider>

            </div>
                
        </>
    )
}

export default Start;


