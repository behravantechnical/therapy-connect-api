from django.urls import path

from .views import (
    CreateAvailabilityView,
    DeleteAvailabilityView,
    ListAvailabilityView,
    TherapyPanelCreateView,
    UpdateAvailabilityView,
)

app_name = "therapy"
urlpatterns = [
    # Create Availability
    path(
        "availability/create/",
        CreateAvailabilityView.as_view(),
        name="create-availability",
    ),
    # List Available Slots
    path("availability/", ListAvailabilityView.as_view(), name="list-availability"),
    # Update and Retrieve Availability
    path(
        "availability/<int:pk>/update/",
        UpdateAvailabilityView.as_view(),
        name="update-availability",
    ),
    # Delete Availability
    path(
        "availability/<int:pk>/delete/",
        DeleteAvailabilityView.as_view(),
        name="delete-availability",
    ),
    # create therapy panel
    path(
        "therapy-panels/", TherapyPanelCreateView.as_view(), name="create-therapy-panel"
    ),
]
