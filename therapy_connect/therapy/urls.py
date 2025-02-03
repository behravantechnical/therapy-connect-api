from django.urls import path

from .views import (
    CreateAvailabilityView,
    DeleteAvailabilityView,
    ListAvailabilityView,
    UpdateAvailabilityView,
)

app_name = "therapy"
urlpatterns = [
    # create
    path(
        "availability/create/",
        CreateAvailabilityView.as_view(),
        name="create-availability",
    ),
    # list
    path("availability/", ListAvailabilityView.as_view(), name="list-availability"),
    # update and retreive
    path(
        "availability/<int:pk>/update/",
        UpdateAvailabilityView.as_view(),
        name="update-availability",
    ),
    # delete
    path(
        "availability/<int:pk>/delete/",
        DeleteAvailabilityView.as_view(),
        name="delete-availability",
    ),
]
