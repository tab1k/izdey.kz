from myaccount.views import *
from django.urls import path, include

app_name = 'myaccount'


urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),

    # PROFILE
    path('resume/', include(('resume.urls', 'resume'), namespace='resume')),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/my-data/', UserProfileData.as_view(), name='user_data'),
    path('profile/my-profile/', UserMyProfileView.as_view(), name='user_my_profile'),
    path('profile/my-company/', UserCompanyView.as_view(), name='user_company'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('delete_account/', UserDeleteView.as_view(), name='delete_account'),

    # RESPONSES
    path('responses/', ResponsesView.as_view(), name='responses'),
    path('responses/done/', DoneVacanciesView.as_view(), name='responses_done'),


    path('help/', HelpView.as_view(), name='help'),
    path('about/', AboutView.as_view(), name='about'),

    path('my-service/', MyServiceView.as_view(), name='my_service'),
    path('my-vacancy/', MyVacancyView.as_view(), name='my_vacancy'),
    path('delete-job/<int:pk>/', JobDeleteView.as_view(), name='delete_job'),




    # DASHBOARD
    path('dashboard/', DashBoardView.as_view(), name='dashboard'),

]