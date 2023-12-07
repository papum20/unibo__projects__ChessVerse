
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
		eloReallyBadChess: obj.elo1,
		eloSecondType: obj.elo2
	};
}