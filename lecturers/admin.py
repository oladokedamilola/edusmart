from django.contrib import admin
from .models import PreexistingLecturer

@admin.register(PreexistingLecturer)
class PreexistingLecturerAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'first_name', 'last_name', 'department', 'faculty')
    search_fields = ('staff_id', 'first_name', 'last_name')
    list_filter = ('department', 'faculty')
