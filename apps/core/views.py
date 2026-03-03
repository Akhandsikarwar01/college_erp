from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from apps.accounts.models import Role, CustomUser
from apps.attendance.models import AttendanceSession, AttendanceRecord


# ======================================================
# HOME
# ======================================================

def home(request):
    return render(request, "core/home.html")


# ======================================================
# DASHBOARD
# ======================================================

@login_required
def dashboard(request):

    user = request.user

    # =====================================================
    # STUDENT DASHBOARD
    # =====================================================
    if user.role == Role.STUDENT:

        if not hasattr(user, "student_profile"):
            return render(request, "dashboard/default.html")

        records = AttendanceRecord.objects.filter(
            student=user.student_profile
        ).select_related(
            "session__teacher_assignment__course"
        )

        # -------- Overall Attendance --------
        total_classes = records.count()
        present_classes = records.filter(is_present=True).count()

        overall_percentage = 0
        if total_classes > 0:
            overall_percentage = round(
                (present_classes / total_classes) * 100, 2
            )

        low_attendance = overall_percentage < 75

        # -------- Subject-wise Attendance --------
        subject_stats = records.values(
            "session__teacher_assignment__course__name"
        ).annotate(
            total=Count("id"),
            present=Count("id", filter=Q(is_present=True))
        ).order_by(
            "session__teacher_assignment__course__name"
        )

        subject_attendance = []

        for s in subject_stats:
            percentage = 0
            if s["total"] > 0:
                percentage = round(
                    (s["present"] / s["total"]) * 100, 2
                )

            subject_attendance.append({
                "subject": s["session__teacher_assignment__course__name"],
                "total": s["total"],
                "present": s["present"],
                "percentage": percentage,
                "is_low": percentage < 75
            })

        return render(
            request,
            "dashboard/student_dashboard.html",
            {
                "total_classes": total_classes,
                "present_classes": present_classes,
                "overall_percentage": overall_percentage,
                "low_attendance": low_attendance,
                "subject_attendance": subject_attendance,
            },
        )

    # =====================================================
    # TEACHER DASHBOARD
    # =====================================================
    elif user.role == Role.TEACHER:

        if not hasattr(user, "teacher_profile"):
            return render(request, "dashboard/default.html")

        sessions = AttendanceSession.objects.filter(
            teacher_assignment__teacher=user.teacher_profile
        ).select_related(
            "teacher_assignment__course",
            "teacher_assignment__section"
        ).order_by("-date")

        session_data = []

        for session in sessions:
            records = session.records.all()

            total = records.count()
            present = records.filter(is_present=True).count()
            absent = total - present

            percentage = 0
            if total > 0:
                percentage = round((present / total) * 100, 2)

            session_data.append({
                "session": session,
                "total": total,
                "present": present,
                "absent": absent,
                "percentage": percentage
            })

        total_students = AttendanceRecord.objects.filter(
            session__teacher_assignment__teacher=user.teacher_profile
        ).values("student").distinct().count()

        return render(
            request,
            "dashboard/teacher_dashboard.html",
            {
                "session_data": session_data,
                "total_sessions": sessions.count(),
                "total_students": total_students,
            },
        )

    # =====================================================
    # ERP MANAGER DASHBOARD
    # =====================================================
    elif user.role == Role.ERP_MANAGER or user.is_superuser:
        
        total_sessions = AttendanceSession.objects.count()

        total_students = CustomUser.objects.filter(
            role=Role.STUDENT,
            is_approved=True
        ).count()

        total_teachers = CustomUser.objects.filter(
            role=Role.TEACHER,
            is_approved=True
        ).count()

        pending_students = CustomUser.objects.filter(
            role=Role.STUDENT,
            is_approved=False
        ).count()

        pending_teachers = CustomUser.objects.filter(
            role=Role.TEACHER,
            is_approved=False
        ).count()

        return render(
            request,
            "dashboard/erp_dashboard.html",
            {
                "total_sessions": total_sessions,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "pending_students": pending_students,
                "pending_teachers": pending_teachers,
            },
        )

    # =====================================================
    # FALLBACK
    # =====================================================
    return render(request, "dashboard/default.html")