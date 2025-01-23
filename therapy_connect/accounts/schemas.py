from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status

from .serializers import UserProfileSerializer, UserProfileUpdateSerializer

user_registration_schema = extend_schema(
    description="Register a new user. A verification email will be sent "
    "to the provided email address.",
    summary="User Registration",
    responses={
        201: {
            "description": "User registered successfully. A verification "
            "email has been sent.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Registration successful. Please check "
                        "your email to verify your account."
                    }
                }
            },
        }
    },
    examples=[
        OpenApiExample(
            name="Example Request",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "mobile_number": "1234567890",
                "password": "securepassword123",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Example Response",
            value={
                "message": "Registration successful. Please check your "
                "email to verify your account."
            },
            response_only=True,
        ),
    ],
)


verify_email_registration_schema = extend_schema(
    description="Verify a user's email address using the token sent to their email. "
    "This endpoint is used to complete the user registration process.",
    summary="Verify Email Registration",
    parameters=[
        OpenApiParameter(
            name="token",
            description="The verification token sent to the user's email address.",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        status.HTTP_200_OK: {
            "description": "Email verified successfully.",
            "content": {
                "application/json": {
                    "example": {"message": "Email verified successfully"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid or expired token.",
            "content": {
                "application/json": {
                    "examples": {
                        "TokenExpired": {
                            "value": {"error": "Verification link has expired"}
                        },
                        "InvalidToken": {
                            "value": {"error": "Invalid verification link"}
                        },
                        "TokenMissing": {"value": {"error": "Token is required"}},
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Email verified successfully"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Expired Token",
            value={"error": "Verification link has expired"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Token",
            value={"error": "Invalid verification link"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Missing Token",
            value={"error": "Token is required"},
            response_only=True,
        ),
    ],
)


logout_schema = extend_schema(
    description="Log out a user by blacklisting their refresh token. "
    "This endpoint requires a valid access token in the Authorization header "
    "and a refresh token in the request body.",
    summary="User Logout",
    parameters=[
        OpenApiParameter(
            name="Authorization",
            description="Access token for authorization. Format: 'Bearer <access_token>'",
            required=True,
            type=str,
            location=OpenApiParameter.HEADER,
        ),
    ],
    request={
        "application/json": {"example": {"refresh_token": "your_refresh_token_here"}}
    },
    responses={
        status.HTTP_205_RESET_CONTENT: {
            "description": "Successfully logged out.",
            "content": {
                "application/json": {"example": {"message": "Successfully logged out."}}
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid request or token error.",
            "content": {
                "application/json": {
                    "examples": {
                        "MissingToken": {
                            "value": {"error": "Refresh token is required."}
                        },
                        "InvalidToken": {
                            "value": {
                                "error": "Invalid token or token already blacklisted."
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication credentials were not provided or are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Successfully logged out."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Missing Token",
            value={"error": "Refresh token is required."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Token",
            value={"error": "Invalid token or token already blacklisted."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Unauthorized",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
        ),
    ],
)


user_profile_schema = extend_schema(
    description="Retrieve the profile of the currently authenticated user.",
    summary="Get User Profile",
    responses={200: UserProfileSerializer},
    parameters=[
        OpenApiParameter(
            name="Authorization",
            description="Bearer token for authentication.",
            required=True,
            type=str,
            location=OpenApiParameter.HEADER,
            examples=[
                OpenApiExample(
                    name="Bearer Token Example",
                    value="Bearer <access_token>",
                ),
            ],
        ),
    ],
    examples=[
        OpenApiExample(
            name="Example Response",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "mobile_number": "1234567890",
            },
            response_only=True,
        ),
    ],
)


user_delete_schema = extend_schema(
    description="Deactivate the currently authenticated user's account. "
    "This endpoint requires a valid access token in the Authorization header.",
    summary="Deactivate User Account",
    parameters=[
        OpenApiParameter(
            name="Authorization",
            description="Access token for authorization. Format: 'Bearer <access_token>'",
            required=True,
            type=str,
            location=OpenApiParameter.HEADER,
        ),
    ],
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Account deactivated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Your account has been deleted successfully."
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication credentials were not provided or are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Your account has been deleted successfully."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Unauthorized",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
        ),
    ],
)


user_profile_update_schema = extend_schema(
    description="Retrieve or update the profile of the currently authenticated user. "
    "Updating sensitive fields (email, password) requires email verification.",
    summary="Update User Profile",
    responses={
        200: UserProfileUpdateSerializer,
    },
    parameters=[
        OpenApiParameter(
            name="Authorization",
            description="Bearer token for authentication.",
            required=True,
            type=str,
            location=OpenApiParameter.HEADER,
            examples=[
                OpenApiExample(
                    name="Bearer Token Example",
                    value="Bearer <access_token>",
                ),
            ],
        ),
    ],
    examples=[
        OpenApiExample(
            name="Example GET Response",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "mobile_number": "1234567890",
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Example PATCH Request",
            value={
                "first_name": "Jane",
                "email": "new_email@example.com",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Example PATCH Response",
            value={
                "message": (
                    "Profile updated successfully. "
                    "Check your email to verify sensitive changes."
                ),
            },
            response_only=True,
        ),
    ],
)


verify_email_password_update_schema = extend_schema(
    description="Verify and update a user's email and/or password using a "
    "token sent to their email. This endpoint is used to complete "
    "the profile update process when the user modifies their email "
    "or password. The token is sent to the user's email and must "
    "be provided as a query parameter.",
    summary="Verify Email/Password Update",
    parameters=[
        OpenApiParameter(
            name="token",
            description="The verification token sent to the user's email " "address.",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        status.HTTP_200_OK: {
            "description": "Email/Password updated successfully.",
            "content": {
                "application/json": {
                    "example": {"message": "Email/Password updated successfully"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid or expired token.",
            "content": {
                "application/json": {
                    "examples": {
                        "TokenExpired": {
                            "value": {"error": "Verification link has expired"}
                        },
                        "InvalidToken": {
                            "value": {"error": "Invalid verification link"}
                        },
                        "TokenMissing": {"value": {"error": "Token is required"}},
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Email/Password updated successfully"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Expired Token",
            value={"error": "Verification link has expired"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Token",
            value={"error": "Invalid verification link"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Missing Token",
            value={"error": "Token is required"},
            response_only=True,
        ),
    ],
)


password_reset_schema = extend_schema(
    description="Request a password reset link. This endpoint sends a password "
    "reset link to the provided email address if it exists in the "
    "system. No authentication is required.",
    summary="Request Password Reset",
    request={"application/json": {"example": {"email": "user@example.com"}}},
    responses={
        status.HTTP_200_OK: {
            "description": "Password reset link sent successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password reset link has been sent to your email."
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid request or email not found.",
            "content": {
                "application/json": {
                    "example": {"error": "Invalid email address or user not found."}
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Password reset link has been sent to your email."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Email",
            value={"error": "Invalid email address or user not found."},
            response_only=True,
        ),
    ],
)


password_reset_confirm_schema = extend_schema(
    description="Confirm and reset a user's password using a token sent to their email. "
    "This endpoint allows the user to set a new password after verifying "
    "the password reset token. The token is included in the URL, and the "
    "new password is provided in the request body.",
    summary="Confirm Password Reset",
    parameters=[
        OpenApiParameter(
            name="token",
            description="The password reset token sent to the user's email address.",
            required=True,
            type=str,
            location=OpenApiParameter.PATH,
        ),
    ],
    request={"application/json": {"example": {"password": "new_secure_password"}}},
    responses={
        status.HTTP_200_OK: {
            "description": "Password reset successfully.",
            "content": {
                "application/json": {
                    "example": {"message": "Password has been reset successfully."}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid or expired token, or invalid password.",
            "content": {
                "application/json": {
                    "examples": {
                        "TokenExpired": {
                            "value": {"error": "Password reset link has expired."}
                        },
                        "InvalidToken": {
                            "value": {"error": "Invalid password reset link."}
                        },
                        "InvalidPassword": {
                            "value": {
                                "error": "Password must be at least 8 characters long."
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found.",
            "content": {"application/json": {"example": {"error": "User not found."}}},
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"message": "Password has been reset successfully."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Expired Token",
            value={"error": "Password reset link has expired."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Token",
            value={"error": "Invalid password reset link."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Password",
            value={"error": "Password must be at least 8 characters long."},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - User Not Found",
            value={"error": "User not found."},
            response_only=True,
        ),
    ],
)


user_login = extend_schema(
    description="Authenticate a user and obtain JWT access and refresh tokens. "
    "Provide valid username and password to receive the tokens.",
    summary="User Login (Obtain JWT Tokens)",
    request={
        "application/json": {
            "example": {"username": "your_email", "password": "your_password"}
        }
    },
    responses={
        200: {
            "description": "JWT tokens obtained successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "access": "your_access_token",
                        "refresh": "your_refresh_token",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No active account found with the given credentials."
                    }
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"access": "your_access_token", "refresh": "your_refresh_token"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Credentials",
            value={"detail": "No active account found with the given credentials."},
            response_only=True,
        ),
    ],
)


get_refresh_token = extend_schema(
    description="Obtain a new JWT access token by providing a valid refresh token. "
    "This endpoint is used to refresh expired access tokens.",
    summary="Refresh JWT Access Token",
    request={"application/json": {"example": {"refresh": "your_refresh_token"}}},
    responses={
        200: {
            "description": "New access token obtained successfully.",
            "content": {
                "application/json": {"example": {"access": "your_new_access_token"}}
            },
        },
        401: {
            "description": "Invalid or expired refresh token.",
            "content": {
                "application/json": {
                    "example": {"detail": "Token is invalid or expired."}
                }
            },
        },
    },
    examples=[
        OpenApiExample(
            name="Success Example",
            value={"access": "your_new_access_token"},
            response_only=True,
        ),
        OpenApiExample(
            name="Error Example - Invalid Refresh Token",
            value={"detail": "Token is invalid or expired."},
            response_only=True,
        ),
    ],
)
