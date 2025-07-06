from django.db import models
from students.models import PreexistingStudent
from users.models import CustomUser
from lecturers.models import PreexistingLecturer


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('faculty', 'name')

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"

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
    assigned_lecturers = models.ManyToManyField(PreexistingLecturer, related_name='assigned_courses', blank=True)
    description = models.TextField(blank=True, null=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    course_type = models.CharField(max_length=1, choices=COURSE_TYPE_CHOICES, default='C')
    session = models.CharField(max_length=9, help_text="e.g. 2024/2025")
    students = models.ManyToManyField(CustomUser, limit_choices_to={'user_type': 'student'}, related_name='enrolled_courses', blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for', help_text="Courses that must be completed before taking this course.")

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


class AdminAnnouncement(models.Model):
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
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)

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
    
class LecturerAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lecturer_announcements',
        help_text="Only courses assigned to the lecturer"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    posted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'lecturer'},
        related_name='announcements_posted'
    )

    recipients = models.ManyToManyField(
        CustomUser,
        related_name='lecturer_announcements_received',
        blank=True,
        limit_choices_to={'user_type': 'student'}
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Automatically set recipients if not already set
        if not self.recipients.exists():
            self.recipients.set(self.get_course_students())

    def get_course_students(self):
        # You need to implement a model or logic to track course enrollment
        return CustomUser.objects.filter(
            user_type='student',
            enrolled_courses__id=self.course.id
        ).distinct()

    def __str__(self):
        return f"{self.title} - {self.course.code}"


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


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)  # Optional: for redirection
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.username}: {self.message[:30]}"
    

class PasswordResetRequest(models.Model):
    matric_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_of_entry = models.PositiveIntegerField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.matric_number} - {self.last_name}"