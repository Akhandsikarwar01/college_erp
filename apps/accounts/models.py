from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random


# ==============================
# ROLE ENUM
# ==============================
class Role(models.TextChoices):
    ERP_MANAGER = "ERP_MANAGER", "ERP Manager"
    TEACHER = "TEACHER", "Teacher"
    STUDENT = "STUDENT", "Student"


# ==============================
# CUSTOM USER
# ==============================
class CustomUser(AbstractUser):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    mobile_number = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


# ==============================
# STUDENT PROFILE
# ==============================
from apps.academics.models import Section


class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="students"
    )

    roll_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"


# ==============================
# TEACHER PROFILE
# ==============================
class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    employee_id = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"


# ==============================
# OTP MODEL
# ==============================
class OTP(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="otps"
    )

    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
@staticmethod
def generate_otp():
    return str(random.randint(100000, 999999))