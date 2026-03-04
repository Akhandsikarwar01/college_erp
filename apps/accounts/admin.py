from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser, StudentProfile, TeacherProfile, DeanProfile, ParentProfile, OTP, Role


# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM USER
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "full_name", "role", "mobile_number",
        "is_verified", "approval_status", "is_active", "date_joined",
    )
    list_filter  = ("role", "is_approved", "is_verified", "is_active")
    search_fields = ("username", "email", "mobile_number", "first_name", "last_name")
    ordering     = ("-date_joined",)
    actions      = ["approve_users", "reject_users"]

    fieldsets = UserAdmin.fieldsets + (
        ("College ERP", {
            "fields": ("role", "mobile_number", "is_verified", "is_approved"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("College ERP", {
            "fields": ("role", "mobile_number", "email"),
        }),
    )

    # ── Computed columns ──────────────────────────────────────────────────
    @admin.display(description="Name")
    def full_name(self, obj):
        return obj.full_name

    @admin.display(description="Approval", ordering="is_approved")
    def approval_status(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color:#6366f1;font-weight:600">Superuser</span>')
        if obj.is_approved:
            return format_html('<span style="color:#10b981;font-weight:600">✓ Approved</span>')
        if obj.is_verified:
            return format_html('<span style="color:#f59e0b;font-weight:600">⏳ Pending</span>')
        return format_html('<span style="color:#94a3b8">Unverified</span>')

    # ── Bulk actions ──────────────────────────────────────────────────────
    @admin.action(description="✅ Approve selected users")
    def approve_users(self, request, queryset):
        updated = queryset.filter(is_verified=True).update(is_approved=True, is_active=True)
        self.message_user(request, f"{updated} user(s) approved successfully.")

    @admin.action(description="❌ Reject / deactivate selected users")
    def reject_users(self, request, queryset):
        updated = queryset.update(is_approved=False, is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")


# ──────────────────────────────────────────────────────────────────────────────
# STUDENT PROFILE
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = (
        "user", "admission_number", "application_number", "enrollment_number",
        "roll_number", "section", "father_name", "guardian_phone"
    )
    list_filter   = ("section__class_obj__course",)
    search_fields = (
        "user__username", "user__first_name", "user__last_name",
        "admission_number", "application_number", "enrollment_number",
        "roll_number", "father_name", "mother_name", "guardian_phone"
    )
    raw_id_fields = ("user", "section")


# ──────────────────────────────────────────────────────────────────────────────
# TEACHER PROFILE
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "employee_id")
    search_fields = ("user__username", "employee_id")
    raw_id_fields = ("user",)


@admin.register(DeanProfile)
class DeanProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "employee_id")
    list_filter = ("department",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "employee_id")
    raw_id_fields = ("user", "department")


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "relationship", "student_count")
    list_filter = ("relationship",)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    filter_horizontal = ("students",)
    raw_id_fields = ("user",)

    @admin.display(description="Linked Students")
    def student_count(self, obj):
        return obj.students.count()


# ──────────────────────────────────────────────────────────────────────────────
# OTP  (read-only — useful for debugging)
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display  = ("user", "code", "created_at", "expired")
    list_filter   = ("created_at",)
    search_fields = ("user__username",)
    readonly_fields = ("user", "code", "created_at")

    @admin.display(description="Expired?", boolean=True)
    def expired(self, obj):
        return obj.is_expired()
