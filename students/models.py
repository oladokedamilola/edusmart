from django.db import models
from users.models import CustomUser

class PreexistingStudent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    matric_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    dob = models.DateField()
    year_of_entry = models.IntegerField()
    level = models.IntegerField()


    def __str__(self):
        return self.matric_number
