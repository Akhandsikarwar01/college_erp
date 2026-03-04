"""
Forms for Faculty app
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import FacultyDepartment, TeacherMaster, TeacherAssignment
from apps.accounts.models import TeacherProfile
from apps.academics.models import Subject, Section


class FacultyDepartmentForm(forms.ModelForm):
    """Form to create/edit faculty department"""
    class Meta:
        model = FacultyDepartment
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department Name'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if FacultyDepartment.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This department already exists.")
        return name


class TeacherMasterForm(forms.ModelForm):
    """Form to create/edit teacher master record"""
    class Meta:
        model = TeacherMaster
        fields = ['teacher_code', 'full_name', 'faculty_department']
        widgets = {
            'teacher_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EMP001'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'faculty_department': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_teacher_code(self):
        code = self.cleaned_data.get('teacher_code')
        if TeacherMaster.objects.filter(teacher_code__iexact=code).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This teacher code already exists.")
        return code.upper()


class TeacherAssignmentForm(forms.ModelForm):
    """Form to assign teacher to subject and section"""
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'subject', 'section']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active teachers
        self.fields['teacher'].queryset = TeacherProfile.objects.filter(
            user__is_active=True
        ).select_related('user')

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        subject = cleaned_data.get('subject')
        section = cleaned_data.get('section')

        if teacher and subject and section:
            existing = TeacherAssignment.objects.filter(
                teacher=teacher,
                subject=subject,
                section=section
            ).exclude(pk=self.instance.pk).exists()
            if existing:
                raise ValidationError("This assignment already exists.")
        
        return cleaned_data


class BulkTeacherAssignmentForm(forms.Form):
    """Form for bulk teacher assignment"""
    teachers = forms.ModelMultipleChoiceField(
        queryset=TeacherProfile.objects.filter(user__is_active=True),
        widget=forms.CheckboxSelectMultiple
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
