/*
	a simple page that contains the login or signup card.
	for now, it doesnt consider facebook login.
*/

import PropTypes from "prop-types";
import { Container } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import LoginOrSignupCard from './LoginOrSignupCard.jsx';



function LoginOrSignupPage({ setUser }) {
 
	function onLoginSuccessful(username, picture) {

		setUser({
			name: username,
			picture: picture
		});
	}
	
	function onSignupSuccessful(username, picture) {
		
		setUser({
			name: username,
			picture: picture
		});
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

LoginOrSignupPage.propTypes = {
	setUser: PropTypes.func.isRequired,
};

export default LoginOrSignupPage;