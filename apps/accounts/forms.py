"""
Forms for Accounts app - User registration, login, imports
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from .models import CustomUser, Role, StudentProfile, TeacherProfile


class CustomUserCreationForm(UserCreationForm):
    """Form for user registration with role selection"""
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(
        max_length=10, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number (10 digits)'})
    )
    role = forms.ChoiceField(
        choices=[(Role.STUDENT, 'Student'), (Role.TEACHER, 'Teacher')],
        widget=forms.RadioSelect
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile_number', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile and not re.match(r'^\d{10}$', mobile):
            raise ValidationError("Mobile number must be 10 digits.")
        if mobile and CustomUser.objects.filter(mobile_number=mobile).exists():
            raise ValidationError("This mobile number is already registered.")
        return mobile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username


class OTPVerificationForm(forms.Form):
    """Form to verify OTP during registration"""
    otp = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6',
            'inputmode': 'numeric'
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise ValidationError("OTP must contain only digits.")
        return otp


class CustomAuthenticationForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class StudentImportForm(forms.Form):
    """Form for bulk import of students via CSV"""
    csv_file = forms.FileField(
        help_text='CSV format: section_id, first_name, last_name, email, admission_number, enrollment_number, roll_number'
    )

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file and not file.name.endswith('.csv'):
            raise ValidationError("Only CSV files are allowed.")
        return file


class StudentProfileUpdateForm(forms.ModelForm):
    """Form to update student profile"""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StudentProfile
        fields = [
            'admission_number', 'application_number', 'enrollment_number', 'roll_number',
            'father_name', 'mother_name', 'date_of_birth', 'gender', 'blood_group',
            'address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'guardian_phone'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'application_number': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TeacherProfileUpdateForm(forms.ModelForm):
    """Form to update teacher profile"""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TeacherProfile
        fields = ['employee_id']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
