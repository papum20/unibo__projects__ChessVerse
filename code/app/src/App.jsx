import loadable from "@loadable/component";
import Alert from "./components/Alert.jsx";
import { Routes, Route, useLocation } from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import { useEffect, useState } from "react";
import {
  DEFAULT_GAME_TIME,
  MIN_BOT_DIFF,
  MIN_GAME_IMB,
} from "./const/const.js";
import LoginOrSignupPage from "./components/login/LoginOrSignupPage.jsx";

//caricamento Lazy
const Game = loadable(() => import("./components/Game.jsx"));

function App() {
  const location = useLocation();

  const [mode, setMode] = useState(0);
  const [gameImb, setGameImb] = useState(MIN_GAME_IMB);
  const [botDiff, setBotDiff] = useState(MIN_BOT_DIFF);
  const [gameTime, setGameTime] = useState(DEFAULT_GAME_TIME);
  const [socket, setSocket] = useState(null);
  const [isLoadingGame, setIsLoadingGame] = useState(true);
  const [data, setData] = useState({});
  const [startFen, setStartFen] = useState(null);
  const [roomId, setRoomId] = useState(null);
  const [color, setColor] = useState("white");
  const [user, setUser] = useState(null);
  const [enemyUsername, setEnemyUsername] = useState("");
  const [elo, setElo] = useState([0, 0]);
  const [rank, setRank] = useState(0);

  const [youAreLogged, setYouAreLogged] = useState(false);

  useEffect(() => {
    setData({
      type: mode,
      rank: gameImb,
      time: gameTime,
      depth: botDiff,
    });
  }, [mode, gameImb, gameTime, botDiff]);

  return (
    <div data-testid="appPage">
      <Alert data-testid="alertDiv" />

      <Routes location={location} key={location.pathname} data-testid="toGame">
        <Route
          path={`/`}
          element={
            <Start
              mode={mode}
              setMode={setMode}
              gameImb={gameImb}
              setGameImb={setGameImb}
              botDiff={botDiff}
              setBotDiff={setBotDiff}
              gameTime={gameTime}
              setGameTime={setGameTime}
              setSocket={setSocket}
              socket={socket}
              setIsLoadingGame={setIsLoadingGame}
              data={data}
              setStartFen={setStartFen}
              setRoomId={setRoomId}
              setColor={setColor}
              setUser={setUser}
              user={user}
              setYouAreLogged={setYouAreLogged}
              youAreLogged={youAreLogged}
              setEnemyUsername={setEnemyUsername}
              setElo={setElo}
              setRank={setRank}
            />
          }
        />

        <Route
          path={`/options`}
          element={
            <Start
              mode={mode}
              setMode={setMode}
              gameImb={gameImb}
              setGameImb={setGameImb}
              botDiff={botDiff}
              setBotDiff={setBotDiff}
              gameTime={gameTime}
              setGameTime={setGameTime}
              setSocket={setSocket}
              socket={socket}
              setIsLoadingGame={setIsLoadingGame}
              data={data}
              setStartFen={setStartFen}
              setRoomId={setRoomId}
              setColor={setColor}
              setUser={setUser}
              user={user}
              setYouAreLogged={setYouAreLogged}
              youAreLogged={youAreLogged}
              setEnemyUsername={setEnemyUsername}
              setElo={setElo}
              setRank={setRank}
            />
          }
        />

        <Route
          path={`/game`}
          element={
            <Game
              data={data}
              isLoadingGame={isLoadingGame}
              socket={socket}
              setSocket={setSocket}
              mode={mode}
              gameTime={gameTime}
              startFen={startFen}
              color={color}
              roomId={roomId}
              user={user}
              elo={elo}
              enemyUsername={enemyUsername}
              rank={rank}
            />
          }
          data-testid="game"
        />
        <Route
          path={`/login`}
          element={
            <LoginOrSignupPage
              isLogin={true}
              setUser={setUser}
              setYouAreLogged={setYouAreLogged}
            />
          }
        />

        <Route
          path={`/signup`}
          element={<LoginOrSignupPage isLogin={false} setUser={setUser} />}
        />

        <Route path="*" element={<NoRoute />} />
      </Routes>
    </div>
  );
}

export default App;
