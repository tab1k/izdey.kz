from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy

from favorites.mixins import FavoritesCountMixin
from jobs.models import Category
from notifications.mixins import UnreadNotificationMixin
from users.models import UserProfile
from .models import Resume
from .forms import ResumeForm


class ResumeDetailView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, DetailView):
    model = Resume
    template_name = 'users/resume/resume_detail.html'

    def get_object(self, queryset=None):
        # Получаем резюме текущего пользователя
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return get_object_or_404(Resume, user_profile=user_profile)


class ResumeCreateView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'users/resume/resume_form.html'
    success_url = reverse_lazy('myaccount:resume:resume_detail')

    def get_context_data(self, **kwargs):
        # Добавляем категории в контекст для отображения их в форме
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        user_profile = self.request.user.profile  # Доступ к UserProfile через 'profile'

        # Проверяем, есть ли уже резюме у текущего пользователя
        if Resume.objects.filter(user_profile=user_profile).exists():
            form.add_error(None, 'У вас уже есть резюме. Вы не можете создать более одного резюме.')
            return self.form_invalid(form)

        form.instance.user_profile = user_profile
        return super().form_valid(form)


class ResumeUpdateView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, UpdateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'users/resume/resume_form.html'
    success_url = reverse_lazy('myaccount:resume:resume_detail')

    def get_object(self):
        return get_object_or_404(Resume, user_profile__user=self.request.user)

    def get_context_data(self, **kwargs):
        # Добавляем категории в контекст для отображения их в форме
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        user_profile = self.request.user.profile  # Доступ к UserProfile через 'profile'
        resume_instance = self.get_object()

        # Проверяем, пытается ли пользователь создать новое резюме
        # Если объект обновляется (существует), пропускаем проверку
        if not resume_instance and Resume.objects.filter(user_profile=user_profile).exists():
            form.add_error(None, 'У вас уже есть резюме. Вы не можете создать более одного резюме.')
            return self.form_invalid(form)

        form.instance.user_profile = user_profile
        return super().form_valid(form)
