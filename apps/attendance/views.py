from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
import csv

from .models import AttendanceSession, AttendanceRecord
from apps.faculty.models import TeacherAssignment
from apps.accounts.models import Role


# ======================================================
# CREATE ATTENDANCE SESSION
# ======================================================

@login_required
def create_session(request):

    if request.user.role != Role.TEACHER:
        return redirect("dashboard")

    if not hasattr(request.user, "teacher_profile"):
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard")

    assignments = TeacherAssignment.objects.filter(
        teacher=request.user.teacher_profile
    )

    if request.method == "POST":

        assignment_id = request.POST.get("assignment")
        date = request.POST.get("date")

        if not assignment_id or not date:
            messages.error(request, "All fields are required.")
            return redirect("create_session")

        try:
            AttendanceSession.objects.create(
                teacher_assignment_id=assignment_id,
                date=date
            )
            messages.success(request, "Attendance session created successfully.")

        except IntegrityError:
            messages.error(request, "Session already exists for this date.")

        return redirect("dashboard")

    return render(
        request,
        "attendance/create_session.html",
        {"assignments": assignments},
    )


# ======================================================
# MARK ATTENDANCE
# ======================================================

@login_required
def mark_attendance(request, session_id):

    if request.user.role != Role.TEACHER:
        return redirect("dashboard")

    session = get_object_or_404(AttendanceSession, id=session_id)

    if session.teacher_assignment.teacher != request.user.teacher_profile:
        messages.error(request, "Unauthorized access.")
        return redirect("dashboard")

    if session.is_locked:
        messages.error(request, "Attendance is locked.")
        return redirect("dashboard")

    records = session.records.select_related("student__user")

    if request.method == "POST":

        for record in records:
            record.is_present = f"student_{record.id}" in request.POST
            record.save()

        messages.success(request, "Attendance updated successfully.")
        return redirect("dashboard")

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "session": session,
            "records": records,
        },
    )


# ======================================================
# LOCK ATTENDANCE SESSION
# ======================================================

@login_required
def lock_session(request, session_id):

    if request.user.role != Role.TEACHER:
        return redirect("dashboard")

    session = get_object_or_404(AttendanceSession, id=session_id)

    if session.teacher_assignment.teacher != request.user.teacher_profile:
        messages.error(request, "Unauthorized action.")
        return redirect("dashboard")

    if session.is_locked:
        messages.info(request, "Session already locked.")
        return redirect("dashboard")

    session.is_locked = True
    session.save()

    messages.success(request, "Attendance locked successfully.")
    return redirect("dashboard")


# ======================================================
# EXPORT ATTENDANCE CSV
# ======================================================

@login_required
def export_attendance_csv(request, session_id):

    if request.user.role != Role.TEACHER:
        return redirect("dashboard")

    session = get_object_or_404(AttendanceSession, id=session_id)

    if session.teacher_assignment.teacher != request.user.teacher_profile:
        messages.error(request, "Unauthorized access.")
        return redirect("dashboard")

    records = session.records.select_related("student__user")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="attendance_{session.date}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Roll Number", "Name", "Status"])

    for record in records:
        writer.writerow([
            record.student.roll_number,
            f"{record.student.user.first_name} {record.student.user.last_name}",
            "Present" if record.is_present else "Absent",
        ])

    return response