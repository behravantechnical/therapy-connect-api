# import os

# from celery import Celery

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "therapy_connect.settings")

# celery_app = Celery("therapy_connect")
# celery_app.config_from_object("django.conf:settings", namespace="CELERY")
# celery_app.autodiscover_tasks()


import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "therapy_connect.settings")

celery_app = Celery(
    "therapy_connect", broker="redis://redis:6379/0"
)  # ✅ Explicitly set Redis
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
