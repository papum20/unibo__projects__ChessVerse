
import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";
import { useState } from 'react';


//caricamento Lazy
const Login = loadable(() => import('./components/Login.jsx'));
const Signup = loadable(() => import('./components/Signup.jsx'));
const Game = loadable(() => import('./components/Game.jsx'));


function App() {

    var location = useLocation();
    const navigator = useNavigate();

    const [isSinglePlayer, setIsSinglePlayer] = useState(false);

  return (
    <>  
            <Alert/> 
                <Routes location={location} key={location.pathname}>
                    <Route path={`/`} element={<Start setIsSinglePlayer={setIsSinglePlayer}/>} />
                    
                    <Route path={`/signin`} element={<Signup  />}/>
                    <Route path={`/login`} element={<Login  />}/>
                    <Route path={`/game`} element={<Game  isSinglePlayer={isSinglePlayer}/>}/>
                    
                    <Route path="*" element={<NoRoute />}/>

                </Routes>
            

		</>
  )
}

export default App
