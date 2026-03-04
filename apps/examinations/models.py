"""
Examinations & Grades models.

ExamType → Exam → ExamSchedule
                → StudentResult
GradeScale — configurable grading system
"""

from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.academics.models import Course, Semester, Subject, Section
from apps.accounts.models import StudentProfile


class ExamType(TimeStampedModel):
    """Internal, Mid-term, End-term, Practical, etc."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Exam(TimeStampedModel):
    """An exam event for a course/semester."""
    exam_type = models.ForeignKey(
        ExamType, on_delete=models.CASCADE, related_name="exams"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="exams"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="exams"
    )
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        unique_together = ("exam_type", "course", "semester", "start_date")

    def clean(self):
        """Validate exam date range and course-semester relationship."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Exam end date must be after start date."})
        
        # Validate that semester belongs to course
        if self.semester and self.course and self.semester.course != self.course:
            raise ValidationError({
                "semester": f"Semester {self.semester.number} belongs to course {self.semester.course.name}, "
                           f"but exam is for course {self.course.name}. They must match."
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.exam_type.name})"


class ExamSchedule(TimeStampedModel):
    """Subject-wise exam date and timing within an Exam."""
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="schedules"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="exam_schedules"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    max_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=40)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ("exam", "subject")

    def clean(self):
        """Validate exam schedule constraints."""
        # Validate time range
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "Exam end time must be after start time."})
        
        # Validate date is within exam period
        if self.exam and self.date:
            if self.date < self.exam.start_date:
                raise ValidationError({
                    "date": f"Exam schedule date ({self.date}) cannot be before exam start date ({self.exam.start_date})."
                })
            if self.date > self.exam.end_date:
                raise ValidationError({
                    "date": f"Exam schedule date ({self.date}) cannot be after exam end date ({self.exam.end_date})."
                })
        
        # Validate subject belongs to exam's semester
        if self.exam and self.subject:
            if self.subject.semester != self.exam.semester:
                raise ValidationError({
                    "subject": f"Subject {self.subject.name} is from semester {self.subject.semester.number}, "
                              f"but exam is for semester {self.exam.semester.number}. They must match."
                })
        
        # Validate passing marks
        if self.passing_marks > self.max_marks:
            raise ValidationError({"passing_marks": "Passing marks cannot exceed maximum marks."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.name} — {self.date}"


class GradeScale(TimeStampedModel):
    """Configurable grading: A+ = 90-100, A = 80-89, etc."""
    grade = models.CharField(max_length=5)
    min_marks = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    class Meta:
        ordering = ["-min_marks"]

    def __str__(self):
        return f"{self.grade} ({self.min_marks}–{self.max_marks})"


class StudentResult(TimeStampedModel):
    """One result per student per exam-schedule (subject)."""
    exam_schedule = models.ForeignKey(
        ExamSchedule, on_delete=models.CASCADE, related_name="results"
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="results"
    )
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("exam_schedule", "student")
        ordering = ["student__roll_number"]

    @property
    def percentage(self):
        if self.exam_schedule.max_marks == 0:
            return 0
        return round(
            (float(self.marks_obtained) / self.exam_schedule.max_marks) * 100, 1
        )

    @property
    def is_pass(self):
        return not self.is_absent and self.marks_obtained >= self.exam_schedule.passing_marks

    @property
    def grade(self):
        if self.is_absent:
            return "AB"
        pct = self.percentage
        scale = GradeScale.objects.filter(
            min_marks__lte=pct, max_marks__gte=pct
        ).first()
        return scale.grade if scale else "—"

    def __str__(self):
        return f"{self.student.user.full_name} — {self.exam_schedule.subject.name}: {self.marks_obtained}"
