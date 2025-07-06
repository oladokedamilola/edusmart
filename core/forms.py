from django import forms
from core.models import *
from lecturers.models import PreexistingLecturer


class CourseRegistrationForm(forms.Form):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class AssignCoursesForm(forms.Form):
    lecturer = forms.ModelChoiceField(
        queryset=PreexistingLecturer.objects.all(),
        label="Select Lecturer",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        label="Assign Courses",
        widget=forms.CheckboxSelectMultiple()
    )

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = AdminAnnouncement
        fields = ['title', 'content', 'target', 'faculty', 'department', 'recipients']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'target': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.CheckboxSelectMultiple()
        }

class AdminAnnouncementAdminForm(forms.ModelForm):
    class Meta:
        model = AdminAnnouncement
        fields = '__all__'

    class Media:
        js = ('admin/js/announcement_field_logic.js',)
        

class LecturerAnnouncementForm(forms.ModelForm):
    class Meta:
        model = LecturerAnnouncement
        fields = ['title', 'content', 'course']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Only show courses this lecturer is assigned to
        self.fields['course'].queryset = Course.objects.filter(
            assigned_lecturers__user=user
        )

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'content']

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender')
        super().__init__(*args, **kwargs)

        # Student-to-Lecturer restriction
        if sender.user_type == 'student':
            # Find lecturers the student has messages from
            previous_lecturers = CustomUser.objects.filter(
                user_type='lecturer',
                sent_messages__recipient=sender
            ).distinct()
            self.fields['recipient'].queryset = previous_lecturers
        elif sender.user_type == 'lecturer':
            # Lecturer can message any student
            self.fields['recipient'].queryset = CustomUser.objects.filter(user_type='student')

        self.fields['recipient'].widget.attrs.update({'class': 'form-select'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 5})



WEEKDAYS = [
    ('', 'Select day of the week'), 
    ('Monday', 'Monday'), 
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
]

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course', 'day', 'time', 'venue']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter venue'}),
        }

    def __init__(self, *args, **kwargs):
        super(TimetableForm, self).__init__(*args, **kwargs)
        self.fields['day'] = forms.ChoiceField(
            choices=WEEKDAYS,
            widget=forms.Select(attrs={'class': 'form-select'})
        )


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['course', 'title', 'file']

    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer')
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(assigned_lecturers=lecturer)
        self.fields['course'].widget.attrs.update({'class': 'form-select'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})


class AttendanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        enrollments = kwargs.pop('enrollments')
        super().__init__(*args, **kwargs)
        for enrollment in enrollments:
            self.fields[f'student_{enrollment.student.id}'] = forms.ChoiceField(
                choices=[('present', 'Present'), ('absent', 'Absent')],
                label=enrollment.student.matric_number,
                initial='present'
            )


class ForgotPasswordForm(forms.ModelForm):
    class Meta:
        model = PasswordResetRequest
        fields = [
            'matric_number', 'first_name', 'middle_name', 'last_name',
            'faculty', 'department', 'year_of_entry', 'message'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }