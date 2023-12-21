import { ShareFill } from "react-bootstrap-icons";
import { PVP, PVE, RANKED, DAILY, WEEKLY } from "../const/const.js";

function Social(props) {
  const end_string =
    props.modalType === "gameover"
      ? " e ho perso 😢"
      : props.modalType === "won"
        ? " e ho vinto! 🎉"
        : " ed è finita in patta 🤝";

  const pve_msg = `ho giocato a scacchi ♔ in modalità Really Bad Chess contro ${props.enemyUser} con livello di profondità ${props.diff} ${end_string}`;

  const pvp_msg = `ho giocato a scacchi ♔ in modalità Really Bad Chess contro ${props.enemyUser} con elo ${props.diff} ${end_string}`;

  const dw_msg = `ho giocato a scacchi ♔ in modalità Really Bad Chess contro ${props.enemyUser}, ho fatto ${props.diff} mosse ${end_string}`;

  const ranked_msg = `ho giocato a scacchi ♔ in modalità Really Bad Chess contro ${props.enemyUser} con ranking ${props.diff} ${end_string}`;

  function getText() {
    switch (props.mode) {
      case PVP:
        return pvp_msg;
      case PVE:
        return pve_msg;
      case DAILY || WEEKLY:
        return dw_msg;
      case RANKED:
        return ranked_msg;
    }
  }

  const destinationURL = encodeURIComponent(props.url);

  const text = encodeURIComponent(getText());

  function Share() {
    const telegramShareURL = `https://t.me/share/url?url=${destinationURL}&text=${text}`;
    window.open(telegramShareURL, "_blank");
  }

  return (
    <ShareFill
      onClick={() => Share()}
      style={{ cursor: "pointer" }}
      role="button"
      size="30"
    />
  );
}

export default Social;
