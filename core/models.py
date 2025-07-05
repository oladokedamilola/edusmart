from django.db import models
from students.models import PreexistingStudent
from users.models import CustomUser
from lecturers.models import PreexistingLecturer


class Course(models.Model):
    SEMESTER_CHOICES = (
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
    )

    COURSE_TYPE_CHOICES = (
        ('C', 'Compulsory'),
        ('R', 'Required'),
        ('E', 'Elective'),
    )

    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    unit = models.PositiveIntegerField()
    level = models.IntegerField()  # e.g. 100, 200
    assigned_lecturers = models.ManyToManyField(PreexistingLecturer, blank=True)
    description = models.TextField(blank=True, null=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    department = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    course_type = models.CharField(max_length=1, choices=COURSE_TYPE_CHOICES, default='C')
    session = models.CharField(max_length=9, help_text="e.g. 2024/2025")

    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for',
        help_text="Courses that must be completed before taking this course."
)


    def __str__(self):
        return f"{self.code} - {self.title} ({self.get_course_type_display()})"


class Enrollment(models.Model):
    student = models.ForeignKey(PreexistingStudent, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # prevent duplicate enrollment

    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}"

class Grade(models.Model):
    GRADE_STATUS = (
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    )

    status = models.CharField(max_length=10, choices=GRADE_STATUS, default='pending')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.enrollment.student.matric_number} - {self.enrollment.course.code}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.subject}"


class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)  # e.g. Monday
    time = models.TimeField()
    venue = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.course.code} on {self.day}"


class Announcement(models.Model):
    TARGET_CHOICES = (
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('lecturers', 'Lecturers Only'),
        ('faculty', 'Faculty'),
        ('department', 'Department'),
        ('custom', 'Specific Users'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    target = models.CharField(max_length=20, choices=TARGET_CHOICES)
    faculty = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    recipients = models.ManyToManyField(
        CustomUser,
        related_name='received_announcements',  # 👈 unique related_name
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    posted_by = models.ForeignKey(
        CustomUser,
        related_name='posted_announcements',  # 👈 unique related_name
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.ForeignKey(PreexistingLecturer, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    session = models.CharField(max_length=20, blank=True, null=True)  # e.g. 2024/2025

    def __str__(self):
        return f"{self.course.code} - {self.title}"
    

class Attendance(models.Model):
    student = models.ForeignKey(PreexistingStudent, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'course', 'date')