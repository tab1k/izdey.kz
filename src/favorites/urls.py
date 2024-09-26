from .views import *
from django.urls import path, include

app_name = 'favorites'

urlpatterns = [
    path('', FavoritesPage.as_view(), name='favorites-list'),
]
