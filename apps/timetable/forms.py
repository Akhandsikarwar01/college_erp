"""
Forms for Timetable app
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import TimeSlot, TimetableEntry, AcademicCalendar, CALENDAR_TYPE_CHOICES
from apps.academics.models import Section
from apps.faculty.models import TeacherAssignment


class TimeSlotForm(forms.ModelForm):
    """Form to create time slot"""
    class Meta:
        model = TimeSlot
        fields = ['slot_number', 'start_time', 'end_time', 'label', 'is_break']
        widgets = {
            'slot_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Lunch Break'
            }),
            'is_break': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time.")
        
        return cleaned_data


class TimetableEntryForm(forms.ModelForm):
    """Form to create timetable entry"""
    class Meta:
        model = TimetableEntry
        fields = ['day', 'time_slot', 'section', 'teacher_assignment']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'time_slot': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'teacher_assignment': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        time_slot = cleaned_data.get('time_slot')
        section = cleaned_data.get('section')

        if time_slot and time_slot.is_break:
            raise ValidationError("Cannot assign teacher to break periods.")

        if day is not None and time_slot and section:
            existing = TimetableEntry.objects.filter(
                day=day,
                time_slot=time_slot,
                section=section
            ).exists()
            if existing:
                raise ValidationError("This slot is already assigned for this section.")
        
        return cleaned_data


class AcademicCalendarForm(forms.ModelForm):
    """Form to create academic calendar event"""
    class Meta:
        model = AcademicCalendar
        fields = ['title', 'date', 'end_date', 'calendar_type', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Title'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'calendar_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Event description (optional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        end_date = cleaned_data.get('end_date')

        if date and end_date and date > end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class TimetableFilterForm(forms.Form):
    """Form for filtering timetable"""
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    day = forms.ChoiceField(
        required=False,
        choices=[('', 'All Days')] + [(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
