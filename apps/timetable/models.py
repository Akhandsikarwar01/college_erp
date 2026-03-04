"""
Timetable & Scheduling models.

TimeSlot — period definitions
TimetableEntry — day + slot + section + subject + teacher
AcademicCalendar — holidays and events
"""

from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.academics.models import Section, Subject
from apps.faculty.models import TeacherAssignment


DAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
]


class TimeSlot(TimeStampedModel):
    """Period definition — e.g. Period 1: 9:00–9:50."""
    slot_number = models.PositiveIntegerField(unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=50, blank=True)  # e.g. "Lunch Break"
    is_break = models.BooleanField(default=False)

    class Meta:
        ordering = ["slot_number"]

    def clean(self):
        """Validate time slot."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_break:
            return f"Break: {self.label or ''} ({self.start_time}–{self.end_time})"
        return f"Period {self.slot_number}: {self.start_time:%H:%M}–{self.end_time:%H:%M}"


class TimetableEntry(TimeStampedModel):
    """One cell on the timetable grid."""
    day = models.IntegerField(choices=DAY_CHOICES)
    time_slot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, related_name="entries"
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="timetable_entries"
    )
    teacher_assignment = models.ForeignKey(
        TeacherAssignment, on_delete=models.CASCADE, related_name="timetable_entries"
    )

    class Meta:
        unique_together = ("day", "time_slot", "section")
        ordering = ["day", "time_slot__slot_number"]

    def clean(self):
        """Validate that teacher assignment's section matches entry's section."""
        if self.teacher_assignment and self.section:
            if self.teacher_assignment.section != self.section:
                raise ValidationError({
                    "teacher_assignment": f"Teacher assignment is for section {self.teacher_assignment.section.name}, "
                                         f"but timetable entry is for section {self.section.name}. They must match."
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.get_day_display()} P{self.time_slot.slot_number} — "
            f"{self.teacher_assignment.subject.name} ({self.section.name})"
        )


CALENDAR_TYPE_CHOICES = [
    ("HOLIDAY", "Holiday"),
    ("EVENT", "Event"),
    ("EXAM", "Exam Period"),
]


class AcademicCalendar(TimeStampedModel):
    """Holidays, events, exam periods."""
    title = models.CharField(max_length=200)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPE_CHOICES, default="HOLIDAY")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]

    def clean(self):
        """Validate date range."""
        if self.end_date and self.date and self.end_date < self.date:
            raise ValidationError({"end_date": "End date must be after start date."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.date})"
