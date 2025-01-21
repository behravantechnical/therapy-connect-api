from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import HomeView, UserRegistrationView, VerifyEmailView

app_name = "accounts"
urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("user/login/", TokenObtainPairView.as_view(), name="auth_login"),
    path("user/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
