/*
	a card that contains a login or signup form
*/

import { useState } from 'react';
import { Card, Form, Button } from 'react-bootstrap';
import '../../styles/LoginOrSignupPage.css';



function LoginOrSignupCard() {
	
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        // Handle form submission here...
    };

    return (
            <Card className="login-signup-card">
                <Card.Body>
                    <h1 className="text-center">{isLogin ? 'Login' : 'Sign Up'}</h1>

                    <Form className="mb-3"
						onSubmit={handleSubmit}
					>
                        <Form.Group controlId="formUsername">
                            <Form.Label>Username</Form.Label>
                            <Form.Control type="text" placeholder="Enter username" value={username} onChange={(e) => setUsername(e.target.value)} />
                        </Form.Group>

                        <Form.Group controlId="formPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        </Form.Group>

                        <Button className="mt-3" block type="submit" variant="primary">
                            {isLogin ? 'Login' : 'Sign Up'}
                        </Button>
                    </Form>

                    <Button block type="submit" variant="link"
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