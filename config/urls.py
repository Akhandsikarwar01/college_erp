from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import (
    home, dashboard,
    pending_approvals, approve_user, reject_user, bulk_approve,
    student_profile_view, teacher_profile_view,
    user_status, debug_otps,
    parent_dashboard, parent_child_attendance, parent_child_fees,
    parent_child_leaves, parent_child_profile,
    download_attendance_report, download_fee_report,
)
from apps.accounts.views import login_view, signup_view, verify_otp_view

def logout_post(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    if request.method == "POST":
        logout(request)
        return redirect("home")
    return redirect("dashboard")


urlpatterns = [
    path("admin/",      admin.site.urls),
    path("",            home,            name="home"),
    path("login/",      login_view,      name="login"),
    path("register/",   signup_view,     name="signup"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path("logout/",     logout_post,     name="logout"),
    path("dashboard/",  dashboard,       name="dashboard"),
    path("status/",     user_status,     name="user_status"),
    path("debug/otps/", debug_otps,      name="debug_otps"),
    path("profile/student/", student_profile_view, name="student_profile"),
    path("profile/teacher/", teacher_profile_view, name="teacher_profile"),

    # Parent Portal
    path("parent/",                           parent_dashboard,           name="parent_dashboard"),
    path("parent/child/<int:child_id>/attendance/", parent_child_attendance, name="parent_child_attendance"),
    path("parent/child/<int:child_id>/fees/",      parent_child_fees,        name="parent_child_fees"),
    path("parent/child/<int:child_id>/leaves/",    parent_child_leaves,      name="parent_child_leaves"),
    path("parent/child/<int:child_id>/profile/",   parent_child_profile,     name="parent_child_profile"),
    path("parent/child/<int:child_id>/attendance/report/", download_attendance_report, name="download_attendance_report"),
    path("parent/child/<int:child_id>/fees/report/",       download_fee_report,       name="download_fee_report"),

    # ERP Manager approval workflow
    path("approvals/",                        pending_approvals, name="pending_approvals"),
    path("approvals/approve/<int:user_id>/",  approve_user,      name="approve_user"),
    path("approvals/reject/<int:user_id>/",   reject_user,       name="reject_user"),
    path("approvals/bulk-approve/",           bulk_approve,      name="bulk_approve"),

    path("accounts/",      include("apps.accounts.urls")),
    path("academics/",     include("apps.academics.urls")),
    path("attendance/",    include("apps.attendance.urls")),
    path("examinations/",  include("apps.examinations.urls")),
    path("fees/",          include("apps.fees.urls")),
    path("timetable/",     include("apps.timetable.urls")),
    path("notices/",       include("apps.notices.urls")),
    path("leave/",         include("apps.leave.urls")),
    path("library/",       include("apps.library.urls")),
    
    # REST API
    path("api/",           include("apps.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
