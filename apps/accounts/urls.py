from django.urls import path
from .views import signup_view, login_view, verify_otp_view, import_students_csv

urlpatterns = [
    path("signup/",          signup_view,        name="signup"),
    path("login/",           login_view,         name="login"),
    path("verify-otp/",      verify_otp_view,    name="verify_otp"),
    path("import-students/", import_students_csv, name="import_students"),
]
