# Generated by Django 5.1.1 on 2025-02-03 17:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_alter_therapistprofile_qualifications"),
        ("therapy", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TherapyPanel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("paused", "Paused"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                (
                    "assigned_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Timestamp when therapist was assigned.",
                        null=True,
                    ),
                ),
                (
                    "last_session_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date of the last session in this therapy panel.",
                        null=True,
                    ),
                ),
                (
                    "progress_notes",
                    models.TextField(
                        blank=True,
                        help_text="Details about patient progress for this issue.",
                        null=True,
                    ),
                ),
                (
                    "completion_notes",
                    models.TextField(
                        blank=True,
                        help_text="Final therapist notes when therapy is completed.",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.psychologicalissue",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="therapy_panels",
                        to="profiles.patientprofile",
                    ),
                ),
                (
                    "therapist",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.therapistprofile",
                    ),
                ),
            ],
        ),
    ]
