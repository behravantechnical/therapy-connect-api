from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from therapy_connect.profiles.models import PatientProfile, TherapistProfile

from .models import Availability, TherapyPanel


class AvailabilitySerializer(serializers.ModelSerializer):
    day_of_week = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ["id", "therapist", "date", "day_of_week", "start_time", "end_time"]
        read_only_fields = ["id", "therapist", "day_of_week"]

    def get_day_of_week(self, obj):
        """Returns the day of the week for the given date (e.g., Monday, Tuesday)."""
        return obj.date.strftime("%A")

    def validate(self, data):
        """
        Custom validation:
        - Required fields must be present.
        - Start time must be before end time.
        - No overlapping slots (excluding the current slot if updating).
        """
        request = self.context.get("request")
        therapist = get_object_or_404(TherapistProfile, user=request.user)

        date = data.get("date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not date or not start_time or not end_time:
            raise serializers.ValidationError(
                "Date, start time, and end time are required."
            )

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        # **Fix: Exclude the current slot when checking for overlaps**
        instance = self.instance  # The availability object being updated (if any)
        overlapping_slots = Availability.objects.filter(
            therapist=therapist,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if instance:
            overlapping_slots = overlapping_slots.exclude(
                id=instance.id
            )  # Exclude current slot

        if overlapping_slots.exists():
            raise serializers.ValidationError(
                "Overlapping availability time slots are not allowed."
            )

        return data


class TherapyPanelCreateSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    suggested_therapists = serializers.SerializerMethodField()

    class Meta:
        model = TherapyPanel
        fields = ["id", "patient", "issue", "suggested_therapists"]

    def get_suggested_therapists(self, obj):
        """
        Suggest therapists based on the selected issue.
        """
        issue_id = self.initial_data.get("issue")
        if issue_id:
            therapists = TherapistProfile.objects.filter(specialties__id=issue_id)
            return [{"id": t.id, "name": t.user.get_full_name()} for t in therapists]
        return []

    def validate(self, data):
        """
        Ensure a patient doesn't already have an active panel for the same issue.
        """
        request = self.context["request"]
        patient = PatientProfile.objects.get(user=request.user)
        if TherapyPanel.objects.filter(
            patient=patient, issue=data["issue"], status="active"
        ).exists():
            raise serializers.ValidationError(
                "You already have an active therapy panel for this issue."
            )

        return data

    def create(self, validated_data):
        """
        Create the therapy panel with the selected therapist.
        """
        request = self.context["request"]
        patient = PatientProfile.objects.get(user=request.user)
        validated_data["patient"] = patient
        return super().create(validated_data)


class TherapyPanelPatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Patients:
    - Can only update the `status` field.
    - Status can only be changed to `paused`.
    """

    class Meta:
        model = TherapyPanel
        fields = ["status", "issue", "therapist"]
        read_only_fields = ["issue", "therapist"]

    def validate(self, data):
        """
        Ensure the patient provides at least one required field.
        """
        if not data:
            raise serializers.ValidationError(
                {"error": "You must provide status field to update."}
            )

        if "status" in data and data["status"] != "paused":
            raise serializers.ValidationError(
                {"status": "Patients can only change the status to 'paused'."}
            )

        return data


class TherapyPanelTherapistUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Therapists:
    - Can update `status` (to 'paused' or 'completed').
    - If setting status to 'completed', automatically set `last_session_date`.
    - Can update `progress_notes` and `completion_notes`.
    """

    class Meta:
        model = TherapyPanel
        fields = [
            "status",
            "progress_notes",
            "completion_notes",
            "assigned_at",
            "last_session_date",
            "issue",
            "patient",
        ]
        read_only_fields = ["assigned_at", "last_session_date", "issue", "patient"]

    def validate(self, data):
        """
        Ensure the therapist provides at least one required field.
        """
        if not data:
            raise serializers.ValidationError(
                {
                    "error": "You must provide at least one field to "
                    "update (e.g., 'status', 'progress_notes', or 'completion_notes')."
                }
            )

        return data

    def validate_status(self, value):
        """Ensure therapists can only change the status to 'paused' or 'completed'."""
        if value not in ["paused", "completed"]:
            raise serializers.ValidationError(
                "Therapists can only set the status to 'paused' or 'completed'."
            )
        return value

    def update(self, instance, validated_data):
        """If therapy is completed, set last_session_date automatically."""
        if validated_data.get("status") == "completed":
            instance.last_session_date = datetime.now(timezone.utc)

        return super().update(instance, validated_data)


class TherapyPanelPatientRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Patients:
    - Can see issue, therapist info, status, and assigned_at.
    """

    class Meta:
        model = TherapyPanel
        fields = ["id", "issue", "therapist", "status", "assigned_at"]


class TherapyPanelTherapistRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Therapists:
    - Can see issue, patient info, status, assigned_at, "
    "last_session_date, progress_notes, and completion_notes.
    """

    class Meta:
        model = TherapyPanel
        fields = [
            "id",
            "issue",
            "patient",
            "status",
            "assigned_at",
            "last_session_date",
            "progress_notes",
            "completion_notes",
        ]
