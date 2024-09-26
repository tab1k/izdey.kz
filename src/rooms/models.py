from django.db import models


class Room(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланировано'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    speaker = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Неизвестный статус')

    def __str__(self):
        return f'{self.name} | {self.time_start} - {self.time_end}'

    class Meta:
        verbose_name = 'Голосовая комната'
        verbose_name_plural = 'Голосовые комнаты'
        ordering = ['-time_start']
