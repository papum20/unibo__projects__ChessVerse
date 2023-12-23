from django.urls import path
from .views import (
    add_guest,
    user_login,
    user_signup,
    user_signout,
    get_weekly_leaderboard,
    get_daily_leaderboard,
    check_start_daily,
    get_multiplayer_leaderboard,
    get_ranked_leaderboard,
)

urlpatterns = [
    path("add_guest/", add_guest, name="add_guest"),
    path("login/", user_login, name="user_login"),
    path("signup/", user_signup, name="user_signup"),
    path("signout/", user_signout, name="user_signout"),
    path(
        "get_weekly_leaderboard/", get_weekly_leaderboard, name="get_weekly_leaderboard"
    ),
    path(
        "get_ranked_leaderboard/", get_ranked_leaderboard, name="get_ranked_leaderboard"
    ),
    path("get_daily_leaderboard/", get_daily_leaderboard, name="get_daily_leaderboard"),
    path("check_start_daily/", check_start_daily, name="check_start_daily"),
    path(
        "get_multiplayer_leaderboard/",
        get_multiplayer_leaderboard,
        name="get_multiplayer_leaderboard",
    ),
]
