from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import JsonResponse
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserRegistrationSerializer
from .utils import send_verification_email


class HomeView(View):
    def get(self, request, *args, **kwargs):
        # Create a dictionary to represent the response data
        response_data = {
            "message": "Hello sensor Api!",
            "status": "success",
            "code": 200,
        }

        # Return the dictionary as a JSON response
        return JsonResponse(response_data)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        send_verification_email(user)

        return Response(
            {
                "message": (
                    "Registration successful. "
                    "Please check your email to verify your account."
                )
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
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
