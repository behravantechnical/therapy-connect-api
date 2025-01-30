from rest_framework import permissions


class IsPatientOrSuperuser(permissions.BasePermission):
    """
    Custom permission to allow only patients to manage their own profiles,
    while superusers can access all profiles.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.user == request.user


class IsTherapistOrSuperuser(permissions.BasePermission):
    """
    Custom permission to allow only therapists and superusers to access the TherapistProfileView.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_superuser
