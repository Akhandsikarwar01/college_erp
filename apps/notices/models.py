"""
Notices & Events models.

NoticeCategory — categorize notices
Notice — announcements with target roles
Event — events with date and venue
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel


TARGET_CHOICES = [
    ("ALL", "Everyone"),
    ("STUDENT", "Students Only"),
    ("TEACHER", "Teachers Only"),
    ("ERP_MANAGER", "ERP Managers Only"),
]


class NoticeCategory(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Notice categories"

    def __str__(self):
        return self.name


class Notice(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(
        NoticeCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="notices"
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notices"
    )
    target_role = models.CharField(max_length=20, choices=TARGET_CHOICES, default="ALL")
    is_pinned = models.BooleanField(default=False)
    attachment = models.FileField(upload_to="notices/", blank=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title


class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )

    class Meta:
        ordering = ["-date"]

    def clean(self):
        """Validate event date range."""
        if self.end_date and self.date and self.end_date < self.date:
            raise ValidationError({"end_date": "Event end date must be after start date."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.date})"
