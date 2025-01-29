from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsOwnerOrSuperUser
from .schemas import (
    logout_schema,
    password_reset_confirm_schema,
    password_reset_schema,
    user_delete_schema,
    user_profile_schema,
    user_profile_update_schema,
    user_registration_schema,
    verify_email_password_update_schema,
    verify_email_registration_schema,
)
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)
from .utils import send_verification_email

User = get_user_model()


@user_registration_schema
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        send_verification_email(user, purpose="registration")

        return Response(
            {
                "message": (
                    "Registration successful. "
                    "Please check your email to verify your account."
                )
            },
            status=status.HTTP_201_CREATED,
        )


@verify_email_registration_schema
class VerifyEmailRegistrationView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        signer = TimestampSigner()

        try:
            user_id = signer.unsign(
                token, max_age=86400
            )  # Token expires after 24 hours

            # Activate the user
            user = User.objects.get(pk=user_id)
            user.is_active = True  # Activate the user
            user.save()
            return Response(
                {"message": "Email verified successfully"}, status=status.HTTP_200_OK
            )
        except SignatureExpired:
            return Response(
                {"error": "Verification link has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@user_profile_schema
class UserProfileView(generics.RetrieveAPIView):
    """
    This View is for display user profile
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperUser]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user


@logout_schema
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperUser]

    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"error": "Invalid token or token already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@user_delete_schema
class UserDeactivateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]  # Only authenticated users can deactivate their account

    def delete(self, request):
        user = request.user  # Get the currently authenticated user

        # Deactivate the user account
        user.is_active = False
        user.save()

        return Response(
            {"message": "Your account has been deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@user_profile_update_schema
class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperUser]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Separate sensitive and non-sensitive fields
        non_sensitive_fields = ["first_name", "last_name", "mobile_number"]
        sensitive_fields = ["email", "password"]

        # Update non-sensitive fields directly
        self.update_non_sensitive_fields(
            user, serializer.validated_data, non_sensitive_fields
        )

        # Check if both email and password are provided in the request
        email = serializer.validated_data.get(
            "email", user.email
        )  # Default to existing
        password = serializer.validated_data.get("password", None)

        if email == user.email and (
            password is None or check_password(password, user.password)
        ):
            return Response(
                {"message": "Profile updated successfully."},
                status=status.HTTP_200_OK,
            )

        # Check if sensitive fields are being updated
        sensitive_data = {
            field: serializer.validated_data.get(field, getattr(user, field))
            for field in sensitive_fields
            if field in serializer.validated_data
        }

        if sensitive_data:
            self.handle_sensitive_fields(user, sensitive_data)
            message = (
                "Profile updated successfully. "
                "Check your email to verify sensitive changes."
            )
            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_non_sensitive_fields(self, user, validated_data, fields):
        """Update non-sensitive fields directly."""
        for field in fields:
            if field in validated_data:
                setattr(user, field, validated_data[field])
        user.save()

    def handle_sensitive_fields(self, user, sensitive_data):
        """Trigger email verification for sensitive fields."""
        send_verification_email(user, **sensitive_data, purpose="profile_update")


@verify_email_password_update_schema
class VerifyEmailPasswordUpdateView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        signer = TimestampSigner()
        try:
            token_data = force_str(
                urlsafe_base64_decode(signer.unsign(token, max_age=86400))
            )  # Token expires after 24 hours
            # Convert string back to dictionary
            token_data = eval(token_data)
            user_id = token_data["user_id"]
            new_email = token_data.get("email")
            new_password = token_data.get("password")

            user = User.objects.get(pk=user_id)

            # Update email if provided
            if new_email:
                user.email = new_email
                user.username = new_email  # Update username as well

            # Update password if provided
            if new_password:
                user.set_password(new_password)

            user.save()

            return Response(
                {"message": "Email/Password updated successfully"},
                status=status.HTTP_200_OK,
            )
        except SignatureExpired:
            return Response(
                {"error": "Verification link has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@password_reset_schema
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Send password reset email
        send_verification_email(user, purpose="password_reset")

        return Response(
            {"message": "Password reset link has been sent to your email."},
            status=status.HTTP_200_OK,
        )


@password_reset_confirm_schema
class PasswordResetConfirmView(APIView):
    def post(self, request, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["password"]

        signer = TimestampSigner()
        try:
            # Verify the token
            user_id = signer.unsign(
                token, max_age=86400
            )  # Token expires after 24 hours
            user = User.objects.get(pk=user_id)

            # Set the new password
            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        except SignatureExpired:
            return Response(
                {"error": "Password reset link has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {"error": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
