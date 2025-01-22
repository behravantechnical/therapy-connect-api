from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(user, email=None, password=None, purpose="registration"):
    """
    Send a verification email to the user.

    Args:
        user: The user object.
        email: New email (for profile updates).
        password: New password (for profile updates).
        purpose: The purpose of the email ("registration", "profile_update", or "password_reset").
    """
    signer = TimestampSigner()

    # Prepare token data based on the purpose
    if purpose == "registration":
        reverse_name = "accounts:user-verify-email"
        subject = "Verify Your Email Address"
        message_action = "verify your email"
        token = signer.sign(user.pk)
    elif purpose == "profile_update":
        token_data = {"user_id": user.pk, "email": email, "password": password}
        reverse_name = "accounts:user-verify-email-password"
        subject = "Verify Your Email/Password Update"
        message_action = "verify your email/password update"
        token = signer.sign(urlsafe_base64_encode(force_bytes(str(token_data))))
    elif purpose == "password_reset":
        reverse_name = "accounts:user-password-reset-confirm"
        subject = "Reset Your Password"
        message_action = "reset your password"
        token = signer.sign(user.pk)
    else:
        raise ValueError(
            "Invalid purpose. Use 'registration', 'profile_update', or 'password_reset'."
        )

    # Create verification link
    if purpose == "password_reset":
        # For password reset, include the token in the URL path
        verification_url = (
            f"{settings.BASE_URL}{reverse(reverse_name, kwargs={'token': token})}"
        )
    else:
        # For other purposes, include the token as a query parameter
        verification_url = f"{settings.BASE_URL}{reverse(reverse_name)}?token={token}"

    # Compose email message
    message = f"Click the link below to {message_action}:\n\n{verification_url}"

    # Send email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
