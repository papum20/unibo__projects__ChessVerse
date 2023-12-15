import random
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import RegisteredUsers, Guest, DailyLeaderboard, WeeklyLeaderboard
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
import os
from datetime import date, timedelta

