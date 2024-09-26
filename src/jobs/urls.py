from jobs.views import *
from django.urls import path, include

app_name = 'jobs'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),

    path('remove-from-favorites/<int:job_id>/', RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),
    path('add-to-favorites/<int:job_id>/', AddToFavoritesView.as_view(), name='add_to_favorites'),

    path('service-create/', CreateServiceView.as_view(), name='service-create'),
    path('vacancy-create/', CreateVacancyView.as_view(), name='vacancy-create'),

    path('service/<int:pk>/', JobDetailView.as_view(), name='service-detail'),
    path('vacancy/<int:pk>/', JobDetailView.as_view(), name='vacancy-detail'),
    path('job/<int:pk>/apply/', SendApplicationView.as_view(), name='job-apply'),
    path('job/<int:pk>/response/<int:response_id>/approve/', ApproveJobResponseView.as_view(), name='approve_job_response'),
    path('job/<int:pk>/response/<int:response_id>/reject/', RejectJobResponseView.as_view(), name='reject_job_response'),

    path('error-404/', Error404View.as_view(), name='error'),

    # CATEGORY
    path('category/', CategoryListView.as_view(), name='category-list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('vacancy/', VacancyListView.as_view(), name='vacancy-list'),
    path('service/', ServiceListView.as_view(), name='service-list'),

]