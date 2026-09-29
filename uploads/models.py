from django.db import models
from django.contrib.auth.models import User


class UploadedFile(models.Model):

    FILE_TYPES = (
        ("image", "Image"),
        ("pdf", "PDF"),
        ("excel", "Excel"),
        ("csv", "CSV"),
        ("other", "Other"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_files"
    )

    file = models.FileField(
        upload_to="uploads/"
    )

    original_name = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default="other"
    )

    file_size = models.BigIntegerField()

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.original_name} - {self.user.username}"