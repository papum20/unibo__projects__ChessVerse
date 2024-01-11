import { API } from "../const/const_api";
import {
  parseCredentialsLogin,
  parseCredentialsSignup,
} from "../models/credentials";
import { SERVER_ADDR } from "../const/const";
import { joinPaths } from "../utils/path";
import { toast } from "react-toastify";

/**
 * Generical function for fetches.
 * Useful for defining only once generical errors and other handling stuff.
 * @param {*} input
 * @param {*} init
 * @param {obj} api_obj reference to object of API constant object
 * @returns
 */
async function fetchData(input, init, api_obj) {
  // grant it's an array
  const codes =
    api_obj && typeof api_obj.codes === "object"
      ? Object.values(api_obj.codes)
      : [];

  const response = await fetch(input, {
    method: init.method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(init.body),
  });
  if (response.ok) {
    return response;
  } else {
    const errorBody = await response.json();
    const errorMessage = errorBody.message;

    if (codes.includes(response.status)) {
      throw new Error(errorMessage);
    } else {
      throw Error(
        "Request failed with status: " +
          response.status +
          " message: " +
          errorMessage,
      );
    }
  }
}

export async function login(credentials) {
  const parsed = parseCredentialsLogin(credentials);
  const response = await fetchData(
    joinPaths(SERVER_ADDR, API.login.endpoint),
    {
      method: API.login.method,
      body: parsed,
    },
    API.login,
  );
  return await response.json();
}

export async function signup(credentials) {
  const parsed = parseCredentialsSignup(credentials);
  const response = await fetchData(
    joinPaths(SERVER_ADDR, API.signup.endpoint),
    {
      method: API.signup.method,
      body: parsed,
    },
    API.signup,
  );

  return await response.json();
}

export async function signout() {
  const response = await fetch(joinPaths(SERVER_ADDR, API.signout.endpoint), {
    method: API.signout.method,
    headers: { "Content-Type": "application/json" },
    body: {},
  });

  if (response.ok) {
    toast.success("logout successfully!", { className: "toast-message" });
  } else {
    const errorBody = await response.json();
    const errorMessage = errorBody.message;

    toast.error(`${errorMessage}`, { className: "toast-message" });
  }
}

export async function addGuest() {
  const response = await fetch(joinPaths(SERVER_ADDR, API.addGuest.endpoint), {
    method: API.addGuest.method,
    headers: { "Content-Type": "application/json" },
    body: {},
  });
  if (response.ok) {
    const json = await response.json();
    return json.guest_nickname;
  } else toast.error(`error`, { className: "toast-message" });
}
