from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.models import CustomUser
from core.models import *
from users.decorators import student_required
from collections import defaultdict
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
    student = request.user.preexistingstudent
    print("🔍 Logged in student:", student)
    print("🔍 Student faculty (raw):", student.faculty)
    print("🔍 Student department (raw):", student.department)
    print("🔍 Student year of entry:", student.year_of_entry)
    print("🔍 Student level:", student.level)

    faculty_obj, department_obj = get_faculty_and_department(student.faculty, student.department)
    print("✅ Matched Faculty object:", faculty_obj)
    print("✅ Matched Department object:", department_obj)

    if not faculty_obj or not department_obj:
        print("❌ Faculty or Department match failed.")
        return render(request, 'students/course_registration.html', {
            'available_courses': [],
            'registered_courses': [],
            'error': 'Faculty or department mapping failed. Please contact admin.'
        })

    available_courses = Course.objects.filter(
        level=student.level
    ).filter(
        models.Q(course_type='C', faculty=faculty_obj, department=department_obj) |
        models.Q(course_type='R', department=department_obj) |
        models.Q(course_type='E')
    )

    print("📚 Available courses count:", available_courses.count())
    for c in available_courses:
        print(f"➡️ {c.code} - {c.title} | Type: {c.course_type} | Dept: {c.department} | Faculty: {c.faculty}")

    registered_courses = Enrollment.objects.filter(student=student).values_list('course__id', flat=True)
    print("✅ Registered course IDs:", list(registered_courses))

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')
        print("📝 POST Action:", action, "Course ID:", course_id)

        try:
            course = Course.objects.get(id=course_id)

            if action == 'register' and int(course_id) not in registered_courses:
                Enrollment.objects.create(student=student, course=course)
                print("✅ Course registered:", course)
            elif action == 'drop':
                Enrollment.objects.filter(student=student, course=course).delete()
                print("❎ Course dropped:", course)

        except Course.DoesNotExist:
            print("❌ Course not found with ID:", course_id)

        return redirect('course_registration')

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