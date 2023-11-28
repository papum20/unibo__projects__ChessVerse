
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Card, Form, Button } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';
import * as users_api from "../../network/users_api";
import PropTypes from "prop-types";



/**
 * A card component for login or signup.
 * It contains a login/signup form.
 *
 * @param {Object} props - The properties passed to the component.
 * @param {Function} props.onLoginSuccessful - Callback called on login or signup successful.
 * 	@param {string} props.onLoginSuccessful.username - The username of the logged-in or signed-up user.
 */
function LoginOrSignupCard({ onLoginSuccessful }) {

	const { register, handleSubmit, formState: {errors} } = useForm();
	
    const [isLogin, setIsLogin] = useState(true);


	
	async function onSubmit(credentials) {

		console.log("sending these credentials obtained from the form:", credentials);
		console.log("is login:", isLogin);

		try {
			const newUser = await (isLogin
				? users_api.login(credentials)
				: users_api.signup(credentials)
			);

			onLoginSuccessful(newUser);
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

export default LoginOrSignupCard;
