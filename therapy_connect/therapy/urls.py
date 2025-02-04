from django.urls import path

from .views import (
    CreateAvailabilityView,
    DeleteAvailabilityView,
    ListAvailabilityView,
    TherapyPanelCreateView,
    TherapyPanelRetrieveUpdateView,
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
    # Create therapy panel (POST /therapy-panels/)
    path(
        "therapy-panels/", TherapyPanelCreateView.as_view(), name="create-therapy-panel"
    ),
    # Retrieve or update therapy panel (GET /therapy-panels/{id}/, PUT /therapy-panels/{id}/)
    path(
        "therapy-panels/<int:pk>/",
        TherapyPanelRetrieveUpdateView.as_view(),
        name="retrieve-update-therapy-panel",
    ),
]
