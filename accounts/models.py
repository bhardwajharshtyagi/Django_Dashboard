from django.db import models
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    otp_created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )

    # Date of Birth
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username








class SupportTicket(models.Model):

    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_tickets"
    )

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.subject} - {self.user.username}"