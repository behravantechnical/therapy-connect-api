from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import PatientProfile
from .permissions import IsPatientOrSuperuser
from .serializers import PatientProfileSerializer


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


# class ListAllProfilesView(generics.ListAPIView):
#     """
#     List all patient profiles. Only accessible by superusers.
#     """

#     serializer_class = PatientProfileSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return PatientProfile.objects.all()
