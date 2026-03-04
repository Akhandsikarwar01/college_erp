from django.urls import path
from .views import (
    signup_view, login_view, verify_otp_view, import_students_csv,
    create_student_account, create_teacher_account, create_admission_user,
)

urlpatterns = [
    path("signup/",          signup_view,        name="signup"),
    path("login/",           login_view,         name="login"),
    path("verify-otp/",      verify_otp_view,    name="verify_otp"),
    path("import-students/", import_students_csv, name="import_students"),
    path("create-student/",  create_student_account, name="create_student_account"),
    path("create-teacher/",  create_teacher_account, name="create_teacher_account"),
    path("create-admission-user/", create_admission_user, name="create_admission_user"),
]
