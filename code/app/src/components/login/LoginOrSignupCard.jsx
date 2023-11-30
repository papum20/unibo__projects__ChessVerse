
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Card, Form, Button } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import * as users_api from "../../network/users_api";
import PropTypes from "prop-types";
import { parseResponseLogin, parseResponseSignup } from '../../models/api_responses';
import { parseCredentialsLogin, parseCredentialsSignup } from '../../models/credentials';



/**
 * A card component for login or signup.
 * It contains a login/signup form.
 *
 * @param {Object} props - The properties passed to the component.
 * @param {Function} props.onLoginSuccessful - Callback called on login or signup successful.
 * 	@param {string} props.onLoginSuccessful.data - The response data json.
 * @param {Function} props.onLoginSuccessful - Callback called on login or signup successful.
 * 	@param {string} props.onLoginSuccessful.data - The response data json.
 */
function LoginOrSignupCard({ onLoginSuccessful, onSignupSuccessful }) {

	const { register, handleSubmit, formState: {errors} } = useForm();
	
    const [isLogin, setIsLogin] = useState(true);


	
	async function onSubmit(credentials) {

		console.log("sending these credentials obtained from the form:", credentials);
		console.log("is login:", isLogin);

		const credential_parsed = (isLogin
			? parseCredentialsLogin(credentials)
			: parseCredentialsSignup(credentials)
		);
		
		try {
			const res = await (isLogin
				? users_api.login(credential_parsed)
				: users_api.signup(credential_parsed)
			);

			if(isLogin)
				onLoginSuccessful(parseResponseLogin(res));
			else
				onSignupSuccessful(parseResponseSignup(res));
			
		} catch (error) {
			console.error("Error:", error);
			alert(error);
		}
	}


    return (
            <Card className="login-signup-card">
                <Card.Body>
                    <h1 className="text-center">{isLogin ? 'Login' : 'Sign Up'}</h1>

                    <Form className="mb-3"
						onSubmit={handleSubmit(onSubmit)}
					>
                        <Form.Group controlId="formUsername">
                            <Form.Label>Username</Form.Label>
                            <Form.Control name="username" placeholder="Enter username" type="text"
								{...register("username", { required: true })}
							/>
							{errors.username && <span>This field is required</span>}
                        </Form.Group>

                        <Form.Group controlId="formPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control name="password" placeholder="Password" type="password" 
								{...register("password", { required: true })}
							/>
							{errors.password && <span>This field is required</span>}
                        </Form.Group>

                        <Button id="buttonSubmit" className="mt-3" block type="submit" variant="primary">
                            {isLogin ? 'Login' : 'Sign Up'}
                        </Button>
                    </Form>

                    <Button id="buttonSwitchLoginSignup" block type="submit" variant="link"
						onClick={() => setIsLogin(!isLogin)}
					>
						<strong>
							{ isLogin
								? "Don't have an account? Sign Up"
								: "Already have an account? Login"
							}
						</strong>
                    </Button>

                </Card.Body>
            </Card>
    );

}

LoginOrSignupCard.propTypes = {
	onLoginSuccessful: PropTypes.func.isRequired
};
LoginOrSignupCard.propTypes = {
	onSignupSuccessful: PropTypes.func.isRequired
};

export default LoginOrSignupCard;
