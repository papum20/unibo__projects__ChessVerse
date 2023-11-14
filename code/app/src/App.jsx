
import loadable from '@loadable/component';
import Alert from "./components/Alert.jsx";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import NoRoute from "./NoRoute.jsx";
import Start from "./components/Start.jsx";

//caricamento Lazy
const Login = loadable(() => import('./components/Login.jsx'));
const Signup = loadable(() => import('./components/Signup.jsx'));
const SinglePlayer = loadable(() => import('./components/SinglePlayer.jsx'));
const MultiPlayer = loadable(() => import('./components/MultiPlayer.jsx'));


function App() {

    var location = useLocation();
    const navigator = useNavigate();


  return (
    <>  
            <Alert/> 
                <Routes location={location} key={location.pathname}>
                    <Route path={`/`} element={<Start/>} />
                    
                    <Route path={`/signin`} element={<Signup  />}/>
                    <Route path={`/login`} element={<Login  />}/>
                    <Route path={`/singlePlayer`} element={<SinglePlayer  />}/>
                    <Route path={`/multiPlayer`} element={<MultiPlayer  />}/>
                    
                    <Route path="*" element={<NoRoute />}/>

                </Routes>
            

		</>
  )
}

export default App
