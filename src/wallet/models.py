from django.db import models
from users.models import *


class Deposit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deposit')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Депозит: {self.amount}. Пользователь: {self.user.username}"

    class Meta:
        verbose_name = 'Депозит'
        verbose_name_plural = 'Депозиты'


class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Перевод: {self.amount} от {self.sender.username} -> {self.receiver.username}"

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
