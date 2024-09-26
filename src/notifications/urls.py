from django.urls import path
from .views import *

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),

    path('card/', NotificationCardView.as_view(), name='notification_card'),
    path('system/', NotificationSystemView.as_view(), name='notification_system'),

    path('<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/delete/', delete_all_notifications, name='delete_all_notifications'),
]
