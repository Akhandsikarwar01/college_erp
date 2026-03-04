"""
Forms for Leave app
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import LeaveApplication, LeaveType, STATUS_CHOICES


class LeaveApplicationForm(forms.ModelForm):
    """Form to apply for leave"""
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Reason for leave'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("End date must be after start date.")
            
            if start_date < timezone.now().date():
                raise ValidationError("Start date cannot be in the past.")
            
            days = (end_date - start_date).days + 1
            leave_type = cleaned_data.get('leave_type')
            if leave_type and days > leave_type.max_days_per_year:
                raise ValidationError(
                    f"Leave period ({days} days) exceeds maximum allowed ({leave_type.max_days_per_year} days)."
                )
        
        return cleaned_data


class LeaveApprovalForm(forms.ModelForm):
    """Form for ERP Manager to approve/reject leave"""
    class Meta:
        model = LeaveApplication
        fields = ['status', 'review_remarks']
        widgets = {
            'status': forms.Select(
                choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
                attrs={'class': 'form-control'}
            ),
            'review_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Approval/Rejection remarks'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        
        if status == 'REJECTED' and not cleaned_data.get('review_remarks'):
            raise ValidationError("Remarks are required when rejecting leave.")
        
        return cleaned_data


class LeaveTypeForm(forms.ModelForm):
    """Form to create leave type"""
    class Meta:
        model = LeaveType
        fields = ['name', 'max_days_per_year']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sick Leave, Casual Leave'
            }),
            'max_days_per_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if LeaveType.objects.filter(name__iexact=name).exists():
            raise ValidationError("This leave type already exists.")
        return name

    def clean_max_days_per_year(self):
        days = self.cleaned_data.get('max_days_per_year')
        if days and days < 1:
            raise ValidationError("Maximum days must be at least 1.")
        return days


class LeaveFilterForm(forms.Form):
    """Form for filtering leave applications"""
    STATUS_FILTER_CHOICES = [('', 'All Statuses')] + STATUS_CHOICES
    
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_FILTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
