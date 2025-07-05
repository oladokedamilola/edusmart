def compute_grade(score):
    score = float(score)
    if score >= 70:
        return 'A', 'Excellent'
    elif score >= 60:
        return 'B', 'Very Good'
    elif score >= 50:
        return 'C', 'Good'
    elif score >= 45:
        return 'D', 'Fair'
    elif score >= 40:
        return 'E', 'Pass'
    else:
        return 'F', 'Fail'


from .models import *
from django.db.models import Q


def check_clash(course, day, time):
    # Get all existing timetable entries for the same day and time
    clashes = Timetable.objects.filter(day=day, time=time)
    for clash in clashes:
        # If the same lecturer or student is involved, consider it a clash
        if clash.course.assigned_lecturers.filter(id__in=course.assigned_lecturers.all()).exists():
            return True
    return False


def get_relevant_announcements(user):
    faculty = None
    department = None

    if user.user_type == 'student':
        faculty = user.preexistingstudent.faculty
        department = user.preexistingstudent.department
    elif user.user_type == 'lecturer':
        faculty = user.preexistinglecturer.faculty
        department = user.preexistinglecturer.department

    return Announcement.objects.filter(
        Q(target='all') |
        Q(target=user.user_type) |
        Q(target='faculty', faculty=faculty) |
        Q(target='department', department=department) |
        Q(target='custom', recipients=user)
    ).order_by('-created_at')[:3]


GRADE_POINTS = {
    'A': 5.0,
    'B': 4.0,
    'C': 3.0,
    'D': 2.0,
    'E': 1.0,
    'F': 0.0
}

def calculate_gpa(grades):
    total_units = 0
    total_points = 0
    for grade_obj in grades:
        try:
            point = GRADE_POINTS[grade_obj.grade]
            unit = grade_obj.enrollment.course.unit
            total_units += unit
            total_points += point * unit
        except KeyError:
            continue
    if total_units == 0:
        return 0.0
    return round(total_points / total_units, 2)