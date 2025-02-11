from django import forms
import django_filters
from django.forms.widgets import DateInput
import django_filters
from django.forms import TextInput, Select, NumberInput, DateInput
from .models import Job, Category
from jobs.models import *


class DateInput(forms.DateInput):
    input_type = 'date'



class JobFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Категория',
        widget=Select(attrs={'class': 'formkz-control'})
    )
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок содержит',
        widget=TextInput(attrs={'class': 'formkz-control', 'placeholder': 'Введите заголовок'})
    )
    location = django_filters.ChoiceFilter(
        choices=Job.LOCATION_CHOICES,
        label='Местоположение',
        widget=Select(attrs={'class': 'formkz-control'})
    )

    pay_rate__gte = django_filters.NumberFilter(
        field_name='pay_rate',
        lookup_expr='gte',
        label='Минимальная оплата',
        widget=NumberInput(attrs={'class': 'formkz-control', 'placeholder': 'Мин. оплата'})
    )
    pay_rate__lte = django_filters.NumberFilter(
        field_name='pay_rate',
        lookup_expr='lte',
        label='Максимальная оплата',
        widget=NumberInput(attrs={'class': 'formkz-control', 'placeholder': 'Макс. оплата'})
    )

    class Meta:
        model = Job
        fields = ['category', 'title', 'location', 'pay_rate__gte', 'pay_rate__lte']


