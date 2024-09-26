from django.urls import path
from .views import ResumeCreateView, ResumeUpdateView, ResumeDetailView

app_name = 'resume'

urlpatterns = [
    path('create/', ResumeCreateView.as_view(), name='resume_create'),
    path('edit/', ResumeUpdateView.as_view(), name='resume_edit'),
    path('detail/', ResumeDetailView.as_view(), name='resume_detail'),  # 'detail/' без параметров
]