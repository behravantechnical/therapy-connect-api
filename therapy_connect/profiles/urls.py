from django.urls import path

from .views import PatientProfileView

app_name = "profiles"
urlpatterns = [
    # path("", include(router.urls)),
    path("me/", PatientProfileView.as_view(), name="patient-profile"),
]
