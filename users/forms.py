from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class IDVerificationForm(forms.Form):
    id_number = forms.CharField(label='Matric No / Staff ID', max_length=50)

class AccountCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']


from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="ID Number", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_image']