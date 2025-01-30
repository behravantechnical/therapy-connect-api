from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PatientListView,
    PatientProfileView,
    TherapistListView,
    TherapistProfileView,
)

router = DefaultRouter()
router.register(r"patients", PatientListView, basename="patients")
router.register(r"therapists", TherapistListView, basename="therapists")

app_name = "profiles"
urlpatterns = [
    path("", include(router.urls)),
    path("patients/me/", PatientProfileView.as_view(), name="patient-profile"),
    path("therapist/me/", TherapistProfileView.as_view(), name="therapist-profile"),
]
