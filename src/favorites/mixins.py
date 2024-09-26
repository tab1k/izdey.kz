from django.shortcuts import get_object_or_404
from favorites.models import Favorite  # Замените на правильный импорт


class FavoritesCountMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorites_count'] = Favorite.objects.filter(user=self.request.user).count()
        else:
            context['favorites_count'] = 0
        return context