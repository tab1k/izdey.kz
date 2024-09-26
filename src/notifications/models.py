from django.db import models
from users.models import User
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']