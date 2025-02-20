from django.urls import path
from .views import OffersIndexPage

app_name = 'offers'

urlpatterns = [
    path('', OffersIndexPage.as_view(), name='index'),
]