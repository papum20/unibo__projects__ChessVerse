6
/*
 * api specs, e.g. paths, methods, codes, data fields (req/res)
 */

export const API = {
	login : {
		endpoint : "login",
		method : "POST",
		codes : {
			"ok" : 200,
			"unauthorized" : 401
		},
		data : [
			"username",
			"password"
		],
		response : [
			"message",
			"token"
		]
	},
	signout : {
		endpoint: "signout",
		method: "",
		codes : {
			"ok" : 200
		}
	},
	signup : {
		endpoint : "signup",
		method : "POST",
		codes : {
			"ok" : 200,
			"bad request" : 400,
			"internal server error" : 500
		},
		data : [
			"username",
			"password",
			"elo1",
			"elo2"
		],
		response : [
			"message"
		]
	}
};