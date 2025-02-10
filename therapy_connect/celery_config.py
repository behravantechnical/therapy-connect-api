import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "therapy_connect.settings.local")

celery_app = Celery(
    "therapy_connect", broker="redis://redis:6379/0"
)  # Explicitly set Redis
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "auto_complete_appointments": {
        "task": "therapy_connect.therapy.tasks.auto_complete_appointments",
        "schedule": crontab(minute="*/10"),
    },
}
