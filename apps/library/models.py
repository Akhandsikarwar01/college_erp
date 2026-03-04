"""
Library Management models.

BookCategory → Book → BookIssue
"""

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel


class BookCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Book categories"

    def __str__(self):
        return self.name


class Book(TimeStampedModel):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    category = models.ForeignKey(
        BookCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="books"
    )
    publisher = models.CharField(max_length=200, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["title"]

    @property
    def is_available(self):
        return self.available_copies > 0

    def __str__(self):
        return f"{self.title} by {self.author}"


ISSUE_STATUS_CHOICES = [
    ("ISSUED", "Issued"),
    ("RETURNED", "Returned"),
    ("OVERDUE", "Overdue"),
]


class BookIssue(TimeStampedModel):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="issues"
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_issues"
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ISSUE_STATUS_CHOICES, default="ISSUED")

    class Meta:
        ordering = ["-issue_date"]

    @property
    def is_overdue(self):
        if self.status == "RETURNED":
            return False
        return timezone.now().date() > self.due_date

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.issue_date or timezone.now().date()) + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} → {self.borrower.full_name}"
