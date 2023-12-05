
import PropTypes from "prop-types";
import { useState } from 'react';
import { Button, Card, Form } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { parseCredentialsLogin, parseCredentialsSignup } from '../../models/credentials';
import * as users_api from "../../network/users_api";
import '../../styles/LoginOrSignupPage.css';
import LoginButtonFacebook from './LoginButtonFacebook';


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

					
			console.log("Logged in!");
			console.log("res:", res);
			
			if(isLogin)
				onLoginSuccessful(credential_parsed.username, "");
			else
				onSignupSuccessful(credential_parsed.username, "");
			
		} catch (error) {
			console.error("Error:", error);
			alert(error);
		}
	}


    return (
            <Card className="login-signup-card">
                <Card.Body>
                    <h1 className="text-center">{isLogin ? 'Login' : 'Sign Up'}</h1>

					{/*
						fields form
					*/}

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
						
						{ !isLogin && 
							<>
								<Form.Group controlId="formElo1">
									<Form.Label>Elo ReallyBadChess</Form.Label>
									<Form.Control name="elo1" placeholder="Elo ReallyBadChess" type="number" 
										{...register("elo1", { required: true })}
									/>
									{errors.elo1 && <span>This field is required</span>}
								</Form.Group>

								<Form.Group controlId="formElo2">
									<Form.Label>Elo ??</Form.Label>
									<Form.Control name="elo2" placeholder="Elo ??" type="number" 
										{...register("elo2", { required: true })}
										/>
									{errors.elo2 && <span>This field is required</span>}
								</Form.Group>
							</>
						}

                        <Button id="buttonSubmit" className="mt-3" block="true" type="submit" variant="primary">
                            {isLogin ? 'Login' : 'Sign Up'}
                        </Button>
                    </Form>

					{/*
						switch login/signup
					*/}

                    <Button id="buttonSwitchLoginSignup" block="true" type="submit" variant="link"
						onClick={() => setIsLogin(!isLogin)}
						>
						<strong>
							{ isLogin
								? "Don't have an account? Sign Up"
								: "Already have an account? Login"
							}
						</strong>
                    </Button>


					{/*
						fb
					*/}
					
					<LoginButtonFacebook />

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
