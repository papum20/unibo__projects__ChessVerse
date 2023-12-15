from django.urls import path
<<<<<<< HEAD
from .views import add_guest, get_guest_name, user_login, user_signup, user_signout, get_weekly_leaderboard, get_daily_leaderboard, check_start_daily
=======

from .views.others import add_guest, get_guest_name, user_login, user_signup, user_signout
from .views.leaderboards import get_leaderboard_ranked, get_leaderboard_daily, get_leaderboard_weekly

>>>>>>> dev-ranked

urlpatterns = [
    path('add_guest/', add_guest, name='add_guest'),
    path('get_guest_name/', get_guest_name, name='get_guest_name'),
    path('login/', user_login, name='user_login'),
    path('signup/', user_signup, name='user_signup'),
    path('signout/', user_signout, name='user_signout'),
<<<<<<< HEAD
    path('get_weekly_leaderboard/', get_weekly_leaderboard, name='get_weekly_leaderboard'),
    path('get_daily_leaderboard/', get_daily_leaderboard, name='get_daily_leaderboard'),
    path('check_start_daily/', check_start_daily, name='check_start_daily')
=======

    path('get_leaderboard/ranked/', get_leaderboard_ranked, name='get_leaderboard_ranked'),
    path('get_leaderboard/daily/', get_leaderboard_daily, name='get_leaderboard_daily'),
    path('get_leaderboard/weekly/', get_leaderboard_weekly, name='get_leaderboard_weekly'),
>>>>>>> dev-ranked
]
