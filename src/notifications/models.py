from django.db import models
from django.utils import timezone
from users.models import User

class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']
