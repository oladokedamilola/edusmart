from django.shortcuts import render
from datetime import datetime
from django.utils.timezone import now


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