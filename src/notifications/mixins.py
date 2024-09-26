from notifications.models import Notification


class UnreadNotificationMixin:
    def get_unread_notification_count(self):
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user, read=False).count()
        return 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_unread_notification_count()
        return context