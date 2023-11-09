from django.shortcuts import render
from .models import Guest
from django.http import JsonResponse
import random

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

def download_file(request, operating_system):
    if operating_system == 'macos':
        file_path = 'Desktop/t4-chessverse/code/app/versions/Chessverse_v1.0.dmg'
    elif operating_system == 'windows':
        file_path = 'Desktop/t4-chessverse/code/app/versions/Chessverse_v1.0.dmg'
    elif operating_system == 'linux':
        file_path = 'Desktop/t4-chessverse/code/app/versions/Chessverse_v1.0.dmg'
    else:
        return HttpResponseBadRequest("Sistema operativo non supportato")

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    else:
        return HttpResponseNotFound("File non trovato")