from django.shortcuts import render
from .models import Guest
from django.http import JsonResponse
import random
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import RegisteredUsers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from backend_django.models import RegisteredUsers

def is_nickname_in_database(nickname):
    try:
        guest = Guest.objects.get(Username=nickname)
        return True
    except Guest.DoesNotExist:
        return False

def generate_random_nickname():
    while True:
        random_number = random.randint(1, 1000000000)
        nickname = f'Guest-{random_number}'

        if not is_nickname_in_database(nickname):
            return nickname

guest_nickname = ''

def add_guest(requests):
    global guest_nickname
    guest_nickname = generate_random_nickname()
    print('Guest name:'+  guest_nickname)
    guest = Guest(Username=guest_nickname)
    guest.save()
    return JsonResponse({"message": "Guest added successfully!"})

def get_guest_name(requests):
    print('Guest nickname:' + guest_nickname)
    return JsonResponse({"guest_nickname": guest_nickname})



@csrf_exempt
def user_login(request):
    # Handle user login
    if request.method == 'POST':
        # Extract username and password from the request body
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        # Use authenticate to check username and password
        try:
            # Attempt to retrieve the user from the database
            user = RegisteredUsers.objects.get(username=username)
        except RegisteredUsers.DoesNotExist:
            # Return an error response if the user does not exist
            return JsonResponse({'message': 'Invalid credentials'}, status=401)

        # Check if the provided password matches the stored password
        if check_password(password, user.password):
            # Return a success response if the login is successful
            return JsonResponse({'message': 'Login successful'})

        if user is not None:
            # If user is authenticated, log them in
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            # If authentication fails, return an error response
            return JsonResponse({'message': 'Invalid credentials'}, status=401)



@csrf_exempt
def user_signup(request):
    # Handle user signup
    if request.method == 'POST':
        try:
            # Extract user information from the request body
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            elo_really_bad_chess = data.get('eloReallyBadChess')
            elo_second_type = data.get('eloSecondType')
            
            # Check if all required fields are provided
            if not all([username, password, elo_really_bad_chess, elo_second_type]):
                return JsonResponse({'message': 'Missing required fields'}, status=400)

            # Hash the password and save the new user using CustomUserManager
            hashed_password = make_password(password)
            User = RegisteredUsers
            new_user = User.objects.create_user(
                username=username,
                password=hashed_password,
                EloReallyBadChess=elo_really_bad_chess,
                EloSecondChess=elo_second_type
            )

            # Return a success response if the signup is successful
            return JsonResponse({'message': 'Signup successful'})
        except Exception as e:
            # Return an error response if an unexpected error occurs during signup
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)
    else:
        # Return an error response for invalid request methods
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
@login_required
def user_signout(request):
    # Handle user signout (logout)
    logout(request)
    # Return a success response if the logout is successful
    return JsonResponse({'message': 'Logout successful'})