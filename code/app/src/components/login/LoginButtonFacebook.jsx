import React from 'react';



class LoginButtonFacebook extends React.Component {

	handleLogin = () => {
		window.FB.login(function(response) {
		if (response.authResponse) {
			console.log('Successfully logged in with Facebook');
			console.log("response:", response);
			// TODO: Send the user's access token to your server
		} else {
			console.log('User did not log in with Facebook');
		}
		});
	}

	render() {
		return (
		<button onClick={this.handleLogin}>
			Login with Facebook
		</button>
		);
	}
}

export default LoginButtonFacebook;