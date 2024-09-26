from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from favorites.mixins import FavoritesCountMixin
from myaccount.forms import JobResponseStatusForm
from notifications.mixins import UnreadNotificationMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from jobs.models import *

from django.views.generic import TemplateView, FormView, ListView, DeleteView, View

from resume.models import Resume
from users.forms import *
from django.urls import reverse_lazy

from django_user_agents.utils import get_user_agent
from django.http import HttpResponseForbidden


class BaseLocation:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'unread_count': self.get_unread_notification_count(),
            'location_choices': Job.LOCATION_CHOICES,
        })
        return context


class SettingsView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/settings.html'

    def dispatch(self, request, *args, **kwargs):
        user_agent = get_user_agent(request)
        if not user_agent.is_mobile:  # Проверка, является ли устройство мобильным
            return HttpResponseForbidden("Эта страница доступна только на мобильных устройствах")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Проверка на наличие услуг (Договорная занятость и Единоразовая услуга)
        context['has_services'] = user.posted_jobs.filter(time_count__in=['part', 'daily']).exists()

        return context


class UserProfileView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('myaccount:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        try:
            resume = Resume.objects.get(user_profile=user_profile)
        except Resume.DoesNotExist:
            resume = None
        context.update({
            'resume': resume,
            'unread_count': self.get_unread_notification_count(),
            'location_choices': Job.LOCATION_CHOICES,
        })
        return context


class UserProfileData(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, FormView):
    form_class = UserForm
    template_name = 'users/settings/user_profile_data.html'
    success_url = reverse_lazy('myaccount:profile')  # Страница куда перенаправлять после успешного сохранения данных

    def get_form_kwargs(self):
        """ Передаем текущего пользователя в форму """
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Обновляем данные пользователя и сохраняем их
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)


class UserMyProfileView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, FormView):
    form_class = UserProfileForm
    template_name = 'users/settings/user_profile_view.html'
    success_url = reverse_lazy('myaccount:profile')  # Страница перенаправления после успешного сохранения

    def get_form_kwargs(self):
        """ Передаем текущий пользовательский профиль в форму """
        kwargs = super().get_form_kwargs()
        user_profile = UserProfile.objects.get(user=self.request.user)
        kwargs['instance'] = user_profile
        return kwargs

    def form_valid(self, form):
        # Сохраняем профиль пользователя
        form.save()
        return super().form_valid(form)


class UserCompanyView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, FormView):
    form_class = UserCompanyForm
    template_name = 'users/settings/user_company_view.html'
    success_url = reverse_lazy('myaccount:profile')  # Страница перенаправления после успешного сохранения

    def get_form_kwargs(self):
        """ Передаем текущий профиль компании в форму """
        kwargs = super().get_form_kwargs()
        user_profile = self.request.user.profile
        kwargs['instance'] = user_profile.company_profile
        return kwargs

    def form_valid(self, form):
        # Сохраняем профиль компании
        form.save()
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, DeleteView):
    model = User
    template_name = 'users/settings/confirm_delete.html'
    success_url = reverse_lazy('jobs:home')

    def get_object(self, queryset=None):
        # Возвращаем текущего пользователя
        return self.request.user

    def post(self, request, *args, **kwargs):
        # Удаляем профиль пользователя перед удалением аккаунта
        UserProfile.objects.filter(user=self.request.user).delete()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        # Перенаправление на главную страницу или другую после удаления
        return reverse_lazy('jobs:home')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/settings/change_password.html'  # Шаблон для страницы изменения пароля
    success_url = reverse_lazy(
        'myaccount:user_my_profile')  # URL, на который перенаправлять после успешного изменения пароля
    form_class = CustomPasswordChangeForm


class ResponsesView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/job_responses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отклики на вакансии текущего пользователя, которые еще не отклонены
        user_jobs = Job.objects.filter(employer=self.request.user)
        context['my_responses'] = JobResponse.objects.filter(
            job__in=user_jobs,
            status__in=['pending']  # Фильтрация по статусам
        ).select_related('user', 'job')

        # Все отклики текущего пользователя (независимо от статуса)
        context['user_responses'] = JobResponse.objects.filter(
            user=self.request.user
        ).select_related('job')

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('index_content.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


class DoneVacanciesView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/done_responses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отклики на вакансии текущего пользователя, которые еще не отклонены
        user_jobs = Job.objects.filter(employer=self.request.user)

        context['my_responses'] = JobResponse.objects.filter(
            job__in=user_jobs,
            status__in=['approved']  # Фильтрация по статусам
        ).select_related('user', 'job')

        context['reject_responses'] = JobResponse.objects.filter(
            job__in=user_jobs,
            status__in=['rejected']  # Фильтрация по статусам
        ).select_related('user', 'job')

        return context







class HelpView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/help.html'


class AboutView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'users/settings/about.html'


class MyServiceView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, ListView):
    model = Job
    template_name = 'users/settings/my_service.html'

    def get_queryset(self):
        # Фильтруем услуги по текущему пользователю и типу занятости (единоразовая услуга)
        queryset = Job.objects.filter(employer=self.request.user, time_count='daily')
        return queryset


class MyVacancyView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, ListView):
    model = Job
    template_name = 'users/settings/my_vacancy.html'
    context_object_name = 'vacancies'

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)

        # Проверяем, что пользователь является подтвержденным работодателем
        if not user_profile.verified or not hasattr(user_profile, 'company_profile'):
            raise PermissionDenied(
                "Вы не можете создавать вакансии, пока ваш профиль не подтвержден и не привязан к компании.")

        # Фильтруем вакансии (полная или договорная занятость)
        return Job.objects.filter(employer=self.request.user, time_count__in=['full', 'part'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job


    def get_success_url(self):
        # Если это услуга (единоразовая), перенаправляем на страницу услуг
        job = self.get_object()
        if job.time_count == 'daily':
            return reverse_lazy('myaccount:my_service')
        # Если это вакансия (полная или частичная занятость), перенаправляем на страницу вакансий
        else:
            return reverse_lazy('myaccount:my_vacancy')

    def get_queryset(self):
        # Ограничиваем удаление только для записей пользователя
        return super().get_queryset().filter(employer=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Проверяем, что пользователь удаляет именно свою запись
        job = self.get_object()
        if job.employer != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужую запись.")
        return super().delete(request, *args, **kwargs)


class DashBoardView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    pass
