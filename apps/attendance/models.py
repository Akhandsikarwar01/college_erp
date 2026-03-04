"""
Attendance models — QR-based system.

Flow:
  Teacher creates AttendanceSession → system generates a rotating QR token
  (5-second expiry, auto-refreshed via AJAX).
  Student scans QR → POST to /attendance/scan/ → AttendanceRecord created.
"""

import hashlib
import hmac
import secrets
import time

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.faculty.models import TeacherAssignment
from apps.accounts.models import StudentProfile


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

QR_WINDOW_SECONDS = 5   # Each QR token is valid for this many seconds


def _make_token(session_id: int, window: int) -> str:
    """
    Build an HMAC-SHA256 token tied to (session_id, time-window).
    window = int(unix_time / QR_WINDOW_SECONDS)

    We sign with Django's SECRET_KEY so tokens cannot be forged
    without server-side knowledge.
    """
    secret = settings.SECRET_KEY.encode()
    msg    = f"{session_id}:{window}".encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def current_qr_token(session_id: int) -> str:
    """Return the valid token for right now."""
    window = int(time.time() / QR_WINDOW_SECONDS)
    return _make_token(session_id, window)


def verify_qr_token(session_id: int, token: str) -> bool:
    """
    Accept the current window AND the previous one to tolerate
    the brief moment between generation and scan.
    """
    window = int(time.time() / QR_WINDOW_SECONDS)
    valid  = {
        _make_token(session_id, window),
        _make_token(session_id, window - 1),   # grace period
    }
    return token in valid


# ──────────────────────────────────────────────────────────────────────────────
# ATTENDANCE SESSION
# ──────────────────────────────────────────────────────────────────────────────

class AttendanceSession(TimeStampedModel):
    """
    One session = one subject + one section on one date.
    QR tokens are computed on-the-fly (not stored) using HMAC.
    """

    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    date       = models.DateField()
    is_active  = models.BooleanField(default=True)   # Teacher can close session
    is_locked  = models.BooleanField(default=False)  # Locked = no more scans

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["teacher_assignment", "date"],
                name="unique_session_per_assignment_per_day",
            )
        ]
        ordering = ["-date", "-created_at"]
        indexes  = [models.Index(fields=["date", "is_active"])]

    # ------------------------------------------------------------------
    # QR helpers (no DB storage needed — pure computation)
    # ------------------------------------------------------------------

    def get_current_token(self) -> str:
        return current_qr_token(self.pk)

    def verify_token(self, token: str) -> bool:
        if self.is_locked or not self.is_active:
            return False
        return verify_qr_token(self.pk, token)

    # ------------------------------------------------------------------
    # Payload embedded in QR image
    # ------------------------------------------------------------------

    def get_qr_payload(self) -> str:
        """
        JSON string encoded inside the QR image.
        The student app POSTs this payload to /attendance/scan/.
        """
        import json
        token = self.get_current_token()
        return json.dumps({"session_id": self.pk, "token": token})

    def __str__(self):
        return (
            f"{self.teacher_assignment.subject.name} | "
            f"{self.teacher_assignment.section.name} | "
            f"{self.date}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# ATTENDANCE RECORD
# ──────────────────────────────────────────────────────────────────────────────

class AttendanceRecord(TimeStampedModel):
    """One row per (student, session). Created when student scans QR."""

    session     = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records",
    )
    student     = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    is_present  = models.BooleanField(default=True)
    marked_at   = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["session", "student"],
                name="unique_attendance_per_session",
            )
        ]
        ordering = ["student__roll_number"]
        indexes  = [models.Index(fields=["marked_at"])]

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return (
            f"{self.student.user.full_name} | "
            f"{self.session.date} | {status}"
        )
