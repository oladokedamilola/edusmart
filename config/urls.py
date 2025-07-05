from django.contrib import admin
from django.urls import path, include
from .views import *
from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('u/', include('users.urls')),
    path('st/', include('students.urls')),
    path('lr/', include('lecturers.urls')),


    path('announcements/', announcements_view, name='announcements'),
    path('send-message/', send_message, name='send_message'),
    path('inbox/', inbox, name='inbox'),

    # Admin URLs
    path('admin/assign-courses/', assign_courses_to_lecturer, name='assign_courses'),
    path('admin/post-announcement/', post_announcement, name='post_announcement'),
    path('admin/grades/pending/', pending_grades, name='pending-grades'),
    path('admin/grades/approve/<int:grade_id>/', approve_grade, name='approve-grade'),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/timetable/', timetable_manager, name='timetable-manager'),
    path('admin/courses/', course_list, name='course-list'),
    path('admin/student-report/', student_report, name='student-report'),




    path('forbidden/', forbidden_view, name='forbidden'),


]

admin.site.site_header = "University Management System Admin"

from django.conf import settings
from django.conf.urls.static import static

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Serve static files in development 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)                                                  
