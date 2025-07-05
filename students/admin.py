from django.contrib import admin
from .models import PreexistingStudent

@admin.register(PreexistingStudent)
class PreexistingStudentAdmin(admin.ModelAdmin):
    list_display = ('matric_number', 'first_name', 'last_name', 'department', 'faculty')
    search_fields = ('matric_number', 'first_name', 'last_name')
    list_filter = ('department', 'faculty')
