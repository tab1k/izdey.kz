from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import FormView, TemplateView, ListView, DetailView
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from jobs.models import Job
from notifications.mixins import UnreadNotificationMixin
from wallet.models import Deposit
from .forms import UserSignInForm, UserSignUpForm, UserProfileForm, CustomPasswordResetForm
from .mixins import AdminRequiredMixin
from .models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import *
import telebot
from django.conf import settings
from django.views.generic.edit import FormView
from .forms import EmployerRequestForm
from django.urls import reverse_lazy
from django.http import Http404
from django.views.generic.edit import UpdateView

User = get_user_model()


class SignInView(FormView):
    form_class = UserSignInForm
    template_name = 'users/signin.html'
    success_url = reverse_lazy('jobs:home')

    def form_valid(self, form):
        phone_number = form.cleaned_data['username']  # username теперь соответствует phone_number
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=phone_number, password=password)
        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error(None, "Неверный номер телефона или пароль.")
            return self.form_invalid(form)


class SignUpView(FormView):
    form_class = UserSignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:signin')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.username = form.cleaned_data['phone_number']  # Set phone_number as username
        user.save()

        # Create UserProfile
        UserProfile.objects.create(user=user, account_type='worker')  # Adjust account_type as needed
        Deposit.objects.create(user=user, amount=0.0)

        return super().form_valid(form)


class EmployerRequestView(FormView):
    template_name = 'users/signup_employer.html'
    form_class = EmployerRequestForm
    success_url = reverse_lazy('jobs:home')  # URL for redirection after successful form submission

    def form_valid(self, form):
        # Save the form data to the database
        employer_request = form.save()

        # Create a bot instance
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

        # Prepare the message to be sent
        chat_id = settings.TELEGRAM_CHAT_ID
        message = (
            f"Новая регистрация работодателя!\n"
            f"Имя: {employer_request.first_name}\n"
            f"Фамилия: {employer_request.last_name}\n"
            f"Компания: {employer_request.company_name}\n"
            f"Номер телефона: {employer_request.phone_number}\n"
            f"Website: {employer_request.website}"
        )
        bot.send_message(chat_id, message)

        # If a document is uploaded, send it to the Telegram chat
        if employer_request.document:
            document_path = employer_request.document.path
            with open(document_path, 'rb') as doc:
                bot.send_document(chat_id, doc)

        # Continue with the form processing
        return super().form_valid(form)


class EmployerProfileView(TemplateView, UnreadNotificationMixin):
    template_name = 'users/employer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employer_profile = get_object_or_404(UserProfile, pk=self.kwargs['pk'])
        context['employer'] = employer_profile
        context['unread_count'] = self.get_unread_notification_count()
        return context


class CompanyViewPage(ListView, UnreadNotificationMixin):
    model = UserProfile
    template_name = 'clients/hi-company.html'

    def get_queryset(self):
        business = UserProfile.objects.filter(entity_type='business')
        return business

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProfileFromResponse(DetailView, UnreadNotificationMixin):
    model = User
    template_name = 'users/profile-from-response.html'
    context_object_name = 'response'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset/password_reset_form.html'
    email_template_name = 'users/password_reset/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = CustomPasswordResetForm


# FUNCTION FOR CHANGE CITY
@csrf_exempt
def update_location(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        location = request.POST.get('location')
        if location in dict(UserProfile.LOCATION_CHOICES):
            user_profile = request.user.profile
            user_profile.location = location
            user_profile.save()
            return JsonResponse({'message': 'Location updated successfully'})
        else:
            return JsonResponse({'error': 'Invalid location'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# FUNCTION FOR CHANGE LANGUAGE

@csrf_exempt
def update_language(request):
    if request.method == 'POST' and request.is_ajax():
        language = request.POST.get('language')
        if language in dict(UserProfile.LANGUAGE_CHOICES):
            user_profile = request.user.profile
            user_profile.language = language
            user_profile.save()
            request.session['django_language'] = language  # Установка языка в сессии Django
            return JsonResponse({'message': 'Language updated successfully'})
        else:
            return JsonResponse({'error': 'Invalid language'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
