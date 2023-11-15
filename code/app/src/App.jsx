
import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import { useEffect, useState } from 'react';


//caricamento Lazy
const Login = loadable(() => import('./components/Login.jsx'));
const Signup = loadable(() => import('./components/Signup.jsx'));
const Game = loadable(() => import('./components/Game.jsx'));


function App() {

    var location = useLocation();
    //const navigator = useNavigate();

    const [isSinglePlayer, setIsSinglePlayer] = useState(false);
    const [gameImb, setGameImb] = useState(0);
    const [botDiff, setBotDiff] = useState(1);
    const [gameTime, setGameTime] = useState(3000);
    const [socket, setSocket] = useState(undefined);

    


  return (
    <>  
            <Alert/> 
                <Routes location={location} key={location.pathname}>
                    <Route path={`/`} element={<Start setIsSinglePlayer={setIsSinglePlayer} gameImb={gameImb} setGameImb={setGameImb} botDiff={botDiff} setBotDiff={setBotDiff}
                                                gameTime={gameTime} setGameTime={setGameTime} setSocket={setSocket} />} />
                    
                    <Route path={`/signin`} element={<Signup  />}/>
                    <Route path={`/login`} element={<Login  />}/>
                    <Route path={`/game`} element={<Game socket={socket}  isSinglePlayer={isSinglePlayer} gameImb={gameImb} botDiff={botDiff} gameTime={gameTime}/>}/>
                    
                    <Route path="*" element={<NoRoute />}/>

                </Routes>
            

		</>
  )
}

export default App
