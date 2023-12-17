export function parseCredentialsLogin(obj) {
  return {
    username: obj.username,
    password: obj.password,
  };
}

export function parseCredentialsSignup(obj) {
  obj.eloReallyBadChess = Number(obj.eloReallyBadChess);
  return {
    username: obj.username,
    password: obj.password,
    eloReallyBadChess: obj.eloReallyBadChess,
  };
}
