import ImageScacchi from "../assets/logo.png";
import { Image } from "react-bootstrap";

function Game () {
    return (
        <div style={{backgroundColor: "#b99b69", width: "100vw", height: "100vh"}}>
            <div style={{paddingTop: "10px", paddingLeft: "10px"}}>
                <Image src={`${ImageScacchi}`} style={{width: "50px", height: "50px", opacity: 0.8, marginTop: "-30px"}} alt="immagine di scacchi" />
                <span style={{color: "white", fontSize: "2.5rem"}}>ChessVerse</span>
            </div>
        </div>
    )
}

export default Game;