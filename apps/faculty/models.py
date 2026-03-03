from django.db import models
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