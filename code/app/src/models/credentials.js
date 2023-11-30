
export function parseCredentialsLogin(obj) {
	return {
		username: obj.username,
		password: obj.password
	};
}

export function parseCredentialsSignup(obj) {
	return {
		username: obj.username,
		password: obj.password,
		elo1: obj.elo1,
		elo2: obj.elo2
	};
}