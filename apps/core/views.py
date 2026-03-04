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
def student_profile_view(request):
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if not hasattr(request.user, "student_profile"):
        messages.warning(request, "Student profile not found.")
        return redirect("dashboard")
    return render(request, "accounts/student_profile.html", {"profile": request.user.student_profile})


@login_required
def teacher_profile_view(request):
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if not hasattr(request.user, "teacher_profile"):
        messages.warning(request, "Teacher profile not found.")
        return redirect("dashboard")
    return render(request, "accounts/teacher_profile.html", {"profile": request.user.teacher_profile})


@login_required
def user_status(request):
    return render(request, "core/user_status.html", {"user": request.user})


@login_required
def debug_otps(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    return render(request, "core/debug_otps.html")


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


# ──────────────────────────────────────────────────────────────────────────────
# PARENT PORTAL
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def parent_dashboard(request):
    """Parent portal: view all children and their status"""
    from apps.accounts.models import ParentProfile
    from apps.fees.models import StudentFee
    from apps.leave.models import LeaveApplication

    if not hasattr(request.user, "parent_profile"):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    children = parent_profile.students.all().select_related("user")

    children_data = []
    for child in children:
        records = AttendanceRecord.objects.filter(student=child)
        total = records.count()
        present = records.filter(is_present=True).count()
        attendance_pct = (present / total * 100) if total else 0

        pending_fees = StudentFee.objects.filter(student=child, status="pending").count()
        pending_leaves = LeaveApplication.objects.filter(student=child, status="pending").count()

        children_data.append({
            "id": child.id,
            "name": child.user.full_name,
            "attendance_pct": round(attendance_pct, 1),
            "pending_fees": pending_fees,
            "pending_leaves": pending_leaves,
        })

    return render(request, "parent/parent_dashboard.html", {
        "parent": parent_profile,
        "children": children_data,
        "total_children": len(children_data),
    })


@login_required
def parent_child_attendance(request, child_id):
    """View child's attendance records"""
    from apps.accounts.models import StudentProfile, ParentProfile

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    records = AttendanceRecord.objects.filter(student=child_profile).select_related(
        "session__teacher_assignment__subject"
    ).order_by("-session__date")

    total = records.count()
    present = records.filter(is_present=True).count()
    absent = total - present
    percentage = (present / total * 100) if total else 0

    late = records.filter(status="late").count() if hasattr(records.model, "status") else 0

    return render(request, "parent/child_attendance.html", {
        "child": child_profile,
        "child_user": child_profile.user,
        "attendance_records": records[:50],
        "summary": {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": round(percentage, 1),
        },
    })


@login_required
def parent_child_fees(request, child_id):
    """View child's fees"""
    from apps.accounts.models import StudentProfile, ParentProfile
    from apps.fees.models import StudentFee

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    try:
        from apps.fees.models import Payment
    except Exception:
        Payment = None

    fees = StudentFee.objects.filter(student=child_profile).select_related("fee_type")
    payments = Payment.objects.filter(student=child_profile).order_by("-payment_date") if Payment else []

    total_amount = sum(getattr(f, "total_amount", f.amount) for f in fees)
    paid_amount = sum(f.paid_amount for f in fees)
    pending_amount = sum(f.pending_amount for f in fees)
    payment_percentage = round((paid_amount / total_amount) * 100, 1) if total_amount else 0

    return render(request, "parent/child_fees.html", {
        "child": child_profile,
        "child_user": child_profile.user,
        "fees": fees,
        "payments": payments,
        "summary": {
            "total": total_amount,
            "paid": paid_amount,
            "pending": pending_amount,
            "payment_percentage": payment_percentage,
        },
    })


@login_required
def parent_child_leaves(request, child_id):
    """View child's leave applications"""
    from apps.accounts.models import StudentProfile, ParentProfile
    from apps.leave.models import LeaveApplication

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    leaves = LeaveApplication.objects.filter(student=child_profile).order_by("-created_at")

    return render(request, "parent/child_leaves.html", {
        "child": child_profile,
        "child_user": child_profile.user,
        "leaves": leaves,
    })


@login_required
def parent_child_profile(request, child_id):
    """View child's profile details"""
    from apps.accounts.models import StudentProfile, ParentProfile

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    return render(request, "parent/child_profile.html", {
        "child_profile": child_profile,
        "child_user": child_profile.user,
    })


@login_required
def download_attendance_report(request, child_id):
    """Download attendance report as PDF"""
    from django.http import HttpResponse
    from apps.accounts.models import StudentProfile, ParentProfile
    from apps.core.pdf_reports import PDFReportGenerator

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    pdf_buffer = PDFReportGenerator.generate_attendance_report(child_profile)

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="attendance_{child_profile.admission_number}.pdf"'
    return response


@login_required
def download_fee_report(request, child_id):
    """Download fee report as PDF"""
    from django.http import HttpResponse
    from apps.accounts.models import StudentProfile, ParentProfile
    from apps.core.pdf_reports import PDFReportGenerator

    if not hasattr(request.user, "parent_profile"):
        return redirect("dashboard")

    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    child_profile = get_object_or_404(StudentProfile, id=child_id, parents=parent_profile)

    pdf_buffer = PDFReportGenerator.generate_fee_receipt(child_profile)

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="fee_report_{child_profile.admission_number}.pdf"'
    return response
