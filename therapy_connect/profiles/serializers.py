from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PatientProfile, PsychologicalIssue, TherapistProfile

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


class TherapistProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    mobile_number = serializers.CharField(source="user.mobile_number", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    # Allow therapists to update specialties using their IDs
    specialties = serializers.PrimaryKeyRelatedField(
        many=True, queryset=PsychologicalIssue.objects.all(), required=False
    )

    is_verified = serializers.BooleanField(read_only=True)  # Read-only

    class Meta:
        model = TherapistProfile
        fields = [
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "profile_image",
            "qualifications",
            "specialties",
            "time_zone",
            "is_verified",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        """
        Allow therapists to update `profile_image`,
        `qualifications`, `specialties`, and `time_zone`.
        """
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image
        )
        instance.qualifications = validated_data.get(
            "qualifications", instance.qualifications
        )
        instance.time_zone = validated_data.get("time_zone", instance.time_zone)

        if "specialties" in validated_data:
            instance.specialties.set(
                validated_data["specialties"]
            )  # Update ManyToMany field

        instance.save()
        return instance


class AdminPatientProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    mobile_number = serializers.CharField(source="user.mobile_number", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "profile_image",
            "conversation_summary",
            "created_at",
            "updated_at",
        ]


class AdminTherapistProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    mobile_number = serializers.CharField(source="user.mobile_number", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    specialties = serializers.SlugRelatedField(
        many=True, queryset=PsychologicalIssue.objects.all(), slug_field="name"
    )

    class Meta:
        model = TherapistProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "profile_image",
            "qualifications",
            "specialties",
            "time_zone",
            "is_verified",
            "created_at",
            "updated_at",
        ]
