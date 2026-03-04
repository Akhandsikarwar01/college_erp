"""
Forms for Examinations app
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import ExamType, Exam, ExamSchedule, StudentResult, GradeScale
from apps.academics.models import Course, Semester, Subject, Section
from apps.accounts.models import StudentProfile


class ExamForm(forms.ModelForm):
    """Form to create/edit exam"""
    class Meta:
        model = Exam
        fields = ['exam_type', 'course', 'semester', 'name', 'start_date', 'end_date', 'is_published']
        widgets = {
            'exam_type': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exam Name'}),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class ExamScheduleForm(forms.ModelForm):
    """Form to create exam schedule"""
    class Meta:
        model = ExamSchedule
        fields = ['subject', 'date', 'start_time', 'end_time', 'room', 'max_marks', 'passing_marks']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room/Hall'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        max_marks = cleaned_data.get('max_marks')
        passing_marks = cleaned_data.get('passing_marks')

        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time.")
        
        if max_marks and passing_marks and passing_marks > max_marks:
            raise ValidationError("Passing marks cannot be greater than maximum marks.")
        
        return cleaned_data


class StudentResultForm(forms.ModelForm):
    """Form to enter student results"""
    class Meta:
        model = StudentResult
        fields = ['marks_obtained', 'is_absent', 'remarks']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_absent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional remarks (optional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        marks = cleaned_data.get('marks_obtained')
        is_absent = cleaned_data.get('is_absent')

        if not is_absent and marks is None:
            raise ValidationError("Marks must be provided if student is not marked absent.")
        
        if is_absent and marks:
            cleaned_data['marks_obtained'] = 0
        
        return cleaned_data


class BulkResultEntryForm(forms.Form):
    """Form for bulk result entry"""
    exam_schedule = forms.ModelChoiceField(
        queryset=ExamSchedule.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['exam_schedule'].queryset = ExamSchedule.objects.filter(
            exam__is_published=False
        ).select_related('exam', 'subject')


class GradeScaleForm(forms.ModelForm):
    """Form to configure grade scale"""
    class Meta:
        model = GradeScale
        fields = ['grade', 'min_marks', 'max_marks', 'grade_point']
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A, A+, B'}),
            'min_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grade_point': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_marks = cleaned_data.get('min_marks')
        max_marks = cleaned_data.get('max_marks')

        if min_marks and max_marks and min_marks > max_marks:
            raise ValidationError("Minimum marks cannot be greater than maximum marks.")
        
        return cleaned_data
