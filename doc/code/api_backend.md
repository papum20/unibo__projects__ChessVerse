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

### 4. `get_daily_leaderboard(request)`

#### Endpoint
- `/backend/get_daily_leaderboard/`

### Method 
- `GET`

### Response
- Success (Status Code: 200): Returns a JSON response containing the daily leaderboard data.
-  Error (Status Code: 500): Returns an error response with details if an exception occurs during the retrieval process.
- Invalid Request Method (Status Code: 405): Returns an error response if the HTTP method is not GET.


## 5. `get_weekly_leaderboard(request)`

**Description:**
This method retrieves the weekly leaderboard for games played from the beginning of the week (Monday) to the current day (Sunday). It specifically includes games with a 'win' result and returns the leaderboard data as a JSON response.

**HTTP Method:** GET

**Response:**
- Success (Status Code: 200): Returns a JSON response containing the weekly leaderboard data.
- Error (Status Code: 500): Returns an error response with details if an exception occurs during the retrieval process.
- Invalid Request Method (Status Code: 405): Returns an error response if the HTTP method is not GET.


## 6. `check_start_daily(request)`

**Description:**
This method checks if a user has already played the maximum number of games (defined by `MAX_DAILY_GAMES`) today. It takes the user's username from the request body, queries the database, and returns the status as a JSON response.

**HTTP Method:** GET

**Parameters:**
- Username (sent in the request body as JSON data)

**Response:**
- Success (Status Code: 200): Returns a JSON response containing the daily leaderboard data if the user has not reached the maximum number of games.
- Error (Status Code: 400): Returns an error response if the user has already played the maximum number of games today.
- Error (Status Code: 500): Returns an error response with details if an exception occurs during the process.
- Invalid Request Method (Status Code: 405): Returns an error response if the HTTP method is not GET.

### 6. Method: get_multiplayer_leaderboard

Purpose: Retrieve Multiplayer Leaderboard.
HTTP Method: GET
Endpoint: /get_multiplayer_leaderboard/
Parameters:

request: HttpRequest object.
Returns:

JSON response containing Multiplayer Leaderboard data or an error message.
Usage:

Make a GET request to /get_multiplayer_leaderboard/ to retrieve the Multiplayer Leaderboard.
Example Response:
{
    "multiplayer_leaderboard": [
        {"username": "player1", "elo": 1500},
        {"username": "player2", "elo": 1600},
        ...
    ]
}
Error Response Example:
{
    "message": "Internal Server Error"
}

### 6. Method: get_multiplayer_leaderboard

Purpose: Retrieve Multiplayer Leaderboard.
HTTP Method: GET
Endpoint: /get_multiplayer_leaderboard/
Parameters:

request: HttpRequest object.
Returns:

JSON response containing Multiplayer Leaderboard data or an error message.
Usage:

Make a GET request to /get_multiplayer_leaderboard/ to retrieve the Multiplayer Leaderboard.
Example Response:
{
    "multiplayer_leaderboard": [
        {"username": "player1", "elo": 1500},
        {"username": "player2", "elo": 1600},
        ...
    ]
}
Error Response Example:
{
    "message": "Internal Server Error"
}

Ho anche messo un file 'test.rest' da cui si possono simulare delle richieste al backend, si può usare come spunto per vedere il tipo di richieste da fare
Per eseguire le richieste assicurarsi di avere l'estensione 'REST Client' di VSCODE

### IMPORTANTE 
    Prima di eseguire Django completare il file '.env.example' 
    INDIRIZZO A CUI VANNO FATTE LE RICHIESTE: https://chessverse.cloud:8000/backend
    
Per lanciare Django eseguire: 
    python3.12  manage.py runserver 
