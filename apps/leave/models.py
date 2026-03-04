"""
Leave Management models.

LeaveType — Sick, Casual, etc.
LeaveApplication — with approval workflow
"""

from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


STATUS_CHOICES = [
    ("PENDING", "Pending"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
]


class LeaveType(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    max_days_per_year = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (max {self.max_days_per_year} days)"


class LeaveApplication(TimeStampedModel):
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_applications"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="applications"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviewed_leaves"
    )
    review_remarks = models.CharField(max_length=200, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.applicant.full_name} — {self.leave_type.name} ({self.start_date} to {self.end_date})"
