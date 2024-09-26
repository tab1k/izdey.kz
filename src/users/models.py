from PIL import Image
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from users.managers import CustomUserManager
import re
from django.core.exceptions import ValidationError
from django.utils import timezone


class User(AbstractUser):
    phone_number = models.CharField(max_length=25, unique=True, blank=False)
    email = models.EmailField(blank=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def clean(self):
        super().clean()
        if not self.phone_number:
            raise ValidationError("Номер телефона не может быть пустым.")
        # Убедитесь, что номер начинается с +7
        if not self.phone_number.startswith('+7'):
            self.phone_number = '+7' + self.phone_number.lstrip('+7')
        # Убедитесь, что номер состоит только из цифр после +7
        if not re.match(r'^\+7[0-9]+$', self.phone_number):
            raise ValidationError("Номер телефона должен состоять из цифр.")

    def save(self, *args, **kwargs):
        # Форматирование номера телефона
        if not self.phone_number.startswith('+7'):
            self.phone_number = '+7' + self.phone_number.lstrip('+7')
        self.phone_number = re.sub(r'[^0-9+]', '', self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    TYPE_OF_ACCOUNT = (
        ('employer', 'Работодатель'),
        ('worker', 'Рабочий'),
    )

    LANGUAGE_CHOICES = (
        ('kaz', _('Казахский')),
        ('rus', _('Русский')),
        ('eng', _('Английский')),
    )

    LOCATION_CHOICES = (
        ('tse', 'Астана'),
        ('ala', 'Алматы'),
        ('sco', 'Актау'),
        ('krg', 'Караганда'),
        ('ust', 'Усть-Каменагорск'),
        ('shym', 'Шымкент'),
    )

    image = models.ImageField(upload_to='user_images', blank=True)
    about = models.TextField(blank=True)
    website_link = models.URLField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=10, choices=TYPE_OF_ACCOUNT, default='worker')
    location = models.CharField(max_length=25, choices=LOCATION_CHOICES, blank=True, default='tse')
    language = models.CharField(max_length=3, choices=LANGUAGE_CHOICES, default='rus')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    verified = models.BooleanField(default=False)  # Общая верификация пользователя

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            img = Image.open(self.image.path)

            crop_width = 300
            crop_height = 300

            current_width, current_height = img.size
            crop_size = min(current_width, current_height)

            left = (current_width - crop_size) / 2
            top = (current_height - crop_size) / 2
            right = (current_width + crop_size) / 2
            bottom = (current_height + crop_size) / 2

            img = img.crop((left, top, right, bottom))
            img.thumbnail((crop_width, crop_height))
            img.save(self.image.path)
        else:
            print("Image is not available or has no path.")

    def get_account_type_display(self):
        return dict(self.TYPE_OF_ACCOUNT).get(self.account_type, 'Неизвестный тип')

    def __str__(self):
        return f'{self.user.phone_number} | {self.get_account_type_display()}'

    def get_location(self):
        return dict(self.LOCATION_CHOICES).get(self.location, 'Unknown location')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class CompanyProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='company_profile',
                                        blank=True, null=True)
    BIN = models.CharField(max_length=12, unique=True, verbose_name='БИН компании', blank=True,
                           null=True)  # БИН компании
    name = models.CharField(max_length=255, verbose_name='Название компании')  # Полное наименование компании
    legal_address = models.CharField(max_length=255, verbose_name='Юридический адрес', blank=True,
                                     null=True)  # Юридический адрес
    about = models.TextField(blank=True, null=True)
    actual_address = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name='Фактический адрес')  # Фактический адрес
    phone_number = models.CharField(max_length=25, verbose_name='Телефон компании', blank=True,
                                    null=True)  # Телефонный номер
    email = models.EmailField(verbose_name='Email компании', blank=True, null=True)  # Электронная почта
    website = models.URLField(blank=True, verbose_name='Сайт компании', null=True)  # Сайт компании
    director_name = models.CharField(max_length=255, verbose_name='ФИО директора', blank=True,
                                     null=True)  # ФИО директора
    bank_account = models.CharField(max_length=20, verbose_name='Расчетный счет', blank=True,
                                    null=True)  # Расчетный счет компании
    bank_name = models.CharField(max_length=255, verbose_name='Банк обслуживания', blank=True,
                                 null=True)  # Банк, обслуживающий компанию
    BIK = models.CharField(max_length=8, verbose_name='БИК банка', blank=True,
                           null=True)  # Банковский идентификационный код
    KBE = models.CharField(max_length=2, verbose_name='КБЕ', blank=True, null=True)  # Код бюджетной единицы
    OKED = models.CharField(max_length=5, verbose_name='ОКЭД', blank=True, null=True)  # Код экономической деятельности
    registration_date = models.DateField(default=timezone.now, verbose_name='Дата регистрации', blank=True,
                                         null=True)  # Дата регистрации компании
    logo = models.ImageField(upload_to='company_logos', blank=True, null=True,
                             verbose_name='Логотип компании')  # Логотип компании
    documents = models.FileField(upload_to='company_docs', blank=True,
                                 verbose_name='Документы компании')  # Учредительные документы
    verified = models.BooleanField(default=False, verbose_name='Профиль подтвержден', blank=True,
                                   null=True)  # Верификация компании
    posts_today = models.PositiveIntegerField(default=0, verbose_name='Публикации сегодня', blank=True,
                                              null=True)  # Количество публикаций сегодня
    last_post_date = models.DateField(default=timezone.now, verbose_name='Дата последней публикации', blank=True,
                                      null=True)  # Дата последней публикации

    def clean(self):
        super().clean()
        if self.BIN:
            if not re.match(r'^\d{12}$', self.BIN):
                raise ValidationError("БИН должен состоять из 12 цифр.")
        if self.phone_number:
            if not re.match(r'^\+7\d+$', self.phone_number):
                raise ValidationError("Телефонный номер должен начинаться с +7 и содержать только цифры.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Профиль компании'
        verbose_name_plural = 'Профили компаний'


class EmployerRequest(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    document = models.FileField(upload_to='documents/', blank=True, null=True, verbose_name="Документ")
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name="Сайт")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.first_name} {self.last_name}"
