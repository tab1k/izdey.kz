# Generated by Django 5.0.6 on 2024-08-23 11:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0010_job_keys_description_job_skills_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="keys_description",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="job",
            name="skills_description",
            field=models.TextField(),
        ),
    ]
