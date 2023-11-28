
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
		]
	},
	signout : {
		endpoint: "signout",
		method: "",
		codes : {
			"ok" : 200
		},
		data : [
			"username",
			"password"
		]
	},
	signup : {
		endpoint : "signup",
		method : "POST",
		codes : {
			"ok" : 200,
			"bad request" : 400,
			"internal server error" : 500
		}
	}
};