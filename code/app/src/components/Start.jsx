import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";
import {createTheme,ThemeProvider} from '@mui/material/styles';
import { Link } from "react-router-dom";
import ChessBoardImg from "../assets/background2.jpg";
import ImageScacchi from "../assets/logo.png";
import ImageSinglePlayer from "../assets/singleplayer-removebg-preview.png";
import ImageMultiPlayer from "../assets/multiplayer-removebg-preview.png";
import {Row, Col, Image, Nav} from "react-bootstrap";
import { useState } from "react";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';


function Start(){

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


    return (
        <>
        <ThemeProvider theme={theme}>

            <div style={{backgroundImage: `url(${ChessBoardImg})`, backgroundSize: "cover", backgroundAttachment: "fixed", backgroundRepeat: "no-repeat", width: "100vw", height: "100vh"}}> 
                <div style={{ paddingTop: "20vh"}}>
                    {!showOptions ? 
                    <>
                        <Row style={{display: "flex", justifyContent: "center"}}>
                            <Col>
                                <Image src={`${ImageScacchi}`} style={{width: "100px", height: "100px", opacity: 0.8, marginBottom: "-10px"}} alt="immagine di scacchi" />
                                <span style={{color: "white", fontSize: "5rem"}}>ChessVerse</span>
                            </Col>
                        </Row>
                        
                        <Row style={{display: "flex", justifyContent: "center"}}>
                            <Col>
                                <p style={{color: "white", fontSize: "3rem"}}>Challenge yourself, Challenge the world</p>
                            </Col>
                        </Row>
                        
                        <Row style={{display: "flex", justifyContent: "center", marginTop: "40px"}}>
                            <Col>
                                <Nav.Link as={Link} to="/login">
                                    <Button disabled={true} color="brown" style={{fontSize: "1.5rem"}}  variant="contained" >
                                    Log In
                                    </Button>
                                </Nav.Link>
                            </Col>
                        </Row>
                        <Row style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Col>
                                <Button color="brown" style={{fontSize: "1.5rem"}} onClick={()=>{setShowOptions(true)}}  variant="contained" >
                                    Play as guest
                                </Button>
                            </Col>
                        </Row>
                    </>
                    : 
                    <>
                        <Row style={{display: "flex", justifyContent: "center"}}>
                            <Col>
                                <p style={{color: "white", fontSize: "5rem"}}>Choose an option:</p>
                            </Col>
                        </Row>
                        <Row style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Col>
                                <Nav.Link as={Link} to="/singlePlayer">
                                    <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}}  variant="contained" >
                                        <div style={{marginTop: "5px", marginBottom: "5px", marginRight: "30px", marginLeft: "30px"}}>
                                            <Image src={`${ImageSinglePlayer}`} style={{width: "30px", height: "30px", marginBottom: "-5px", marginRight: "5px"}} alt="immagine di scacchi SinglePlayer" />
                                            <span>Single Player</span>
                                        </div>
                                        
                                    </Button>
                                </Nav.Link>
                            </Col>
                        </Row>
                        <Row style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Col>
                                <Nav.Link as={Link} to="/multiPlayer">
                                    <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}}  variant="contained" >
                                        <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                            <Image src={`${ImageMultiPlayer}`} style={{width: "50px", height: "30px", marginBottom: "-5px", marginRight: "10px"}} alt="immagine di scacchi SinglePlayer" />
                                            <span>MultiPlayer</span>
                                        </div>  
                                    </Button>
                                </Nav.Link>
                            </Col>
                        </Row>
                        <Row style={{display: "flex", justifyContent: "center", marginTop: "30px"}}>
                            <Col>
                                <Button color="brown" style={{fontSize: "1.5rem", borderRadius: "20px"}} onClick={()=>setShowOptions(false)} variant="contained" >
                                    <div style={{marginTop: "5px", marginBottom: "5px"}}>
                                        <HighlightOffIcon style={{marginRight: "10px", marginBottom: "-8px"}} fontSize="large"/>
                                        <span>Quit</span>
                                    </div>
                                    
                                </Button>
                            </Col>
                        </Row>
                    </>
                    }
                </div>
            </div>
        </ThemeProvider>
        </>
    )
}

export default Start;