import FacebookLogin from '@greatsumini/react-facebook-login';

const LoginButtonFacebook = () => {

	const responseFacebook = (response) => {
		console.log(response);
		// Send the 'response' to your Django backend
	};

	return (
			<FacebookLogin
				appId="655569260099474"
				autoLoad={false}
				fields="name,email,picture"
				callback={responseFacebook}
			/>
	);
};

export default LoginButtonFacebook;