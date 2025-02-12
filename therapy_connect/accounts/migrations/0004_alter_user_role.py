# Generated by Django 5.1.1 on 2025-01-21 12:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("PATIENT", "Patient"), ("THERAPIST", "Therapist")],
                max_length=10,
            ),
        ),
    ]
