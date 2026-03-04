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
    list_display  = ("teacher", "subject", "section", "course_check", "created_at")
    list_filter   = ("subject__semester__course", "section__class_obj__course", "created_at")
    search_fields = ("teacher__user__username", "teacher__user__first_name", "subject__name", "section__name")
    readonly_fields = ("created_at", "updated_at", "course_validation_display")
    
    fieldsets = (
        ("Assignment", {
            "fields": ("teacher", "subject", "section")
        }),
        ("Validation", {
            "fields": ("course_validation_display",),
            "description": "Subject and Section must belong to the same course."
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def course_check(self, obj):
        if obj.subject and obj.section:
            subject_course = obj.subject.semester.course
            section_course = obj.section.class_obj.course
            return "✅" if subject_course == section_course else "❌"
        return "—"
    course_check.short_description = "Course Match"
    
    def course_validation_display(self, obj):
        if obj.subject and obj.section:
            subject_course = obj.subject.semester.course.name
            section_course = obj.section.class_obj.course.name
            match = subject_course == section_course
            status = "✅ Match" if match else "❌ Mismatch"
            return f"{status}: Subject course = {subject_course}, Section course = {section_course}"
        return "—"
    course_validation_display.short_description = "Course Validation"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher__user', 'subject__semester__course', 'section__class_obj__course'
        )


@admin.register(SectionIncharge)
class SectionInchargeAdmin(admin.ModelAdmin):
    list_display = ("section", "teacher", "assigned_by", "created_at")
    list_filter = ("section__class_obj__course",)
    search_fields = ("section__name", "teacher__user__username", "teacher__user__first_name")
