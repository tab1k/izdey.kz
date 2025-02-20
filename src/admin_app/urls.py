from .views import *
from django.urls import path, include

app_name = 'admin_app'


urlpatterns = [
    path('', AdminPanelView.as_view(), name='info'),

    path('employer-requests/', EmployerRequestsView.as_view(), name='employer-requests'),
    path('employer-requests/detail/<int:pk>/', EmployerRequestDetailView.as_view(), name='employer_detail'),
    path('employer-requests/delete/<int:pk>/', EmployerRequestDeleteView.as_view(), name='employer_delete'),



    path('users/', UsersListView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('users/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('users/detail/<int:pk>/', UserDetailView.as_view(), name='users_detail'),

    path('companies/', CompaniesListView.as_view(), name='companies'),
    path('companies/create/', CompanyCreateView.as_view(), name='company_create'),
    path('companies/update/<int:pk>/', CompanyUpdateView.as_view(), name='company_update'),
    path('companies/delete/<int:pk>/', CompanyDeleteView.as_view(), name='company_delete'),
    path('companies/detail/<int:pk>/', CompaniesDetailView.as_view(), name='companies_detail'),
]

