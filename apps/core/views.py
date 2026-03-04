"""
Core views: home, role-dispatched dashboard, and ERP Manager approval workflow.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import CustomUser, Role
from apps.attendance.models import AttendanceRecord, AttendanceSession


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    user = request.user

    if user.is_student:
        if not hasattr(user, "student_profile"):
            return render(request, "dashboard/default.html", {
                "message": "Your student profile is not set up yet. Contact the ERP Manager."
            })

        records = AttendanceRecord.objects.filter(
            student=user.student_profile
        ).select_related("session__teacher_assignment__subject")

        total   = records.count()
        present = records.filter(is_present=True).count()
        overall = round((present / total) * 100, 1) if total else 0

        subject_rows = records.values(
            "session__teacher_assignment__subject__name"
        ).annotate(
            total=Count("id"),
            present=Count("id", filter=Q(is_present=True)),
        ).order_by("session__teacher_assignment__subject__name")

        subject_attendance = []
        for row in subject_rows:
            pct = round((row["present"] / row["total"]) * 100, 1) if row["total"] else 0
            subject_attendance.append({
                "subject":    row["session__teacher_assignment__subject__name"],
                "total":      row["total"],
                "present":    row["present"],
                "absent":     row["total"] - row["present"],
                "percentage": pct,
                "is_low":     pct < 75,
            })

        recent = records.select_related(
            "session__teacher_assignment__subject"
        ).order_by("-session__date", "-marked_at")[:10]

        return render(request, "dashboard/student_dashboard.html", {
            "profile":            user.student_profile,
            "total_classes":      total,
            "present_classes":    present,
            "absent_classes":     total - present,
            "overall_percentage": overall,
            "low_attendance":     overall < 75,
            "subject_attendance": subject_attendance,
            "recent_records":     recent,
        })

    elif user.is_teacher:
        if not hasattr(user, "teacher_profile"):
            return render(request, "dashboard/default.html", {
                "message": "Your teacher profile is not set up yet."
            })

        sessions = (
            AttendanceSession.objects
            .filter(teacher_assignment__teacher=user.teacher_profile)
            .select_related(
                "teacher_assignment__subject",
                "teacher_assignment__section__class_obj__course",
            )
            .prefetch_related("records")
            .order_by("-date", "-created_at")
        )

        session_data = []
        for s in sessions:
            recs    = s.records.all()
            total   = recs.count()
            present = recs.filter(is_present=True).count()
            session_data.append({
                "session":    s,
                "total":      total,
                "present":    present,
                "absent":     total - present,
                "percentage": round((present / total) * 100, 1) if total else 0,
            })

        return render(request, "dashboard/teacher_dashboard.html", {
            "session_data":    session_data,
            "total_sessions":  sessions.count(),
            "total_students":  (
                AttendanceRecord.objects
                .filter(session__teacher_assignment__teacher=user.teacher_profile)
                .values("student").distinct().count()
            ),
            "active_sessions": sessions.filter(is_active=True),
        })

    elif user.is_erp_manager:
        pending_users = CustomUser.objects.filter(
            is_approved=False, is_verified=True
        ).order_by("role", "date_joined")

        return render(request, "dashboard/erp_dashboard.html", {
            "total_sessions": AttendanceSession.objects.count(),
            "total_students": CustomUser.objects.filter(role=Role.STUDENT,  is_approved=True).count(),
            "total_teachers": CustomUser.objects.filter(role=Role.TEACHER,  is_approved=True).count(),
            "pending_count":  pending_users.count(),
            "pending_users":  pending_users,
        })

    return render(request, "dashboard/default.html")


@login_required
def pending_approvals(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    pending = CustomUser.objects.filter(
        is_approved=False, is_verified=True
    ).order_by("role", "date_joined")
    return render(request, "core/pending_approvals.html", {"pending_users": pending})


@login_required
def approve_user(request, user_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if request.method != "POST":
        return redirect("pending_approvals")
    target = get_object_or_404(CustomUser, pk=user_id, is_verified=True)
    target.is_approved = True
    target.is_active   = True
    target.save(update_fields=["is_approved", "is_active"])
    messages.success(request, f"Approved: {target.full_name} ({target.get_role_display()})")
    return redirect(request.POST.get("next", "pending_approvals"))


@login_required
def reject_user(request, user_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if request.method != "POST":
        return redirect("pending_approvals")
    target = get_object_or_404(CustomUser, pk=user_id)
    name = target.full_name
    target.delete()
    messages.success(request, f"Rejected and removed: {name}")
    return redirect(request.POST.get("next", "pending_approvals"))


@login_required
def bulk_approve(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if request.method == "POST":
        ids = request.POST.getlist("user_ids")
        if ids:
            n = CustomUser.objects.filter(
                pk__in=ids, is_verified=True, is_approved=False
            ).update(is_approved=True, is_active=True)
            messages.success(request, f"{n} user(s) approved.")
        else:
            messages.warning(request, "No users selected.")
    return redirect("pending_approvals")
