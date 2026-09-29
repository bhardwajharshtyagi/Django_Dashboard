from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    send_mail(
        subject="Email Verification OTP",
        message=f"""
Welcome to Django Dashboard!

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )







def send_birthday_email(email, username):

    subject = f"Happy Birthday {username}! 🎂🎉"

    message = f"""
Happy Birthday, {username}! 🎂🎉

Wishing you a very happy birthday and a wonderful year ahead.

Have an amazing day!

Best Wishes,
Django Dashboard Team
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )