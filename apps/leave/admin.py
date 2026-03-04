from django.contrib import admin
from .models import LeaveType, LeaveApplication


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "max_days_per_year")
    search_fields = ("name",)


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "leave_type", "start_date", "end_date", "days", "status", "reviewed_by")
    list_filter = ("status", "leave_type")
    search_fields = ("applicant__username", "applicant__first_name")
    date_hierarchy = "start_date"

    @admin.display(description="Days")
    def days(self, obj):
        return obj.days
