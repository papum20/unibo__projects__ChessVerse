import { API } from "../const/const_api.js";


export function parseCredentialsLogin(obj) {
	return Object.fromEntries(
		API.login.data
			.map(field_name => [field_name, obj[field_name]] )
	);
}

export function parseCredentialsSignup(obj) {
	return Object.fromEntries(
		API.signup.data
			.map(field_name => [field_name, obj[field_name]] )
	);
}