from django.urls import path
from .views import *  

urlpatterns = [
    path('student/dashboard/', student_dashboard, name='student_dashboard'),

    path('register-courses/', course_registration, name='course_registration'),

    path('my-courses/', my_courses, name='my_courses'),


    path('results/', view_results, name='view_results'),

    path('inbox/', inbox, name='inbox'),

    path('timetable/', student_timetable, name='student_timetable'),

    path('materials/', student_course_materials, name='student_course_materials'),
    path('attendance/', student_attendance_view, name='student_attendance'),
    path('gpa/', student_gpa_view, name='student_gpa'),

]
