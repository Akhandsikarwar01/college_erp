from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import (
    home, dashboard,
    pending_approvals, approve_user, reject_user, bulk_approve,
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

    # ERP Manager approval workflow
    path("approvals/",                        pending_approvals, name="pending_approvals"),
    path("approvals/approve/<int:user_id>/",  approve_user,      name="approve_user"),
    path("approvals/reject/<int:user_id>/",   reject_user,       name="reject_user"),
    path("approvals/bulk-approve/",           bulk_approve,      name="bulk_approve"),

    path("accounts/",   include("apps.accounts.urls")),
    path("academics/",  include("apps.academics.urls")),
    path("attendance/", include("apps.attendance.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
