from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"
