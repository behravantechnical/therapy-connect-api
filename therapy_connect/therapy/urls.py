from django.urls import path

from .views import (
    CreateAvailabilityView,
    DeleteAvailabilityView,
    ListAvailabilityView,
    TherapyPanelCreateView,
    TherapyPanelListView,
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
    # POST: Create therapy panel (patients only)
    path(
        "therapy-panels/create/",
        TherapyPanelCreateView.as_view(),
        name="create-therapy-panel",
    ),
    # GET: List therapy panels (patients & therapists)
    path("therapy-panels/", TherapyPanelListView.as_view(), name="therapy-panel-list"),
    # GET/PUT: Retrieve or update a therapy panel (patients & therapists)
    path(
        "therapy-panels/<int:pk>/",
        TherapyPanelRetrieveUpdateView.as_view(),
        name="retrieve-update-therapy-panel",
    ),
]
