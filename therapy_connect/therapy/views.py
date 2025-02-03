from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from therapy_connect.profiles.models import TherapistProfile

from .models import Availability
from .serializers import AvailabilitySerializer
from .services import filter_availability


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
