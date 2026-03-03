from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.faculty.models import TeacherAssignment
from apps.accounts.models import StudentProfile


# ======================================================
# ATTENDANCE SESSION
# ======================================================

class AttendanceSession(TimeStampedModel):

    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    date = models.DateField()

    # 🔒 ERP-style locking
    is_locked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["teacher_assignment", "date"],
                name="unique_session_per_day"
            )
        ]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Auto-create attendance records only once
        if is_new:
            section = self.teacher_assignment.section
            students = StudentProfile.objects.filter(section=section)

            records = [
                AttendanceRecord(
                    session=self,
                    student=student,
                    is_present=False
                )
                for student in students
            ]

            AttendanceRecord.objects.bulk_create(records)

    def __str__(self):
        return f"{self.teacher_assignment} | {self.date}"


# ======================================================
# ATTENDANCE RECORD
# ======================================================

class AttendanceRecord(TimeStampedModel):

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records"
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    is_present = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["session", "student"],
                name="unique_student_per_session"
            )
        ]
        ordering = ["student__roll_number"]
        indexes = [
            models.Index(fields=["is_present"]),
        ]

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.user.username} | {self.session.date} | {status}"