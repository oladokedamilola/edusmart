from django import forms
from core.models import *
from lecturers.models import PreexistingLecturer


class CourseRegistrationForm(forms.Form):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class AssignCoursesForm(forms.Form):
    lecturer = forms.ModelChoiceField(queryset=PreexistingLecturer.objects.all(), label="Select Lecturer")
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Assign Courses"
    )

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target', 'faculty', 'department', 'recipients']
        widgets = {
            'recipients': forms.CheckboxSelectMultiple
        }

class CourseAnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['course', 'title', 'content']

    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer')
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(assigned_lecturers=lecturer)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'content']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['recipient'].queryset = CustomUser.objects.exclude(id=sender.id)



class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course', 'day', 'time', 'venue']


# core/forms.py
from .models import CourseMaterial

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['course', 'title', 'file']

    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer')
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(assigned_lecturers=lecturer)


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