"""
Academics models: Department → Program → Course → Class → Section
                            ↓
                         Semester → Subject
"""

from django.db import models
from apps.core.models import TimeStampedModel


class Department(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} – {self.name}"


class Program(TimeStampedModel):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="programs"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("department", "name")

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class Course(TimeStampedModel):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("program", "name")

    def __str__(self):
        return f"{self.name} – {self.program.name}"


class Class(TimeStampedModel):
    """Represents a year/level within a course, e.g. Year 1, Year 2."""
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="classes"
    )
    name = models.CharField(max_length=50)  # e.g. "Year 1"

    class Meta:
        ordering = ["name"]
        unique_together = ("course", "name")
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} – {self.course}"


class Section(TimeStampedModel):
    """Batch/division within a class, e.g. A, B, C."""
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ["name"]
        unique_together = ("class_obj", "name")

    def __str__(self):
        return f"Section {self.name} ({self.class_obj})"


class Semester(TimeStampedModel):
    """Semester within a Course, numbered 1–8."""
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="semesters"
    )
    number = models.PositiveIntegerField()

    class Meta:
        ordering = ["number"]
        unique_together = ("course", "number")

    def __str__(self):
        return f"{self.course.name} – Sem {self.number}"


class Subject(TimeStampedModel):
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="subjects"
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("semester", "name")

    def __str__(self):
        return f"{self.name} (Sem {self.semester.number})"
