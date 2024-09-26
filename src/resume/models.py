from django.db import models

from jobs.models import Category
from users.models import *


class Resume(models.Model):
    EDUCATION_LEVELS = (
        ('none', 'Без образования'),
        ('high_school', 'Среднее образование'),
        ('bachelor', 'Бакалавр'),
        ('master', 'Магистр'),
        ('phd', 'Доктор наук'),
    )

    EXPERIENCE_CHOICES = (
        ('no_experience', 'Нет опыта'),
        ('less_than_1', 'Меньше года'),
        ('1_to_3', '1-3 года'),
        ('3_to_5', '3-5 лет'),
        ('more_than_5', 'Более 5 лет'),
    )

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255, verbose_name='Название резюме')
    about = models.TextField(verbose_name='О себе')
    education = models.CharField(max_length=20, choices=EDUCATION_LEVELS, default='none',
                                 verbose_name='Уровень образования')
    vuz = models.CharField(max_length=255, verbose_name='Учреждение', blank=True, null=True)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='no_experience',
                                  verbose_name='Опыт работы')
    skills = models.TextField(verbose_name='Навыки')
    phone_number = models.CharField(max_length=25, verbose_name='Телефон для связи', blank=True, null=True)
    email = models.EmailField(verbose_name='Email для связи', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    active = models.BooleanField(default=True, verbose_name='Резюме активно')

    def get_education_level(self):
        return dict(self.EDUCATION_LEVELS).get(self.education, 'None')

    def get_experience(self):
        return dict(self.EXPERIENCE_CHOICES).get(self.experience, 'None')

    def __str__(self):
        return f"{self.title} - {self.user_profile.user.phone_number}"

    class Meta:
        verbose_name = 'Резюме'
        verbose_name_plural = 'Резюме'
        ordering = ['-created_at']
