from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import lecturer_required
from lecturers.models import PreexistingLecturer
from core.models import *
from django.contrib import messages
from core.models import Announcement
from django.db.models import Q
from django.shortcuts import get_object_or_404
from core.forms import *
from core.utils import compute_grade
from django.forms import modelformset_factory   
from core.utils import *
from django.utils import timezone


@login_required
def lecturer_courses(request):
    try:
        lecturer = request.user.preexistinglecturer
    except PreexistingLecturer.DoesNotExist:
        messages.error(request, "Only lecturers can access this page.")
        return redirect('forbidden')

    courses = Course.objects.filter(assigned_lecturers=lecturer)
    return render(request, 'lecturers/lecturer_courses.html', {'courses': courses})


@login_required
@lecturer_required
def lecturer_dashboard(request):
    lecturer = request.user.preexistinglecturer
    recent_announcements = get_relevant_announcements(request.user)
    return render(request, 'lecturers/dashboard.html', {'lecturer': lecturer, 'recent_announcements': recent_announcements})



@login_required
@lecturer_required
def lecturer_timetable(request):
    lecturer = request.user.preexistinglecturer
    courses = Course.objects.filter(assigned_lecturers=lecturer)
    timetable_entries = Timetable.objects.filter(course__in=courses).order_by('day', 'time')

    from collections import defaultdict
    grouped_timetable = defaultdict(list)
    for entry in timetable_entries:
        grouped_timetable[entry.day].append(entry)

    return render(request, 'lecturers/timetable.html', {'grouped_timetable': dict(grouped_timetable)})


@login_required
def upload_results(request, course_id):
    try:
        lecturer = request.user.preexistinglecturer
    except:
        messages.error(request, "Only lecturers can upload results.")
        return redirect('forbidden')

    course = get_object_or_404(Course, id=course_id, assigned_lecturers=lecturer)
    enrollments = Enrollment.objects.filter(course=course)

    GradeFormSet = modelformset_factory(Grade, fields=('score',), extra=0, can_delete=False)

    # Prepare initial data
    initial_data = []
    for enrollment in enrollments:
        grade_obj, created = Grade.objects.get_or_create(enrollment=enrollment)
        initial_data.append({'score': grade_obj.score if not created else None})

    if request.method == 'POST':
        formset = GradeFormSet(request.POST, queryset=Grade.objects.filter(enrollment__in=enrollments))
        if formset.is_valid():
            for form, enrollment in zip(formset.forms, enrollments):
                score = form.cleaned_data.get('score')
                if score is not None:
                    grade, remarks = compute_grade(score)
                    Grade.objects.update_or_create(
                        enrollment=enrollment,
                        defaults={'score': score, 'grade': grade, 'remarks': remarks}
                    )
            messages.success(request, "Results uploaded successfully.")
            return redirect('lecturer_courses')
    else:
        formset = GradeFormSet(queryset=Grade.objects.filter(enrollment__in=enrollments))

    return render(request, 'core/upload_results.html', {
        'formset': formset,
        'course': course,
        'enrollments': enrollments
    })

@login_required
@lecturer_required
def upload_material(request):
    lecturer = request.user.preexistinglecturer

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES, lecturer=lecturer)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = lecturer
            material.save()
            messages.success(request, "Material uploaded successfully.")
            return redirect('lecturer_courses')
    else:
        form = CourseMaterialForm(lecturer=lecturer)

    return render(request, 'lecturers/upload_material.html', {'form': form})


@login_required
@lecturer_required
def enrolled_students(request, course_id):
    lecturer = request.user.preexistinglecturer
    course = get_object_or_404(Course, id=course_id, assigned_lecturers=lecturer)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    return render(request, 'lecturers/enrolled_students.html', {
        'course': course,
        'enrollments': enrollments
    })

@login_required
@lecturer_required
def mark_attendance(request, course_id):
    lecturer = request.user.preexistinglecturer
    course = get_object_or_404(Course, id=course_id, assigned_lecturers=lecturer)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')

    if request.method == 'POST':
        form = AttendanceForm(request.POST, enrollments=enrollments)
        if form.is_valid():
            date = timezone.now().date()
            for enrollment in enrollments:
                status = form.cleaned_data.get(f'student_{enrollment.student.id}')
                Attendance.objects.update_or_create(
                    student=enrollment.student,
                    course=course,
                    date=date,
                    defaults={'status': status}
                )
            messages.success(request, "Attendance marked successfully.")
            return redirect('lecturer_courses')
    else:
        form = AttendanceForm(enrollments=enrollments)

    return render(request, 'lecturers/mark_attendance.html', {'form': form, 'course': course})


@login_required
@lecturer_required
def approved_results(request, course_id):
    lecturer = request.user.preexistinglecturer
    course = get_object_or_404(Course, id=course_id, assigned_lecturers=lecturer)
    grades = Grade.objects.filter(enrollment__course=course, status='approved').select_related('enrollment__student')
    return render(request, 'lecturers/approved_results.html', {'grades': grades, 'course': course})

@login_required
@lecturer_required
def course_materials(request, course_id):
    lecturer = request.user.preexistinglecturer
    course = get_object_or_404(Course, id=course_id, assigned_lecturers=lecturer)
    
    materials = CourseMaterial.objects.filter(course=course)

    file_type = request.GET.get('type')
    session_filter = request.GET.get('session')

    if file_type:
        materials = materials.filter(file__iendswith=f".{file_type.lower()}")
    if session_filter:
        materials = materials.filter(session=session_filter)

    return render(request, 'lecturers/course_materials.html', {
        'course': course,
        'materials': materials,
        'file_type': file_type,
        'session_filter': session_filter
    })

@login_required
@lecturer_required
def post_course_announcement(request):
    lecturer = request.user.preexistinglecturer

    if request.method == 'POST':
        form = CourseAnnouncementForm(request.POST, lecturer=lecturer)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.target = 'students'
            announcement.save()
            # Optional: auto-assign recipients = all enrolled students for course
            enrollments = Enrollment.objects.filter(course=announcement.course)
            recipients = [e.student.user for e in enrollments]
            announcement.recipients.set(recipients)
            messages.success(request, "Announcement posted successfully.")
            return redirect('lecturer_dashboard')
    else:
        form = CourseAnnouncementForm(lecturer=lecturer)

    return render(request, 'lecturers/post_course_announcement.html', {'form': form})


@login_required
@lecturer_required
def my_announcements(request):
    lecturer = request.user
    announcements = Announcement.objects.filter(posted_by=lecturer).order_by('-created_at')
    return render(request, 'lecturers/my_announcements.html', {'announcements': announcements})