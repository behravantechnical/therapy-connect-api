from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "mobile_number", "password"]

    def create(self, validated_data):
        # Create the user using the UserManager
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile_number", "email"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile_number", "email", "password"]

    def validate(self, data):
        # Ensure at least one field is provided
        if not any(
            field in data
            for field in [
                "first_name",
                "last_name",
                "mobile_number",
                "email",
                "password",
            ]
        ):
            raise ValidationError("At least one field must be provided.")
        return data

    def validate_email(self, value):
        """
        Validate that the email is unique and not already in use by another user.
        """
        user = self.context["request"].user  # Get the current user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise ValidationError("This email is already in use.")
        return value

    def validate_mobile_number(self, value):
        """
        Validate that the mobile number is unique and not already in use by another user.
        """
        user = self.context["request"].user  # Get the current user
        if User.objects.filter(mobile_number=value).exclude(pk=user.pk).exists():
            raise ValidationError("This mobile number is already in use.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if the email exists in the database
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        # Add password complexity validation if needed
        if len(value) < 3:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value
