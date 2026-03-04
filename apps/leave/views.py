"""
Leave Management views — apply, approve/reject, history.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import Role
from apps.faculty.models import SectionIncharge

from .models import LeaveType, LeaveApplication


def _get_pending_leave_queryset_for_reviewer(user):
    base = LeaveApplication.objects.select_related(
        "applicant", "leave_type", "reviewed_by"
    )

    if user.is_erp_manager:
        return base

    if getattr(user, "is_dean", False) and hasattr(user, "dean_profile"):
        department = user.dean_profile.department
        return base.filter(
            applicant__role=Role.STUDENT,
            applicant__student_profile__section__class_obj__course__program__department=department,
        )

    if user.is_teacher and hasattr(user, "teacher_profile"):
        section_ids = SectionIncharge.objects.filter(
            teacher=user.teacher_profile
        ).values_list("section_id", flat=True)
        return base.filter(
            applicant__role=Role.STUDENT,
            applicant__student_profile__section_id__in=section_ids,
        )

    return base.none()


@login_required
def apply_leave(request):
    if request.user.is_erp_manager:
        messages.error(request, "Managers don't need to apply for leave here.")
        return redirect("dashboard")

    if request.method == "POST":
        leave_type_id = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason", "").strip()

        if not all([leave_type_id, start_date, end_date, reason]):
            messages.error(request, "All fields are required.")
        else:
            LeaveApplication.objects.create(
                applicant=request.user,
                leave_type_id=leave_type_id,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )
            messages.success(request, "Leave application submitted.")
            return redirect("leave_history")

    leave_types = LeaveType.objects.all()
    return render(request, "leave/apply_leave.html", {"leave_types": leave_types})


@login_required
def leave_history(request):
    if request.user.is_erp_manager:
        return redirect("leave_approvals")

    applications = LeaveApplication.objects.filter(
        applicant=request.user
    ).select_related("leave_type", "reviewed_by").order_by("-created_at")

    return render(request, "leave/leave_history.html", {
        "applications": applications,
    })


@login_required
def leave_approvals(request):
    if not (request.user.is_erp_manager or getattr(request.user, "is_dean", False) or request.user.is_teacher):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.user.is_teacher and hasattr(request.user, "teacher_profile"):
        incharge_exists = SectionIncharge.objects.filter(teacher=request.user.teacher_profile).exists()
        if not incharge_exists:
            messages.error(request, "Access denied. You are not assigned as section incharge.")
            return redirect("dashboard")

    applications = _get_pending_leave_queryset_for_reviewer(request.user).order_by("-created_at")

    pending = applications.filter(status="PENDING")
    reviewed = applications.exclude(status="PENDING")

    return render(request, "leave/leave_approvals.html", {
        "pending": pending,
        "reviewed": reviewed,
    })


@login_required
def approve_leave(request, leave_id):
    if not (request.user.is_erp_manager or getattr(request.user, "is_dean", False) or request.user.is_teacher):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        leave = get_object_or_404(_get_pending_leave_queryset_for_reviewer(request.user), pk=leave_id)
        action = request.POST.get("action")
        remarks = request.POST.get("remarks", "").strip()

        if action == "approve":
            leave.status = "APPROVED"
        elif action == "reject":
            leave.status = "REJECTED"

        leave.reviewed_by = request.user
        leave.review_remarks = remarks
        leave.reviewed_at = timezone.now()
        leave.save()
        messages.success(request, f"Leave {leave.status.lower()}.")

    return redirect("leave_approvals")
