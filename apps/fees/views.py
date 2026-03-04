"""
Fees views — Fee structure setup, student fee status, payment recording.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import StudentProfile
from apps.academics.models import Course, Semester, Section

from .models import FeeType, FeeStructure, StudentFee, Payment


# ──────────────────────────────────────────────────────────────────────────────
# FEE STRUCTURE (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def fee_structure_list(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    structures = FeeStructure.objects.select_related(
        "fee_type", "course__program__department", "semester"
    ).order_by("course", "semester__number")

    return render(request, "fees/fee_structure.html", {
        "structures": structures,
        "fee_types": FeeType.objects.all(),
        "courses": Course.objects.select_related("program__department").all(),
        "semesters": Semester.objects.select_related("course").all(),
    })


@login_required
def add_fee_structure(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        fee_type_id = request.POST.get("fee_type")
        course_id = request.POST.get("course")
        semester_id = request.POST.get("semester")
        amount = request.POST.get("amount")

        if not all([fee_type_id, course_id, semester_id, amount]):
            messages.error(request, "All fields are required.")
        else:
            try:
                FeeStructure.objects.create(
                    fee_type_id=fee_type_id,
                    course_id=course_id,
                    semester_id=semester_id,
                    amount=amount,
                )
                messages.success(request, "Fee structure added.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    return redirect("fee_structure_list")


# ──────────────────────────────────────────────────────────────────────────────
# GENERATE STUDENT FEES (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def generate_fees(request):
    """Generate StudentFee records for all students in a course/semester."""
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        course_id = request.POST.get("course")
        semester_id = request.POST.get("semester")
        due_date = request.POST.get("due_date")

        if not all([course_id, semester_id, due_date]):
            messages.error(request, "All fields are required.")
            return redirect("generate_fees")

        course = get_object_or_404(Course, pk=course_id)
        semester = get_object_or_404(Semester, pk=semester_id)

        # Calculate total from fee structures
        structures = FeeStructure.objects.filter(course=course, semester=semester)
        total = structures.aggregate(total=Sum("amount"))["total"] or 0

        if total == 0:
            messages.error(request, "No fee structure defined for this course/semester.")
            return redirect("generate_fees")

        # Get all students in this course
        sections = Section.objects.filter(class_obj__course=course)
        students = StudentProfile.objects.filter(section__in=sections)

        created = skipped = 0
        for student in students:
            _, was_created = StudentFee.objects.get_or_create(
                student=student,
                semester=semester,
                defaults={"total_amount": total, "due_date": due_date},
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        messages.success(request, f"Fees generated: {created} created, {skipped} already existed.")
        return redirect("fee_collection_report")

    courses = Course.objects.select_related("program__department").all()
    semesters = Semester.objects.select_related("course").all()

    return render(request, "fees/generate_fees.html", {
        "courses": courses,
        "semesters": semesters,
    })


# ──────────────────────────────────────────────────────────────────────────────
# FEE COLLECTION REPORT (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def fee_collection_report(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    fees = StudentFee.objects.select_related(
        "student__user", "semester__course"
    ).order_by("-created_at")

    total_due = fees.aggregate(total=Sum("total_amount"))["total"] or 0
    total_paid = fees.aggregate(total=Sum("paid_amount"))["total"] or 0

    return render(request, "fees/fee_report.html", {
        "fees": fees,
        "total_due": total_due,
        "total_paid": total_paid,
        "total_balance": total_due - total_paid,
    })


# ──────────────────────────────────────────────────────────────────────────────
# RECORD PAYMENT (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def record_payment(request, fee_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    student_fee = get_object_or_404(
        StudentFee.objects.select_related("student__user", "semester"),
        pk=fee_id,
    )

    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("method", "CASH")
        remarks = request.POST.get("remarks", "").strip()

        if not amount:
            messages.error(request, "Amount is required.")
        else:
            try:
                Payment.objects.create(
                    student_fee=student_fee,
                    amount=Decimal(amount),
                    method=method,
                    remarks=remarks,
                )
                messages.success(request, f"Payment of ₹{amount} recorded.")
                return redirect("fee_collection_report")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    return render(request, "fees/record_payment.html", {
        "student_fee": student_fee,
    })


# ──────────────────────────────────────────────────────────────────────────────
# STUDENT FEE STATUS (Student view)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def my_fees(request):
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if not hasattr(request.user, "student_profile"):
        messages.error(request, "Student profile not set up.")
        return redirect("dashboard")

    profile = request.user.student_profile
    fees = StudentFee.objects.filter(
        student=profile
    ).select_related("semester__course").prefetch_related("payments").order_by("-semester__number")

    return render(request, "fees/my_fees.html", {
        "profile": profile,
        "fees": fees,
    })
