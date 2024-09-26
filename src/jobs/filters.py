from django import forms
import django_filters
from django.forms.widgets import DateInput

from jobs.models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class JobFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Категория')
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Заголовок содержит')
    location = django_filters.ChoiceFilter(choices=Job.LOCATION_CHOICES, label='Местоположение')
    date_posted__gte = django_filters.DateFilter(field_name='date_posted', lookup_expr='gte', label='Опубликована после (Дата)', widget=DateInput)
    date_posted__lte = django_filters.DateFilter(field_name='date_posted', lookup_expr='lte', label='Опубликована до (Дата)', widget=DateInput)
    pay_rate__gte = django_filters.NumberFilter(field_name='pay_rate', lookup_expr='gte', label='Минимальная оплата')
    pay_rate__lte = django_filters.NumberFilter(field_name='pay_rate', lookup_expr='lte', label='Максимальная оплата')

    class Meta:
        model = Job
        fields = []



