from django.urls import path
from drf_spectacular.utils import extend_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .schemas import get_refresh_token, user_login
from .views import (
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserDeactivateView,
    UserProfileUpdateView,
    UserProfileView,
    UserRegistrationView,
    VerifyEmailPasswordUpdateView,
    VerifyEmailRegistrationView,
)

# Apply the schemas to the JWT views
token_obtain_pair_view = extend_schema_view(post=user_login)(
    TokenObtainPairView.as_view()
)
token_refresh_view = extend_schema_view(post=get_refresh_token)(
    TokenRefreshView.as_view()
)


app_name = "accounts"
urlpatterns = [
    # User registration and email verification
    path("users/register/", UserRegistrationView.as_view(), name="user-register"),
    path(
        "users/verify-email/",
        VerifyEmailRegistrationView.as_view(),
        name="user-verify-email",
    ),
    # JWT authentication
    path("users/login/", token_obtain_pair_view, name="user-login"),
    path("users/token/refresh/", token_refresh_view, name="user-token-refresh"),
    # User update and Email/password update verification
    path(
        "users/profile/update/",
        UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
    path(
        "users/verify-email-password/",
        VerifyEmailPasswordUpdateView.as_view(),
        name="user-verify-email-password",
    ),
    # User profile
    path("users/profile/", UserProfileView.as_view(), name="user-profile"),
    # User Logout
    path("users/logout/", LogoutView.as_view(), name="logout"),
    # User delete
    path("users/delete/", UserDeactivateView.as_view(), name="user-deactivate"),
    # User reset password and Email verification
    path(
        "users/password/reset/",
        PasswordResetRequestView.as_view(),
        name="user-password-reset",
    ),
    path(
        "users/password/reset/confirm/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="user-password-reset-confirm",
    ),
]
