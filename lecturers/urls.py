# lecturers/urls.py
from . import views
from django.urls import path

urlpatterns = [
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('courses/', views.lecturer_courses, name='lecturer_courses'),
    path('courses/<int:course_id>/students/', views.enrolled_students, name='enrolled_students'),
    path('courses/<int:course_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('courses/<int:course_id>/results/approved/', views.approved_results, name='approved_results'),
    path('upload-material/', views.upload_material, name='upload_material'),
    path('timetable/', views.lecturer_timetable, name='lecturer_timetable'),
    path('course/<int:course_id>/materials/', views.course_materials, name='course_materials'),
    path('announcements/new/', views.post_course_announcement, name='post_course_announcement'),
     path('announcements/', views.my_announcements, name='my_announcements'),
]
