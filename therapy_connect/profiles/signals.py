from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PatientProfile, TherapistProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    """
    Automatically create a PatientProfile when a patient user is created.
    """
    if created and instance.role == "patient":
        PatientProfile.objects.get_or_create(user=instance)
    if created and instance.role == "therapist":
        TherapistProfile.objects.get_or_create(user=instance)
