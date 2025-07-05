from django.shortcuts import redirect
from functools import wraps

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'student':
            return view_func(request, *args, **kwargs)
        return redirect('forbidden')
    return _wrapped_view

def lecturer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'lecturer':
            return view_func(request, *args, **kwargs)
        return redirect('forbidden')
    return _wrapped_view
