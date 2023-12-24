import { useNavigate, Link, useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import { Button, Typography, Slider } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import ChessBoardImg from "../assets/background2.jpg";
import ImageScacchi from "../assets/logo.png";
import ImageSinglePlayer from "../assets/singleplayer-removebg-preview.png";
import ImageMultiPlayer from "../assets/multiplayer-removebg-preview.png";
import { Image, Nav, Modal, Form, CloseButton } from "react-bootstrap";
import { useState, useEffect } from "react";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import { joinPaths } from "../utils/path";
import useWindowDimensions from "./useWindowDimensions.jsx";
import {
  MAX_BOT_DIFF,
  MAX_GAME_IMB,
  MAX_GAME_TIME,
  MIN_BOT_DIFF,
  MIN_GAME_IMB,
  MIN_GAME_TIME,
  PVP,
  PVE,
  DAILY,
  WEEKLY,
  RANKED,
  TIME_OPTIONS,
  SERVER_ADDR,
} from "../const/const.js";
import { io } from "socket.io-client";
import * as users_api from "../network/users_api";
import { CalendarEvent, CalendarWeek } from "react-bootstrap-icons";
import { FaCrown } from "react-icons/fa";
import Scores from "./Scores.jsx";
import { toast } from "react-toastify";
import { API } from "../const/const_api.js";

function Start({
  mode,
  setMode,
  gameImb,
  setGameImb,
  botDiff,
  setBotDiff,
  gameTime,
  setGameTime,
  socket,
  setSocket,
  setIsLoadingGame,
  data,
  setStartFen,
  setRoomId,
  setColor,
  setUser,
  user,
  setYouAreLogged,
  youAreLogged,
  setElo,
  setEnemyUsername,
  setRank,
}) {
  const { width } = useWindowDimensions();
  const theme = createTheme({
    palette: {
      brown: {
        main: "#795548",
        light: "#543b32",
        dark: "#543b32",
        contrastText: "#fff",
      },
    },
  });

  const location = useLocation();

  const navigator = useNavigate();

  const [showModal, setShowModal] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (botDiff === 0) setBotDiff(MIN_BOT_DIFF);
    setShowModal(false);
    const host = import.meta.env.VITE_GAME_HOST ?? "http://localhost:8080";
    const secure = import.meta.env.VITE_NODE_ENV == "production";
    const options = { transports: ["websocket"], secure };
    setSocket(io(host, options));
  }

  useEffect(() => {
    if (socket) {
      socket.connect();
      socket.on("connect", () => {
        socket.on("config", (config) => {
          if (config?.elo !== undefined)
            setElo(config?.elo);
          setEnemyUsername(config?.username || "Stockfish");
          setStartFen(config.fen);
          setColor(config.color);
          setRoomId(config.id);
          setIsLoadingGame(false);
          if ("rank" in config) setRank(config.rank);
        });

        const tmpData = {
          ...data,
        };
        tmpData.session_id = sessionStorage.getItem("session_id");
        tmpData.type = mode; //ho messo sta riga perche' mi dava dei bug

        socket.emit("start", tmpData);
        setIsLoadingGame(true);
      });
      navigator("../game", { relative: "path" });
    }
  }, [socket]);

  function getShowOptions() {
    if (location.pathname[1] === undefined) return false;
    else return true;
  }

  //serve per quando sei nelle opzioni e ricarichi la pagina
  useEffect(() => {
    if (user === null) {
      navigator("../", { relative: "path" });
      sessionStorage.setItem("session_id", undefined);
    }
  }, [socket]);

  return (
    <div data-testid="startPage">
      <Modal show={showModal} centered size="lg">
        <ThemeProvider theme={theme}>
          <Modal.Title
            style={{
              display: "flex",
              justifyContent: "flex-end",
              backgroundColor: "#b6884e",
            }}
          >
            <CloseButton
              style={{ marginRight: "10px", marginTop: "5px" }}
              onClick={() => setShowModal(false)}
            />
          </Modal.Title>
          <Modal.Body style={{ backgroundColor: "#b6884e" }}>
            <Form onSubmit={async (e) => await handleSubmit(e)}>
              {mode === PVE && (
                <>
                  <Typography
                    id="botDifficult"
                    gutterBottom
                    style={{ display: "flex", justifyContent: "center" }}
                  >
                    Bot Strength: {botDiff}
                  </Typography>
                  <Slider
                    style={{ width: "80%", marginLeft: "10%" }}
                    value={botDiff}
                    min={MIN_BOT_DIFF}
                    step={1}
                    max={MAX_BOT_DIFF}
                    color="brown"
                    onChange={(e) => {
                      setBotDiff(
                        Math.max(
                          MIN_BOT_DIFF,
                          Math.min(MAX_BOT_DIFF, e.target.value),
                        ),
                      );
                    }}
                    valueLabelDisplay="auto"
                    aria-labelledby="botDifficult"
                  />
                </>
              )}

              <>
                <Typography
                  id="gameImbalance"
                  gutterBottom
                  style={{ display: "flex", justifyContent: "center" }}
                >
                  Rank: {gameImb}
                </Typography>
                <Slider
                  style={{ width: "80%", marginLeft: "10%" }}
                  value={gameImb}
                  min={MIN_GAME_IMB}
                  step={1}
                  max={MAX_GAME_IMB}
                  color="brown"
                  onChange={(e) => {
                    setGameImb(
                      Math.max(
                        MIN_GAME_IMB,
                        Math.min(MAX_GAME_IMB, e.target.value),
                      ),
                    );
                  }}
                  valueLabelDisplay="auto"
                  aria-labelledby="gameImbalance"
                />
              </>
              {mode === PVE ? (
                <>
                  <Typography
                    id="gameTime"
                    gutterBottom
                    style={{ display: "flex", justifyContent: "center" }}
                  >
                    Clocktime: {gameTime} sec
                  </Typography>
                  <Slider
                    style={{ width: "80%", marginLeft: "10%" }}
                    value={gameTime}
                    min={MIN_GAME_TIME}
                    step={1}
                    max={MAX_GAME_TIME}
                    onChange={(e) => {
                      if (e.target.value < 0) setGameTime(MAX_GAME_IMB);
                      else setGameTime(e.target.value);
                    }}
                    color="brown"
                    valueLabelDisplay="auto"
                    aria-labelledby="gameTime"
                  />
                </>
              ) : (
                <div
                  style={{
                    marginTop: "20px",
                    display: "flex",
                    justifyContent: "center",
                  }}
                >
                  <Form.Label style={{ marginRight: "20px" }}>
                    Clocktime in minutes:
                  </Form.Label>
                  {TIME_OPTIONS.map((el, i) => (
                    <Form.Check
                      key={i}
                      inline
                      // label={`${el%60}`}
                      label={`${Math.floor(el / 60)}`}
                      type="radio"
                      id={el}
                      name="clocktime"
                      onChange={() => {
                        setGameTime(el);
                      }}
                      defaultChecked={gameTime === el}
                    />
                  ))}
                </div>
              )}
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <Button
                  size="large"
                  color="brown"
                  type="submit"
                  variant="contained"
                >
                  start
                </Button>
              </div>
            </Form>
          </Modal.Body>
        </ThemeProvider>
      </Modal>

      <div
        style={{
          fontFamily: "Helvetica Neue",
          backgroundImage: `${
            !getShowOptions() ? `url(${ChessBoardImg})` : ""
          }`,
          backgroundSize: "cover",
          backgroundAttachment: "fixed",
          backgroundRepeat: "no-repeat",
          backgroundColor: `${getShowOptions() ? "#b99b69" : ""}`,
          width: "100vw",
          minHeight: "100vh",
          paddingBottom: "20px",
        }}
      >
        <ThemeProvider theme={theme}>
          <div style={{ paddingTop: `${!getShowOptions() ? "18vh" : ""}` }}>
            {!getShowOptions() ? (
              <>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    flexDirection: `${width < 600 ? "column" : "row"}`,
                  }}
                >
                  <Image
                    src={`${ImageScacchi}`}
                    alt="immagine di scacchi"
                    style={{
                      width: "100px",
                      height: "100px",
                      opacity: 0.8,
                      marginTop: "-5px",
                    }}
                  />
                  <span
                    style={{
                      color: "white",
                      fontSize: `${width < 600 ? "2rem" : "5rem"}`,
                    }}
                  >
                    ChessVerse
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "center" }}>
                  <p
                    style={{
                      color: "white",
                      fontSize: `${width < 600 ? "1.2rem" : "3rem"}`,
                    }}
                  >
                    Challenge yourself, Challenge the world
                  </p>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "40px",
                  }}
                >
                  <Nav.Link as={Link} to="/login">
                    <Button
                      id="login"
                      color="brown"
                      style={{ fontSize: "1.5rem" }}
                      variant="contained"
                    >
                      Log In
                    </Button>
                  </Nav.Link>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    id="play-as-guest"
                    color="brown"
                    style={{ fontSize: "1.5rem" }}
                    onClick={async () => {
                      const guest = await users_api.addGuest();
                      sessionStorage.setItem("session_id", undefined);
                      setUser(guest);
                      setYouAreLogged(false);
                      navigator("./options", { relative: "path" });
                    }}
                    variant="contained"
                  >
                    Play as guest
                  </Button>
                </div>
              </>
            ) : (
              <>
                <span
                  style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    fontWeight: "bold",
                    marginRight: "20px",
                    fontSize: "25px",
                  }}
                >
                  {user}
                </span>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "-20px",
                  }}
                >
                  <p
                    style={{
                      color: "white",
                      fontSize: `${width < 600 ? "2.5rem" : "4rem"}`,
                    }}
                  >
                    Choose an option:
                  </p>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "10px",
                  }}
                >
                  <Button
                    id="daily-board"
                    color="brown"
                    disabled={
                      sessionStorage.getItem("session_id") === "undefined"
                    }
                    onClick={async () => {
                      console.log(API.checkStartDaily.endpoint);
                      console.log(
                        `${API.checkStartDaily.endpoint}?username=${user}`,
                      );
                      const response = await fetch(
                        joinPaths(
                          SERVER_ADDR,
                          `${API.checkStartDaily.endpoint}?username=${user}`,
                        ),
                      );
                      console.log("response status", response.status);
                      if (
                        response.status ===
                        API.checkStartDaily.codes["maximum reached"]
                      ) {
                        toast.info("wait tomorrow to play", {
                          className: "toast-message",
                        });
                      } else if (
                        response.status === API.checkStartDaily.codes["ok"]
                      ) {
                        setMode(DAILY);
                        setBotDiff(MIN_BOT_DIFF);
                        const host = import.meta.env.VITE_GAME_HOST;
                        const secure =
                          import.meta.env.VITE_NODE_ENV == "production";
                        const options = { transports: ["websocket"], secure };
                        setSocket(io(host, options));
                      } else {
                        toast.error(
                          "unexpected error on server communication",
                          { className: "toast-message" },
                        );
                      }
                    }}
                    style={{ fontSize: "1.5rem", borderRadius: "20px" }}
                    variant="contained"
                  >
                    <div
                      style={{
                        marginTop: "5px",
                        marginBottom: "5px",
                        marginRight: "50px",
                        marginLeft: "50px",
                      }}
                    >
                      <CalendarEvent size="30" style={{ marginTop: "-5px" }} />
                      <span style={{ marginLeft: "10px" }}>Daily Board</span>
                    </div>
                  </Button>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    id="weekly-challenge"
                    color="brown"
                    disabled={
                      sessionStorage.getItem("session_id") === "undefined"
                    }
                    style={{ fontSize: "1.5rem", borderRadius: "20px" }}
                    variant="contained"
                    onClick={() => {
                      setMode(WEEKLY);
                      setBotDiff(MIN_BOT_DIFF);
                      const host = import.meta.env.VITE_GAME_HOST;
                      const secure =
                        import.meta.env.VITE_NODE_ENV == "production";
                      const options = { transports: ["websocket"], secure };
                      setSocket(io(host, options));
                    }}
                  >
                    <div
                      style={{
                        marginTop: "5px",
                        marginBottom: "5px",
                      }}
                    >
                      <CalendarWeek size="30" style={{ marginTop: "-5px" }} />
                      <span style={{ marginLeft: "10px" }}>
                        weekly challenge
                      </span>
                    </div>
                  </Button>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    id="ranked"
                    color="brown"
                    disabled={
                      sessionStorage.getItem("session_id") === "undefined"
                    }
                    onClick={() => {
                      setMode(RANKED);
                      setBotDiff(MIN_BOT_DIFF);
                      const host = import.meta.env.VITE_GAME_HOST;
                      const secure =
                        import.meta.env.VITE_NODE_ENV == "production";
                      const options = { transports: ["websocket"], secure };
                      setSocket(io(host, options));
                    }}
                    style={{ fontSize: "1.5rem", borderRadius: "20px" }}
                    variant="contained"
                  >
                    <div
                      style={{
                        marginTop: "5px",
                        marginBottom: "5px",
                        marginRight: "50px",
                        marginLeft: "50px",
                      }}
                    >
                      <FaCrown style={{ marginTop: "-8px" }} size="35" />
                      <span style={{ marginLeft: "10px" }}>Ranked</span>
                    </div>
                  </Button>
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    id="freeplay"
                    color="brown"
                    onClick={() => {
                      setMode(PVE);
                      setShowModal(true);
                    }}
                    style={{ fontSize: "1.5rem", borderRadius: "20px" }}
                    variant="contained"
                  >
                    <div
                      style={{
                        marginTop: "5px",
                        marginBottom: "5px",
                        marginRight: "30px",
                        marginLeft: "30px",
                      }}
                    >
                      <Image
                        src={`${ImageSinglePlayer}`}
                        alt="immagine di scacchi SinglePlayer"
                        style={{
                          width: "30px",
                          height: "30px",
                          marginBottom: "5px",
                          marginRight: "2px",
                        }}
                      />
                      <span>freeplay</span>
                    </div>
                  </Button>
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    id="1v1"
                    color="brown"
                    onClick={() => {
                      setMode(PVP);
                      setShowModal(true);
                    }}
                    style={{
                      fontSize: "1.5rem",
                      borderRadius: "20px",
                      width: "200px",
                    }}
                    variant="contained"
                  >
                    <div style={{ marginTop: "5px", marginBottom: "5px" }}>
                      <Image
                        src={`${ImageMultiPlayer}`}
                        alt="immagine di scacchi multiplayer"
                        style={{
                          width: "50px",
                          height: "30px",
                          marginBottom: "2px",
                          marginRight: "10px",
                        }}
                      />
                      <span>1v1</span>
                    </div>
                  </Button>
                </div>

                <Scores />

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginTop: "30px",
                  }}
                >
                  <Button
                    color="brown"
                    id="quit-button"
                    style={{ fontSize: "1.5rem", borderRadius: "20px" }}
                    onClick={async () => {
                      sessionStorage.setItem("session_id", undefined);
                      navigator("../", { relative: "path" });
                      setUser(null);
                      if (youAreLogged) await users_api.signout();
                      setYouAreLogged(false);
                    }}
                    variant="contained"
                  >
                    <div style={{ marginTop: "5px", marginBottom: "5px" }}>
                      <HighlightOffIcon
                        style={{ marginRight: "10px", marginTop: "-3px" }}
                        fontSize="large"
                      />
                      <span>Quit</span>
                    </div>
                  </Button>
                </div>
              </>
            )}
          </div>
        </ThemeProvider>
      </div>
    </div>
  );
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
  setUser: PropTypes.func,
  setRoomId: PropTypes.func,
  user: PropTypes.string,
  setYouAreLogged: PropTypes.func,
  youAreLogged: PropTypes.bool,
  setElo: PropTypes.func,
  setEnemyUsername: PropTypes.func,
};

export default Start;
