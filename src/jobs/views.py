from datetime import timezone
from django.db.models import Exists, OuterRef
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, View, TemplateView
from notifications.mixins import UnreadNotificationMixin
from resume.models import Resume
from users.models import UserProfile
from .filters import JobFilter
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic.detail import DetailView
from favorites.mixins import *
from django.core.cache import cache
from .forms import *
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import ListView
from django.shortcuts import render
from .models import JobResponse


class BaseLocation:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        return context




class HomePageView(FavoritesCountMixin, UnreadNotificationMixin, ListView):
    model = Job
    template_name = 'jobs/index.html'
    paginate_by = 10
    context_object_name = 'jobs'
    ordering = ('-date_posted',)
    filterset_class = JobFilter

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True).select_related('employer')

        # Применяем фильтры из JobFilter (location, title, category и оплата)
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs  # Применяем отфильтрованный queryset

        # 📌 Если пользователь НЕ выбрал город вручную, применяем его город из профиля
        if not self.request.GET.get('location'):  # Если в GET-запросе нет 'location'
            if self.request.user.is_authenticated and hasattr(self.request.user,
                                                              'profile') and self.request.user.profile.location:
                queryset = queryset.filter(location=self.request.user.profile.location)

        # Оптимизируем проверку "избранных" вакансий
        if self.request.user.is_authenticated:
            favorite_subquery = Favorite.objects.filter(user=self.request.user, job=OuterRef('pk'))
            queryset = queryset.annotate(is_favorite=Exists(favorite_subquery))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'unread_count': self.get_unread_notification_count(),
            'location_choices': Job.LOCATION_CHOICES,
            'filter': self.filterset_class(self.request.GET, queryset=self.get_queryset()),
        })
        return context



    def get_cache_key(self):
        """Generate a unique cache key based on request parameters."""
        location_filter = self.request.GET.get('location', 'all')

        # Проверка на наличие профиля
        if self.request.user.is_authenticated:
            user_profile = getattr(self.request.user, 'profile', None)
            user_profile_location = getattr(user_profile, 'location', 'unknown') if user_profile else 'unknown'
        else:
            user_profile_location = 'unknown'

        return f'jobs_queryset_{location_filter}_{user_profile_location}'


class JobDetailView(FavoritesCountMixin, UnreadNotificationMixin, DetailView):
    model = Job
    context_object_name = 'job'
    template_name = 'jobs/job_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('employer')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()

        if self.request.user.is_authenticated:
            context['is_favorited'] = self.request.user.favorites.filter(job=job).exists()
            context['has_applied'] = job.user_has_applied(self.request.user)

            # Определение статуса заявки пользователя
            application_status = JobResponse.objects.filter(
                job=job,
                user=self.request.user
            ).first()

            if application_status:
                context['application_status'] = application_status.status
            else:
                context['application_status'] = None
        else:
            context['is_favorited'] = False
            context['has_applied'] = False
            context['application_status'] = None

        context['job_url'] = self.request.build_absolute_uri()
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        context['keys_description_items'] = job.keys_description.split('\n')
        context['skills_description_items'] = job.skills_description.split('\n')

        # Подборка похожих вакансий
        similar_jobs = Job.objects.filter(
            category=job.category,
            location=job.location
        ).exclude(id=job.id)
        context['similar_jobs'] = similar_jobs

        return context


class SendApplicationView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)

        # Проверка наличия резюме у пользователя
        if not Resume.objects.filter(user_profile__user=request.user).exists():
            messages.error(request, "У вас нет резюме. Пожалуйста, создайте резюме перед подачей заявки.")
            return redirect('myaccount:resume:resume_create')

        # Проверка, отправлял ли пользователь уже отклик на эту вакансию
        if JobResponse.objects.filter(user=request.user, job=job).exists():
            messages.error(request, "Вы уже отправили отклик на эту вакансию.")
            return redirect('jobs:service-detail', pk=pk)

        # Создаем отклик
        JobResponse.objects.create(
            user=request.user,
            job=job,
            message="Ваше стандартное сообщение отклика",
        )
        messages.success(request, "Ваш отклик успешно отправлен.")
        return redirect('jobs:service-detail', pk=pk)


class ApproveJobResponseView(LoginRequiredMixin, View):
    def post(self, request, pk, response_id, *args, **kwargs):
        response = get_object_or_404(JobResponse, id=response_id, job__pk=pk)

        # Проверка, что пользователь является работодателем этой вакансии
        if response.job.employer != request.user:
            raise PermissionDenied("Вы не можете одобрить отклик на эту вакансию.")

        # Обновляем статус отклика на одобренный
        response.status = 'approved'
        response.save()
        messages.success(request, "Отклик успешно одобрен.")
        return redirect('myaccount:responses')


class RejectJobResponseView(LoginRequiredMixin, View):
    def post(self, request, pk, response_id, *args, **kwargs):
        response = get_object_or_404(JobResponse, id=response_id, job__pk=pk)

        # Проверка, что пользователь является работодателем этой вакансии
        if response.job.employer != request.user:
            raise PermissionDenied("Вы не можете отклонить отклик на эту вакансию.")

        # Обновляем статус отклика на отклоненный
        response.status = 'rejected'
        response.save()
        messages.success(request, "Отклик успешно отклонен.")
        return redirect('myaccount:responses')


class Error404View(TemplateView, FavoritesCountMixin, UnreadNotificationMixin, ):
    template_name = 'error404.html'


class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        favorite = Favorite.objects.filter(user=request.user, job=job).first()

        if favorite:
            favorite.delete()
            return JsonResponse({"status": "removed"})
        else:
            Favorite.objects.create(user=request.user, job=job)
            return JsonResponse({"status": "added"})


class RemoveFromFavoritesView(View):
    def post(self, request, job_id):
        favorite = get_object_or_404(Favorite, job_id=job_id, user=request.user)
        favorite.delete()
        return redirect('favorites:favorites-list')




class CategoryListView(BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, ListView):
    model = Category
    template_name = 'jobs/impact/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        queryset = Category.objects.all().order_by('name')

        search_form = CategorySearchForm(self.request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            if query:
                queryset = queryset.filter(name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = CategorySearchForm(self.request.GET or None)
        context['search_form'] = search_form
        return context

    def render_to_response(self, context, **response_kwargs):
        # Если это AJAX-запрос, возвращаем только обновлённый список категорий
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render(self.request, 'jobs/impact/category_list.html', context).content.decode('utf-8')
            return JsonResponse({'html': html})

        return super().render_to_response(context, **response_kwargs)


class CategoryDetailView(BaseLocation, LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, DetailView):
    model = Category
    template_name = 'jobs/impact/category_detail.html'
    context_object_name = 'category'
    paginate_by = 10  # Количество объектов на странице

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем категорию
        category = self.get_object()

        # Получаем местоположение пользователя
        user_location = getattr(self.request.user.profile, 'location', None)

        # Базовый queryset для фильтрации
        jobs = Job.objects.filter(category=category, is_active=True)

        # Фильтруем вакансии по местоположению пользователя
        if user_location:
            jobs = jobs.filter(location=user_location)

        # Применяем фильтр JobFilter
        filter = JobFilter(self.request.GET, queryset=jobs)

        # Пагинация вакансий
        paginator = Paginator(filter.qs, self.paginate_by)  # Пагинация по 10 объектов на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Добавляем отфильтрованные вакансии, фильтр и пагинацию в контекст
        context['jobs'] = page_obj
        context['filter'] = filter
        context['paginator'] = paginator
        context['page_obj'] = page_obj

        return context


class VacancyListView(FavoritesCountMixin, UnreadNotificationMixin, BaseLocation, ListView):
    model = Job
    template_name = 'jobs/impact/vacancy_list.html'
    paginate_by = 10
    context_object_name = 'jobs'
    ordering = ('-date_posted',)
    filterset_class = JobFilter

    def get_queryset(self):
        # Получаем начальный queryset
        queryset = super().get_queryset().filter(is_active=True).select_related('employer')

        # Применяем фильтры
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        queryset = self.filterset.qs

        # Применяем фильтрацию по полной занятости
        queryset = queryset.filter(time_count='full')

        # Получаем местоположение пользователя, если доступно
        if self.request.user.is_authenticated:
            user_profile = getattr(self.request.user, 'profile', None)
            user_profile_location = getattr(user_profile, 'location', 'unknown') if user_profile else 'unknown'
        else:
            user_profile_location = 'unknown'

        # Фильтрация по местоположению пользователя
        if user_profile_location != 'unknown':
            queryset = queryset.filter(location=user_profile_location)

        # Убедитесь, что используете правильное поле для сортировки
        queryset = queryset.order_by('time_count', '-date_posted')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передача формы фильтра в контекст
        context['filter'] = self.filterset
        return context

    def get_cache_key(self):
        """Generate a unique cache key based on request parameters."""
        location_filter = self.request.GET.get('location', 'all')

        if self.request.user.is_authenticated:
            user_profile = getattr(self.request.user, 'profile', None)
            user_profile_location = getattr(user_profile, 'location', 'unknown') if user_profile else 'unknown'
        else:
            user_profile_location = 'unknown'

        return f'jobs_queryset_{location_filter}_{user_profile_location}'


class ServiceListView(FavoritesCountMixin, UnreadNotificationMixin, BaseLocation, ListView):
    model = Job
    template_name = 'jobs/impact/service_list.html'
    paginate_by = 10
    context_object_name = 'services'
    filterset_class = JobFilter

    def get_queryset(self):
        # Получаем начальный queryset
        queryset = super().get_queryset().filter(is_active=True).select_related('employer', 'category')

        # Применяем фильтры
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        queryset = self.filterset.qs

        # Применяем фильтрацию по типу занятости (услуги)
        queryset = queryset.filter(time_count__in=['part', 'daily'])

        # Получаем местоположение пользователя, если доступно
        if self.request.user.is_authenticated:
            user_profile = getattr(self.request.user, 'profile', None)
            user_profile_location = getattr(user_profile, 'location', 'unknown') if user_profile else 'unknown'
        else:
            user_profile_location = 'unknown'

        # Фильтрация по местоположению пользователя
        if user_profile_location != 'unknown':
            queryset = queryset.filter(location=user_profile_location)

        # Убедитесь, что используете правильное поле для сортировки
        queryset = queryset.order_by('-date_posted')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передача формы фильтра в контекст
        context['filter'] = self.filterset
        return context

    def get_cache_key(self):
        """Generate a unique cache key based on request parameters."""
        location_filter = self.request.GET.get('location', 'all')

        if self.request.user.is_authenticated:
            user_profile = getattr(self.request.user, 'profile', None)
            user_profile_location = getattr(user_profile, 'location', 'unknown') if user_profile else 'unknown'
        else:
            user_profile_location = 'unknown'

        return f'services_queryset_{location_filter}_{user_profile_location}'


class CreateServiceView(LoginRequiredMixin, BaseLocation, FavoritesCountMixin, UnreadNotificationMixin, CreateView):
    model = Job
    template_name = 'jobs/create/service_create.html'
    form_class = CreateServiceForm

    def form_valid(self, form):
        # Устанавливаем работодателя перед сохранением формы
        form.instance.employer = self.request.user

        try:
            response = super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

        return redirect('jobs:service-detail', pk=form.instance.pk)

    def get_success_url(self):
        return reverse('jobs:service-detail', kwargs={'pk': self.object.pk})


User = get_user_model()


class CreateVacancyView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, CreateView):
    model = Job
    template_name = 'jobs/create/vacancy_create.html'
    form_class = CreateVacancyForm

    def dispatch(self, request, *args, **kwargs):
        # Проверка на наличие профиля компании у пользователя
        try:
            user_profile = self.request.user.profile  # Пытаемся получить профиль пользователя
            if not user_profile.company_profile:  # Проверяем привязан ли пользователь к компании
                # Сообщение об ошибке и редирект, если пользователь не привязан к компании
                messages.error(self.request, "Вы должны быть привязаны к компании, чтобы создавать вакансии.")
                return redirect('jobs:home')  # Перенаправление на главную страницу
        except ObjectDoesNotExist:
            # Если профиль пользователя не найден (RelatedObjectDoesNotExist)
            messages.error(self.request, "Профиль пользователя не найден. Пожалуйста, создайте профиль.")
            return redirect('jobs:home')  # Перенаправление на главную страницу

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Устанавливаем работодателя перед сохранением формы
        form.instance.employer = self.request.user

        # Устанавливаем текущую дату и время для полей date и time, если они не установлены
        if form.instance.date is None:
            form.instance.date = timezone.now().date()
        if form.instance.time is None:
            form.instance.time = timezone.now().time()

        # Устанавливаем значение по умолчанию для time_count, если оно не установлено
        if not form.instance.time_count:
            form.instance.time_count = 'full'

        # Проверка принадлежности пользователя к компании
        try:
            user_profile = self.request.user.profile
            if not user_profile.company_profile:
                form.add_error(None, "Вы должны быть привязаны к компании для создания вакансии.")
                return self.form_invalid(form)
        except User.profile.RelatedObjectDoesNotExist:
            form.add_error(None, "Профиль пользователя не найден.")
            return self.form_invalid(form)

        # Проверка количества вакансий за текущий день только для типа 'full'
        if form.instance.time_count == 'full':
            today = timezone.now().date()
            daily_jobs_count = Job.objects.filter(
                employer=self.request.user,
                time_count='full',
                date_posted__date=today
            ).count()
            if daily_jobs_count >= 5:
                form.add_error(None, "Вы не можете публиковать более 5 вакансий типа 'Полная занятость' в день.")
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('jobs:vacancy-detail', kwargs={'pk': self.object.pk})
