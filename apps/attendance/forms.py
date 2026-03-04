"""
Forms for Attendance app
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.faculty.models import TeacherAssignment
from .models import AttendanceSession, AttendanceRecord


class AttendanceSessionForm(forms.ModelForm):
    """Form to create attendance session"""
    class Meta:
        model = AttendanceSession
        fields = ['teacher_assignment', 'date']
        widgets = {
            'teacher_assignment': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date > timezone.now().date():
            raise ValidationError("Cannot create session for future dates.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        assignment = cleaned_data.get('teacher_assignment')
        date = cleaned_data.get('date')

        if assignment and date:
            # Check if session already exists for this date
            existing = AttendanceSession.objects.filter(
                teacher_assignment=assignment,
                date=date
            ).exists()
            if existing:
                raise ValidationError("A session already exists for this assignment on this date.")
        return cleaned_data


class QRScanForm(forms.Form):
    """Form for QR code scanning"""
    qr_payload = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    def clean_qr_payload(self):
        payload = self.cleaned_data.get('qr_payload')
        if not payload:
            raise ValidationError("Invalid QR code.")
        return payload


class BulkAttendanceForm(forms.Form):
    """Form for marking attendance in bulk"""
    session = forms.ModelChoiceField(
        queryset=AttendanceSession.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'teacher_profile'):
            self.fields['session'].queryset = AttendanceSession.objects.filter(
                teacher_assignment__teacher=user.teacher_profile
            ).order_by('-date')
