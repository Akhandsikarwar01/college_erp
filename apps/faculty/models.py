from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.accounts.models import TeacherProfile
from apps.academics.models import Subject, Section
from django.db import models



class TeacherAssignment(TimeStampedModel):
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_assignments"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teacher_assignments"
    )

    class Meta:
        unique_together = ("teacher", "subject", "section")

    def clean(self):
        """Validate that subject's course matches section's class's course"""
        if self.subject and self.section:
            subject_course = self.subject.semester.course
            section_course = self.section.class_obj.course
            if subject_course != section_course:
                raise ValidationError(
                    f"Subject '{self.subject.name}' is from course {subject_course.name}, "
                    f"but section is in course {section_course.name}. "
                    f"Subject and section must be from the same course."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.name} ({self.section.name})"
    


class FacultyDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TeacherMaster(models.Model):
    teacher_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    faculty_department = models.ForeignKey(
        FacultyDepartment,
        on_delete=models.CASCADE,
        related_name="teachers"
    )
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.teacher_code})"


class SectionIncharge(TimeStampedModel):
    section = models.OneToOneField(
        Section,
        on_delete=models.CASCADE,
        related_name="section_incharge_assignment"
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="section_incharge_sections"
    )
    assigned_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_section_incharges"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["section"], name="unique_incharge_per_section")
        ]

    def __str__(self):
        return f"{self.section} → {self.teacher.user.full_name}"