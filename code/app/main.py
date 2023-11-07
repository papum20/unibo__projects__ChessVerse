import eel
from screeninfo import get_monitors
import requests

def get_full_screen_size():
    monitors = get_monitors()
    screen_width = max(m.width for m in monitors)
    screen_height = max(m.height for m in monitors)
    return screen_width, screen_height

screen_width, screen_height = get_full_screen_size()

eel.init('web')
@eel.expose
def frontend_add_guest():
    response = requests.get('http://localhost:8080/backend_django/add_guest/')
    return response.json()

@eel.expose
def frontend_get_guest_name():
    response = requests.get('http://localhost:8080/backend_django/get_guest_name/')
    data = response.json()
    return data['guest_nickname']

eel.start('login/login.html', size=(screen_width, screen_height))