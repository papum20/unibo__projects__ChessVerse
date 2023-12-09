/*
	a simple page that contains the login or signup card.
	for now, it doesnt consider facebook login.
*/


import { Container } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import LoginOrSignupCard from './LoginOrSignupCard.jsx';



function LoginOrSignupPage(props) {
 

    return (
        <Container className="login-signup-page d-flex align-items-center justify-content-center">

            <LoginOrSignupCard
				isLogin = {props.isLogin}

			/>

        </Container>
    );

}



export default LoginOrSignupPage;