from django.db import models
from users.models import CustomUser

class PreexistingLecturer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    staff_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.staff_id
