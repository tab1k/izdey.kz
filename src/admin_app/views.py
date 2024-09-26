from jobs.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
import uuid
from admin_app.forms import UserProfileFormSet
from users.models import *
from rooms.models import Room
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy


class AdminBaseView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # Проверка, что пользователь является администратором
        return self.request.user.is_staff

    def handle_no_permission(self):
        # Редирект, если пользователь не прошел проверку
        return redirect('jobs:home')


class AdminPanelView(AdminBaseView, TemplateView):
    template_name = 'admin_app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        context['rooms'] = Room.objects.all().order_by('-time_start')
        context['request'] = EmployerRequest.objects.all().order_by('-created_at')
        context['companies'] = CompanyProfile.objects.all().order_by('last_post_date')
        context['vacancies'] = Job.objects.filter(time_count='full')
        return context


class EmployerRequestsView(AdminBaseView,  TemplateView):
    template_name = 'admin_app/employers/employer_requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = EmployerRequest.objects.all().order_by('-created_at')
        return context


class EmployerRequestDetailView(AdminBaseView,  DetailView):
    model = EmployerRequest
    context_object_name = 'request'
    template_name = 'admin_app/employers/employer_request_detail.html'


class EmployerRequestDeleteView(AdminBaseView, DeleteView):
    model = EmployerRequest
    template_name = 'admin_app/employers/employer_request_confirm_delete.html'
    success_url = reverse_lazy('admin_app:employer-requests')

# ----------------------------------------------------


class RoomsListView(AdminBaseView,  ListView):
    model = Room
    template_name = 'admin_app/rooms/rooms_admin.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.all()


class RoomsCreateView(AdminBaseView, CreateView):
    model = Room
    fields = ['name', 'description']  # Укажите необходимые поля
    template_name = 'admin_app/rooms/rooms_form.html'
    success_url = reverse_lazy('admin_app:rooms')


class RoomsUpdateView(AdminBaseView, UpdateView):
    model = Room
    fields = ['name', 'description']  # Укажите необходимые поля
    template_name = 'admin_app/rooms/rooms_form.html'
    success_url = reverse_lazy('admin_app:rooms')


class RoomsDeleteView(AdminBaseView, DeleteView):
    model = Room
    template_name = 'admin_app/rooms/rooms_confirm_delete.html'
    success_url = reverse_lazy('admin_app:rooms')


class RoomsDetailView(AdminBaseView,  DetailView):
    model = Room
    template_name = 'admin_app/rooms/rooms_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RoomsDetailView, self).get_context_data(**kwargs)
        return context

# ----------------------------------------------------


class UsersListView(AdminBaseView,  ListView):
    template_name = 'admin_app/users/users_admin.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all()


class UserCreateView(AdminBaseView, CreateView):
    model = User
    fields = ['first_name', 'last_name', 'is_staff', 'phone_number', 'email']  # Поля для модели User
    template_name = 'admin_app/users/user_form.html'
    success_url = reverse_lazy('admin_app:users')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['profile_formset'] = UserProfileFormSet(self.request.POST, self.request.FILES)
        else:
            data['profile_formset'] = UserProfileFormSet()
        return data

    def form_valid(self, form):
        form.instance.username = str(uuid.uuid4())  # Генерация уникального username
        context = self.get_context_data()
        profile_formset = context['profile_formset']
        if form.is_valid() and profile_formset.is_valid():
            self.object = form.save()  # Сохранение основного объекта User
            profile_formset.instance = self.object  # Привязка профиля к пользователю
            profile_formset.save()  # Сохранение профиля
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class UserUpdateView(AdminBaseView, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'is_staff', 'phone_number', 'email']  # Поля для модели User
    template_name = 'admin_app/users/user_form.html'
    success_url = reverse_lazy('admin_app:users')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['profile_formset'] = UserProfileFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['profile_formset'] = UserProfileFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        profile_formset = context['profile_formset']
        if profile_formset.is_valid():
            self.object = form.save()
            profile_formset.instance = self.object
            profile_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class UserDeleteView(AdminBaseView, DeleteView):
    model = User
    template_name = 'admin_app/users/user_confirm_delete.html'
    success_url = reverse_lazy('admin_app:users')

    def delete(self, request, *args, **kwargs):
        # Добавьте логику для подтверждения удаления здесь, если необходимо
        return super().delete(request, *args, **kwargs)



class UserDetailView(AdminBaseView,  DetailView):
    model = User
    template_name = 'admin_app/users/users_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        try:
            user_profile = user.profile
        except UserProfile.DoesNotExist:
            user_profile = None

        context['user_profile'] = user_profile
        return context

# ----------------------------------------------------


class CompaniesListView(AdminBaseView,  ListView):
    model = CompanyProfile
    template_name = 'admin_app/companies/companies_admin.html'
    context_object_name = 'companies'

    def get_queryset(self):
        return CompanyProfile.objects.all().order_by('last_post_date')


class CompanyCreateView(AdminBaseView, CreateView):
    model = CompanyProfile
    fields = '__all__'  # Включить все поля модели CompanyProfile для создания компании
    template_name = 'admin_app/companies/company_form.html'
    success_url = reverse_lazy('admin_app:companies')

    def form_valid(self, form):
        # Добавьте логику проверки и обработки формы здесь, если необходимо
        return super().form_valid(form)


class CompanyUpdateView(AdminBaseView, UpdateView):
    model = CompanyProfile
    fields = '__all__'  # Включить все поля модели CompanyProfile
    template_name = 'admin_app/companies/company_form.html'
    success_url = reverse_lazy('admin_app:companies')

    def form_valid(self, form):
        # Добавьте логику проверки и обработки формы здесь, если необходимо
        return super().form_valid(form)


class CompanyDeleteView(AdminBaseView, DeleteView):
    model = CompanyProfile
    template_name = 'admin_app/companies/company_confirm_delete.html'
    success_url = reverse_lazy('admin_app:companies')

    def delete(self, request, *args, **kwargs):
        # Добавьте логику для подтверждения удаления здесь, если необходимо
        return super().delete(request, *args, **kwargs)


class CompaniesDetailView(AdminBaseView, DetailView):
    model = CompanyProfile
    context_object_name = 'company'
    template_name = 'admin_app/companies/companies_detail.html'
