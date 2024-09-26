from django.views.generic import ListView, DetailView, RedirectView, TemplateView

from favorites.mixins import FavoritesCountMixin
from users.models import *
from wallet.models import Deposit, Transaction
from .mixins import UnreadNotificationMixin
from .models import Notification
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


class NotificationListView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'notifications/notifications.html'


class NotificationCardView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'notifications/notification_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        context['user_amount'] = Deposit.objects.get(user=self.request.user).amount

        # Извлекаем транзакции, где текущий пользователь отправитель или получатель
        sent_transactions = Transaction.objects.filter(sender=self.request.user)
        received_transactions = Transaction.objects.filter(receiver=self.request.user)

        # Объединяем QuerySet'ы с использованием union()
        all_transactions = sent_transactions.union(received_transactions).order_by('-created_at')

        # Передаем только 10 последних транзакций
        context['transactions'] = all_transactions
        # Подсчитываем количество всех транзакций
        context['count'] = all_transactions.count()

        return context


class NotificationSystemView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_system.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        return context


class NotificationDetailView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, DetailView):
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем подсчет непрочитанных уведомлений в контекст
        context['unread_count'] = Notification.objects.filter(user=self.request.user, read=False).count()
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        return context


class MarkAsReadView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('notifications:notification_list')

    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(pk=kwargs['pk'], user=request.user)
        notification.read = True
        notification.save()
        return super().get(request, *args, **kwargs)


@login_required
def delete_all_notifications(request):
    if request.method == 'POST':
        # Удаление всех уведомлений для текущего пользователя
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'message': 'All notifications deleted successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)
