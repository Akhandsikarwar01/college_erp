from django.contrib import admin
from .models import (
    Department,
    Program,
    Course,
    Semester,
    Subject,
    Class,
    Section,
)

# -------- Inlines --------

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 1


class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 1


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


# -------- Department --------

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    inlines = [ProgramInline]


# -------- Program --------

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "department")


# -------- Course --------

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "program")
    inlines = [SemesterInline]


# -------- Semester --------

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("course", "number")


# -------- Subject --------

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "semester")


# -------- Class (Batch for now) --------

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "course")
    inlines = [SectionInline]


# -------- Section --------

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "class_obj")