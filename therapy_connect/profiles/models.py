from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


# Model for psychological issues/categories
class PsychologicalIssue(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    # class Meta:
    # app_label = "profiles"
    # app_label = "therapy_connect.profiles"
    # app_label = "therapy_connect.profiles.models.PsychologicalIssue"


# Profile for Patients
class PatientProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    profile_image = models.ImageField(
        upload_to="patient_profile_images/",
        blank=True,
        null=True,
        help_text="Upload a profile picture for the patient.",
    )
    conversation_summary = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "A brief summary of the analyzed conversation between the "
            "patient and therapist."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def clean(self):
        if self.user.role != "patient":
            raise ValidationError(
                "PatientProfile can only be associated with a patient user."
            )


# Profile for Therapists
class TherapistProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="therapist_profile"
    )
    profile_image = models.ImageField(
        upload_to="patient_profile_images/",
        blank=True,
        null=True,
        help_text="Upload a profile picture for the patient.",
    )
    qualifications = models.TextField()
    specialties = models.ManyToManyField(PsychologicalIssue, blank=True)
    time_zone = models.CharField(
        max_length=50,
        help_text="IANA time zone format (e.g., 'Europe/London', 'America/New_York')",
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
