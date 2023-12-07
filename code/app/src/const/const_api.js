/*
 * api specs, e.g. paths, methods, codes, data fields (req/res)
 */

export const API = {
	login : {
		endpoint : "backend/login/",
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
		endpoint: "backend/signout/",
		method: "",
		codes : {
			"ok" : 200
		}
	},
	signup : {
		endpoint : "backend/signup/",
		method : "POST",
		codes : {
			"ok" : 200,
			"bad request" : 400,
			"internal server error" : 500
		},
		data : [
			"username",
			"password",
			"eloReallyBadChess",
			"eloSecondType"
		],
		response : [
			"message"
		]
	}
};