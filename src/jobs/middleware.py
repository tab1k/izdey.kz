from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


class StaffOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверка пути и пользователя
        if request.path.startswith('/admin/') and not request.user.is_staff:
            return redirect('jobs:home')
        return self.get_response(request)
