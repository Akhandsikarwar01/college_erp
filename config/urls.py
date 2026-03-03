from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from apps.core.views import home, dashboard
from apps.accounts.views import login_view, signup_view


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Home
    path("", home, name="home"),

    # Auth
    path("register/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),

    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),

    # App URLs
    path("accounts/", include("apps.accounts.urls")),
    path("academics/", include("apps.academics.urls")),
    path("attendance/", include("apps.attendance.urls")),
]