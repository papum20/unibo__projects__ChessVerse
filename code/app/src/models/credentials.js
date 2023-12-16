export function parseCredentialsLogin(obj) {
  return {
    username: obj.username,
    password: obj.password,
  };
}

export function parseCredentialsSignup(obj) {
  return {
    username: obj.username,
    password: obj.password,
    eloReallyBadChess: obj.eloReallyBadChess,
  };
}
