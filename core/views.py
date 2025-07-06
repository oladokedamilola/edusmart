from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from lecturers.models import PreexistingLecturer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from students.models import PreexistingStudent
from .utils import *
from django.urls import reverse


@staff_member_required
def assign_courses_to_lecturer(request):
    if request.method == 'POST':
        form = AssignCoursesForm(request.POST)
        if form.is_valid():
            lecturer = form.cleaned_data['lecturer']
            courses = form.cleaned_data['courses']

            # ✅ Correctly update the many-to-many relationship
            lecturer.assigned_courses.set(courses)

            # ✅ Notify lecturer
            for course in courses:
                notify(
                    lecturer.user,
                    f"You’ve been assigned to the course {course.code} - {course.title}",
                    url=reverse('course_materials')  # Update this if needed
                )

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

            # ✅ Notify all recipients
            for user in ann.recipients.all():
                notify(
                    user,
                    f"New Admin Announcement: {ann.title}",
                    url=reverse('announcement_detail', args=[ann.id]) 
                )

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

    # ✅ Notify student
    notify(
        grade.enrollment.student.user,
        f"Your grade for {grade.enrollment.course.code} has been approved."
    )

    return redirect('pending-grades')



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





#General views
@login_required
def announcements_view(request):
    user = request.user
    faculty = None
    department = None

    # Get faculty and department using the utility function
    if user.user_type == 'student':
        faculty_name = user.preexistingstudent.faculty
        department_name = user.preexistingstudent.department
        faculty, department = get_faculty_and_department(faculty_name, department_name)
    elif user.user_type == 'lecturer':
        faculty_name = user.preexistinglecturer.faculty
        department_name = user.preexistinglecturer.department
        faculty, department = get_faculty_and_department(faculty_name, department_name)

    # Filter admin announcements based on target and scope
    admin_announcements = AdminAnnouncement.objects.filter(
        Q(target='all') |
        Q(target=user.user_type) |
        Q(target='faculty', faculty=faculty) |
        Q(target='department', department=department) |
        Q(target='custom', recipients=user)
    )

    # Lecturer announcements logic
    if user.user_type == 'student':
        lecturer_announcements = LecturerAnnouncement.objects.filter(course__students=user)
    elif user.user_type == 'lecturer':
        lecturer_announcements = LecturerAnnouncement.objects.filter(posted_by=user)
    else:
        lecturer_announcements = LecturerAnnouncement.objects.none()

    # Combine and sort all announcements
    all_announcements = list(admin_announcements) + list(lecturer_announcements)
    all_announcements.sort(key=lambda x: x.created_at, reverse=True)

    # Add flags to each announcement for template logic
    for ann in all_announcements:
        ann.is_admin = isinstance(ann, AdminAnnouncement)
        ann.is_lecturer = isinstance(ann, LecturerAnnouncement)

    # Pagination
    paginator = Paginator(all_announcements, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/announcements.html', {
        'announcements': page_obj,
        'page_obj': page_obj,
    })




@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()

            # Send notification
            notify(
                message.recipient,
                f"New message from {message.sender.get_full_name()}",
                url=reverse('chat_detail', args=[message.sender.id])
            )

            messages.success(request, "Message sent successfully.")
            return redirect('inbox')
    else:
        form = MessageForm(sender=request.user)
    
    return render(request, 'core/send_message.html', {'form': form})


from django.db.models import Q

@login_required
def inbox(request):
    user = request.user
    messages = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-sent_at')
    
    # Extract unique conversation partners
    conversations = {}
    for msg in messages:
        partner = msg.recipient if msg.sender == user else msg.sender
        if partner.id not in conversations:
            conversations[partner.id] = {
                'user': partner,
                'last_message': msg
            }

    return render(request, 'core/inbox.html', {
        'conversations': conversations.values()
    })


from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from core.models import Notification

@login_required
def notifications_view(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')

    # Optional: mark all as read when visited
    notifications.filter(is_read=False).update(is_read=True)

    # Pagination (10 per page)
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/notifications.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
    })


def forgot_password_view(request):
    form = ForgotPasswordForm()
    show_modal = False

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            form = ForgotPasswordForm()  # Clear form
            show_modal = True

    return render(request, 'registration/forgot_password.html', {
        'form': form,
        'show_modal': show_modal
    })