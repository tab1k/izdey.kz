# Generated by Django 5.0.6 on 2024-06-29 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_verification_options_verification_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
