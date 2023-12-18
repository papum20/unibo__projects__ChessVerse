import random
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from django.views.decorators.http import require_http_methods

from .models import (
    RegisteredUsers,
    Guest,
    DailyLeaderboard,
    WeeklyLeaderboard,
)
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
import os
from datetime import date, timedelta


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
            if (int(elo_really_bad_chess) not in possible_elos):
                return JsonResponse({'message': 'Invalid elo'}, status=400)
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


def get_daily_leaderboard(request):
    if request.method == "GET":
        try:
            # Retrieve only the games played today from the database
            daily_leaderboard = DailyLeaderboard.objects.filter(
                challenge_date=date.today(), result="win"
            ).values("username", "moves_count").order_by("moves_count")
            # Return the daily leaderboard as a JSON response
            return JsonResponse(
                {"daily_leaderboard": list(daily_leaderboard)}, status=200
            )
        except Exception as e:
            # Return an error response for any exception
            return JsonResponse({"message": str(e)}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({"message": "Invalid request method"}, status=405)


def get_weekly_leaderboard(request):
    if request.method == "GET":
        try:
            # Retrieve only the games played from this Monday to this Sunday from the database
            start_of_week = date.today() - timedelta(days=date.today().weekday())
            end_of_week = start_of_week + timedelta(days=6)

            weekly_leaderboard = WeeklyLeaderboard.objects.filter(
                result="win",
                challenge_date__range=[start_of_week, end_of_week],  # Add this filter
            ).values("username", "moves_count").order_by("moves_count")

            # Return the weekly leaderboard as a JSON response
            return JsonResponse(
                {"weekly_leaderboard": list(weekly_leaderboard)}, status=200
            )
        except Exception as e:
            # Return an error response for any exception
            return JsonResponse({"message": str(e)}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({"message": "Invalid request method"}, status=405)


MAX_DAILY_GAMES = 2


# check if the user has already played the maximum number of games today
def check_start_daily(request):
    if request.method == "GET":
        # Usa request.GET.get per ottenere il parametro della query string
        username = request.GET.get("username")

        if not username:
            return JsonResponse(
                {"message": "Username is required as a query parameter"},
                status=400,
            )

        try:
            daily_leaderboard = DailyLeaderboard.objects.filter(
                challenge_date=date.today(), username=username
            ).values("username", "attempts")

            if daily_leaderboard:
                print(daily_leaderboard[0]["attempts"])
            if daily_leaderboard and daily_leaderboard[0]["attempts"] >= MAX_DAILY_GAMES:
                return JsonResponse(
                    {
                        "message": "You have already played the maximum number of games today"
                    },
                    status=400,
                )
            else:
                return JsonResponse(
                    {"daily_leaderboard": list(daily_leaderboard)}, status=200
                )
        except Exception as e:
            print(f"Error in check_start_daily: {str(e)}")
            return JsonResponse(
                {"message": "An error occurred while processing your request"},
                status=500,
            )
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)


# get the Multiplayer leaderboard
def get_multiplayer_leaderboard(request):
    if request.method == "GET":
        try:
            multiplayer_leaderboard = RegisteredUsers.objects.all().values(
                "username", "EloReallyBadChess"
            ).order_by("-EloReallyBadChess")
            return JsonResponse(
                {"multiplayer_leaderboard": list(multiplayer_leaderboard)}, status=200
            )
        except Exception as e:
            # Return an error response for any exception
            return JsonResponse({"message": str(e)}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({"message": "Invalid request method"}, status=405)


@require_http_methods(["GET"])
def get_ranked_leaderboard(request):
    try:
        # Retrieve all users ordered by score_ranked in descending order
        ranked_leaderboard = RegisteredUsers.objects.all().values('username', 'score_ranked').order_by('-score_ranked')
        return JsonResponse(
                {"ranked_leaderboard": list(ranked_leaderboard)}, status=200
            )
    except Exception as e:
        # Return an error response for any exception
        return JsonResponse({"message": str(e)}, status=500)
