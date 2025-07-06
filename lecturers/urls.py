# lecturers/urls.py
from . import views
from django.urls import path

urlpatterns = [
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),

    path('courses/', views.lecturer_courses, name='lecturer_courses'),


    path('courses/students/', views.all_enrolled_students, name='all_enrolled_students'),


    path('courses/<int:course_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('courses/<int:course_id>/results/approved/', views.approved_results, name='approved_results'),
    path('courses-and-materials/', views.course_materials, name='course_materials'),

    path('upload-material/', views.upload_material, name='upload_material'),
    path('my-materials/', views.my_materials, name='my_materials'),
    path('material/<int:pk>/', views.material_detail, name='material_detail'),
    path('material/<int:pk>/update/', views.update_material, name='update_material'),
    path('material/<int:pk>/delete/', views.delete_material, name='delete_material'),



    path('timetable/', views.lecturer_timetable, name='lecturer_timetable'),

    path('announcements/new/', views.post_course_announcement, name='post_course_announcement'),
    path('announcements/', views.my_announcements, name='my_announcements'),
]
