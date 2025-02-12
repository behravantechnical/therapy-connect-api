# Generated by Django 5.1.1 on 2025-01-21 12:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("PATIENT", "Patient"), ("THERAPIST", "Therapist")],
                default="PATIENT",
                max_length=10,
            ),
        ),
    ]
