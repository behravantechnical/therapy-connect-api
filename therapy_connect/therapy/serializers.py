from django.shortcuts import get_object_or_404
from rest_framework import serializers

from therapy_connect.profiles.models import TherapistProfile

from .models import Availability

# import datetime


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
