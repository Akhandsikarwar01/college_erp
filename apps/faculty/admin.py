from django.contrib import admin
from .models import TeacherAssignment, FacultyDepartment, TeacherMaster

admin.site.register(TeacherAssignment)

@admin.register(FacultyDepartment)
class FacultyDepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(TeacherMaster)
class TeacherMasterAdmin(admin.ModelAdmin):
    list_display = ("teacher_code", "full_name", "faculty_department", "is_registered")
    list_filter = ("faculty_department", "is_registered")
    search_fields = ("teacher_code", "full_name")