from django.contrib.auth.models import User
from django.db import models

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = ProcessedImageField(
        upload_to='userprofile/avatar/%Y%m%d',
        processors=[ResizeToFill(width=60, height=60)],
        format='JPEG',
        options={'quality': 80},
        blank=True
    )
