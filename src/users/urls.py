from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from users.views import *
from django.urls import path, include

app_name = 'users'


urlpatterns = [
    path('signin/', SignInView.as_view(), name='signin'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('employer-request/', EmployerRequestView.as_view(), name='employer_request'),



    path('employer-settings/<int:pk>/', EmployerProfileView.as_view(), name='employer-settings'),
    path('company/', CompanyViewPage.as_view(), name='company-list'),

    path('<int:pk>/', ProfileFromResponse.as_view(), name='profile-response'),


    path('reset_password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path("search-city/", search_city, name="search_city"),
    path('update-location/', update_location, name='update_location'),
    path('update-language', update_language, name='update_language'),

    path('logout/', LogoutView.as_view(), name='logout'),
]

