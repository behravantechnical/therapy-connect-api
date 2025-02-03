from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

from .serializers import AvailabilitySerializer

create_availability_schema = extend_schema_view(
    post=extend_schema(
        summary="Create an availability slot",
        description=(
            "Allows authenticated therapists to create their availability slots. "
            "Each slot must have a valid date, start time, and end time, and "
            "should not overlap with existing slots. Therapists must be authenticated "
            "using a JWT access token."
        ),
        request=AvailabilitySerializer,
        responses={
            201: AvailabilitySerializer,
            400: "Bad Request - Invalid data or overlapping slots.",
            401: "Unauthorized - Invalid or missing access token.",
        },
        examples=[
            OpenApiExample(
                "Valid Availability Slot",
                value={
                    "date": "2025-02-10",
                    "start_time": "09:00:00",
                    "end_time": "12:00:00",
                },
                description="An example of a valid availability slot creation request.",
            )
        ],
        parameters=[
            OpenApiParameter(
                name="Authorization",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT access token required in the format: Bearer <token>",
            )
        ],
    ),
)


list_availability_schema = extend_schema_view(
    get=extend_schema(
        summary="List available time slots",
        description=(
            "Allows patients to view available time slots. Filters can be applied "
            "to narrow down results based on therapist, day of the week, and time ranges. "
            "Therapists must be authenticated using a JWT access token."
        ),
        parameters=[
            OpenApiParameter(
                name="Authorization",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT access token required in the format: Bearer <token>",
            ),
            OpenApiParameter(
                name="therapist_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter available slots by therapist ID.",
            ),
            OpenApiParameter(
                name="day_of_week",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by day of the week (e.g., Monday, Tuesday).",
            ),
            OpenApiParameter(
                name="start_time_after",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter slots starting after this time (format: HH:MM:SS).",
            ),
            OpenApiParameter(
                name="start_time_before",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter slots starting before this time (format: HH:MM:SS).",
            ),
            OpenApiParameter(
                name="end_time_after",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter slots ending after this time (format: HH:MM:SS).",
            ),
            OpenApiParameter(
                name="end_time_before",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter slots ending before this time (format: HH:MM:SS).",
            ),
        ],
        responses={
            200: AvailabilitySerializer(many=True),
            401: "Unauthorized - Invalid or missing access token.",
        },
        examples=[
            OpenApiExample(
                "Filtered Availability List",
                value=[
                    {
                        "id": 1,
                        "therapist": 5,
                        "date": "2025-02-10",
                        "day_of_week": "Monday",
                        "start_time": "09:00:00",
                        "end_time": "12:00:00",
                    },
                    {
                        "id": 2,
                        "therapist": 5,
                        "date": "2025-02-12",
                        "day_of_week": "Wednesday",
                        "start_time": "14:00:00",
                        "end_time": "17:00:00",
                    },
                ],
                description="Example response showing filtered available slots.",
            )
        ],
    ),
)


update_availability_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve an availability slot",
        description=(
            "Allows a therapist to retrieve details of their availability slot. "
            "Only the therapist who created the slot can access it."
        ),
        parameters=[
            OpenApiParameter(
                name="Authorization",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT access token required in the format: Bearer <token>",
            ),
        ],
        responses={
            200: AvailabilitySerializer,
            401: "Unauthorized - Invalid or missing access token.",
            404: "Not Found - The requested availability slot does "
            "not exist or does not belong to the therapist.",
        },
    ),
    put=extend_schema(
        summary="Update an availability slot",
        description=(
            "Allows a therapist to update their availability slot. "
            "Only the therapist who created the slot can modify it."
        ),
        request=AvailabilitySerializer,
        parameters=[
            OpenApiParameter(
                name="Authorization",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT access token required in the format: Bearer <token>",
            ),
        ],
        responses={
            200: AvailabilitySerializer,
            400: "Bad Request - Invalid data provided.",
            401: "Unauthorized - Invalid or missing access token.",
            404: "Not Found - The requested availability slot "
            "does not exist or does not belong to the therapist.",
        },
        examples=[
            OpenApiExample(
                "Update Availability Slot",
                value={
                    "date": "2025-02-15",
                    "start_time": "10:00:00",
                    "end_time": "13:00:00",
                },
                description="Example request for updating an availability slot.",
            )
        ],
    ),
)


delete_availability_schema = extend_schema_view(
    delete=extend_schema(
        summary="Delete an availability slot",
        description=(
            "Allows a therapist to delete their availability slot. "
            "Only the therapist who created the slot can delete it."
        ),
        parameters=[
            OpenApiParameter(
                name="Authorization",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT access token required in the format: Bearer <token>",
            ),
        ],
        responses={
            204: "No Content - Availability slot successfully deleted.",
            401: "Unauthorized - Invalid or missing access token.",
            404: "Not Found - The requested availability slot "
            "does not exist or does not belong to the therapist.",
        },
    ),
)
