/*
	a simple page that contains the login or signup card
*/

import { Container } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import LoginOrSignupCard from './LoginOrSignupCard.jsx';



function LoginOrSignupPage() {
	

    return (
        <Container className="login-signup-page d-flex align-items-center justify-content-center">

            <LoginOrSignupCard/>

        </Container>
    );

}

export default LoginOrSignupPage;