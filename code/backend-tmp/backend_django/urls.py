from django.urls import path
from .views import add_guest, get_guest_name, user_login, user_signup, user_signout

urlpatterns = [
    path('add_guest/', add_guest, name='add_guest'),
    path('get_guest_name/', get_guest_name, name='get_guest_name'),
    path('login/', user_login, name='user_login'),
    path('signup/', user_signup, name='user_signup'),
    path('signout/', user_signout, name='user_signout'),
]
