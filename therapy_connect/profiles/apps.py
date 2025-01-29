from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "therapy_connect.profiles"

    def ready(self):
        from . import signals  # noqa: F401  # Ensure signals are imported
