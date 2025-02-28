# Generated by Django 5.0.6 on 2024-08-25 10:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0028_alter_employerrequest_created_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="companyprofile",
            name="user",
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="BIK",
            field=models.CharField(
                blank=True, max_length=8, null=True, verbose_name="БИК банка"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="BIN",
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                unique=True,
                verbose_name="БИН компании",
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="KBE",
            field=models.CharField(
                blank=True, max_length=2, null=True, verbose_name="КБЕ"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="OKED",
            field=models.CharField(
                blank=True, max_length=5, null=True, verbose_name="ОКЭД"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="actual_address",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Фактический адрес"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="bank_account",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Расчетный счет"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="bank_name",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Банк обслуживания"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="director_name",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="ФИО директора"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="email",
            field=models.EmailField(
                blank=True, max_length=254, null=True, verbose_name="Email компании"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="legal_address",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Юридический адрес"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="company_logos",
                verbose_name="Логотип компании",
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="phone_number",
            field=models.CharField(
                blank=True, max_length=25, null=True, verbose_name="Телефон компании"
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="registration_date",
            field=models.DateField(
                blank=True,
                default=django.utils.timezone.now,
                null=True,
                verbose_name="Дата регистрации",
            ),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="website",
            field=models.URLField(blank=True, null=True, verbose_name="Сайт компании"),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="documents",
            field=models.FileField(
                blank=True, upload_to="company_docs", verbose_name="Документы компании"
            ),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="last_post_date",
            field=models.DateField(
                blank=True,
                default=django.utils.timezone.now,
                null=True,
                verbose_name="Дата последней публикации",
            ),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Название компании"),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="posts_today",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Публикации сегодня"
            ),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="verified",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="Профиль подтвержден"
            ),
        ),
    ]
