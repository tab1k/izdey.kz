# Generated by Django 5.0.6 on 2024-08-24 10:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0024_alter_user_email"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Verification",
        ),
    ]
