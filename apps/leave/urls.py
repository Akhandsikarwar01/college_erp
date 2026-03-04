from django.urls import path
from . import views

urlpatterns = [
    path("apply/",                    views.apply_leave,    name="apply_leave"),
    path("history/",                  views.leave_history,  name="leave_history"),
    path("approvals/",               views.leave_approvals, name="leave_approvals"),
    path("<int:leave_id>/review/",   views.approve_leave,  name="approve_leave"),
]
