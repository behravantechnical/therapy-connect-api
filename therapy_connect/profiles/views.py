from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from .models import PatientProfile, TherapistProfile
from .permissions import (
    IsAdminUser,
    IsPatientOrSuperuser,
    IsTherapistOrSuperuser,
)
from .schemas import (
    admin_can_list_patient_profile_schema,
    admin_can_list_therapist_profile_schema,
    patient_profile_schema,
    therapist_profile_schema,
)
from .serializers import (
    AdminPatientProfileSerializer,
    AdminTherapistProfileSerializer,
    PatientProfileSerializer,
    TherapistProfileSerializer,
)


@patient_profile_schema
@extend_schema(tags=["PatientProfile"])
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


@therapist_profile_schema
@extend_schema(tags=["TherapistProfile"])
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


@admin_can_list_patient_profile_schema
@extend_schema(tags=["AdminPatientProfileList"])
class PatientListView(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve a list of all patients (admin-only).
    - GET /patients/ -> List all patient profiles (Admin only)
    - GET /patients/<id>/ -> Retrieve a specific patient profile (Admin only)
    """

    queryset = PatientProfile.objects.all()
    serializer_class = AdminPatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@admin_can_list_therapist_profile_schema
@extend_schema(tags=["AdminTherapistProfileList"])
class TherapistListView(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve a list of all therapists.
    - GET /therapists/ -> List all therapist profiles (Public or Admin-only)
    - GET /therapists/<id>/ -> Retrieve a specific therapist profile (Public or Admin-only)
    """

    queryset = TherapistProfile.objects.all()
    serializer_class = AdminTherapistProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
