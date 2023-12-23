/*
 * api specs, e.g. paths, methods, codes, data fields (req/res)
 */

export const API = {
  login: {
    endpoint: "login/",
    method: "POST",
    codes: {
      ok: 200,
      unauthorized: 401,
    },
    data: ["username", "password"],
    response: ["message", "token"],
  },
  signout: {
    endpoint: "signout/",
    method: "POST",
    codes: {
      ok: 200,
    },
  },
  signup: {
    endpoint: "signup/",
    method: "POST",
    codes: {
      ok: 200,
      "bad request": 400,
      "internal server error": 500,
    },
    data: ["username", "password", "eloReallyBadChess"],
    response: ["message"],
  },
  addGuest: {
    endpoint: "add_guest/",
    method: "POST",
  },
  dailyLeaderboard: {
    endpoint: "get_daily_leaderboard/",
    method: "GET",
    codes: {
      ok: 200,
      "internal server error": 500,
      "invalid request": 405,
    },
  },
  weeklyLeaderboard: {
    endpoint: "get_weekly_leaderboard/",
    method: "GET",
    codes: {
      ok: 200,
      "internal server error": 500,
      "invalid request": 405,
    },
  },
  rankedLeaderboard: {
    endpoint: "get_ranked_leaderboard/",
    method: "GET",
    codes: {},
  },
  checkStartDaily: {
    endpoint: "check_start_daily/",
    method: "GET",
    codes: {
      ok: 200,
      "maximum reached": 400,
      "internal server error": 500,
      "invalid request": 405,
    },
  },
  multiplayerLeaderboard: {
    endpoint: "get_multiplayer_leaderboard/",
    method: "GET",
    codes: {
      ok: 200,
      "internal server error": 500,
      "invalid request": 405,
    },
  },
};
