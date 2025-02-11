from django import forms
from .models import Job, Category


class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'keys_description',
            'skills_description',
            'location',
            'time_count',
            'date',
            'time',
            'pay_rate',
            'category'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'keys_description': forms.Textarea(attrs={'rows': 4}),
            'skills_description': forms.Textarea(attrs={'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'pay_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'category': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        initial_category = kwargs.pop('initial_category', None)
        super().__init__(*args, **kwargs)

        # Customize the form fields if needed
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Название'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подробнее'})
        self.fields['keys_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ключевые моменты'})
        self.fields['skills_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пунктуальность...'})
        self.fields['location'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Локация'})
        self.fields['date'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Дата'})
        self.fields['time'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Время'})
        self.fields['pay_rate'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Оплата'})
        self.fields['category'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Категория'})

        # Restrict time_count choices to only 'part' and 'daily'
        self.fields['time_count'].choices = [choice for choice in Job.TIME_CHOICES if choice[0] in ('part', 'daily')]

        # Set initial category if provided
        if initial_category:
            self.fields['category'].initial = initial_category

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('category'):
            default_category = Category.objects.first()  # Or some logic to select the default category
            cleaned_data['category'] = default_category
        return cleaned_data


class CreateVacancyForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'keys_description',
            'skills_description',
            'location',
            'time_count',
            'pay_rate',
            'category'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'keys_description': forms.Textarea(attrs={'rows': 4}),
            'skills_description': forms.Textarea(attrs={'rows': 4}),
            'pay_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'category': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        initial_category = kwargs.pop('initial_category', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем значение по умолчанию для time_count
        if 'time_count' not in self.data:
            self.fields['time_count'].initial = 'full'

        # Настраиваем поля формы
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Название'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подробнее'})
        self.fields['keys_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ключевые моменты'})
        self.fields['skills_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пунктуальность...'})
        self.fields['location'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Локация'})
        self.fields['pay_rate'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Оплата'})
        self.fields['category'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Категория'})

        # Restrict time_count choices to only 'full' and 'part'
        self.fields['time_count'].choices = [choice for choice in Job.TIME_CHOICES if choice[0] in ('full', 'part')]

        # Set initial category if provided
        if initial_category:
            self.fields['category'].initial = initial_category

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('category'):
            default_category = Category.objects.first()  # Or some logic to select the default category
            cleaned_data['category'] = default_category
        return cleaned_data



class CategorySearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'formkz-control',
            'placeholder': 'Поиск по названию категории'
        })
    )