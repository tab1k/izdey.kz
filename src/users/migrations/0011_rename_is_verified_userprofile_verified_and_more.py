# Generated by Django 5.0.6 on 2024-06-28 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_individualverification_user_verification_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_verified',
            new_name='verified',
        ),
        migrations.RemoveField(
            model_name='verification',
            name='verified',
        ),
    ]
