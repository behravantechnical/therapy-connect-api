from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.urls import reverse


def send_verification_email(user):
    # Generate a secure token
    signer = TimestampSigner()
    token = signer.sign(user.pk)  # Sign the user's primary key

    # Create verification link
    verification_url = (
        f"{settings.BASE_URL}{reverse('accounts:verify-email')}?token={token}"
    )

    # Send email
    subject = "Verify Your Email Address"
    message = f"Click the link below to verify your email:\n\n{verification_url}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
