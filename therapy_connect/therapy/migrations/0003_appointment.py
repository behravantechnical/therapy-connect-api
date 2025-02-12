# Generated by Django 5.1.1 on 2025-02-06 12:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("therapy", "0002_therapypanel"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Appointment",
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
                    "scheduled_time",
                    models.DateTimeField(help_text="Scheduled time in UTC"),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(
                        default=60, help_text="Duration of the appointment in minutes"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("completed", "Completed"),
                            ("canceled", "Canceled"),
                        ],
                        default="scheduled",
                        max_length=10,
                    ),
                ),
                (
                    "meeting_platform",
                    models.CharField(
                        choices=[
                            ("google_meet", "Google Meet"),
                            ("zoom", "Zoom"),
                            ("skype", "Skype"),
                            ("other", "Other"),
                        ],
                        default="zoom",
                        max_length=20,
                    ),
                ),
                (
                    "meeting_link",
                    models.URLField(
                        blank=True, help_text="Link to the virtual meeting.", null=True
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("refunded", "Refunded"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                (
                    "cancellation_reason",
                    models.TextField(
                        blank=True,
                        help_text="Reason for cancellation if applicable.",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "canceled_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="Who canceled the appointment?",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "panel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="therapy.therapypanel",
                    ),
                ),
                (
                    "rescheduled_from",
                    models.ForeignKey(
                        blank=True,
                        help_text="Reference to the previous appointment if rescheduled.",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="therapy.appointment",
                    ),
                ),
            ],
            options={
                "ordering": ["scheduled_time"],
            },
        ),
    ]
