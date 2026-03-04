"""
Custom user model with role-based access (ERP_MANAGER, TEACHER, STUDENT).
StudentProfile stores admission_number + enrollment_number as required.
"""

import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    ERP_MANAGER = "ERP_MANAGER", "ERP Manager"
    TEACHER     = "TEACHER",     "Teacher"
    STUDENT     = "STUDENT",     "Student"


class CustomUser(AbstractUser):
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    email         = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    role          = models.CharField(max_length=20, choices=Role.choices)
    is_verified   = models.BooleanField(default=False)
    is_approved   = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_approved"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_erp_manager(self):
        return self.role == Role.ERP_MANAGER or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    user              = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student_profile"
    )
    section           = models.ForeignKey(
        "academics.Section", on_delete=models.CASCADE, related_name="students"
    )
    admission_number  = models.CharField(max_length=30, unique=True)
    enrollment_number = models.CharField(max_length=30, unique=True)
    roll_number       = models.CharField(max_length=20)

    class Meta:
        ordering = ["roll_number"]

    def __str__(self):
        return f"{self.user.full_name} – {self.admission_number}"


class TeacherProfile(models.Model):
    user        = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    employee_id = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} – {self.employee_id}"


class OTP(models.Model):
    user       = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="otps"
    )
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    OTP_EXPIRY_MINUTES = 5

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=self.OTP_EXPIRY_MINUTES)

    def __str__(self):
        return f"{self.user.username} – {self.code}"
