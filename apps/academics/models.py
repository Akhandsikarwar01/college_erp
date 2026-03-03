from django.db import models
from apps.core.models import TimeStampedModel



class Department(TimeStampedModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Program(TimeStampedModel):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="programs"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class Course(TimeStampedModel):
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.program.name}"
    

class Year(TimeStampedModel):
    name = models.CharField(max_length=50)  # Example: 2025-2026

    def __str__(self):
        return self.name


class Semester(TimeStampedModel):
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=50)  # Example: Semester 1

    def __str__(self):
        return f"{self.name} ({self.year})"




class Class(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=50)  # Year 1 / Year 2

    def __str__(self):
        return f"{self.name} - {self.course}"


class Section(TimeStampedModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=10)  # A, B, C

    def __str__(self):
        return f"{self.name} ({self.class_obj})"
    
class Semester(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="semesters"
    )
    number = models.PositiveIntegerField()  # 1 to 8

    def __str__(self):
        return f"{self.course.name} - Sem {self.number}"


class Subject(TimeStampedModel):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} (Sem {self.semester.number})"
    

