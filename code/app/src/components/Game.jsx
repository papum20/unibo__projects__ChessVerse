import ImageScacchi from "../assets/logo.png";
import { Chess } from "chess.js";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Card, Col, Image, Modal, Nav, Row, Offcanvas } from "react-bootstrap";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { Gear, ExclamationDiamond, Clipboard } from "react-bootstrap-icons";
import { Button } from "@mui/material";
import "../styles/Game.css";
import useWindowDimensions from "./useWindowDimensions.jsx";
import {
  PVP,
  PVE,
  DAILY,
  WEEKLY,
  RANKED,
  RANKED_SCORE_LOSS,
  RANKED_SCORE_WIN,
  RANKED_SCORE_TIE,
  MOBILEWIDTH,
} from "../const/const.js";
import ImageBlackTime from "../assets/blackTime.png";
import ImageWhiteTime from "../assets/whiteTime.png";
import Board from "./Board.jsx";
import PropTypes from "prop-types";
import Social from "./Social.jsx";
import { FaCrown } from "react-icons/fa";
import { propTypes } from "react-bootstrap/esm/Image.js";

function Game({
  gameTime,
  isLoadingGame,
  socket,
  setSocket,
  data,
  mode,
  startFen,
  color,
  roomId,
  user,
  elo,
  enemyUsername,
  rank,
}) {
  const { width, height } = useWindowDimensions();

  const [fontSize, setFontSize] = useState("20px");

  useLayoutEffect(() => {
    if (width < 440) setFontSize("18px");
    else if (width > 440 && width < 540) setFontSize("22px");
    else setFontSize("26px");
  }, [width]);

  const defaultTime = new Date();
  defaultTime.setSeconds(defaultTime.getSeconds() + gameTime);

  const navigator = useNavigate();
  const [moves, setMoves] = useState([]);
  const [showModalMenu, setShowModalMenu] = useState(false);
  const [showEndGame, setShowEndGame] = useState(false);
  const [timers, setTimers] = useState([gameTime, gameTime]);
  const [timerInterval, setTimerInterval] = useState(null);
  const [turn, setTurn] = useState(null);
  const [game, setGame] = useState(new Chess(""));
  const [position, setPosition] = useState("");
  const movesRef = useRef(null);
  const [timerOut, setTimerOut] = useState(false);

  useEffect(() => {
    if (turn !== null && !isLoadingGame) {
      const interval = 100;

      if (timerInterval !== null) clearInterval(timerInterval);
      setTimerInterval(
        setInterval(() => {
          if (timers)
            setTimers((prevTime) => {
              const updatedTime = [...prevTime];
              updatedTime[Number(game.turn() === "b")] -= interval / 1000;
              return updatedTime;
            });
          }, interval),
      );
    }

    return () => {
      clearInterval(timerInterval);
      setTimerInterval(null);
    };
  }, [turn, isLoadingGame]);

  var location = useLocation();

  useEffect(() => {
    if (timers && (timers[0] <= 1 || timers[1] <= 1)) {
      clearInterval(timerInterval);
      setTimerInterval(null);
    }
  }, [timers]);

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

  function handleUndo() {
    socket.emit("pop", { type: mode, id: roomId });
  }

  useEffect(() => {
    movesRef?.current?.scrollTo({
      top: movesRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [moves]);

  //questo useEffect serve a fare in modo che se refreshi game ti fa tornare al menu
  useEffect(() => {
    if (socket === null) {
      navigator(`../`, { relative: "path" });
      sessionStorage.setItem("session_id", undefined);
    } else if (socket === undefined) {
      navigator(`../options`, { relative: "path" });
    }
  }, [socket]);

  const [modalType, setModalType] = useState(null);
  const [numMoves, setNumMoves] = useState(0);
  const [showCanvas, setShowCanvas] = useState(false);

  return (
    <div data-testid="game">
      <Offcanvas
        style={{ backgroundColor: "#b6884e" }}
        show={showCanvas}
        onHide={() => setShowCanvas(false)}
      >
        <ThemeProvider theme={theme}>
          <Offcanvas.Header closeButton>
            <Offcanvas.Title style={{ fontWeight: "bold" }}>
              Moves History
            </Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body
            ref={width < MOBILEWIDTH ? movesRef : null}
            style={{
              overflow: "auto",
              height: `calc(${height}px / 2)`,
              marginLeft: "20px",
              overflowY: "auto",
            }}
          >
            <Row>
              <Col xs={2} sm={2}>
                {moves.map((el, i) => {
                  if (el.index % 2 === 0) {
                    return (
                      <span
                        style={{
                          fontWeight: "bold",
                          display: "flex",
                          alignItems: "center",
                          paddingTop: "8px",
                          paddingBottom: "8px",
                          marginBottom: "10px",
                        }}
                        key={i}
                      >
                        {Math.floor(el.index / 2) + 1}.
                      </span>
                    );
                  }
                })}
              </Col>
              <Col xs={5} sm={5}>
                {moves.map((el, i) => {
                  if (el.index % 2 === 0) {
                    return (
                      <Card
                        style={{
                          marginBottom: "10px",
                          backgroundColor: "#9f7a48",
                          border: `${
                            el.isUndo ? "3px solid red" : "3px solid white"
                          }`,
                          display: "flex",
                          alignItems: "center",
                        }}
                        key={i}
                      >
                        <span
                          style={{
                            paddingTop: "5px",
                            paddingBottom: "5px",
                          }}
                        >
                          {el.move}
                        </span>
                      </Card>
                    );
                  }
                })}
              </Col>
              <Col xs={5} sm={5}>
                {moves.map((el, i) => {
                  if (el.index % 2 === 1) {
                    return (
                      <Card
                        style={{
                          marginBottom: "10px",
                          backgroundColor: "#9f7a48",
                          border: `${
                            el.isUndo ? "3px solid red" : "3px solid black"
                          }`,
                          display: "flex",
                          alignItems: "center",
                        }}
                        key={i}
                      >
                        <span
                          style={{
                            paddingTop: "5px",
                            paddingBottom: "5px",
                          }}
                        >
                          {el.move}
                        </span>
                      </Card>
                    );
                  }
                })}
              </Col>
            </Row>
            <Row>
              <div style={{ paddingTop: "20px" }}>
                <Button
                  disabled={moves.length === 0}
                  color="brown"
                  style={{ width: "100%", fontSize: `${fontSize}` }}
                  onClick={handleUndo}
                  variant="contained"
                >
                  Undo
                </Button>
              </div>
            </Row>
          </Offcanvas.Body>
        </ThemeProvider>
      </Offcanvas>

      <Modal show={showEndGame} centered dialogClassName="my-modal">
        <div
          style={{
            border: `${
              modalType === "gameover"
                ? "4px solid red"
                : modalType === "won"
                  ? "4px solid green"
                  : "4px solid gray"
            }`,
          }}
        >
          <Modal.Body style={{ backgroundColor: "#b6884e" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                fontSize: `${fontSize}`,
              }}
            >
              <span style={{ fontWeight: "bold", marginRight: "10px" }}>{`${
                modalType === "gameover"
                  ? "Game Over"
                  : modalType === "won"
                    ? "You won!"
                    : "It's a tie!"
              }`}</span>
              <ExclamationDiamond
                size={40}
                color={`${
                  modalType === "gameover"
                    ? "red"
                    : modalType === "won"
                      ? "green"
                      : "gray"
                }`}
              />
            </div>
            {timerOut && (
              <p
                style={{
                  display: "flex",
                  justifyContent: "center",
                  width: "100%",
                  marginTop: "20px",
                  fontSize: "22px",
                }}
              >
                Time has run out!
              </p>
            )}
            {mode === RANKED && (
              <p
                style={{
                  display: "flex",
                  justifyContent: "center",
                  width: "100%",
                  marginTop: "20px",
                  fontSize: "22px",
                }}
              >
                {modalType === "gameover"
                  ? "- 2"
                  : modalType === "won"
                    ? "+ 8"
                    : "+ 0"}
                <FaCrown
                  style={{
                    marginTop: "2px",
                    color: "yellow",
                    marginRight: "5px",
                    marginLeft: "5px",
                  }}
                  size="25"
                />
              </p>
            )}
            <div
              style={{
                display: "flex",
                justifyContent: "space-around",
                marginTop: "40px",
                marginBottom: "15px",
              }}
            >
              <ThemeProvider theme={theme}>
                <Nav.Link as={Link} to={"/options"}>
                  <Button
                    style={{ fontSize: "1.2rem" }}
                    size="large"
                    color="brown"
                    onClick={() => {
                      socket.emit("resign", { type: mode, id: roomId });
                      setSocket(null);
                      setGame(null);
                      setModalType(null);
                    }}
                    variant="contained"
                  >
                    Return to menu
                  </Button>
                </Nav.Link>
                <div style={{ marginTop: "10px" }}>
                  <Social
                    url={import.meta.env.VITE_APP_HOST + location.pathname}
                    modalType={modalType}
                    enemyUser={enemyUsername}
                    diff={`${
                      mode === PVE
                        ? data.depth
                        : mode === DAILY || mode === WEEKLY
                          ? `${Math.floor(numMoves / 2) + 1}`
                          : mode === RANKED
                            ? `${rank}`
                            : `${color === "white" ? elo[0] : elo[1]}`
                    }`}
                    mode={mode}
                  />
                </div>
              </ThemeProvider>
            </div>
          </Modal.Body>
        </div>
      </Modal>

      <Modal show={showModalMenu} centered dialogClassName="my-modal">
        <Modal.Body
          style={{ backgroundColor: "#b6884e", fontSize: `${fontSize}` }}
        >
          <div style={{ display: "flex", justifyContent: "center" }}>
            <p>Are you sure you want to go back</p>
          </div>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <p>to the main menu?</p>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              marginTop: "20px",
              marginBottom: "15px",
            }}
          >
            <ThemeProvider theme={theme}>
              <Button
                style={{ fontSize: "1.2rem" }}
                size="large"
                color="brown"
                onClick={() => setShowModalMenu(false)}
                variant="contained"
              >
                No
              </Button>

              <Nav.Link
                as={Link}
                to="/options"
                style={{ display: "flex", justifyContent: "center" }}
              >
                <Button
                  style={{ fontSize: "1.2rem" }}
                  size="large"
                  color="brown"
                  onClick={() => {
                    socket.emit("resign", { type: mode, id: roomId });
                    setSocket(undefined);
                    setPosition("");
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

      <div
        style={{
          backgroundColor: "#b99b69",
          width: "100vw",
          height: "100vh",
          overflow: "auto",
          overflowX: "hidden",
        }}
      >
        <ThemeProvider theme={theme}>
          <div style={{ paddingTop: "10px", paddingLeft: "10px" }}>
            <Row>
              <Col>
                <Row style={{ marginBottom: "20px" }}>
                  <Col
                    style={{
                      display: "flex",
                      justifyContent: `${
                        width < MOBILEWIDTH ? "center" : "flex-end"
                      }`,
                    }}
                  >
                    <Image
                      src={`${ImageScacchi}`}
                      style={{ width: "50px", height: "50px", opacity: 0.8 }}
                      alt="immagine di scacchi"
                    />
                    <span
                      style={{
                        color: "white",
                        fontSize: `${width < MOBILEWIDTH ? "2rem" : "2.7rem"}`,
                      }}
                    >
                      ChessVerse
                    </span>
                  </Col>
                </Row>
              </Col>
              <Col
                style={{
                  display: "flex",
                  justifyContent: `${
                    width < MOBILEWIDTH ? "space-between" : "flex-end"
                  }`,
                  marginRight: "40px",
                }}
              >
                <Button
                  color="brown"
                  onClick={() => setShowModalMenu(true)}
                  variant="contained"
                >
                  <Gear size={30} />
                </Button>
                {width < MOBILEWIDTH && (
                  <Button
                    color="brown"
                    onClick={() => setShowCanvas(true)}
                    variant="contained"
                  >
                    <Clipboard size={30} />
                  </Button>
                )}
              </Col>
            </Row>
          </div>
          <Row>
            {!isLoadingGame && (
              <Col>
                <div
                  style={{
                    marginTop: "40px",
                    marginLeft: "150px",
                    marginBottom: "10px",
                  }}
                >
                  <span style={{ fontWeight: "bold" }}>
                    {mode === PVE ? "Stockfish" : enemyUsername}
                  </span>
                  {mode === PVP && (
                    <>
                      <span
                        style={{ fontWeight: "bold", marginLeft: "3px" }}
                      >{`(${
                        color === "white"
                          ? elo[0]
                          : color === "black"
                            ? elo[1]
                            : ""
                      })`}</span>

                      <img
                        src={`${
                          color === "black" ? ImageWhiteTime : ImageBlackTime
                        }`}
                        alt={`${
                          color === "black" ? "clock white" : "clock black"
                        }`}
                        style={{
                          maxWidth: "30px",
                          maxHeight: "30px",
                          marginTop: "-6px",
                          marginLeft: "10px",
                        }}
                      />
                      <span>{`${String(
                        Math.floor(timers[Number(color === "white")] / 60),
                      ).padStart(2, "0")}:${String(
                        Math.floor(timers[Number(color === "white")] % 60),
                      ).padStart(2, "0")}`}</span>
                    </>
                  )}
                </div>
              </Col>
            )}
          </Row>
          <Row>
            <Col>
              <div
                style={{
                  display: "flex",
                  justifyContent: `${
                    width < MOBILEWIDTH ? "center" : "flex-start"
                  }`,
                  marginLeft: `${width < MOBILEWIDTH ? "0px" : "150px"}`,
                }}
              >
                <div>
                  <Board
                    navigator={navigator}
                    width={width}
                    height={height}
                    setShowEndGame={setShowEndGame}
                    setModalType={setModalType}
                    moves={moves}
                    setMoves={setMoves}
                    data={data}
                    isLoadingGame={isLoadingGame}
                    socket={socket}
                    setSocket={setSocket}
                    mode={mode}
                    startFen={startFen}
                    color={color}
                    setTurn={setTurn}
                    setTimers={setTimers}
                    roomId={roomId}
                    game={game}
                    setGame={setGame}
                    position={position}
                    setPosition={setPosition}
                    setNumMoves={setNumMoves}
                    setTimerOut={setTimerOut}
                  />
                </div>
              </div>
            </Col>
            {width >= MOBILEWIDTH && (
              <Col style={{ maxWidth: "30vw" }}>
                <Row>
                  <Col>
                    <Card
                      style={{
                        backgroundColor: "#b6884e",
                        marginTop: "4vh",
                        marginRight: "80px",
                        marginLeft: "-50px",
                      }}
                    >
                      <Card.Title
                        style={{ display: "flex", justifyContent: "center" }}
                      >
                        <p
                          style={{
                            fontWeight: "bold",
                            fontSize: `${fontSize}`,
                            marginTop: "5px",
                          }}
                        >
                          Moves History
                        </p>
                      </Card.Title>
                      <Card.Body
                        ref={width >= MOBILEWIDTH ? movesRef : null}
                        style={{
                          overflow: "auto",
                          height: `calc(${height}px / 2)`,
                          marginLeft: "20px",
                          marginBottom: "20px",
                          overflowY: "auto",
                        }}
                      >
                        <Row>
                          <Col sm={2}>
                            {moves.map((el, i) => {
                              if (el.index % 2 === 0) {
                                return (
                                  <span
                                    style={{
                                      fontWeight: "bold",
                                      display: "flex",
                                      alignItems: "center",
                                      paddingTop: "8px",
                                      paddingBottom: "8px",
                                      marginBottom: "10px",
                                    }}
                                    key={i}
                                  >
                                    {Math.floor(el.index / 2) + 1}.
                                  </span>
                                );
                              }
                            })}
                          </Col>
                          <Col sm={5}>
                            {moves.map((el, i) => {
                              if (el.index % 2 === 0) {
                                return (
                                  <Card
                                    style={{
                                      marginBottom: "10px",
                                      backgroundColor: "#9f7a48",
                                      border: `${
                                        el.isUndo
                                          ? "3px solid red"
                                          : "3px solid white"
                                      }`,
                                      display: "flex",
                                      alignItems: "center",
                                    }}
                                    key={i}
                                  >
                                    <span
                                      style={{
                                        paddingTop: "5px",
                                        paddingBottom: "5px",
                                      }}
                                    >
                                      {el.move}
                                    </span>
                                  </Card>
                                );
                              }
                            })}
                          </Col>
                          <Col sm={5}>
                            {moves.map((el, i) => {
                              if (el.index % 2 === 1) {
                                return (
                                  <Card
                                    style={{
                                      marginBottom: "10px",
                                      backgroundColor: "#9f7a48",
                                      border: `${
                                        el.isUndo
                                          ? "3px solid red"
                                          : "3px solid black"
                                      }`,
                                      display: "flex",
                                      alignItems: "center",
                                    }}
                                    key={i}
                                  >
                                    <span
                                      style={{
                                        paddingTop: "5px",
                                        paddingBottom: "5px",
                                      }}
                                    >
                                      {el.move}
                                    </span>
                                  </Card>
                                );
                              }
                            })}
                          </Col>
                        </Row>
                        <Row>
                          <div style={{ paddingTop: "20px" }}>
                            <Button
                              disabled={moves.length === 0}
                              color="brown"
                              style={{ width: "100%", fontSize: `${fontSize}` }}
                              onClick={handleUndo}
                              variant="contained"
                            >
                              Undo
                            </Button>
                          </div>
                        </Row>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Col>
            )}
          </Row>
          <Row>
            {!isLoadingGame && (
              <Col
                style={{
                  display: "flex",
                  justifyContent: "center",
                  marginTop: "10px",
                  marginRight: `${width < MOBILEWIDTH ? "" : "25vw"}`,
                }}
              >
                <span style={{ marginRight: "15px", fontWeight: "bold" }}>
                  {user}
                </span>
                {mode === PVP && (
                  <span
                    style={{
                      fontWeight: "bold",
                      marginLeft: "3px",
                      marginRight: "3px",
                    }}
                  >
                    {`(${
                      color === "white"
                        ? elo[1]
                        : color === "black"
                          ? elo[0]
                          : ""
                    })`}
                  </span>
                )}
                {(mode === PVE || mode === PVP) && (
                  <>
                    <img
                      src={`${
                        color === "white" || color === undefined
                          ? ImageWhiteTime
                          : ImageBlackTime
                      }`}
                      alt={`${
                        color === "white" || color === undefined
                          ? "clock white"
                          : "clock black"
                      }`}
                      style={{
                        maxWidth: "30px",
                        maxHeight: "30px",
                        marginTop: "-6px",
                      }}
                    />
                    <span>
                      {`${timers?String(
                        Math.floor(timers[Number(color === "black")] / 60),
                      ).padStart(2, "0"):""}:${timers?String(
                        Math.floor(timers[Number(color === "black")] % 60),
                      ).padStart(2, "0"):""}`}
                    </span>
                  </>
                )}
                {mode === RANKED && (
                  <>
                    <FaCrown
                      style={{ marginTop: "-4px", color: "yellow" }}
                      size="25"
                    />
                    <span style={{ marginLeft: "5px" }}>{rank}</span>
                  </>
                )}
              </Col>
            )}
          </Row>
        </ThemeProvider>
      </div>
    </div>
  );
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
  roomId: PropTypes.string,
  user: PropTypes.string,
  elo: PropTypes.array,
  enemyUsername: PropTypes.string,
  rank: PropTypes.number,
};

export default Game;
