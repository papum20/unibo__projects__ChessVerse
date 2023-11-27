/*
	a card that contains a login or signup form
*/

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Card, Form, Button } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';



function LoginOrSignupCard() {

	const { register, handleSubmit, formState: {errors} } = useForm();
	
    const [isLogin, setIsLogin] = useState(true);


	
	async function onSubmit(credentials) {
		console.log(credentials.username);
		console.log(credentials.password);
		/*try {
			const newUser = await NotesApi.signUp(credentials);
			onSignUpSuccessful(newUser);
		} catch (error) {
			if(error instanceof ConflictError) {
				setErrorText(error.message);
			} else {
				alert(error);
			}
			console.error(error);
		}*/
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

export default LoginOrSignupCard;