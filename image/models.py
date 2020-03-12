from django.db import models
from django.urls import reverse
from django.utils import timezone


class ContentImage(models.Model):
    image = models.ImageField(upload_to='article/content/%Y%m%d', blank=True)
    uploaded = models.DateTimeField(default=timezone.now)
