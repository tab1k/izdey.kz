# Generated by Django 5.0.6 on 2024-09-12 22:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0013_alter_job_date_alter_job_time"),
        ("resume", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="resume",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="jobs.category",
                verbose_name="Категория",
            ),
        ),
    ]
