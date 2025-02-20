from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from favorites.forms import FavoriteSearchForm
from favorites.models import Favorite
from notifications.mixins import UnreadNotificationMixin
from favorites.mixins import *
from users.models import *
from django.http import JsonResponse
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class FavoritesPage(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'favorites/index.html'

    def get(self, request, *args, **kwargs):
        search_form = FavoriteSearchForm(self.request.GET or None)
        favorites = Favorite.objects.filter(user=self.request.user)

        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            if query:
                favorites = favorites.filter(job__title__icontains=query)

        context = {
            'favorites': favorites,
            'search_form': search_form,
            'unread_count': self.get_unread_notification_count(),
            'location_choices': UserProfile.LOCATION_CHOICES
        }

        # Если это AJAX-запрос, возвращаем JSON с HTML-кодом вакансий
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render(request, 'favorites/index.html', context).content.decode('utf-8')
            return JsonResponse({'html': html})

        return self.render_to_response(context)
