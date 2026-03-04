"""
Forms for Library app
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Book, BookCategory, BookIssue
from apps.academics.models import Section
from apps.accounts.models import CustomUser


class BookForm(forms.ModelForm):
    """Form to add/edit book"""
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'publisher', 'total_copies']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book Title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author Name'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISBN (optional)',
                'required': False
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher'
            }),
            'total_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and Book.objects.filter(isbn=isbn).exists():
            raise ValidationError("This ISBN already exists.")
        return isbn

    def clean_total_copies(self):
        copies = self.cleaned_data.get('total_copies')
        if copies and copies < 1:
            raise ValidationError("Total copies must be at least 1.")
        return copies


class BookIssueForm(forms.ModelForm):
    """Form to issue book to user"""
    class Meta:
        model = BookIssue
        fields = ['book', 'borrower', 'issue_date', 'due_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'borrower': forms.Select(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)
        # Only show students and teachers
        from apps.accounts.models import Role
        self.fields['borrower'].queryset = CustomUser.objects.filter(
            role__in=[Role.STUDENT, Role.TEACHER],
            is_active=True
        )

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')
        book = cleaned_data.get('book')

        if issue_date and due_date and issue_date > due_date:
            raise ValidationError("Due date must be after issue date.")
        
        if book and book.available_copies <= 0:
            raise ValidationError("This book is not available.")
        
        return cleaned_data


class BookReturnForm(forms.ModelForm):
    """Form to return book"""
    fine_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Fine amount in ₹ (if any)'
        })
    )

    class Meta:
        model = BookIssue
        fields = ['return_date']
        widgets = {
            'return_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        return_date = cleaned_data.get('return_date')
        
        if return_date and return_date > timezone.now().date():
            raise ValidationError("Return date cannot be in the future.")
        
        return cleaned_data


class BookSearchForm(forms.Form):
    """Form for book catalog search"""
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('author', 'Author'),
        ('isbn', 'ISBN'),
    ]

    search_by = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.RadioSelect
    )
    search_query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter search term'
        })
    )
    category = forms.ModelChoiceField(
        queryset=BookCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BookCategoryForm(forms.ModelForm):
    """Form to create book category"""
    class Meta:
        model = BookCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category Name'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if BookCategory.objects.filter(name__iexact=name).exists():
            raise ValidationError("This category already exists.")
        return name
