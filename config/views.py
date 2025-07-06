from django.shortcuts import render
from datetime import datetime
from django.utils.timezone import now
from users.models import *
from core.models import *
from django.contrib.admin.views.decorators import staff_member_required

def home(request):
    return render(request, 'home.html')


def forbidden_view(request):
    return render(request, 'errors/403.html', status=403)


def error_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)

def error_403_view(request, exception):
    return render(request, 'errors/403.html', status=403)

def error_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500_view(request):
    return render(request, 'errors/500.html', status=500)


@staff_member_required
def admin_dashboard(request):
    context = {
        'total_students': PreexistingStudent.objects.count(),
        'total_lecturers': PreexistingLecturer.objects.count(),
        'total_courses': Course.objects.count(),
        'pending_grades': Grade.objects.filter(status='pending').count(),
    }
    return render(request, 'admin/dashboard.html', context)