from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    HomeView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserDeactivateView,
    UserProfileUpdateView,
    UserProfileView,
    UserRegistrationView,
    VerifyEmailPasswordUpdateView,
    VerifyEmailView,
)

app_name = "accounts"
urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    # User registration and email verification
    path("users/register/", UserRegistrationView.as_view(), name="user-register"),
    path("users/verify-email/", VerifyEmailView.as_view(), name="user-verify-email"),
    # JWT authentication
    path("users/login/", TokenObtainPairView.as_view(), name="user-login"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="user-token-refresh"),
    # User profile
    path("users/profile/", UserProfileView.as_view(), name="user-profile"),
    # User Logout
    path("users/logout/", LogoutView.as_view(), name="logout"),
    # User delete
    path("users/delete/", UserDeactivateView.as_view(), name="user-deactivate"),
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
