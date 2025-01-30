from django.urls import path

from .views import PatientProfileView, TherapistProfileView

app_name = "profiles"
urlpatterns = [
    # path("", include(router.urls)),
    path("patients/me/", PatientProfileView.as_view(), name="patient-profile"),
    path("therapist/me/", TherapistProfileView.as_view(), name="therapist-profile"),
]
