/*
	a simple page that contains the login or signup card
*/

import { Container } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import LoginOrSignupCard from './LoginOrSignupCard.jsx';



function LoginOrSignupPage() {
	

	function onLoginSuccessful(username) {
		console.log(username + "was logged in!");
	}

    return (
        <Container className="login-signup-page d-flex align-items-center justify-content-center">

            <LoginOrSignupCard
				onLoginSuccessful={onLoginSuccessful}
			/>

        </Container>
    );

}

export default LoginOrSignupPage;