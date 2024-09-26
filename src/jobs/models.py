from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from users.models import User
from datetime import date


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.category.name} - {self.name}'


class Keyword(models.Model):
    word = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.word} -> {self.category.name} -> {self.subcategory.name if self.subcategory else "No Subcategory"}'


class Job(models.Model):
    TIME_CHOICES = (
        ('full', 'Полная занятость'),
        ('part', 'Договорная занятость'),
        ('daily', 'Единоразовая услуга'),
    )

    LOCATION_CHOICES = (
        ('tse', 'Астана'),
        ('ala', 'Алматы'),
        ('sco', 'Актау'),
        ('krg', 'Караганда'),
        ('ust', 'Усть-Каменагорск'),
        ('shym', 'Шымкент'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    keys_description = models.TextField(blank=True, null=True)
    skills_description = models.TextField(blank=True, null=True)
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    location = models.CharField(max_length=25, choices=LOCATION_CHOICES, blank=True, default='tse')
    time_count = models.CharField(max_length=155, choices=TIME_CHOICES, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_time_display(self):
        return dict(self.TIME_CHOICES).get(self.time_count, 'None')

    def get_location_display(self):
        return dict(self.LOCATION_CHOICES).get(self.location, 'Unknown')

    def save(self, *args, **kwargs):
        # Проверка количества публикаций за текущий день
        today = now().date()
        daily_jobs_count = Job.objects.filter(employer=self.employer, date_posted__date=today).count()

        if daily_jobs_count >= 5:
            raise ValidationError("Вы не можете публиковать более 5 вакансий в день.")

        # Автоматический подбор категории и подкатегории
        if not self.category or not self.subcategory:
            self._suggest_category_and_subcategory()

        super().save(*args, **kwargs)

    def _suggest_category_and_subcategory(self):
        title_keywords = self.title.lower().split()  # Преобразуем заголовок в список ключевых слов

        for word in title_keywords:
            keyword_entry = Keyword.objects.filter(word=word).first()  # Ищем ключевое слово в базе данных

            if keyword_entry:
                self.category = keyword_entry.category  # Устанавливаем категорию
                self.subcategory = keyword_entry.subcategory  # Устанавливаем подкатегорию (если есть)
                break  # Прерываем цикл, если нашли соответствие

    def user_has_applied(self, user):
        # Метод для проверки, отправил ли пользователь заявку
        return JobResponse.objects.filter(user=user, job=self).exists()

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'


class JobResponse(models.Model):
    STATUS_CHOICES = (
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
        ('pending', 'На рассмотрении'),
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_responses')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='job_responses')
    resume = models.ForeignKey('resume.Resume', on_delete=models.SET_NULL, related_name='resume_responses', null=True,
                               blank=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заявка от {self.user.first_name} {self.user.last_name} на {self.job.title}'

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        indexes = [
            models.Index(fields=['user', 'job']),
        ]
