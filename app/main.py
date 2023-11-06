import eel
from screeninfo import get_monitors
from backend.api import add_guest, get_guest_name

def get_full_screen_size():
    monitors = get_monitors()
    screen_width = max(m.width for m in monitors)
    screen_height = max(m.height for m in monitors)
    return screen_width, screen_height

screen_width, screen_height = get_full_screen_size()

eel.init('web')
@eel.expose

def frontend_add_guest():
    return add_guest()

@eel.expose
def frontend_get_guest_name():
    return get_guest_name()

eel.start('login/login.html', size=(screen_width, screen_height))

cursor.close()
conn.close()