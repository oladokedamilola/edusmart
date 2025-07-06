from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from students.models import PreexistingStudent
from lecturers.models import PreexistingLecturer
from .forms import AccountCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


User = get_user_model()

def verify_id(request):
    if request.method == 'POST':
        form = IDVerificationForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            
            student = PreexistingStudent.objects.filter(matric_number=id_number).first()
            lecturer = PreexistingLecturer.objects.filter(staff_id=id_number).first()

            # Check if ID is already linked to a user
            if student:
                if User.objects.filter(preexistingstudent=student).exists():
                    messages.warning(request, "This student ID is already linked to an account. Please log in.")
                    return redirect('login')

                request.session['user_type'] = 'student'
                request.session['pre_id'] = student.matric_number
                return redirect('create_account')

            elif lecturer:
                if User.objects.filter(preexistinglecturer=lecturer).exists():
                    messages.warning(request, "This lecturer ID is already linked to an account. Please log in.")
                    return redirect('login')

                request.session['user_type'] = 'lecturer'
                request.session['pre_id'] = lecturer.staff_id
                return redirect('create_account')

            else:
                messages.error(request, "ID not found in our records.")
    else:
        form = IDVerificationForm()

    return render(request, 'registration/id_verification.html', {'form': form})




def create_account(request):
    user_type = request.session.get('user_type')
    pre_id = request.session.get('pre_id')

    if not user_type or not pre_id:
        messages.error(request, "Session expired. Please start again.")
        return redirect('verify_id')

    # Get the preexisting record to retrieve the first name
    if user_type == 'student':
        preexisting_user = PreexistingStudent.objects.filter(matric_number=pre_id).first()
    else:
        preexisting_user = PreexistingLecturer.objects.filter(staff_id=pre_id).first()

    if not preexisting_user:
        messages.error(request, "Preexisting record not found.")
        return redirect('verify_id')

    first_name = preexisting_user.first_name  # This is what we want to display

    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = user_type

            # Set username based on preexisting ID
            if user_type == 'student':
                user.username = pre_id
            else:
                user.username = pre_id

            user.save()  # ✅ Save first before linking to related model

            # Now assign to related preexisting model
            if user_type == 'student':
                student = PreexistingStudent.objects.get(matric_number=pre_id)
                student.user = user
                student.save()
            elif user_type == 'lecturer':
                lecturer = PreexistingLecturer.objects.get(staff_id=pre_id)
                lecturer.user = user
                lecturer.save()

            login(request, user)
            messages.success(request, "Account created and you're now logged in.")
            if user_type == 'student':
                return redirect('student_dashboard')
            elif user_type == 'lecturer':
                return redirect('lecturer_dashboard')
            else:
                return redirect('home')  # fallback
    else:
        form = AccountCreationForm()

    return render(request, 'registration/create_account.html', {
        'form': form,
        'first_name': first_name,
        'user_type': user_type
    })




def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # ✅ Check if the user is a superuser (admin)
                if user.is_superuser:
                    messages.success(request, 'Admin login successful. Welcome back!')
                    return redirect('admin-dashboard')

                # ✅ Continue with the regular user_type checks
                if user.user_type == 'student':
                    messages.success(request, 'Login Successful. Welcome back! ')
                    return redirect('student_dashboard')
                elif user.user_type == 'lecturer':
                    messages.success(request, 'Login Successful. Welcome back! ')
                    return redirect('lecturer_dashboard')
                elif user.user_type == 'admin':
                    messages.success(request, 'Login Successful. Welcome back! ')
                    return redirect('admin-dashboard')
                else:
                    messages.error(request, 'User type not recognized.')
                    return redirect('login')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Invalid login details')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})



from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out Successfully. ')
    return redirect('login')

import os

@login_required
def update_profile_image(request):
    user_type = request.session.get('user_type')
    if request.method == 'POST':
        # Trim the uploaded file name if too long
        if 'profile_image' in request.FILES:
            file = request.FILES['profile_image']
            max_length = 10 
            name, ext = os.path.splitext(file.name)
            if len(name) > max_length:
                trimmed_name = name[:max_length]
                file.name = trimmed_name + ext

        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile image updated successfully.')
            if user_type == 'student':
                return redirect('student_dashboard')
            elif user_type == 'lecturer':
                return redirect('lecturer_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Please upload a valid image.')
    else:
        form = ProfileImageForm(instance=request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def view_profile(request):
    user = request.user

    context = {
        'user': user,
        'user_type': user.user_type
    }

    if user.user_type == 'student':
        try:
            student = PreexistingStudent.objects.get(user=user)
            context['profile'] = student
        except PreexistingStudent.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('home') 

    elif user.user_type == 'lecturer':
        try:
            lecturer = PreexistingLecturer.objects.get(user=user)
            context['profile'] = lecturer
        except PreexistingLecturer.DoesNotExist:
            messages.error(request, "Lecturer profile not found.")
            return redirect('home')

    return render(request, 'profile/view_profile.html', context)