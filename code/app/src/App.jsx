
import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import { Routes, Route, useLocation } from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import { useEffect, useState } from 'react';


//caricamento Lazy
const Login = loadable(() => import('./components/Login.jsx'));
const Signup = loadable(() => import('./components/Signup.jsx'));
const Game = loadable(() => import('./components/Game.jsx'));


function App() {

    var location = useLocation();

    const [isSinglePlayer, setIsSinglePlayer] = useState(false);
    const [gameImb, setGameImb] = useState(0);
    const [botDiff, setBotDiff] = useState(1);
    const [gameTime, setGameTime] = useState(3000);
    const [socket, setSocket] = useState(undefined);
    const [isLoadingGame, setIsLoadingGame] = useState(false);
    const [data, setData] = useState({});


    useEffect(()=>{
      setData({
        type: isSinglePlayer,
        rank: gameImb,
        time: gameTime,
        depth: botDiff
      })


    },[isSinglePlayer, gameImb, gameTime, botDiff])

    



  return (
    <>  
            <Alert/> 
                <Routes location={location} key={location.pathname}>
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
                        data = {data}
                        />
                    }/> 
                    
                    <Route path={`/signin`} element={<Signup  />}/>
                    <Route path={`/login`} element={<Login  />}/>
                    <Route path={`/game`} element={<Game data = {data} isLoadingGame={isLoadingGame}  setIsLoadingGame={setIsLoadingGame} socket={socket} setSocket={setSocket}  isSinglePlayer={isSinglePlayer} gameImb={gameImb} botDiff={botDiff} gameTime={gameTime}/>}/>
                    
                    <Route path="*" element={<NoRoute />}/>

                </Routes>
            

		</>
  )
}

export default App
