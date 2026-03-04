"""
Forms for Academics app
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Department, Program, Course, Class, Section, Semester, Subject


class DepartmentForm(forms.ModelForm):
    """Form to create/edit department"""
    class Meta:
        model = Department
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CSE',
                'maxlength': '20'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department Name'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Department.objects.filter(code__iexact=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This department code already exists.")
        return code.upper()


class ProgramForm(forms.ModelForm):
    """Form to create/edit program"""
    class Meta:
        model = Program
        fields = ['department', 'name']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Program Name'
            }),
        }


class CourseForm(forms.ModelForm):
    """Form to create/edit course"""
    class Meta:
        model = Course
        fields = ['program', 'name']
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course Name'
            }),
        }


class ClassForm(forms.ModelForm):
    """Form to create/edit class"""
    class Meta:
        model = Class
        fields = ['course', 'name']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Year 1, Year 2'
            }),
        }


class SectionForm(forms.ModelForm):
    """Form to create/edit section"""
    class Meta:
        model = Section
        fields = ['class_obj', 'name']
        widgets = {
            'class_obj': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A, B, C',
                'maxlength': '10'
            }),
        }


class SemesterForm(forms.ModelForm):
    """Form to create/edit semester"""
    class Meta:
        model = Semester
        fields = ['course', 'number']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '8'
            }),
        }

    def clean_number(self):
        number = self.cleaned_data.get('number')
        if number and (number < 1 or number > 8):
            raise ValidationError("Semester number must be between 1 and 8.")
        return number

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        number = cleaned_data.get('number')

        if course and number:
            existing = Semester.objects.filter(
                course=course,
                number=number
            ).exclude(pk=self.instance.pk).exists()
            if existing:
                raise ValidationError("This semester already exists for this course.")
        
        return cleaned_data


class SubjectForm(forms.ModelForm):
    """Form to create/edit subject"""
    class Meta:
        model = Subject
        fields = ['semester', 'name', 'code']
        widgets = {
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject Name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject Code (optional)',
                'maxlength': '20'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        semester = cleaned_data.get('semester')
        name = cleaned_data.get('name')

        if semester and name:
            existing = Subject.objects.filter(
                semester=semester,
                name__iexact=name
            ).exclude(pk=self.instance.pk).exists()
            if existing:
                raise ValidationError("This subject already exists in this semester.")
        
        return cleaned_data
