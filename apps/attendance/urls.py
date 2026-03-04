from django.urls import path
from . import views

urlpatterns = [
    # Teacher — session management
    path("sessions/",                   views.session_list,           name="session_list"),
    path("sessions/create/",            views.create_session,         name="create_session"),
    path("sessions/<int:session_id>/",          views.session_detail, name="session_detail"),
    path("sessions/<int:session_id>/qr/",       views.qr_display,     name="qr_display"),
    path("sessions/<int:session_id>/close/",    views.close_session,  name="close_session"),
    path("sessions/<int:session_id>/export/",   views.export_attendance_csv, name="export_attendance_csv"),

    # AJAX — fresh token for QR page
    path("api/token/<int:session_id>/", views.get_qr_token,           name="get_qr_token"),

    # Student — scan
    path("scan/",                        views.scan_attendance,        name="scan_attendance"),
    path("my-attendance/",              views.my_attendance,          name="my_attendance"),
    path("section-overview/",           views.section_attendance_overview, name="section_attendance_overview"),
]
