"""
Forms for Notices app
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Notice, NoticeCategory, Event, TARGET_CHOICES


class NoticeForm(forms.ModelForm):
    """Form to create/edit notice"""
    class Meta:
        model = Notice
        fields = ['title', 'content', 'category', 'target_role', 'is_pinned', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notice Title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Notice Content'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'target_role': forms.Select(attrs={'class': 'form-control'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise ValidationError("Notice content must be at least 10 characters long.")
        return content

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size must not exceed 5MB.")
        return attachment


class NoticeCategoryForm(forms.ModelForm):
    """Form to create notice category"""
    class Meta:
        model = NoticeCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category Name'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if NoticeCategory.objects.filter(name__iexact=name).exists():
            raise ValidationError("This category already exists.")
        return name


class EventForm(forms.ModelForm):
    """Form to create/edit event"""
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'end_date', 'venue']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Event Description'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Venue'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        end_date = cleaned_data.get('end_date')

        if date and date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        
        if date and end_date and date > end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class NoticeSearchForm(forms.Form):
    """Form for searching notices"""
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('content', 'Content'),
        ('category', 'Category'),
    ]

    search_by = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + SEARCH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search notices...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=NoticeCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class EventFilterForm(forms.Form):
    """Form for filtering events"""
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
    venue = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by venue'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date.")
        
        return cleaned_data
