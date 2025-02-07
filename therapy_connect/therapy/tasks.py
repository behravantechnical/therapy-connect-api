from celery import shared_task
from django.utils import timezone

from .models import Appointment


@shared_task
def auto_complete_appointments():
    """
    Automatically mark appointments as 'completed' if their duration has passed.
    """
    now = timezone.now()
    completed_appointments = Appointment.objects.filter(
        status="scheduled",
        scheduled_time__lte=now - timezone.timedelta(hours=1),
    )
    count = completed_appointments.update(status="completed")
    return f"Updated {count} appointments to 'completed'"
