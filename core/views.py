from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from lecturers.models import PreexistingLecturer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from students.models import PreexistingStudent

@staff_member_required
def assign_courses_to_lecturer(request):
    if request.method == 'POST':
        form = AssignCoursesForm(request.POST)
        if form.is_valid():
            lecturer = form.cleaned_data['lecturer']
            courses = form.cleaned_data['courses']
            lecturer.course_set.set(courses)  # replaces existing
            messages.success(request, f"Courses successfully assigned to {lecturer.staff_id}")
            return redirect('assign_courses')
    else:
        form = AssignCoursesForm()
    return render(request, 'admin/assign_courses.html', {'form': form})


@staff_member_required
def post_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.posted_by = request.user
            ann.save()
            form.save_m2m()
            messages.success(request, "Announcement posted successfully.")
            return redirect('post_announcement')
    else:
        form = AnnouncementForm()

    return render(request, 'admin/post_announcement.html', {'form': form})


@staff_member_required
def pending_grades(request):
    grades = Grade.objects.filter(status='pending')
    return render(request, 'admin/pending_grades.html', {'grades': grades})

@staff_member_required
def approve_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    grade.status = 'approved'
    grade.save()
    return redirect('pending-grades')

@staff_member_required
def admin_dashboard(request):
    context = {
        'total_students': PreexistingStudent.objects.count(),
        'total_lecturers': PreexistingLecturer.objects.count(),
        'total_courses': Course.objects.count(),
        'pending_grades': Grade.objects.filter(status='pending').count(),
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def timetable_manager(request):
    timetable = Timetable.objects.select_related('course').all()
    form = TimetableForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_slot = form.save(commit=False)

        # Basic clash prevention (optional)
        clash = Timetable.objects.filter(
            day=new_slot.day,
            time=new_slot.time,
            venue=new_slot.venue
        ).exists()

        if clash:
            messages.error(request, "A course is already scheduled at this time and venue.")
        else:
            new_slot.save()
            messages.success(request, "Timetable slot added successfully.")
            return redirect('timetable-manager')

    return render(request, 'admin/timetable_manager.html', {'form': form, 'timetable': timetable})


@staff_member_required
def course_list(request):
    courses = Course.objects.all().select_related()
    return render(request, 'admin/course_list.html', {'courses': courses})

@staff_member_required
def student_report(request):
    matric = request.GET.get('matric')
    student = None
    grades = []

    if matric:
        try:
            student = PreexistingStudent.objects.get(matric_number__iexact=matric)
            grades = Grade.objects.filter(enrollment__student=student).select_related('enrollment__course')
        except PreexistingStudent.DoesNotExist:
            student = None
            grades = []

    return render(request, 'admin/student_report.html', {
        'student': student,
        'grades': grades,
    })




@login_required
def announcements_view(request):
    user = request.user
    faculty = None
    department = None

    # Try to get user details for filtering
    if user.user_type == 'student':
        faculty = user.preexistingstudent.faculty
        department = user.preexistingstudent.department
    elif user.user_type == 'lecturer':
        faculty = user.preexistinglecturer.faculty
        department = user.preexistinglecturer.department

    announcements = Announcement.objects.filter(
        models.Q(target='all') |
        models.Q(target=user.user_type) |
        models.Q(target='faculty', faculty=faculty) |
        models.Q(target='department', department=department) |
        models.Q(target='custom', recipients=user)
    ).order_by('-created_at')

    return render(request, 'core/announcements.html', {'announcements': announcements})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully.")
            return redirect('send_message')
    else:
        form = MessageForm(sender=request.user)
    
    return render(request, 'core/send_message.html', {'form': form})


@login_required
def inbox(request):
    received = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'core/inbox.html', {'messages': received})

