from django.urls import path
from .views import *


app_name = 'rooms'

urlpatterns = [
    path('', RoomTemplateView.as_view(), name='room-list'),
]