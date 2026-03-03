from django.urls import path
from .views import (
    create_session,
    mark_attendance,
    lock_session,
    export_attendance_csv
)

urlpatterns = [
    path("create/", create_session, name="create_session"),
    path("mark/<int:session_id>/", mark_attendance, name="mark_attendance"),
    path("lock/<int:session_id>/", lock_session, name="lock_session"),
    path("export/<int:session_id>/", export_attendance_csv, name="export_attendance_csv"),
]