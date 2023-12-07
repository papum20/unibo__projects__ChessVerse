import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import {Routes, Route, useLocation} from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import {useEffect, useState} from 'react';
import {DEFAULT_GAME_TIME, MIN_BOT_DIFF, MIN_GAME_IMB} from "./const/const.js";
import LoginOrSignupPage from './components/login/LoginOrSignupPage.jsx';
import AppNavbar from './components/AppNavbar.jsx';

//caricamento Lazy
const Game = loadable(() => import('./components/Game.jsx'));

function App() {
  const location = useLocation();

  const [mode, setMode] = useState(0);
  const [gameImb, setGameImb] = useState(MIN_GAME_IMB);
  const [botDiff, setBotDiff] = useState(MIN_BOT_DIFF);
  const [gameTime, setGameTime] = useState(DEFAULT_GAME_TIME);
  const [socket, setSocket] = useState(null);
  const [isLoadingGame, setIsLoadingGame] = useState(false);
  const [data, setData] = useState({});
  const [startFen, setStartFen] = useState(null);
  const [roomId, setRoomId] = useState(null);
  const [color, setColor] = useState("white");


  useEffect(() => {
    setData({
      type: mode,
      rank: gameImb,
      time: gameTime,
      depth: botDiff
    })
  }, [mode, gameImb, gameTime, botDiff])



  /* user data */
  const [user, setUser] = useState(null);

  const handleSignOut = () => {
	// Sign the user out
	setUser(null);
  };


  return (
    <div data-testid="appPage">
      <Alert data-testid="alertDiv"/>

		<AppNavbar 
			user={user}
			onSignOut={handleSignOut}
		/>
		
      <Routes location={location} key={location.pathname} data-testid="toGame">
		
        <Route path={`/`} element={
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

          />
        }/>

       
        <Route
          path={`/game`}
          element={
            <Game
              data={data}
              isLoadingGame={isLoadingGame}
              setIsLoadingGame={setIsLoadingGame}
              socket={socket}
              setSocket={setSocket}
              mode={mode}
              gameTime={gameTime}
              startFen={startFen}
              color={color}
              roomId={roomId}
            />
          }
          data-testid="game"
        />
		<Route
			path={`/login`}
			element={
				<LoginOrSignupPage
					setUser={setUser}
				/>
			}
		/>

        <Route path="*" element={<NoRoute/>}/>
      </Routes>

    </div>
  )
}

export default App