from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, TeacherProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "role",
        "mobile_number",
        "is_approved",
        "is_active",
    )
    list_filter = ("role", "is_approved", "is_active")
    search_fields = ("username", "mobile_number")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Info",
            {
                "fields": (
                    "role",
                    "mobile_number",
                    "is_approved",
                )
            },
        ),
    )


admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)