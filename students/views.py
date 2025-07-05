from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.models import CustomUser
from core.models import *
from users.decorators import student_required
from collections import defaultdict
from core.models import Announcement
from django.db.models import Q
from core.utils import *


@login_required
@student_required
def student_dashboard(request):
    student = request.user.preexistingstudent
    recent_announcements = get_relevant_announcements(request.user)
    return render(request, 'students/dashboard.html', {'student': student, 'recent_announcements': recent_announcements})


@login_required
@student_required
def course_registration(request):
    if request.user.user_type != 'student':
        return redirect('login')

    student = request.user.preexistingstudent
    # Filtering logic
    available_courses = Course.objects.filter(
        level=student.year_of_entry
    ).filter(
        models.Q(course_type='C', faculty=student.faculty, department=student.department) |
        models.Q(course_type='R', department=student.department) |
        models.Q(course_type='E')  # Elective is open to all
    )
    registered_courses = Enrollment.objects.filter(student=student).values_list('course__id', flat=True)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id and int(course_id) not in registered_courses:
            course = Course.objects.get(id=course_id)
            Enrollment.objects.create(student=student, course=course)
            return redirect('course_registration')
        
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')

        course = Course.objects.get(id=course_id)

        if action == 'register' and int(course_id) not in registered_courses:
            Enrollment.objects.create(student=student, course=course)
        elif action == 'drop':
            Enrollment.objects.filter(student=student, course=course).delete()


    context = {
        'available_courses': available_courses,
        'registered_courses': registered_courses,
    }
    return render(request, 'students/course_registration.html', context)

@login_required
@student_required
def my_courses(request):
    student = request.user.preexistingstudent
    enrolled_courses = Enrollment.objects.filter(student=student)
    return render(request, 'students/my_courses.html', {'enrolled_courses': enrolled_courses})


@login_required
@student_required
def view_results(request):
    if request.user.user_type != 'student':
        return redirect('login')

    student = request.user.preexistingstudent
    enrollments = Enrollment.objects.filter(student=student)
    results = Grade.objects.filter(enrollment__in=enrollments)

    return render(request, 'students/view_results.html', {'results': results})


@login_required
@student_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'students/inbox.html', {'messages': messages})


@login_required
@student_required
def student_timetable(request):
    student = request.user.preexistingstudent
    enrollments = Enrollment.objects.filter(student=student)
    courses = [e.course for e in enrollments]
    timetable_entries = Timetable.objects.filter(course__in=courses).order_by('day', 'time')

    grouped_timetable = defaultdict(list)
    for entry in timetable_entries:
        grouped_timetable[entry.day].append(entry)

    return render(request, 'students/timetable.html', {'grouped_timetable': dict(grouped_timetable)})


@login_required
@student_required
def student_course_materials(request):
    student = request.user.preexistingstudent
    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course', flat=True)
    materials = CourseMaterial.objects.filter(course__id__in=enrolled_courses).order_by('-uploaded_at')

    return render(request, 'students/course_materials.html', {
        'materials': materials
    })

@login_required
@student_required
def student_attendance_view(request):
    student = request.user.preexistingstudent
    enrollments = Enrollment.objects.filter(student=student).select_related('course')

    attendance_records = Attendance.objects.filter(student=student)
    grouped = defaultdict(list)
    for record in attendance_records:
        grouped[record.course].append(record)

    return render(request, 'students/attendance.html', {
        'enrollments': enrollments,
        'attendance_by_course': dict(grouped)
    })


@login_required
@student_required
def student_gpa_view(request):
    student = request.user.preexistingstudent
    enrollments = Enrollment.objects.filter(student=student)
    grades = Grade.objects.filter(enrollment__in=enrollments, status='approved')

    gpa = calculate_gpa(grades)

    return render(request, 'students/gpa_cgpa.html', {
        'grades': grades,
        'gpa': gpa
    })