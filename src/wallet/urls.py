from .views import *
from django.urls import path, include

app_name = 'wallet'

urlpatterns = [
    path('', WalletInfoPage.as_view(), name='info'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('get_user_info/<str:phone_number>/', get_user_info, name='get_user_info'),
    path('replenishment/', ReplenishmentView.as_view(), name='replenishment'),
]
