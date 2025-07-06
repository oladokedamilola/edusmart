from django.db.models import Q
from core.models import *

def get_faculty_and_department(faculty_name: str, department_name: str):
    """
    Given faculty and department names (as strings), this returns:
    - faculty instance
    - department instance (within that faculty)
    Returns (None, None) if not found.
    """
    try:
        faculty = Faculty.objects.get(name__iexact=faculty_name.strip())
        department = Department.objects.get(name__iexact=department_name.strip(), faculty=faculty)
        return faculty, department
    except (Faculty.DoesNotExist, Department.DoesNotExist):
        return None, None
    

def get_relevant_announcements(user):
    faculty = None
    department = None

    if user.user_type == 'student':
        # Retrieve clean faculty/department names (strings) from the student record
        faculty_name = user.preexistingstudent.faculty
        department_name = user.preexistingstudent.department

        # Use utility function to get the actual model instances
        faculty, department = get_faculty_and_department(faculty_name, department_name)

        admin_announcements = AdminAnnouncement.objects.filter(
            Q(target='all') |
            Q(target='students') |
            Q(target='faculty', faculty=faculty) |
            Q(target='department', department=department) |
            Q(target='custom', recipients=user)
        )

        lecturer_announcements = LecturerAnnouncement.objects.filter(
            course__students=user
        )

        combined = list(admin_announcements) + list(lecturer_announcements)
        combined.sort(key=lambda x: x.created_at, reverse=True)
        return combined[:3]

    elif user.user_type == 'lecturer':
        faculty_name = user.preexistinglecturer.faculty
        department_name = user.preexistinglecturer.department

        faculty, department = get_faculty_and_department(faculty_name, department_name)

        return AdminAnnouncement.objects.filter(
            Q(target='all') |
            Q(target='lecturers') |
            Q(target='faculty', faculty=faculty) |
            Q(target='department', department=department) |
            Q(target='custom', recipients=user)
        ).order_by('-created_at')[:3]

    return []




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


from .models import Notification

def notify(user, message, url=None):
    Notification.objects.create(user=user, message=message, url=url)



