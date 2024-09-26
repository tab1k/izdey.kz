from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.models import Notification


@receiver(user_logged_in)
def notify_user_logged_in(sender, request, user, **kwargs):
    message = f'Вы вошли в систему.'
    Notification.objects.create(user=user, message=message)


@receiver(user_logged_out)
def notify_user_logged_out(sender, request, user, **kwargs):
    message = f'Вы вышли из системы.'
    Notification.objects.create(user=user, message=message)