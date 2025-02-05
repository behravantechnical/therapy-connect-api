from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from therapy_connect.profiles.models import PatientProfile, TherapistProfile

from .models import Availability, TherapyPanel
from .schemas import (
    create_availability_schema,
    delete_availability_schema,
    list_availability_schema,
    update_availability_schema,
)
from .serializers import (
    AvailabilitySerializer,
    TherapyPanelCreateSerializer,
    TherapyPanelPatientRetrieveSerializer,
    TherapyPanelPatientUpdateSerializer,
    TherapyPanelTherapistRetrieveSerializer,
    TherapyPanelTherapistUpdateSerializer,
)
from .services import filter_availability


@create_availability_schema
@extend_schema(tags=["CreateAvailability"])
class CreateAvailabilityView(generics.CreateAPIView):
    """
    Allows therapists to create their own availability slots.
    Only authenticated therapists can access this endpoint.
    """

    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def perform_create(self, serializer):
        """Assigns the therapist automatically from the authenticated user."""
        therapist = get_object_or_404(TherapistProfile, user=self.request.user)
        serializer.save(therapist=therapist)  # Assign therapist before saving


@list_availability_schema
@extend_schema(tags=["ListAvailability"])
class ListAvailabilityView(generics.ListAPIView):
    """
    Allows patients to view available time slots.
    Filters:
    - therapist_id
    - day_of_week
    - start_time_after / start_time_before
    - end_time_after / end_time_before
    """

    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["therapist", "date"]

    def get_queryset(self):
        """
        Uses the `filter_availability` function from services.py to apply filters.
        """
        queryset = Availability.objects.all()
        return filter_availability(queryset, self.request.query_params)


@update_availability_schema
@extend_schema(tags=["UpdateAvailability"])
class UpdateAvailabilityView(generics.RetrieveUpdateAPIView):
    """
    Allows a therapist to update their availability slots.
    Only the therapist who created the slot can update it.
    """

    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Ensure that only the therapist who created the slot can access it.
        """
        therapist = get_object_or_404(TherapistProfile, user=self.request.user)
        availability = get_object_or_404(
            Availability, id=self.kwargs["pk"], therapist=therapist
        )
        return availability


@delete_availability_schema
@extend_schema(tags=["DeleteAvailability"])
class DeleteAvailabilityView(generics.DestroyAPIView):
    """
    Allows a therapist to delete their availability slots.
    Only the therapist who created the slot can delete it.
    """

    queryset = Availability.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Ensure that only the therapist who created the slot can access it.
        """
        therapist = get_object_or_404(TherapistProfile, user=self.request.user)
        availability = get_object_or_404(
            Availability, id=self.kwargs["pk"], therapist=therapist
        )
        return availability


class TherapyPanelCreateView(generics.CreateAPIView):
    """
    API endpoint for patients to create a therapy panel.
    """

    queryset = TherapyPanel.objects.all()
    serializer_class = TherapyPanelCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Ensure only patients can create therapy panels.
        """
        patient = PatientProfile.objects.filter(user=self.request.user).first()
        if not patient:
            raise PermissionDenied("Only patients can create a therapy panel.")

        serializer.save(patient=patient)


class TherapyPanelRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve OR update a therapy panel.

    - GET: Patients can see issue, therapist info, status, and assigned_at.
      - Therapists can see issue, patient info, status, "
      "assigned_at, last_session_date, progress_notes, and completion_notes.

    - PUT:
      - Patients:
        - First update: Must select a therapist from the suggested list.
        - Later updates: Can only update `status` (to "paused").
      - Therapists:
        - Can update `status` (to "paused" or "completed"), "
        "`progress_notes`, and `completion_notes`.
        - If a therapist sets `status` to 'completed', `last_session_date` is recorded.
    """

    queryset = TherapyPanel.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Dynamically select serializer based on user type (Patient or Therapist)."""
        user = self.request.user

        if self.request.method == "GET":
            if hasattr(user, "patient_profile"):
                return TherapyPanelPatientRetrieveSerializer
            if hasattr(user, "therapist_profile"):
                return TherapyPanelTherapistRetrieveSerializer

        elif self.request.method == "PUT":
            if hasattr(user, "patient_profile"):
                return TherapyPanelPatientUpdateSerializer
            if hasattr(user, "therapist_profile"):
                return TherapyPanelTherapistUpdateSerializer

        raise PermissionDenied(
            "You do not have permission to view or update this therapy panel."
        )

    def get_object(self):
        """Ensure only the associated patient or therapist can access the panel."""
        therapy_panel = super().get_object()
        user = self.request.user

        if hasattr(user, "patient_profile") and therapy_panel.patient.user == user:
            return therapy_panel  # Patient accessing their own panel

        if (
            hasattr(user, "therapist_profile")
            and therapy_panel.therapist
            and therapy_panel.therapist.user == user
        ):
            return therapy_panel  # Therapist accessing their assigned panel

        raise PermissionDenied(
            "You do not have permission to view or update this therapy panel."
        )


class TherapyPanelListView(generics.ListAPIView):
    """
    API endpoint for listing therapy panels.

    - Patients can see their own therapy panels.
    - Therapists can see therapy panels assigned to them.
    """

    # serializer_class = TherapyPanelListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Dynamically select serializer based on user type (Patient or Therapist)."""
        user = self.request.user

        if self.request.method == "GET":
            if hasattr(user, "patient_profile"):
                return TherapyPanelPatientRetrieveSerializer
            if hasattr(user, "therapist_profile"):
                return TherapyPanelTherapistRetrieveSerializer

        raise PermissionDenied(
            "You do not have permission to view or update this therapy panel."
        )

    def get_queryset(self):
        """Filter therapy panels based on user type (patient or therapist)."""
        user = self.request.user

        if hasattr(user, "patient_profile"):
            return TherapyPanel.objects.filter(patient=user.patient_profile)

        if hasattr(user, "therapist_profile"):
            return TherapyPanel.objects.filter(therapist=user.therapist_profile)

        return TherapyPanel.objects.none()  # No access for other users
