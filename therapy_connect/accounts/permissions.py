from rest_framework import permissions


class IsOwnerOrSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow the owner of the profile or a superuser to access or modify it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow superusers to access any object
        if request.user.is_superuser:
            return True

        # Allow the owner of the profile to access or modify it
        return obj == request.user
