import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import {Routes, Route, useLocation} from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import {useEffect, useState} from 'react';
import {DEFAULT_GAME_TIME, MIN_BOT_DIFF, MIN_GAME_IMB} from "./Const.js";
import LoginOrSignupPage from './components/login/LoginOrSignupPage.jsx';
import AppNavbar from './components/AppNavbar.jsx';

//caricamento Lazy
const Login = loadable(() => import('./components/Login.jsx'));
const Game = loadable(() => import('./components/Game.jsx'));

function App() {
  const location = useLocation();

  const [isSinglePlayer, setIsSinglePlayer] = useState(false);
  const [gameImb, setGameImb] = useState(MIN_GAME_IMB);
  const [botDiff, setBotDiff] = useState(MIN_BOT_DIFF);
  const [gameTime, setGameTime] = useState(DEFAULT_GAME_TIME);
  const [socket, setSocket] = useState(null);
  const [isLoadingGame, setIsLoadingGame] = useState(false);
  const [data, setData] = useState({});

  useEffect(() => {
    setData({
      type: isSinglePlayer,
      rank: gameImb,
      time: gameTime,
      depth: botDiff
    })
  }, [isSinglePlayer, gameImb, gameTime, botDiff])



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
            isSinglePlayer={isSinglePlayer}
            setIsSinglePlayer={setIsSinglePlayer}
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
          />
        }/>

        {/* Ancora da implementare
                    <Route path={`/signin`} element={<Login  />} data-testid="signIn"/>
                    <Route path={`/login`} element={<Login  />} data-testid="logIn" />
                    */}

        <Route
          path={`/game`}
          element={
            <Game
              data={data}
              isLoadingGame={isLoadingGame}
              setIsLoadingGame={setIsLoadingGame}
              socket={socket}
              setSocket={setSocket}
              isSinglePlayer={isSinglePlayer}
              gameImb={gameImb}
              botDiff={botDiff}
              gameTime={gameTime}
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