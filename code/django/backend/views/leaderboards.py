
from datetime import date, timedelta

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import RegisteredUsers, DailyLeaderboard, WeeklyLeaderboard



# ranked


@require_http_methods(["GET"])
def get_leaderboard_ranked(request):
	try:
		# Retrieve all users ordered by score_ranked in descending order
		leaderboard = RegisteredUsers.objects.order_by('-score_ranked').values('username', 'score_ranked')

		# Optional: Implement pagination
		paginator = Paginator(leaderboard, 10)  # Show 10 users per page
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)

		# Return the leaderboard as a JSON response
		return JsonResponse({'ranked_leaderboard': list(page_obj)}, status=200)
	except Exception as e:
		# Return an error response for any exception
		return JsonResponse({'message': str(e)}, status=500)


# periodic challenges

def get_leaderboard_daily(request):
	if request.method == 'GET':
		try:
			# Retrieve only the games played today from the database 
			daily_leaderboard = DailyLeaderboard.objects.filter(challenge_date=date.today(), result='win').values('username', 'moves_count')
			# Return the daily leaderboard as a JSON response
			return JsonResponse({'daily_leaderboard': list(daily_leaderboard)}, status=200)
		except Exception as e:
			# Return an error response for any exception
			return JsonResponse({'message': str(e)}, status=500)
	else:
		# Return an error response for invalid request methods
		return JsonResponse({'message': 'Invalid request method'}, status=405)


def get_leaderboard_weekly(request):
	if request.method == 'GET':
		try:
			# Retrieve only the games played from this Monday to this Sunday from the database
			start_of_week = date.today() - timedelta(days=date.today().weekday())
			end_of_week = start_of_week + timedelta(days=6)
			weekly_leaderboard = WeeklyLeaderboard.objects.filter(challenge_date__range=[start_of_week, end_of_week], result='win').values('username', 'moves_count')
			# Return the weekly leaderboard as a JSON response
			return JsonResponse({'weekly_leaderboard': list(weekly_leaderboard)}, status=200)
		except Exception as e:
			# Return an error response for any exception
			return JsonResponse({'message': str(e)}, status=500)
	else:
		# Return an error response for invalid request methods
		return JsonResponse({'message': 'Invalid request method'}, status=405)