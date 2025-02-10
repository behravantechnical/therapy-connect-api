from django.urls import path

from .views import (
    AppointmentRetrieveView,
    CreateAppointmentView,
    CreateAvailabilityView,
    DeleteAvailabilityView,
    ListAvailabilityView,
    PatientAppointmentListView,
    TherapistAppointmentListView,
    TherapistCancelAppointmentView,
    TherapyPanelCreateView,
    TherapyPanelListView,
    TherapyPanelRetrieveUpdateView,
    UpdateAppointmentView,
    UpdateAvailabilityView,
)

app_name = "therapy"
urlpatterns = [
    # Availability Management
    path(
        "availabilities/", ListAvailabilityView.as_view(), name="list-availability"
    ),  # GET: List all availability slots
    path(
        "availabilities/create/",
        CreateAvailabilityView.as_view(),
        name="create-availability",
    ),  # POST: Create availability
    path(
        "availabilities/<int:pk>/",
        UpdateAvailabilityView.as_view(),
        name="retrieve-update-availability",
    ),  # GET/PUT: Retrieve or update
    path(
        "availabilities/<int:pk>/delete/",
        DeleteAvailabilityView.as_view(),
        name="delete-availability",
    ),  # DELETE: Remove availability
    # Therapy Panel Management
    path(
        "therapy-panels/", TherapyPanelListView.as_view(), name="list-therapy-panels"
    ),  # GET: List therapy panels (patients & therapists)
    path(
        "therapy-panels/create/",
        TherapyPanelCreateView.as_view(),
        name="create-therapy-panel",
    ),  # POST: Create therapy panel (patients only)
    path(
        "therapy-panels/<int:pk>/",
        TherapyPanelRetrieveUpdateView.as_view(),
        name="retrieve-update-therapy-panel",
    ),  # GET/PUT: Retrieve or update therapy panel
    # Appointment Management
    path(
        "appointments/", CreateAppointmentView.as_view(), name="create-appointment"
    ),  # POST: Create appointment (panel_id in body)
    path(
        "appointments/<int:pk>/",
        AppointmentRetrieveView.as_view(),
        name="retrieve-appointment",
    ),  # GET: Retrieve a specific appointment
    path(
        "appointments/<int:pk>/update/",
        UpdateAppointmentView.as_view(),
        name="update-appointment",
    ),  # PUT/PATCH: Reschedule or update appointment
    path(
        "appointments/<int:pk>/cancel/",
        TherapistCancelAppointmentView.as_view(),
        name="cancel-appointment",
    ),  # PATCH: Cancel appointment (therapist or patient)
    # Patient-Specific Appointments
    path(
        "appointments/patient/",
        PatientAppointmentListView.as_view(),
        name="list-patient-appointments",
    ),  # GET: List patient’s scheduled appointments
    # Therapist-Specific Appointments
    path(
        "appointments/therapist/",
        TherapistAppointmentListView.as_view(),
        name="list-therapist-appointments",
    ),  # GET: List therapist’s appointments with filters
]
