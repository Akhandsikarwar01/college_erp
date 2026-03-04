from django.contrib import admin
from .models import FacultyDepartment, TeacherMaster, TeacherAssignment, SectionIncharge


@admin.register(FacultyDepartment)
class FacultyDepartmentAdmin(admin.ModelAdmin):
    list_display  = ("id", "name")
    search_fields = ("name",)


@admin.register(TeacherMaster)
class TeacherMasterAdmin(admin.ModelAdmin):
    list_display   = ("teacher_code", "full_name", "faculty_department", "is_registered")
    list_filter    = ("faculty_department", "is_registered")
    search_fields  = ("teacher_code", "full_name")
    list_editable  = ("is_registered",)
    ordering       = ("teacher_code",)
    actions        = ["mark_unregistered"]

    @admin.action(description="Mark selected as unregistered (allow re-signup)")
    def mark_unregistered(self, request, queryset):
        updated = queryset.update(is_registered=False)
        self.message_user(request, f"{updated} teacher(s) marked as unregistered.")


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display  = ("teacher", "subject", "section", "created_at")
    list_filter   = ("subject__semester__course", "section__class_obj__course")
    search_fields = ("teacher__user__username", "subject__name", "section__name")
    autocomplete_fields = []


@admin.register(SectionIncharge)
class SectionInchargeAdmin(admin.ModelAdmin):
    list_display = ("section", "teacher", "assigned_by", "created_at")
    list_filter = ("section__class_obj__course",)
    search_fields = ("section__name", "teacher__user__username", "teacher__user__first_name")
