# Generated by Django 5.0.6 on 2024-08-21 14:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_remove_userprofile_entity_type_companyprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]
