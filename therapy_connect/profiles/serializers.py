from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PatientProfile

User = get_user_model()


class PatientProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    mobile_number = serializers.CharField(source="user.mobile_number", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    conversation_summary = serializers.CharField(read_only=True)  # Read-only

    class Meta:
        model = PatientProfile
        fields = [
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "profile_image",
            "conversation_summary",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        """
        Allow only `profile_image` to be updated.
        """
        if "profile_image" in validated_data:
            instance.profile_image = validated_data["profile_image"]
            instance.save()
            return instance
        raise serializers.ValidationError(
            {"detail": "Only profile_image can be updated."}
        )
