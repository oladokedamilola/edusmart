from django.contrib import admin
from .models import *

# ---------------------
# Inline Enrollments (optional)
# ---------------------
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0

# ---------------------
# Course Admin
# ---------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'unit', 'semester', 'session', 'level', 'department', 'course_type')
    list_filter = ('semester', 'department', 'level')
    search_fields = ('code', 'title', 'department', 'faculty')
    filter_horizontal = ('assigned_lecturers', 'prerequisites')  # For easier selection in admin

# ---------------------
# Enrollment Admin
# ---------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'registered_at')
    search_fields = ('student__matric_number', 'course__code')
    list_filter = ('course__semester', 'course__department')

# ---------------------
# Grade Admin
# ---------------------
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'score', 'grade', 'status')
    list_filter = ('status',)
    search_fields = ('enrollment__student__matric_number', 'enrollment__course__code')

    actions = ['approve_selected_grades', 'reject_selected_grades']

    def approve_selected_grades(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} grade(s) approved.")

    def reject_selected_grades(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} grade(s) rejected.")

    approve_selected_grades.short_description = "✅ Approve selected grades"
    reject_selected_grades.short_description = "❌ Reject selected grades"

# ---------------------
# Message Admin
# ---------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'subject')

# ---------------------
# Timetable Admin (with clash check placeholder)
# ---------------------
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'day', 'time', 'venue')
    list_filter = ('day', 'course__department')
    search_fields = ('course__code', 'venue')

    # Optional clash detection logic
    def save_model(self, request, obj, form, change):
        clashes = Timetable.objects.filter(day=obj.day, time=obj.time)
        for clash in clashes:
            if clash.course.assigned_lecturers.filter(id__in=obj.course.assigned_lecturers.all()).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError("⚠️ Clash detected with existing timetable.")
        super().save_model(request, obj, form, change)

# ---------------------
# Announcement Admin
# ---------------------
from core.forms import AdminAnnouncementAdminForm
@admin.register(AdminAnnouncement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target', 'faculty', 'department', 'created_at')
    list_filter = ('target', 'faculty', 'department')
    search_fields = ('title', 'content', 'posted_by__username')
    filter_horizontal = ('recipients',)
    form = AdminAnnouncementAdminForm  # 👈 add this line

    class Media:
        js = ('admin/js/announcement_field_logic.js',)

# ---------------------
# Lecturer Announcement Admin
# ---------------------
@admin.register(LecturerAnnouncement)
class LecturerAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'posted_by', 'created_at')
    list_filter = ('course__department', 'course__semester', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username', 'course__code')
    autocomplete_fields = ('course', 'posted_by', 'recipients')
    filter_horizontal = ('recipients',)

# ---------------------
# Course Material Admin
# ---------------------
@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_by', 'uploaded_at', 'session')
    list_filter = ('course__department', 'session')
    search_fields = ('title', 'course__code', 'uploaded_by__user__username')

# ---------------------
# Attendance Admin
# ---------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status')
    list_filter = ('course__department', 'status', 'date')
    search_fields = ('student__matric_number', 'course__code')
    
# ---------------------
# PasswordReset Admin
# ---------------------
@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('matric_number', 'last_name', 'faculty', 'department', 'submitted_at')
    search_fields = ('matric_number', 'first_name', 'last_name', 'faculty', 'department')
    list_filter = ('faculty', 'department', 'year_of_entry')