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
    list_display  = ("code", "name", "semester", "course_display", "created_at")
    list_filter   = ("semester__course", "semester__course__program__department", "created_at")
    search_fields = ("code", "name", "semester__course__name")
    ordering      = ("code",)
    readonly_fields = ("created_at", "updated_at", "course_display", "semester_display")
    
    fieldsets = (
        ("Subject Information", {
            "fields": ("code", "name", "semester")
        }),
        ("Display Information", {
            "fields": ("semester_display", "course_display"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def course_display(self, obj):
        """Show which course this subject belongs to."""
        if obj.semester:
            return f"{obj.semester.course.name} (Sem {obj.semester.number})"
        return "—"
    course_display.short_description = "Course (Semester)"
    
    def semester_display(self, obj):
        """Show full semester information."""
        if obj.semester:
            course = obj.semester.course
            program = course.program
            dept = program.department
            return f"{dept.name} → {program.name} → {course.name} → Semester {obj.semester.number}"
        return "—"
    semester_display.short_description = "Full Path"
    
    def get_queryset(self, request):
        """Optimize queries."""
        return super().get_queryset(request).select_related(
            'semester__course__program__department'
        )
