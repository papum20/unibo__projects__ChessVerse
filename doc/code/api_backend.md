Method: add_guest
    Endpoint: /add_guest/
    GET: add a new guest

Method: get_guest_name
    Endpoint: /get_guest_name/
    GET: get the name of the last added guest user

# Leaderboards

- Endpoint: `/get_leaderboard/<leaderboard_type>/`
- Method: `GET`
- Parameters: `leaderboard_type` can be `ranked`, `daily`, or `weekly`.
- Response: `200 OK` with a JSON object containing the requested leaderboard. The JSON object will have a key named after the `<mode>_leaderboard` parameter and its value will be an array of objects, each containing the specified fields. Here `<mode>` can be one of `"ranked","daily","weekly"`.  

## responses

```json
{
  <mode>_leaderboard: [
    {
      // object fields...
    },
    // more users...
  ]
}
```

Ranked mode object:  
```json
{
    "user": <string>,
    "score_ranked": <int>,
}
```

Periodic challenges object:
```json
{
  "user": <string>,
  "moves_count": <int>,
}
```

# User Authentication

This API provides basic user authentication functionalities, including user login, signup, and logout.

## Endpoints

# 1. User Login

## Endpoint
- `/backend/login/`

## Method
- `POST`

## Request Body
- The request body should contain a JSON object with the following fields:
  - `username` (string): The username of the user trying to log in.
  - `password` (string): The password associated with the username.

## Response
- `200 OK` with a JSON object containing the message "Login successful" and a token if the login is successful.
- `401 Unauthorized` with a JSON object containing the message "Invalid credentials" if the provided credentials are incorrect.

## Example
```json
// Successful Login Response
{
  "message": "Login successful",
  "token": "your_generated_jwt_token_here"
}

// Unauthorized Login Response
{
  "message": "Invalid credentials"
}
```


### 2. User Signup

#### Endpoint
- `/backend/signup/`

#### Method
- `POST`

#### Request Body
- The request body should contain a JSON object with the following fields:
  - `username` (string): The desired username for the new user.
  - `password` (string): The password for the new user.
  - `eloReallyBadChess` (integer): The initial Elo rating for Really Bad Chess.

#### Response
- `200 OK` with a JSON object containing the message "Signup successful" if the signup is successful.
- `400 Bad Request` with a JSON object containing the message "Missing required fields" if any required field is not provided in the request body.
- `500 Internal Server Error` with a JSON object containing an error message if an unexpected error occurs during signup.

### 3. User Signout

#### Endpoint
- `/backend/signout/`

#### Method
- `POST`

#### Response
- `200 OK` with a JSON object containing the message "Logout successful" if the user is successfully logged out.

## Additional Notes

- The `@login_required` decorator is used for the `user_signout` view to ensure that only authenticated users can log out.
- Passwords are hashed using Django's `make_password` function before being stored in the database, enhancing security.


Ho anche messo un file 'test.rest' da cui si possono simulare delle richieste al backend, si può usare come spunto per vedere il tipo di richieste da fare
Per eseguire le richieste assicurarsi di avere l'estensione 'REST Client' di VSCODE

### IMPORTANTE 
    Prima di eseguire Django completare il file '.env.example' 
    INDIRIZZO A CUI VANNO FATTE LE RICHIESTE: https://chessverse.cloud:8000/backend
    
Per lanciare Django eseguire: 
    python3.12  manage.py runserver 
