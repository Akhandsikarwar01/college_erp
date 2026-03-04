from django.contrib import admin
from django.utils.html import format_html

from .models import AttendanceSession, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display  = (
        "teacher_assignment", "date", "present_count",
        "is_active", "is_locked", "created_at",
    )
    list_filter   = ("is_active", "is_locked", "date")
    search_fields = (
        "teacher_assignment__teacher__user__username",
        "teacher_assignment__subject__name",
    )
    ordering      = ("-date", "-created_at")
    actions       = ["lock_sessions", "unlock_sessions"]

    @admin.display(description="Present")
    def present_count(self, obj):
        total   = obj.records.count()
        present = obj.records.filter(is_present=True).count()
        pct     = round((present / total) * 100) if total else 0
        colour  = "#10b981" if pct >= 75 else "#ef4444"
        return format_html(
            '<span style="color:{};font-weight:600">{}/{}</span> ({}%)',
            colour, present, total, pct
        )

    @admin.action(description="🔒 Lock selected sessions")
    def lock_sessions(self, request, queryset):
        updated = queryset.update(is_active=False, is_locked=True)
        self.message_user(request, f"{updated} session(s) locked.")

    @admin.action(description="🔓 Unlock selected sessions")
    def unlock_sessions(self, request, queryset):
        updated = queryset.update(is_active=True, is_locked=False)
        self.message_user(request, f"{updated} session(s) unlocked.")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ("student", "session", "is_present", "marked_at")
    list_filter   = ("is_present", "session__date")
    search_fields = (
        "student__user__username",
        "student__admission_number",
        "student__enrollment_number",
    )
    ordering      = ("-marked_at",)
    readonly_fields = ("marked_at",)
