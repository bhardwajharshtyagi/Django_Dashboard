from datetime import date

from django.contrib.auth.models import User

from .email import send_birthday_email
from .models import UserProfile


def check_birthdays():

    today = date.today()

    profiles = UserProfile.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    )

    for profile in profiles:

        user = profile.user

        if user.email:

            send_birthday_email(
                user.email,
                user.username
            )

            print(
                f"Birthday email sent to {user.email}"
            )