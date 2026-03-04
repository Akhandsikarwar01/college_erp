"""
Forms for Fees app
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import FeeType, FeeStructure, StudentFee, Payment, PAYMENT_METHODS
from apps.academics.models import Course, Semester


class FeeStructureForm(forms.ModelForm):
    """Form to create fee structure"""
    class Meta:
        model = FeeStructure
        fields = ['fee_type', 'course', 'semester', 'amount']
        widgets = {
            'fee_type': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Amount in ₹'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        fee_type = cleaned_data.get('fee_type')
        course = cleaned_data.get('course')
        semester = cleaned_data.get('semester')

        if fee_type and course and semester:
            existing = FeeStructure.objects.filter(
                fee_type=fee_type,
                course=course,
                semester=semester
            ).exists()
            if existing:
                raise ValidationError("This fee structure already exists.")
        
        return cleaned_data


class GenerateFeeForm(forms.Form):
    """Form to generate fees for students"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    overwrite = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Check to overwrite existing fees'
    )

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        
        if due_date:
            from django.utils import timezone
            if due_date < timezone.now().date():
                raise ValidationError("Due date cannot be in the past.")
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    """Form to record student payment"""
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'remarks']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Amount paid in ₹'
            }),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Payment notes (optional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        if amount and amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")
        
        return cleaned_data


class PaymentSearchForm(forms.Form):
    """Form for filtering payment records"""
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
    payment_method = forms.ChoiceField(
        required=False,
        choices=[('', 'All Methods')] + PAYMENT_METHODS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by student name or ID'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date.")
        
        return cleaned_data


class FeeTypeForm(forms.ModelForm):
    """Form to create fee type"""
    class Meta:
        model = FeeType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tuition Fee, Lab Fee'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if FeeType.objects.filter(name__iexact=name).exists():
            raise ValidationError("This fee type already exists.")
        return name
