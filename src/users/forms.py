from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import EmailValidator
from .models import *
from .models import User, UserProfile, CompanyProfile
from django import forms
from .models import UserProfile
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import re

User = get_user_model()


class UserSignInForm(AuthenticationForm):
    phone_number = forms.CharField(
        max_length=25,
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер телефона',
            'value': '+7 (',  # Начальное значение поля с префиксом +7 и открывающей скобкой
            'oninput': """if (!this.value.startsWith('+7 (')) {
                            this.value = '+7 (' + this.value.replace('+7 (', '');
                        } 
                        if (this.value.length === 8 && this.value[7] !== ')') {
                            this.value = this.value.slice(0, 7) + ')' + this.value.slice(7);
                        }
                        if (this.value.length === 9 && this.value[8] !== ' ') {
                            this.value = this.value.slice(0, 8) + ' ' + this.value.slice(8);
                        }
                        if (this.value.length === 13 && this.value[12] !== ' ') {
                            this.value = this.value.slice(0, 12) + ' ' + this.value.slice(12);
                        }""",  # Скрипт для автоматического добавления скобок и пробелов
        }),
        required=True
    )

    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = self.fields.pop('phone_number')
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        phone_number = self.cleaned_data.get('username')
        # Remove all non-digit characters except the plus sign
        cleaned_phone_number = re.sub(r'[^\d]', '', phone_number)

        # Ensure the number starts with '7' (after the plus sign) and has exactly 10 digits following it
        if not cleaned_phone_number.startswith('7') or len(cleaned_phone_number) != 11:
            raise ValidationError("Введите номер телефона в формате +7 (XXX) XXX-XXXX.")

        # Reformat the number to include the '+7' prefix
        cleaned_phone_number = '+7' + cleaned_phone_number[1:]

        return cleaned_phone_number


class UserSignUpForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=25,
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер телефона',
            'value': '+7 (',
            'oninput': """if (!this.value.startsWith('+7 (')) {
                            this.value = '+7 (' + this.value.replace('+7 (', '');
                        } 
                        if (this.value.length === 8 && this.value[7] !== ')') {
                            this.value = this.value.slice(0, 7) + ')' + this.value.slice(7);
                        }
                        if (this.value.length === 9 && this.value[8] !== ' ') {
                            this.value = this.value.slice(0, 8) + ' ' + this.value.slice(8);
                        }
                        if (this.value.length === 13 && this.value[12] !== ' ') {
                            this.value = this.value.slice(0, 12) + ' ' + this.value.slice(12);
                        }""",
        }),
        required=True
    )
    email = forms.EmailField(
        max_length=254,
        label='Email адрес',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email адрес'
        }),
        required=True
    )

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password1', 'password2']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Remove all non-digit characters except the plus sign
        cleaned_phone_number = re.sub(r'[^\d]', '', phone_number)

        # Ensure the number starts with '7' (without the plus sign) and has exactly 10 digits following it
        if not cleaned_phone_number.startswith('7') or len(cleaned_phone_number) != 11:
            raise ValidationError("Номер телефона должен начинаться с +7 и содержать 10 цифр после +7.")

        # Reformat the number to include the '+7' prefix
        cleaned_phone_number = '+7' + cleaned_phone_number[1:]

        return cleaned_phone_number


class EmployerRequestForm(forms.ModelForm):
    class Meta:
        model = EmployerRequest
        fields = ['first_name', 'last_name', 'company_name', 'document', 'phone_number', 'website']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'company_name': 'Название компании',
            'document': 'Документ',
            'phone_number': 'Номер телефона',
            'website': 'Сайт (если есть)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите ваше имя', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите вашу фамилию', 'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Название вашей компании', 'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Введите номер телефона', 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://example.com', 'class': 'form-control'}),
        }




class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'formkz-control', 'placeholder': 'Имя'}),
        label='Имя'
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'formkz-control', 'placeholder': 'Фамилия'}),
        label='Фамилия'
    )

    email = forms.EmailField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'formkz-control', 'placeholder': 'Email'}),
        label='Email'
    )

    phone_number = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'formkz-control', 'placeholder': 'Телефонный номер', 'pattern': r'\+7[0-9]{10}'}),
        label='Номер телефона'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email']



    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        user_id = self.instance.id  # Получаем ID текущего пользователя

        # Проверка уникальности номера телефона, исключая текущего пользователя
        if User.objects.filter(phone_number=phone_number).exclude(id=user_id).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует.')

        return phone_number


class UserProfileForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Фото'
    )

    about = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'formkz-control', 'placeholder': 'О себе', 'rows': 3}),
        label='Подробнее'
    )

    website_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'formkz-control', 'placeholder': 'Ссылка на сайт'}),
        label='Вебсайт'
    )

    location = forms.ChoiceField(
        choices=UserProfile.LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'formkz-control'}),
        label='Город'
    )

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'formkz-control'}),
        label='Язык'
    )

    class Meta:
        model = UserProfile
        fields = ['image', 'about', 'website_link', 'location', 'language']
        labels = {
            'image': 'Изображение',
            'about': 'О себе',
            'website_link': 'Ссылка на сайт',
            'location': 'Местоположение',
            'language': 'Язык',
        }


class UserCompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'BIN', 'name', 'legal_address', 'actual_address',
            'phone_number', 'email', 'website', 'director_name',
            'bank_account', 'bank_name', 'BIK', 'KBE', 'OKED',
            'registration_date', 'logo', 'documents'
        ]
        labels = {
            'BIN': 'БИН компании',
            'name': 'Название компании',
            'legal_address': 'Юридический адрес',
            'actual_address': 'Фактический адрес',
            'phone_number': 'Телефон компании',
            'email': 'Email компании',
            'website': 'Сайт компании',
            'director_name': 'ФИО директора',
            'bank_account': 'Расчетный счет',
            'bank_name': 'Банк обслуживания',
            'BIK': 'БИК банка',
            'KBE': 'КБЕ',
            'OKED': 'ОКЭД',
            'registration_date': 'Дата регистрации',
            'logo': 'Логотип компании',
            'documents': 'Документы компании',
        }
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'documents': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control ко всем полям, кроме тех, которые уже имеют свои виджеты
        for field_name in self.fields:
            if field_name not in ['logo', 'documents', 'registration_date']:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем сообщения по умолчанию
        self.error_messages = {
            'password_incorrect': 'Неверный текущий пароль.',
            'password_mismatch': 'Пароли не совпадают.',
            'new_password_required': 'Введите новый пароль.',
        }
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None

        # Добавляем класс form-control ко всем полям
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'formkz-control'})

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            if new_password1.isdigit():
                raise ValidationError("Пароль не может состоять только из цифр.")
            # Проверка на слишком простой пароль
            if len(new_password1) < 8:
                raise ValidationError("Пароль должен содержать как минимум 8 символов.")
            # Здесь можно добавить дополнительные проверки на сложность пароля
        return new_password1


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'documents']


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254, widget=forms.EmailInput(
        attrs={'autocomplete': 'email', 'class': 'form-control', 'placeholder': 'Введите ваш email'}))


class LanguageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['language']
