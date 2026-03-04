from django.contrib import admin
from .models import Department, Program, Course, Class, Section, Semester, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ("code", "name", "created_at")
    search_fields = ("code", "name")
    ordering      = ("code",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display  = ("name", "department")
    list_filter   = ("department",)
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ("name", "program")
    list_filter   = ("program__department",)
    search_fields = ("name",)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display  = ("name", "course")
    list_filter   = ("course__program__department",)
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display  = ("name", "class_obj")
    list_filter   = ("class_obj__course",)
    search_fields = ("name",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display  = ("number", "course")
    list_filter   = ("course",)
    ordering      = ("course", "number")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ("name", "code", "semester")
    list_filter   = ("semester__course",)
    search_fields = ("name", "code")
