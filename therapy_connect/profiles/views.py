from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import PatientProfile, TherapistProfile
from .permissions import IsPatientOrSuperuser, IsTherapistOrSuperuser
from .serializers import PatientProfileSerializer, TherapistProfileSerializer


class PatientProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve and update a patient's profile.
    - GET: View full profile details.
    - PATCH: Update only the `profile_image`.
    - DELETE: Soft delete (deactivate the user).
    """

    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatientOrSuperuser]

    def get_object(self):
        """Returns the logged-in user's profile."""
        user = self.request.user
        return get_object_or_404(PatientProfile, user=user)

    def perform_destroy(self, instance):
        """
        Soft delete: Deactivate the user instead of deleting the profile.
        """
        user = instance.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Profile deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class TherapistProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve and update a therapist's profile.
    - GET: View full profile details.
    - PATCH: Update only specific fields (e.g., profile_image,
    qualifications, specialties, time_zone).
    - DELETE: Soft delete (deactivate the user).
    """

    serializer_class = TherapistProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsTherapistOrSuperuser]

    def get_object(self):
        """Returns the logged-in therapist's profile."""
        user = self.request.user
        return get_object_or_404(TherapistProfile, user=user)

    def perform_destroy(self, instance):
        """
        Soft delete: Deactivate the user instead of deleting the profile.
        """
        user = instance.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Profile deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
