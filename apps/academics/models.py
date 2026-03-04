"""
Academics models: Department → Program → Course → Class → Section
                            ↓
                         Semester → Subject
"""

from django.db import models
from django.core.exceptions import ValidationError
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
    """Subject taught in a specific semester of a course.
    
    Each subject:
    - Belongs to exactly ONE semester (hence ONE course, ONE specific semester number)
    - Has a globally unique code (e.g., CS101, MATH201)
    - Can be taught by multiple teachers to different sections
    - Cannot be duplicated per semester (unique_together on semester + name)
    """
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="subjects"
    )
    name = models.CharField(max_length=100, help_text="Full subject name (e.g., 'Data Structures')")
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique subject code (e.g., 'CS301'). Globally unique across all courses."
    )

    class Meta:
        ordering = ["code"]
        unique_together = ("semester", "name")  # Can't repeat same name in same semester
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["semester", "name"]),
        ]

    def clean(self):
        """Validate subject code format and uniqueness."""
        if not self.code:
            raise ValidationError({"code": "Subject code is required."})
        
        # Validate code format: alphanumeric, no spaces
        if not self.code.replace("-", "").replace("_", "").isalnum():
            raise ValidationError({
                "code": "Subject code must be alphanumeric (e.g., CS301, MATH-201). Hyphens and underscores allowed."
            })
        
        # Check for existing code (excluding self)
        if Subject.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError({"code": f"Subject code '{self.code}' already exists. Codes must be globally unique."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} – {self.name} (Sem {self.semester.number})"
