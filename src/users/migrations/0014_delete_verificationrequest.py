# Generated by Django 5.0.6 on 2024-06-28 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_verificationrequest_created_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VerificationRequest',
        ),
    ]
