from datetime import date, timedelta
import json

from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import (
    RegisteredUsers,
    Guest,
    DailyLeaderboard,
    WeeklyLeaderboard,
    RankedLeaderboard,
)

from backend.models import (
    RegisteredUsers,
    DailyLeaderboard,
    MultiplayerLeaderboard,
    WeeklyLeaderboard,
)


def is_nickname_in_database(nickname):
    try:
        guest = Guest.objects.get(Username=nickname)
        return True
    except Guest.DoesNotExist:
        return False


def generate_random_nickname():
    while True:
        random_number = random.randint(1, 1000000000)
        nickname = f"Guest-{random_number}"

        if not is_nickname_in_database(nickname):
            return nickname


guest_nickname = ""


def add_guest(requests):
    if requests.method == "POST":
        global guest_nickname
        guest_nickname = generate_random_nickname()
        print("Guest name:" + guest_nickname)
        guest = Guest(Username=guest_nickname)
        guest.save()
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
    return JsonResponse({"guest_nickname": guest_nickname})


def get_guest_name(requests):
    print("Guest nickname:" + guest_nickname)
    return JsonResponse({"guest_nickname": guest_nickname})


@csrf_exempt
def user_login(request):
    # Handle user login
    if request.method == "POST":
        # Extract username and password from the request body
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        # Use authenticate to check username and password
        try:
            # Attempt to retrieve the user from the database
            user = RegisteredUsers.objects.get(username=username)
        except RegisteredUsers.DoesNotExist:
            # Return an error response if the user does not exist
            return JsonResponse({"message": "Invalid credentials"}, status=401)

        # Check if the provided password matches the stored password using bcrypt

        if check_password(password, user.password):
            # If user is authenticated, log them in
            login(request, user)
            # get the user from the database
            user = RegisteredUsers.objects.get(username=username)
            # add the session id to the user
            user.session_id = request.session.session_key
            user.save()
            return JsonResponse(
                {
                    "message": "Login successful",
                    "elo_really_bad_chess": user.EloReallyBadChess,
                    "session_id": user.session_id,
                }
            )

        else:
            # If authentication fails, return an error response
            return JsonResponse({"message": "Invalid credentials"}, status=401)


@csrf_exempt
def user_signup(request):
    # Handle user signup
    if request.method == "POST":
        try:
            # Extract user information from the request body
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            elo_really_bad_chess = data.get("eloReallyBadChess")

            possible_elos = [400, 800, 1200, 1600, 2000]
            if int(elo_really_bad_chess) not in possible_elos:
                return JsonResponse({"message": "Invalid elo"}, status=400)
            # Check if all required fields are provided
            if not all([username, password, elo_really_bad_chess]):
                return JsonResponse({"message": "Missing required fields"}, status=400)

            User = RegisteredUsers
            User.objects.create_user(
                username=username,
                password=password,
                EloReallyBadChess=elo_really_bad_chess,
            )

            # Return a success response if the signup is successful
            return JsonResponse({"message": "Signup successful"})
        except Exception as e:
            # Return an error response if an unexpected error occurs during signup
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({"message": "Invalid request method"}, status=405)


# @login_required(login_url='/backend/login/')
def user_signout(request):
    # Handle user signout (logout)
    logout(request)
    # Return a success response if the logout is successful
    return JsonResponse({"message": "Logout successful"})


# ranked
