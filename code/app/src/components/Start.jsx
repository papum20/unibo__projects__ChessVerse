import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";
import {createTheme,ThemeProvider} from '@mui/material/styles';
import { Link } from "react-router-dom";
import ChessBoardImg from "../assets/background2.jpg";
import ImageScacchi from "../assets/logo.png";
import ImageSinglePlayer from "../assets/singleplayer-removebg-preview.png";
import ImageMultiPlayer from "../assets/multiplayer-removebg-preview.png";
import {Row, Col, Image, Nav, Modal, Container} from "react-bootstrap";
import { useState, useEffect } from "react";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';


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

    
    const [showOptions, setShowOptions] = useState(false);

    const [showModal, setShowModal] = useState(false);

    return (
        <>

        <Modal show={showModal} centered size="lg">
                <Modal.Title>
                
                </Modal.Title>
                <Modal.Body>
                    
                </Modal.Body>
        </Modal>

        <ThemeProvider theme={theme}>

            
            <div style={{fontFamily: "'Open Sans', sans-serif", backgroundImage: `${!showOptions ?  `url(${ChessBoardImg})` : "" }`, backgroundSize: "cover", backgroundAttachment: "fixed", backgroundRepeat: "no-repeat", backgroundColor: `${showOptions ? "#b99b69" : ""}`, width: "100vw", height: "100vh"}}> 
                <div style={{ paddingTop: "20vh"}}>
                    {!showOptions ? 
                    <>
                        <div style={{display: "flex", justifyContent: "center"}}>
                            <div>
                                <Image src={`${ImageScacchi}`} style={{width: "100px", height: "100px", opacity: 0.8, marginBottom: "-10px"}} alt="immagine di scacchi" />
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
                                <Nav.Link as={Link} to="/game" onClick={()=>props.setIsSinglePlayer(false)}>
                                    <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}}  variant="contained" >
                                        <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                            <Image src={`${ImageMultiPlayer}`} style={{width: "50px", height: "30px", marginBottom: "-5px", marginRight: "10px"}} alt="immagine di scacchi SinglePlayer" />
                                            <span>MultiPlayer</span>
                                        </div>  
                                    </Button>
                                </Nav.Link>
                            </div>
                        </div>
                        <div style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <div>
                                <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}} onClick={()=>setShowOptions(false)} variant="contained" >
                                    <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                        <HighlightOffIcon style={{marginRight: "10px", marginBottom: "-8px"}} fontSize="large"/>
                                        <span>Quit</span>
                                    </div>
                                    
                                </Button>
                            </div>
                        </div>
                    </>
                    }
                </div>
            </div>
       </ThemeProvider>
                
        </>
    )
}

export default Start;


