from .models import User, UserProfile
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.models import Notification  # предполагаем, что создали модель Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def notify_password_change(sender, instance, created, **kwargs):
    if instance.password:
        message = f'Ваш пароль был изменен {timezone.now().strftime("%Y-%m-%d %H:%M")}.'
        Notification.objects.create(user=instance, message=message)