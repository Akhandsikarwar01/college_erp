from django.contrib import admin
from .models import ExamType, Exam, ExamSchedule, GradeScale, StudentResult


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "course", "semester", "start_date", "end_date", "is_published")
    list_filter = ("exam_type", "is_published", "course")
    search_fields = ("name",)
    date_hierarchy = "start_date"


class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 1


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("exam", "subject", "date", "start_time", "end_time", "room", "max_marks")
    list_filter = ("exam", "date")
    search_fields = ("subject__name",)


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("grade", "min_marks", "max_marks", "grade_point")
    ordering = ("-min_marks",)


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam_schedule", "marks_obtained", "is_absent", "is_pass_display")
    list_filter = ("exam_schedule__exam", "is_absent")
    search_fields = ("student__user__username", "student__roll_number")
    raw_id_fields = ("student", "exam_schedule")

    @admin.display(description="Pass?", boolean=True)
    def is_pass_display(self, obj):
        return obj.is_pass
