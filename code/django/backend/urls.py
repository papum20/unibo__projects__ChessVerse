from django.urls import path

from .views.others import add_guest, get_guest_name, user_login, user_signup, user_signout
from .views.leaderboards import (
	get_leaderboard_ranked,
	get_leaderboard_daily,
	get_leaderboard_weekly,
	check_start_daily
)

>>>>>>> dev-ranked

urlpatterns = [
    path('add_guest/', add_guest, name='add_guest'),
    path('get_guest_name/', get_guest_name, name='get_guest_name'),
    path('login/', user_login, name='user_login'),
    path('signup/', user_signup, name='user_signup'),
    path('signout/', user_signout, name='user_signout'),

    path('get_leaderboard/ranked/', get_leaderboard_ranked, name='get_leaderboard_ranked'),
    path('get_leaderboard/daily/', get_leaderboard_daily, name='get_leaderboard_daily'),
    path('get_leaderboard/weekly/', get_leaderboard_weekly, name='get_leaderboard_weekly'),
    
    path('check_start_daily/', check_start_daily, name='check_start_daily')
]
