from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
from users.models import *
from django.core.paginator import Paginator


class RoomTemplateView(TemplateView):
    template_name = 'rooms/room_list.html'

    def get_context_data(self, **kwargs):
        context = super(RoomTemplateView, self).get_context_data(**kwargs)

        # Получаем все объекты Room
        room_list = Room.objects.all()

        # Настройка пагинации
        paginator = Paginator(room_list, 10)  # 10 объектов на странице
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Добавляем данные в контекст
        context['room_list'] = page_obj
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        return context
