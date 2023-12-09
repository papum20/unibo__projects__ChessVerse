
import { useState } from 'react';
import { Button, Card, Form, CloseButton } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { parseCredentialsLogin, parseCredentialsSignup } from '../../models/credentials';
import * as users_api from "../../network/users_api";
import '../../styles/LoginOrSignupPage.css';
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";


/**
 * 
 * A card component for login or signup.
 * It contains a login/signup form.
 *
 */
function LoginOrSignupCard(props) {

	const { register, handleSubmit, formState: {errors} } = useForm();
	
    const [isLogin, setIsLogin] = useState(props.isLogin);

	const navigator = useNavigate();

	
	async function onSubmit(credentials) {
		const credential_parsed = (isLogin
			? parseCredentialsLogin(credentials)
			: parseCredentialsSignup(credentials)
		);
		try {
			await (isLogin
				? users_api.login(credential_parsed)
				: users_api.signup(credential_parsed)
			);
			if(!isLogin)
				toast.success("Signed up!", {className: "toast-message"});
		} catch (error) {
			console.error(error);
			toast.error(`${error}`, {className: "toast-message"});
		}
	}


    return (
            <Card className="login-signup-card" style={{color: "white"}}>
                <Card.Body>
					<div style={{display: "flex", justifyContent: "space-between"}}>
						<h1  >{isLogin ? 'Login' : 'Sign Up'}</h1>
						<CloseButton onClick={()=>navigator(`../`, { relative: "path" })} variant="white"/>
					</div>

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
								<Form.Group controlId="formElo1" style={{marginTop: "10px"}}>
									<Form.Label>Elo ReallyBadChess</Form.Label>
									<Form.Control name="eloReallyBadChess" placeholder="Elo ReallyBadChess" type="number"
											{...register("eloReallyBadChess", { required: true })}
									/>
									{errors.eloReallyBadChess && <span>This field is required</span>}
								</Form.Group>


								
							</>
						}

						<div style={{marginTop: "10px", display: "flex", justifyContent: "flex-end"}}>
							<Button id="buttonSubmit" className="mt-3" size="lg"  type="submit" variant="primary" >
									{isLogin ? 'Login' : 'Sign Up'}
							</Button>
						</div>

                    </Form>

					<span size="lg" id="buttonSwitchLoginSignup"  type="submit"
							onClick={() => { isLogin ? navigator(`../signup`, { relative: "path" }) : navigator(`../login`, { relative: "path" }); setIsLogin(!isLogin); }}
							style={{marginTop: "10px", cursor: "pointer"}}
							role="link"
					>
							<strong>
									{ isLogin
											? "Don't have an account? Sign Up"
											: "Already have an account? Login"
									}
							</strong>
                    </span>


                </Card.Body>
            </Card>
    );

}



export default LoginOrSignupCard;
