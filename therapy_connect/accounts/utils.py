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
        purpose: The purpose of the email ("registration" or "profile_update").
    """
    signer = TimestampSigner()

    # Prepare token data based on the purpose
    if purpose == "registration":
        # token_data = {"user_id": user.pk}
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
    else:
        raise ValueError("Invalid purpose. Use 'registration' or 'profile_update'.")

    # Create verification link
    verification_url = f"{settings.BASE_URL}{reverse(reverse_name)}?token={token}"

    # Compose email message
    message = f"Click the link below to {message_action}:\n\n{verification_url}"

    # Send email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
