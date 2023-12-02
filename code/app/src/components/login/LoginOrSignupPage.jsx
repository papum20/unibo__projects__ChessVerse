/*
	a simple page that contains the login or signup card
*/

import { Container } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import LoginOrSignupCard from './LoginOrSignupCard.jsx';
import { parseResponseLogin, parseResponseSignup } from '../../models/api_responses.js';



function LoginOrSignupPage() {
	

	function onLoginSuccessful(data) {
		
		data = parseResponseLogin(data);
		console.log("Logged in!");
		console.log("res:", data);
	}
	
	function onSignupSuccessful(data) {
		
		data = parseResponseSignup(data);
		console.log("Signed up!");
		console.log("res:", data);
	}

    return (
        <Container className="login-signup-page d-flex align-items-center justify-content-center">

            <LoginOrSignupCard
				onLoginSuccessful={onLoginSuccessful}
				onSignupSuccessful={onSignupSuccessful}
			/>

        </Container>
    );

}

export default LoginOrSignupPage;