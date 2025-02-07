from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from therapy_connect.profiles.models import PatientProfile, TherapistProfile

from .models import Appointment, Availability, TherapyPanel


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
        print("therapist", therapist)
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
    issue_detail = serializers.SerializerMethodField()

    class Meta:
        model = TherapyPanel
        fields = ["id", "patient", "issue", "issue_detail", "suggested_therapists"]
        extra_kwargs = {"issue": {"write_only": True}}

    def get_suggested_therapists(self, obj):
        """
        Suggest therapists based on the selected issue.
        """
        issue_id = self.initial_data.get("issue")
        if issue_id:
            therapists = TherapistProfile.objects.filter(specialties__id=issue_id)
            return [{"id": t.id, "name": t.user.get_full_name()} for t in therapists]
        return []

    def get_issue_detail(self, obj):
        """Return issue as {id, name} instead of just an ID."""
        return {"id": obj.issue.id, "name": obj.issue.name}

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
    - First update: Patients must select a therapist from the suggested list.
    - Later updates: Patients can only change the status to "paused".
    - Once a therapist is set, it cannot be changed.
    """

    therapist_detail = serializers.SerializerMethodField()

    class Meta:
        model = TherapyPanel
        fields = [
            "status",
            "therapist",
            "therapist_detail",
        ]
        extra_kwargs = {"therapist": {"write_only": True}}

    def get_therapist_detail(self, obj):
        """Return therapist as {id, name} instead of just ID."""
        return {"id": obj.therapist.id, "name": obj.therapist.user.get_full_name()}

    def validate(self, data):
        therapy_panel = self.instance  # Get the existing therapy panel
        request = self.context["request"]
        patient = request.user.patient_profile

        # Ensure only patients can update this panel
        if not hasattr(request.user, "patient_profile"):
            raise serializers.ValidationError(
                {"error": "Only patients can update this panel."}
            )

        # **FIRST UPDATE (Therapist Selection)**
        if therapy_panel.therapist is None:
            if "therapist" not in data:
                raise serializers.ValidationError(
                    {
                        "therapist": "You must select a therapist from the suggested list."
                    }
                )

            # Get suggested therapists (not included in response)
            suggested_therapists = TherapistProfile.objects.filter(
                specialties=therapy_panel.issue
            )

            if data["therapist"] not in suggested_therapists:
                raise serializers.ValidationError(
                    {
                        "therapist": "You can only choose a therapist from the suggested list."
                    }
                )

            # Ensure the selected therapist has availability
            if not data["therapist"].availabilities.exists():
                raise serializers.ValidationError(
                    {"therapist": "The selected therapist has no available time slots."}
                )

            # Ensure the patient does not have an active
            # panel with this therapist for the same issue
            if TherapyPanel.objects.filter(
                patient=patient,
                issue=therapy_panel.issue,
                therapist=data["therapist"],
                status="active",
            ).exists():
                raise serializers.ValidationError(
                    {
                        "therapist": "You already have an active panel with this "
                        "therapist for this issue."
                    }
                )

            return data  # Allow therapist selection

        # **SUBSEQUENT UPDATES (Only Status Allowed)**
        if "therapist" in data:
            raise serializers.ValidationError(
                {"therapist": "You cannot change your therapist after selection."}
            )

        if "status" in data:
            if data["status"] != "paused":
                raise serializers.ValidationError(
                    {"status": "You can only change the status to 'paused'."}
                )

            return data  # Allow status update

        # **Fix: Return error only if neither `therapist` nor `status` is provided**
        raise serializers.ValidationError(
            {
                "error": "Invalid update. You must provide either "
                "`therapist` (if not set) or `status`."
            }
        )


class TherapyPanelTherapistUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Therapists:
    - Can update `status` (to 'paused' or 'completed').
    - If setting status to 'completed', automatically set `last_session_date`.
    - Can update `progress_notes` and `completion_notes`.
    """

    issue = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

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

    def get_issue(self, obj):
        """Return issue as {id, name} instead of just ID."""
        return {"id": obj.issue.id, "name": obj.issue.name}

    def get_patient(self, obj):
        """Return patient as {id, name} instead of just ID."""
        return {"id": obj.patient.id, "name": obj.patient.user.get_full_name()}

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

    issue = serializers.SerializerMethodField()
    therapist = serializers.SerializerMethodField()

    class Meta:
        model = TherapyPanel
        fields = ["id", "issue", "therapist", "status", "assigned_at"]

    def get_issue(self, obj):
        """Return issue as {id, name} instead of just ID."""
        return {"id": obj.issue.id, "name": obj.issue.name}

    def get_therapist(self, obj):
        """Return therapist as {id, name} instead of just ID."""
        if obj.therapist:
            return {"id": obj.therapist.id, "name": obj.therapist.user.get_full_name()}
        return None


class TherapyPanelTherapistRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Therapists:
    - Can see issue, patient info, status, assigned_at, "
    "last_session_date, progress_notes, and completion_notes.
    """

    issue = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

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

    def get_issue(self, obj):
        """Return issue as {id, name} instead of just ID."""
        return {"id": obj.issue.id, "name": obj.issue.name}

    def get_patient(self, obj):
        """Return patient as {id, name} instead of just ID."""
        return {"id": obj.patient.id, "name": obj.patient.user.get_full_name()}


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "panel",
            "scheduled_time",
            "duration",
            "meeting_platform",
            "meeting_link",
            "status",
            "payment_status",
            "created_at",
        ]

    def validate(self, data):
        user = self.context["request"].user
        scheduled_time = data.get("scheduled_time")
        duration = data.get("duration", 60)
        panel = self.instance.panel if self.instance else data.get("panel")

        if not panel or panel.patient.user != user:
            raise serializers.ValidationError("Invalid therapy panel.")

        therapist = panel.therapist
        if not therapist:
            raise serializers.ValidationError("No therapist assigned to this panel.")

        # Ensure the scheduled time is at least 6 hours in the future
        now = timezone.now()
        min_allowed_time = now + timedelta(hours=6)
        if scheduled_time < min_allowed_time:
            raise serializers.ValidationError(
                "Appointments must be scheduled at least 6 hours in advance."
            )

        # Check therapist availability
        availability = Availability.objects.filter(
            therapist=therapist,
            date=scheduled_time.date(),
            start_time__lte=scheduled_time.time(),
            end_time__gte=(scheduled_time + timedelta(minutes=duration)).time(),
        ).exists()

        if not availability:
            raise serializers.ValidationError(
                "Therapist is not available at this time."
            )

        # Check for scheduling conflicts
        overlapping_appointments = Appointment.objects.filter(
            panel__therapist=therapist,
            scheduled_time__lt=scheduled_time + timedelta(minutes=duration),
            scheduled_time__gte=scheduled_time - timedelta(minutes=duration),
            status="scheduled",
        ).exists()

        if overlapping_appointments:
            raise serializers.ValidationError(
                "Therapist already has an appointment at this time."
            )

        return data


# # Ensure payment is completed
# payment = Payment.objects.filter(panel=panel, status="paid").exists()
# if not payment:
#     raise serializers.ValidationError("Payment is required before scheduling an appointment.")
