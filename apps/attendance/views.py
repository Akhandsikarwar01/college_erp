"""
Attendance views — QR-based system.

Teacher flow:
  1. GET  /attendance/sessions/          → list sessions
  2. POST /attendance/sessions/create/   → create new session
  3. GET  /attendance/sessions/<id>/qr/  → display live QR page
  4. GET  /attendance/api/token/<id>/    → AJAX: return fresh token (JSON)
  5. POST /attendance/sessions/<id>/close/ → close / lock session

Student flow:
  6. GET  /attendance/scan/              → scan landing page
  7. POST /attendance/scan/              → submit QR payload → mark present

Teacher review:
  8. GET  /attendance/sessions/<id>/     → session detail + records
  9. GET  /attendance/sessions/<id>/export/ → CSV export
"""

import json
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from apps.accounts.models import Role, StudentProfile
from apps.faculty.models import TeacherAssignment

from .models import AttendanceSession, AttendanceRecord, current_qr_token


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _teacher_required(request):
    return request.user.is_authenticated and request.user.is_teacher and hasattr(request.user, "teacher_profile")

def _student_required(request):
    return request.user.is_authenticated and request.user.is_student and hasattr(request.user, "student_profile")

def _owns_session(request, session):
    return session.teacher_assignment.teacher == request.user.teacher_profile


# ──────────────────────────────────────────────────────────────────────────────
# 1. SESSION LIST  (teacher dashboard — sessions tab)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def session_list(request):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    sessions = (
        AttendanceSession.objects
        .filter(teacher_assignment__teacher=request.user.teacher_profile)
        .select_related(
            "teacher_assignment__subject",
            "teacher_assignment__section__class_obj__course",
        )
        .prefetch_related("records")
        .order_by("-date", "-created_at")
    )

    session_data = []
    for s in sessions:
        records = s.records.all()
        total   = records.count()
        present = records.filter(is_present=True).count()
        session_data.append({
            "session":    s,
            "total":      total,
            "present":    present,
            "absent":     total - present,
            "percentage": round((present / total) * 100, 1) if total else 0,
        })

    return render(request, "attendance/session_list.html", {
        "session_data": session_data,
    })


# ──────────────────────────────────────────────────────────────────────────────
# 2. CREATE SESSION
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def create_session(request):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    assignments = TeacherAssignment.objects.filter(
        teacher=request.user.teacher_profile
    ).select_related("subject", "section__class_obj__course")

    if request.method == "POST":
        assignment_id = request.POST.get("assignment")
        date          = request.POST.get("date")

        if not assignment_id or not date:
            messages.error(request, "Please fill in all fields.")
            return render(request, "attendance/create_session.html", {"assignments": assignments})

        if not assignments.filter(id=assignment_id).exists():
            messages.error(request, "Invalid assignment selected.")
            return render(request, "attendance/create_session.html", {"assignments": assignments})

        try:
            session = AttendanceSession.objects.create(
                teacher_assignment_id=assignment_id, date=date
            )
            messages.success(request, "Session created. Share the QR with students.")
            return redirect("qr_display", session_id=session.pk)
        except IntegrityError:
            messages.error(request, "A session already exists for this subject on that date.")

    return render(request, "attendance/create_session.html", {"assignments": assignments})


# ──────────────────────────────────────────────────────────────────────────────
# 3. QR DISPLAY PAGE  (teacher projects this on screen)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def qr_display(request, session_id):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    session = get_object_or_404(
        AttendanceSession.objects.select_related(
            "teacher_assignment__subject",
            "teacher_assignment__section__class_obj__course",
        ),
        pk=session_id,
    )

    if not _owns_session(request, session):
        messages.error(request, "You do not own this session.")
        return redirect("dashboard")

    if session.is_locked:
        messages.warning(request, "This session is locked.")
        return redirect("session_detail", session_id=session_id)

    # Pass initial token so page renders immediately
    initial_token = current_qr_token(session.pk)
    initial_payload = json.dumps({"session_id": session.pk, "token": initial_token})

    return render(request, "attendance/qr_display.html", {
        "session":         session,
        "initial_payload": initial_payload,
        "qr_window":       5,   # seconds per token
    })


# ──────────────────────────────────────────────────────────────────────────────
# 4. AJAX: GET FRESH TOKEN  (polled every 5s by teacher QR page)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
@require_GET
def get_qr_token(request, session_id):
    """Return JSON with fresh QR payload. Called by the QR display page via AJAX."""
    if not _teacher_required(request):
        return JsonResponse({"error": "Access denied"}, status=403)

    session = get_object_or_404(AttendanceSession, pk=session_id)

    if not _owns_session(request, session):
        return JsonResponse({"error": "Not your session"}, status=403)

    if session.is_locked or not session.is_active:
        return JsonResponse({"error": "Session closed"}, status=410)

    import time
    token = current_qr_token(session.pk)
    payload = json.dumps({"session_id": session.pk, "token": token})

    # Time remaining until this token expires
    window      = int(time.time() / 5)
    expires_in  = 5 - (int(time.time()) % 5)

    # Live present count
    present_count = session.records.filter(is_present=True).count()

    return JsonResponse({
        "payload":       payload,
        "expires_in":    expires_in,
        "present_count": present_count,
    })


# ──────────────────────────────────────────────────────────────────────────────
# 5. CLOSE / LOCK SESSION  (teacher action)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def close_session(request, session_id):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    session = get_object_or_404(AttendanceSession, pk=session_id)

    if not _owns_session(request, session):
        messages.error(request, "You do not own this session.")
        return redirect("dashboard")

    session.is_active = False
    session.is_locked = True
    session.save(update_fields=["is_active", "is_locked"])
    messages.success(request, "Session closed and locked.")
    return redirect("session_detail", session_id=session_id)


# ──────────────────────────────────────────────────────────────────────────────
# 6 + 7. STUDENT SCAN PAGE + POST HANDLER
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def scan_attendance(request):
    """
    GET  → render the scan page (uses browser camera via jsQR library)
    POST → validate token, record attendance
    """
    if not _student_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        raw = request.POST.get("qr_payload", "").strip()
        if not raw:
            return JsonResponse({"success": False, "message": "No QR data received."}, status=400)

        try:
            data       = json.loads(raw)
            session_id = int(data["session_id"])
            token      = str(data["token"])
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({"success": False, "message": "Invalid QR code format."}, status=400)

        session = AttendanceSession.objects.filter(pk=session_id).first()
        if not session:
            return JsonResponse({"success": False, "message": "Session not found."}, status=404)

        # ── Security checks ────────────────────────────────────────────────
        if not session.is_active or session.is_locked:
            return JsonResponse({"success": False, "message": "This session is no longer active."}, status=410)

        if not session.verify_token(token):
            return JsonResponse({"success": False, "message": "QR code has expired. Please scan the latest QR."}, status=400)

        student = request.user.student_profile

        # ── Section check ──────────────────────────────────────────────────
        if student.section != session.teacher_assignment.section:
            return JsonResponse({
                "success": False,
                "message": "You are not enrolled in this section."
            }, status=403)

        # ── Duplicate check ────────────────────────────────────────────────
        if AttendanceRecord.objects.filter(session=session, student=student).exists():
            return JsonResponse({
                "success": False,
                "message": "Attendance already marked for this session."
            }, status=409)

        # ── Record attendance ──────────────────────────────────────────────
        try:
            AttendanceRecord.objects.create(
                session=session,
                student=student,
                is_present=True,
                marked_at=timezone.now(),
            )
            return JsonResponse({
                "success": True,
                "message": f"✅ Attendance marked! Present for {session.teacher_assignment.subject.name}.",
                "student_name": student.user.full_name,
                "subject":      session.teacher_assignment.subject.name,
                "date":         str(session.date),
                "time":         timezone.localtime(timezone.now()).strftime("%H:%M"),
            })
        except IntegrityError:
            # Race condition: two concurrent requests from same student
            return JsonResponse({
                "success": False,
                "message": "Attendance already marked (concurrent request)."
            }, status=409)

    # GET → render scan page
    return render(request, "attendance/scan.html")


# ──────────────────────────────────────────────────────────────────────────────
# 8. SESSION DETAIL  (teacher view: list of records)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def session_detail(request, session_id):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    session = get_object_or_404(
        AttendanceSession.objects.select_related(
            "teacher_assignment__subject",
            "teacher_assignment__section",
        ),
        pk=session_id,
    )

    if not _owns_session(request, session):
        messages.error(request, "You do not own this session.")
        return redirect("dashboard")

    records = session.records.select_related("student__user").order_by("student__roll_number")
    total   = records.count()
    present = records.filter(is_present=True).count()

    return render(request, "attendance/session_detail.html", {
        "session":    session,
        "records":    records,
        "total":      total,
        "present":    present,
        "absent":     total - present,
        "percentage": round((present / total) * 100, 1) if total else 0,
    })


# ──────────────────────────────────────────────────────────────────────────────
# 9. EXPORT CSV
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def export_attendance_csv(request, session_id):
    if not _teacher_required(request):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    session = get_object_or_404(AttendanceSession, pk=session_id)

    if not _owns_session(request, session):
        messages.error(request, "You do not own this session.")
        return redirect("dashboard")

    records = session.records.select_related("student__user").order_by("student__roll_number")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="attendance_{session.teacher_assignment.subject.name}_{session.date}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Roll Number", "Student Name",
        "Admission No", "Enrollment No",
        "Date", "Time", "Subject",
        "Section", "Teacher", "Status"
    ])

    for rec in records:
        writer.writerow([
            rec.student.roll_number,
            rec.student.user.full_name,
            rec.student.admission_number,
            rec.student.enrollment_number,
            session.date,
            timezone.localtime(rec.marked_at).strftime("%H:%M") if rec.is_present else "—",
            session.teacher_assignment.subject.name,
            session.teacher_assignment.section.name,
            session.teacher_assignment.teacher.user.full_name,
            "Present" if rec.is_present else "Absent",
        ])

    return response
