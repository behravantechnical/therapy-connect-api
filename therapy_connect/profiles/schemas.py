from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status

patient_profile_schema = extend_schema_view(
    retrieve=extend_schema(
        description="Retrieve a patient's profile, "
        "including basic details and conversation summary.",
        summary="Retrieve Patient Profile",
        responses={
            status.HTTP_200_OK: {
                "description": "Patient profile retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "mobile_number": "+1234567890",
                            "email": "johndoe@example.com",
                            "profile_image": (
                                "https://example.com/media/"
                                "patient_profile_images/image.jpg"
                            ),
                            "conversation_summary": "Summary of the last session...",
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-02T14:30:00Z",
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Profile not found.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "No patient profile found for the logged-in user."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "mobile_number": "+1234567890",
                    "email": "johndoe@example.com",
                    "profile_image": "https://example.com/media/patient_profile_images/image.jpg",
                    "conversation_summary": "Summary of the last session...",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-02T14:30:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Profile Not Found",
                value={"detail": "No patient profile found for the logged-in user."},
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        description="Update the patient's profile image. Only `profile_image` can be updated.",
        summary="Update Patient Profile Image",
        request={
            "multipart/form-data": {
                "example": {"profile_image": "(binary file)"},
            }
        },
        responses={
            status.HTTP_200_OK: {
                "description": "Profile image updated successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "profile_image": (
                                "https://example.com/media/"
                                "patient_profile_images/new_image.jpg"
                            ),
                            "updated_at": "2024-01-02T15:45:00Z",
                        }
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: {
                "description": "Invalid request. Only `profile_image` can be updated.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Only profile_image can be updated."}
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "profile_image": (
                        "https://example.com/media/patient_profile_images/"
                        "new_image.jpg"
                    ),
                    "updated_at": "2024-01-02T15:45:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Invalid Update",
                value={"detail": "Only profile_image can be updated."},
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Soft delete the patient's profile by deactivating their account.",
        summary="Deactivate Patient Profile",
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "Profile deactivated successfully.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Profile deactivated successfully."}
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized action.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={"detail": "Profile deactivated successfully."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
)


therapist_profile_schema = extend_schema_view(
    retrieve=extend_schema(
        description=(
            "Retrieve a therapist's profile, including qualifications, "
            "specialties, and time zone information."
        ),
        summary="Retrieve Therapist Profile",
        responses={
            status.HTTP_200_OK: {
                "description": "Therapist profile retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "mobile_number": "+1234567890",
                            "email": "alice@example.com",
                            "profile_image": (
                                "https://example.com/media/"
                                "therapist_profile_images/image.jpg"
                            ),
                            "qualifications": "PhD in Clinical Psychology",
                            "specialties": [1, 2],  # IDs of related issues
                            "time_zone": "America/New_York",
                            "is_verified": True,
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-02T14:30:00Z",
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": (
                                "You do not have permission to perform " "this action."
                            )
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Profile not found.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": (
                                "No therapist profile found for the " "logged-in user."
                            )
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "mobile_number": "+1234567890",
                    "email": "alice@example.com",
                    "profile_image": (
                        "https://example.com/media/"
                        "therapist_profile_images/image.jpg"
                    ),
                    "qualifications": "PhD in Clinical Psychology",
                    "specialties": [1, 2],  # IDs of related issues
                    "time_zone": "America/New_York",
                    "is_verified": True,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-02T14:30:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Profile Not Found",
                value={"detail": "No therapist profile found for the logged-in user."},
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        description=(
            "Update the therapist's profile. Allowed fields: `profile_image`, "
            "`qualifications`, `specialties`, and `time_zone`."
        ),
        summary="Update Therapist Profile",
        request={
            "multipart/form-data": {
                "example": {
                    "profile_image": "(binary file)",
                    "qualifications": "PhD in Clinical Psychology",
                    "specialties": [1, 3],  # IDs of new specialties
                    "time_zone": "Europe/London",
                }
            }
        },
        responses={
            status.HTTP_200_OK: {
                "description": "Profile updated successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "profile_image": (
                                "https://example.com/media/"
                                "therapist_profile_images/new_image.jpg"
                            ),
                            "qualifications": "PhD in Clinical Psychology",
                            "specialties": [1, 3],  # Updated specialties
                            "time_zone": "Europe/London",
                            "updated_at": "2024-01-02T15:45:00Z",
                        }
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: {
                "description": "Invalid request.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Only profile_image, qualifications, "
                            "specialties, and time_zone can be updated."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "profile_image": (
                        "https://example.com/media/"
                        "therapist_profile_images/new_image.jpg"
                    ),
                    "qualifications": "PhD in Clinical Psychology",
                    "specialties": [1, 3],  # Updated specialties
                    "time_zone": "Europe/London",
                    "updated_at": "2024-01-02T15:45:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Invalid Update",
                value={
                    "detail": (
                        "Only profile_image, qualifications, specialties, "
                        "and time_zone can be updated."
                    )
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Soft delete the therapist's profile by deactivating their account.",
        summary="Deactivate Therapist Profile",
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "Profile deactivated successfully.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Profile deactivated successfully."}
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized action.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={"detail": "Profile deactivated successfully."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
)


admin_can_list_patient_profile_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of all patients. Admin-only access.",
        summary="List All Patients",
        responses={
            status.HTTP_200_OK: {
                "description": "List of patient profiles retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": 1,
                                "first_name": "John",
                                "last_name": "Doe",
                                "mobile_number": "+1234567890",
                                "email": "johndoe@example.com",
                                "profile_image": (
                                    "https://example.com/media/"
                                    "patient_profile_images/image.jpg"
                                ),
                                "conversation_summary": (
                                    "Patient has shown signs of anxiety. "
                                    "Recommended therapy sessions."
                                ),
                                "created_at": "2024-01-01T12:00:00Z",
                                "updated_at": "2024-01-02T14:30:00Z",
                            },
                            {
                                "id": 2,
                                "first_name": "Jane",
                                "last_name": "Smith",
                                "mobile_number": "+1987654321",
                                "email": "janesmith@example.com",
                                "profile_image": (
                                    "https://example.com/media/"
                                    "patient_profile_images/image2.jpg"
                                ),
                                "conversation_summary": (
                                    "Depression symptoms detected. Suggested "
                                    "cognitive behavioral therapy."
                                ),
                                "created_at": "2024-02-05T09:15:00Z",
                                "updated_at": "2024-02-06T10:20:00Z",
                            },
                        ]
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access. Admins only.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value=[
                    {
                        "id": 1,
                        "first_name": "John",
                        "last_name": "Doe",
                        "mobile_number": "+1234567890",
                        "email": "johndoe@example.com",
                        "profile_image": (
                            "https://example.com/media/"
                            "patient_profile_images/image.jpg"
                        ),
                        "conversation_summary": (
                            "Patient has shown signs of anxiety. "
                            "Recommended therapy sessions."
                        ),
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-02T14:30:00Z",
                    }
                ],
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Retrieve a specific patient's profile by ID. Admin-only access.",
        summary="Retrieve Patient Profile",
        responses={
            status.HTTP_200_OK: {
                "description": "Patient profile retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "first_name": "John",
                            "last_name": "Doe",
                            "mobile_number": "+1234567890",
                            "email": "johndoe@example.com",
                            "profile_image": (
                                "https://example.com/media/"
                                "patient_profile_images/image.jpg"
                            ),
                            "conversation_summary": (
                                "Patient has shown signs of anxiety. "
                                "Recommended therapy sessions."
                            ),
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-02T14:30:00Z",
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Patient profile not found.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "No patient profile found with the given ID."
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access. Admins only.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "mobile_number": "+1234567890",
                    "email": "johndoe@example.com",
                    "profile_image": (
                        "https://example.com/media/" "patient_profile_images/image.jpg"
                    ),
                    "conversation_summary": (
                        "Patient has shown signs of anxiety. "
                        "Recommended therapy sessions."
                    ),
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-02T14:30:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Profile Not Found",
                value={"detail": "No patient profile found with the given ID."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
)


admin_can_list_therapist_profile_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of all therapists. Admin-only access.",
        summary="List All Therapists",
        responses={
            status.HTTP_200_OK: {
                "description": "List of therapist profiles retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": 1,
                                "first_name": "Alice",
                                "last_name": "Johnson",
                                "mobile_number": "+1234567890",
                                "email": "alice@example.com",
                                "profile_image": (
                                    "https://example.com/media/"
                                    "therapist_profile_images/image.jpg"
                                ),
                                "qualifications": (
                                    "Licensed Clinical Psychologist with "
                                    "10 years of experience."
                                ),
                                "specialties": ["Anxiety", "Depression"],
                                "time_zone": "America/New_York",
                                "is_verified": True,
                                "created_at": "2024-01-01T12:00:00Z",
                                "updated_at": "2024-01-02T14:30:00Z",
                            },
                            {
                                "id": 2,
                                "first_name": "Bob",
                                "last_name": "Smith",
                                "mobile_number": "+1987654321",
                                "email": "bob@example.com",
                                "profile_image": (
                                    "https://example.com/media/"
                                    "therapist_profile_images/image2.jpg"
                                ),
                                "qualifications": (
                                    "Cognitive Behavioral Therapist with "
                                    "8 years of experience."
                                ),
                                "specialties": ["PTSD", "Stress Management"],
                                "time_zone": "Europe/London",
                                "is_verified": False,
                                "created_at": "2024-02-05T09:15:00Z",
                                "updated_at": "2024-02-06T10:20:00Z",
                            },
                        ]
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access. Admins only.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value=[
                    {
                        "id": 1,
                        "first_name": "Alice",
                        "last_name": "Johnson",
                        "mobile_number": "+1234567890",
                        "email": "alice@example.com",
                        "profile_image": (
                            "https://example.com/media/"
                            "therapist_profile_images/image.jpg"
                        ),
                        "qualifications": (
                            "Licensed Clinical Psychologist with "
                            "10 years of experience."
                        ),
                        "specialties": ["Anxiety", "Depression"],
                        "time_zone": "America/New_York",
                        "is_verified": True,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-02T14:30:00Z",
                    }
                ],
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Retrieve a specific therapist's profile by ID. Admin-only access.",
        summary="Retrieve Therapist Profile",
        responses={
            status.HTTP_200_OK: {
                "description": "Therapist profile retrieved successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "first_name": "Alice",
                            "last_name": "Johnson",
                            "mobile_number": "+1234567890",
                            "email": "alice@example.com",
                            "profile_image": (
                                "https://example.com/media/"
                                "therapist_profile_images/image.jpg"
                            ),
                            "qualifications": (
                                "Licensed Clinical Psychologist with "
                                "10 years of experience."
                            ),
                            "specialties": ["Anxiety", "Depression"],
                            "time_zone": "America/New_York",
                            "is_verified": True,
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-02T14:30:00Z",
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Therapist profile not found.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "No therapist profile found with the given ID."
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Unauthorized access. Admins only.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Success Example",
                value={
                    "id": 1,
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "mobile_number": "+1234567890",
                    "email": "alice@example.com",
                    "profile_image": (
                        "https://example.com/media/"
                        "therapist_profile_images/image.jpg"
                    ),
                    "qualifications": (
                        "Licensed Clinical Psychologist with " "10 years of experience."
                    ),
                    "specialties": ["Anxiety", "Depression"],
                    "time_zone": "America/New_York",
                    "is_verified": True,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-02T14:30:00Z",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Profile Not Found",
                value={"detail": "No therapist profile found with the given ID."},
                response_only=True,
            ),
            OpenApiExample(
                name="Error Example - Unauthorized",
                value={"detail": "You do not have permission to perform this action."},
                response_only=True,
            ),
        ],
    ),
)
