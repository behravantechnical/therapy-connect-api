from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from therapy_connect.profiles.models import PatientProfile, TherapistProfile

from .models import Appointment, Availability, TherapyPanel
from .schemas import (
    create_availability_schema,
    delete_availability_schema,
    list_availability_schema,
    update_availability_schema,
)
from .serializers import (
    AppointmentSerializer,
    AvailabilitySerializer,
    CancelAppointmentSerializer,
    RescheduleAppointmentSerializer,
    TherapistCancelAppointmentSerializer,
    TherapyPanelCreateSerializer,
    TherapyPanelPatientRetrieveSerializer,
    TherapyPanelPatientUpdateSerializer,
    TherapyPanelTherapistRetrieveSerializer,
    TherapyPanelTherapistUpdateSerializer,
)
from .services import filter_availability, generate_meeting_link


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


class CreateAppointmentView(generics.CreateAPIView):
    """
    Create a new appointment for a therapy panel.
    - Patients can only create appointments for their own therapy panels.
    - The `panel_id` is provided in the request body.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):
        # Get panel_id from request body
        panel_id = request.data.get("panel_id")

        if not panel_id:
            raise ValidationError({"panel_id": "This field is required."})

        # Validate panel existence and ownership
        try:
            panel = TherapyPanel.objects.get(id=panel_id, patient__user=request.user)
        except TherapyPanel.DoesNotExist:
            raise ValidationError(
                {"panel_id": "Invalid therapy panel or unauthorized access."}
            )

        # Validate appointment data
        data = request.data.copy()
        data["panel"] = panel.id  # Assign the correct panel ID

        serializer = self.get_serializer(data=data, context={"request": request})

        if serializer.is_valid():
            # Generate meeting link dynamically
            meeting_link = generate_meeting_link(
                panel_id,
                serializer.validated_data["scheduled_time"],
            )

            appointment = serializer.save(meeting_link=meeting_link)
            return Response(
                AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateAppointmentView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(panel__patient__user=self.request.user)

    def get_serializer_class(self):
        """Determine the correct serializer based on the request."""
        action = self.request.data.get("action")

        if not action:
            raise ValidationError(
                {
                    "action": [
                        "This field is required and must be 'reschedule' or 'cancel'."
                    ]
                }
            )

        if action == "reschedule":
            return RescheduleAppointmentSerializer
        elif action == "cancel":
            return CancelAppointmentSerializer
        else:
            raise ValidationError(
                {"action": ["Invalid action. Use 'reschedule' or 'cancel'."]}
            )

    def update(self, request, *args, **kwargs):
        """Handles both rescheduling and canceling (refund)."""
        action = request.data.get("action")

        # Ensure 'action' is explicitly checked before proceeding
        if not action:
            raise ValidationError(
                {
                    "action": [
                        "This field is required and must be 'reschedule' or 'cancel'."
                    ]
                }
            )

        # Fetch the appointment
        appointment = self.get_object()

        if action == "reschedule":
            serializer = RescheduleAppointmentSerializer(
                appointment, data=request.data, context={"request": request}
            )
        elif action == "cancel":
            serializer = CancelAppointmentSerializer(
                appointment, data=request.data, context={"request": request}
            )
        else:
            raise ValidationError(
                {"action": ["Invalid action. Use 'reschedule' or 'cancel'."]}
            )

        if serializer.is_valid():
            updated_appointment = serializer.save()
            return Response(
                {
                    "message": "Appointment updated successfully.",
                    "appointment": (
                        RescheduleAppointmentSerializer(updated_appointment).data
                        if action == "reschedule"
                        else CancelAppointmentSerializer(updated_appointment).data
                    ),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TherapistCancelAppointmentView(generics.UpdateAPIView):
    """
    API endpoint for therapists to cancel an appointment.
    - Therapists can only cancel their own scheduled appointments.
    - Appointment must be at least 6 hours away.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TherapistCancelAppointmentSerializer

    def get_queryset(self):
        """Filter to return only the appointments of the logged-in therapist."""
        user = self.request.user

        if hasattr(user, "therapist_profile"):
            return Appointment.objects.filter(panel__therapist__user=user)

        return Appointment.objects.none()  # No access for non-therapists

    def update(self, request, *args, **kwargs):
        """Handles therapist appointment cancellation."""
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)

        if serializer.is_valid():
            updated_appointment = serializer.save()
            return Response(
                {
                    "message": "Appointment canceled successfully.",
                    "appointment": TherapistCancelAppointmentSerializer(
                        updated_appointment
                    ).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientAppointmentListView(generics.ListAPIView):
    """
    List all scheduled appointments for the authenticated patient.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only the scheduled appointments where the current user is the patient.
        """
        user = self.request.user

        # Ensure the user is a patient
        if not hasattr(user, "patient_profile"):
            raise PermissionDenied(
                "Only patients can view their scheduled appointments."
            )

        return Appointment.objects.filter(
            panel__patient__user=user,  # Filter by logged-in patient's appointments
            status="scheduled",  # Only show scheduled appointments
        ).order_by("scheduled_time")


class TherapistAppointmentListView(generics.ListAPIView):
    """
    List all appointments (scheduled, completed, or canceled) for the authenticated therapist.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return appointments filtered by the logged-in therapist and requested status.
        """
        user = self.request.user

        # Ensure the user is a therapist
        if not hasattr(user, "therapist_profile"):
            raise PermissionDenied("Only therapists can view their appointments.")

        # Get the therapist's profile
        therapist = user.therapist_profile

        # Get the status filter from query parameters
        status_filter = self.request.query_params.get("status", "").lower()

        # Define default queryset (all appointments for this therapist)
        queryset = Appointment.objects.filter(panel__therapist=therapist)

        # Apply filters based on status
        if status_filter == "scheduled":
            queryset = queryset.filter(
                status="scheduled", scheduled_time__gte=timezone.now()
            ).order_by("scheduled_time")
        elif status_filter == "completed":
            queryset = queryset.filter(status="completed").order_by("-scheduled_time")
        elif status_filter == "canceled":
            queryset = queryset.filter(status="canceled").order_by("-scheduled_time")

        return queryset


class AppointmentRetrieveView(generics.RetrieveAPIView):
    """
    Retrieve a specific appointment by ID.
    Access Control:
    - Patients can only retrieve their own appointments.
    - Therapists can only retrieve appointments related to their patients.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve an appointment only if the user is allowed to access it.
        """
        user = self.request.user
        appointment_id = self.kwargs.get("pk")

        # Get the appointment or return 404 if not found
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Access control: Check if user is allowed to view this appointment
        if hasattr(user, "patient_profile"):  # If user is a patient
            if appointment.panel.patient.user != user:
                raise PermissionDenied("You can only view your own appointments.")

        elif hasattr(user, "therapist_profile"):  # If user is a therapist
            if appointment.panel.therapist.user != user:
                raise PermissionDenied(
                    "You can only view your own patient appointments."
                )

        else:
            raise PermissionDenied("Access denied.")

        return appointment
