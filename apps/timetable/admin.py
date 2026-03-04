from django.contrib import admin
from .models import TimeSlot, TimetableEntry, AcademicCalendar


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("slot_number", "start_time", "end_time", "label", "is_break")
    ordering = ("slot_number",)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("day", "time_slot", "section", "teacher_assignment")
    list_filter = ("day", "section")
    search_fields = ("teacher_assignment__subject__name",)


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "end_date", "calendar_type")
    list_filter = ("calendar_type",)
    date_hierarchy = "date"
    search_fields = ("title",)
