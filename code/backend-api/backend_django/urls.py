from django.urls import path
from .views import add_guest, get_guest_name

urlpatterns = [
    path('add_guest/', add_guest, name='add_guest'),
    path('get_guest_name/', get_guest_name, name='get_guest_name'),
]
