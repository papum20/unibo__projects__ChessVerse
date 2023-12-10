import {ShareFill} from "react-bootstrap-icons"
import { PVP, PVE } from "../const/const.js";

function Social(props){


    function Share(){



        const msg = `ho giocato a scacchi ♔ in modalità Really Bad Chess contro ` + `${props.enemyUser}` + `${props.mode === PVE ? " con livello di profondità " : " con elo "}` + `${props.diff}`  
          + `${props.modalType === "gameover" ? " e ho perso 😢" : props.modalType === "victory" ? " e ho vinto! 🎉" : " ed è finita in patta 🤝"}`


        const destinationURL = encodeURIComponent(props.url);

        const text = encodeURIComponent(msg);

        const telegramShareURL = `https://t.me/share/url?url=${destinationURL}&text=${text}`;

        window.open(telegramShareURL, '_blank');
    }

    return (
        <ShareFill onClick={()=>Share()} style={{cursor: "pointer"}} role="button" size="30" />
    )
}
export default Social;           