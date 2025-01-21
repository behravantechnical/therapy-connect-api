from django.contrib.auth import get_user_model
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
