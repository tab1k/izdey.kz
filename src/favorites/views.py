from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from favorites.forms import FavoriteSearchForm
from favorites.models import Favorite
from notifications.mixins import UnreadNotificationMixin
from favorites.mixins import *
from users.models import *


class FavoritesPage(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'favorites/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = FavoriteSearchForm(self.request.GET or None)
        favorites = Favorite.objects.filter(user=self.request.user)

        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            if query:
                favorites = favorites.filter(job__title__icontains=query)

        context['favorites'] = favorites
        context['search_form'] = search_form
        context['unread_count'] = self.get_unread_notification_count()  # Подсчет непрочитанных уведомлений
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        return context