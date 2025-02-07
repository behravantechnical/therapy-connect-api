from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from therapy_connect.profiles.models import (
    PatientProfile,
    PsychologicalIssue,
    TherapistProfile,
)

User = get_user_model()


class Availability(models.Model):
    therapist = models.ForeignKey(
        TherapistProfile, on_delete=models.CASCADE, related_name="availabilities"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        # Prevent duplicate time slots
        unique_together = (
            "therapist",
            "date",
            "start_time",
            "end_time",
        )

    def __str__(self):
        return f"{self.therapist.user.email} - {self.date}: {self.start_time} to {self.end_time}"

    def clean(self):
        """
        Ensure start_time is before end_time and prevent overlapping time slots.
        """
        if not self.date or not self.start_time or not self.end_time:
            raise ValidationError("Date, start time, and end time are required.")

        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

        overlapping_slots = (
            Availability.objects.filter(
                therapist=self.therapist,
                date=self.date,
            )
            .exclude(id=self.id)
            .filter(start_time__lt=self.end_time, end_time__gt=self.start_time)
        )

        if overlapping_slots.exists():
            raise ValidationError(
                "Overlapping availability time slots are not allowed."
            )


class TherapyPanel(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="therapy_panels"
    )
    issue = models.ForeignKey(PsychologicalIssue, on_delete=models.CASCADE)
    therapist = models.ForeignKey(
        TherapistProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    assigned_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when therapist was assigned."
    )
    last_session_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date of the last session in this therapy panel.",
    )
    progress_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Details about patient progress for this issue.",
    )
    completion_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Final therapist notes when therapy is completed.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.user.email} - {self.issue.name} ({self.status})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    MEETING_CHOICES = [
        ("google_meet", "Google Meet"),
        ("zoom", "Zoom"),
        ("skype", "Skype"),
        ("other", "Other"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    ]

    panel = models.ForeignKey(
        "TherapyPanel", on_delete=models.CASCADE, related_name="appointments"
    )
    scheduled_time = models.DateTimeField(help_text="Scheduled time in UTC")
    duration = models.PositiveIntegerField(
        help_text="Duration of the appointment in minutes", default=60
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="scheduled"
    )

    meeting_platform = models.CharField(
        max_length=20, choices=MEETING_CHOICES, default="zoom"
    )
    meeting_link = models.URLField(
        blank=True, null=True, help_text="Link to the virtual meeting."
    )

    is_deleted = models.BooleanField(default=False)

    rescheduled_from = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Reference to the previous appointment if rescheduled.",
    )

    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    cancellation_reason = models.TextField(
        blank=True, null=True, help_text="Reason for cancellation if applicable."
    )
    canceled_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Who canceled the appointment?",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_time"]

    def __str__(self):
        return (
            f"Appointment for {self.panel.patient.user.email} on {self.scheduled_time}"
        )

    def clean(self):
        """
        Ensure no overlapping appointments for the same therapist.
        """
        overlapping_appointments = Appointment.objects.filter(
            panel__therapist=self.panel.therapist,
            scheduled_time__lt=self.scheduled_time + timedelta(minutes=self.duration),
            scheduled_time__gte=self.scheduled_time - timedelta(minutes=self.duration),
        ).exclude(id=self.id)

        if overlapping_appointments.exists():
            raise ValidationError(
                "This therapist already has an appointment at this time."
            )

    def can_reschedule(self):
        """
        Returns True if the patient can still reschedule (max 2 times per panel).
        """
        reschedule_count = Appointment.objects.filter(
            panel=self.panel, rescheduled_from__isnull=False
        ).count()
        return reschedule_count < 2


# # Tasks (assign tasks to patients in specific therapy panels)
# class Task(models.Model):
#     PRIORITY_CHOICES = [
#         ("low", "Low"),
#         ("medium", "Medium"),
#         ("high", "High"),
#     ]
#     panel = models.ForeignKey(
#         TherapyPanel, on_delete=models.CASCADE, related_name="tasks"
#     )
#     description = models.TextField()
#     due_date = models.DateField()
#     priority = models.CharField(
#         max_length=10, choices=PRIORITY_CHOICES, default="medium"
#     )
#     is_completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Task for {self.panel.patient.user.email}"


# class Payment(models.Model):
#     appointment = models.OneToOneField(
#         Appointment, on_delete=models.CASCADE, related_name="payment"
#     )
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     is_confirmed = models.BooleanField(default=False)
#     refunded = models.BooleanField(default=False)
#     refund_reason = models.TextField(null=True, blank=True)

#     def process_payment(self):
#         """
#         Marks the payment as confirmed and updates appointment status.
#         """
#         self.is_confirmed = True
#         self.appointment.payment_status = "paid"
#         self.appointment.save()
#         self.save()

#     def process_refund(self, reason):
#         """
#         Marks the payment as refunded.
#         """
#         if not self.is_confirmed:
#             raise ValidationError("Cannot refund an unconfirmed payment.")
#         self.refunded = True
#         self.refund_reason = reason
#         self.appointment.payment_status = "refunded"
#         self.appointment.status = "canceled"
#         self.appointment.save()
#         self.save()

#     def __str__(self):
#         return (
#             f"Payment for {self.appointment.panel.patient.user.email} - {self.amount}"
#         )
