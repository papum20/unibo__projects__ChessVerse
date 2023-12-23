from datetime import date, timedelta
import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from backend.models import (
    RegisteredUsers,
    DailyLeaderboard,
    MultiplayerLeaderboard,
    WeeklyLeaderboard,
)


# ranked


@require_http_methods(["GET"])
def get_leaderboard_ranked(request):
    try:
        # Retrieve all users ordered by score_ranked in descending order
        leaderboard = RegisteredUsers.objects.order_by("-score_ranked").values(
            "username", "score_ranked"
        )

        # Optional: Implement pagination
        paginator = Paginator(leaderboard, 10)  # Show 10 users per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        # print(request, list(page_obj))
        # Return the leaderboard as a JSON response
        return JsonResponse({"ranked_leaderboard": list(page_obj)}, status=200)
    except Exception as e:
        # Return an error response for any exception
        return JsonResponse({"message": str(e)}, status=500)


# periodic challenges


def get_leaderboard_daily(request):
    if request.method == "GET":
        try:
            # Retrieve only the games played today from the database
            daily_leaderboard = DailyLeaderboard.objects.filter(
                challenge_date=date.today(), result="win"
            ).values("username", "moves_count")
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


def get_leaderboard_weekly(request):
    if request.method == "GET":
        try:
            # Retrieve only the games played from this Monday to this Sunday from the database
            start_of_week = date.today() - timedelta(days=date.today().weekday())
            end_of_week = start_of_week + timedelta(days=6)
            weekly_leaderboard = WeeklyLeaderboard.objects.filter(
                challenge_date__range=[start_of_week, end_of_week], result="win"
            ).values("username", "moves_count")
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
            if (
                daily_leaderboard
                and daily_leaderboard[0]["attempts"] >= MAX_DAILY_GAMES
            ):
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
def get_leaderboard_multiplayer(request):
    if request.method == "GET":
        try:
            multiplayer_leaderboard = MultiplayerLeaderboard.objects.all().values(
                "username", "elo"
            )
            return JsonResponse(
                {"multiplayer_leaderboard": list(multiplayer_leaderboard)}, status=200
            )
        except Exception as e:
            # Return an error response for any exception
            return JsonResponse({"message": str(e)}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({"message": "Invalid request method"}, status=405)
