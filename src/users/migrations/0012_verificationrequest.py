# Generated by Django 5.0.6 on 2024-06-28 05:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_rename_is_verified_userprofile_verified_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='pending', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
