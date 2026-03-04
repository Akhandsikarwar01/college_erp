"""
Examinations views — Exam management, result entry, student results view.
"""

import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import StudentProfile, Role
from apps.academics.models import Course, Semester, Subject, Section

from .models import ExamType, Exam, ExamSchedule, StudentResult, GradeScale


# ──────────────────────────────────────────────────────────────────────────────
# EXAM LIST
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def exam_list(request):
    """List exams — all roles see published exams, ERP manager sees all."""
    user = request.user

    if user.is_erp_manager:
        exams = Exam.objects.all()
    elif user.is_teacher:
        exams = Exam.objects.all()
    else:
        exams = Exam.objects.filter(is_published=True)

    exams = exams.select_related(
        "exam_type", "course__program__department", "semester"
    ).order_by("-start_date")

    return render(request, "examinations/exam_list.html", {
        "exams": exams,
    })


# ──────────────────────────────────────────────────────────────────────────────
# CREATE EXAM (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def create_exam(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("exam_list")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        exam_type_id = request.POST.get("exam_type")
        course_id = request.POST.get("course")
        semester_id = request.POST.get("semester")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not all([name, exam_type_id, course_id, semester_id, start_date, end_date]):
            messages.error(request, "All fields are required.")
        else:
            try:
                exam = Exam.objects.create(
                    name=name,
                    exam_type_id=exam_type_id,
                    course_id=course_id,
                    semester_id=semester_id,
                    start_date=start_date,
                    end_date=end_date,
                )
                messages.success(request, f"Exam '{exam.name}' created successfully.")
                return redirect("exam_detail", exam_id=exam.pk)
            except Exception as e:
                messages.error(request, f"Error creating exam: {e}")

    exam_types = ExamType.objects.all()
    courses = Course.objects.select_related("program__department").all()
    semesters = Semester.objects.select_related("course").all()

    return render(request, "examinations/create_exam.html", {
        "exam_types": exam_types,
        "courses": courses,
        "semesters": semesters,
    })


# ──────────────────────────────────────────────────────────────────────────────
# EXAM DETAIL + SCHEDULE
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(
        Exam.objects.select_related("exam_type", "course", "semester"),
        pk=exam_id,
    )
    schedules = exam.schedules.select_related("subject").order_by("date", "start_time")
    return render(request, "examinations/exam_detail.html", {
        "exam": exam,
        "schedules": schedules,
    })


# ──────────────────────────────────────────────────────────────────────────────
# ADD EXAM SCHEDULE (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def add_schedule(request, exam_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("exam_list")

    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == "POST":
        subject_id = request.POST.get("subject")
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        room = request.POST.get("room", "").strip()
        max_marks = request.POST.get("max_marks", 100)
        passing_marks = request.POST.get("passing_marks", 40)

        if not all([subject_id, date, start_time, end_time]):
            messages.error(request, "Subject, date, and timings are required.")
        else:
            try:
                ExamSchedule.objects.create(
                    exam=exam,
                    subject_id=subject_id,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    room=room,
                    max_marks=max_marks,
                    passing_marks=passing_marks,
                )
                messages.success(request, "Schedule added.")
                return redirect("exam_detail", exam_id=exam.pk)
            except Exception as e:
                messages.error(request, f"Error: {e}")

    subjects = Subject.objects.filter(semester=exam.semester).order_by("name")
    return render(request, "examinations/add_schedule.html", {
        "exam": exam,
        "subjects": subjects,
    })


# ──────────────────────────────────────────────────────────────────────────────
# ENTER RESULTS (Teacher / ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def enter_results(request, schedule_id):
    if not (request.user.is_teacher or request.user.is_erp_manager):
        messages.error(request, "Access denied.")
        return redirect("exam_list")

    schedule = get_object_or_404(
        ExamSchedule.objects.select_related(
            "exam__course", "exam__semester", "subject"
        ),
        pk=schedule_id,
    )

    # Get students in the relevant sections for this course
    sections = Section.objects.filter(
        class_obj__course=schedule.exam.course
    )
    students = StudentProfile.objects.filter(
        section__in=sections
    ).select_related("user").order_by("roll_number")

    if request.method == "POST":
        saved = 0
        for student in students:
            marks = request.POST.get(f"marks_{student.pk}", "").strip()
            absent = request.POST.get(f"absent_{student.pk}") == "on"
            remarks = request.POST.get(f"remarks_{student.pk}", "").strip()

            if absent or marks:
                marks_val = 0 if absent else float(marks)
                StudentResult.objects.update_or_create(
                    exam_schedule=schedule,
                    student=student,
                    defaults={
                        "marks_obtained": marks_val,
                        "is_absent": absent,
                        "remarks": remarks,
                    },
                )
                saved += 1

        messages.success(request, f"Results saved for {saved} students.")
        return redirect("exam_detail", exam_id=schedule.exam.pk)

    # Pre-fill existing results
    existing = {
        r.student_id: r
        for r in StudentResult.objects.filter(exam_schedule=schedule)
    }
    student_data = []
    for s in students:
        result = existing.get(s.pk)
        student_data.append({
            "student": s,
            "marks": result.marks_obtained if result else "",
            "is_absent": result.is_absent if result else False,
            "remarks": result.remarks if result else "",
        })

    return render(request, "examinations/enter_results.html", {
        "schedule": schedule,
        "student_data": student_data,
    })


# ──────────────────────────────────────────────────────────────────────────────
# PUBLISH / UNPUBLISH EXAM (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def toggle_publish(request, exam_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("exam_list")

    exam = get_object_or_404(Exam, pk=exam_id)
    exam.is_published = not exam.is_published
    exam.save(update_fields=["is_published"])
    status = "published" if exam.is_published else "unpublished"
    messages.success(request, f"Exam '{exam.name}' {status}.")
    return redirect("exam_detail", exam_id=exam.pk)


# ──────────────────────────────────────────────────────────────────────────────
# STUDENT RESULTS VIEW
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def my_results(request):
    """Student views their own results across all exams."""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if not hasattr(request.user, "student_profile"):
        messages.error(request, "Student profile not set up.")
        return redirect("dashboard")

    profile = request.user.student_profile
    results = StudentResult.objects.filter(
        student=profile
    ).select_related(
        "exam_schedule__exam__exam_type",
        "exam_schedule__subject",
    ).order_by("-exam_schedule__exam__start_date", "exam_schedule__subject__name")

    # Group by exam
    exam_results = {}
    for r in results:
        exam = r.exam_schedule.exam
        if exam.pk not in exam_results:
            exam_results[exam.pk] = {
                "exam": exam,
                "results": [],
                "total_marks": 0,
                "total_max": 0,
            }
        exam_results[exam.pk]["results"].append(r)
        if not r.is_absent:
            exam_results[exam.pk]["total_marks"] += float(r.marks_obtained)
        exam_results[exam.pk]["total_max"] += r.exam_schedule.max_marks

    for data in exam_results.values():
        if data["total_max"] > 0:
            data["percentage"] = round((data["total_marks"] / data["total_max"]) * 100, 1)
        else:
            data["percentage"] = 0

    return render(request, "examinations/my_results.html", {
        "profile": profile,
        "exam_results": exam_results.values(),
    })


# ──────────────────────────────────────────────────────────────────────────────
# EXPORT RESULTS CSV
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def export_results_csv(request, schedule_id):
    if not (request.user.is_teacher or request.user.is_erp_manager):
        messages.error(request, "Access denied.")
        return redirect("exam_list")

    schedule = get_object_or_404(
        ExamSchedule.objects.select_related("exam", "subject"),
        pk=schedule_id,
    )
    results = schedule.results.select_related("student__user").order_by("student__roll_number")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="results_{schedule.subject.name}_{schedule.exam.name}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Roll Number", "Student Name", "Admission No",
        "Subject", "Max Marks", "Marks Obtained",
        "Percentage", "Grade", "Status", "Remarks"
    ])

    for r in results:
        writer.writerow([
            r.student.roll_number,
            r.student.user.full_name,
            r.student.admission_number,
            schedule.subject.name,
            schedule.max_marks,
            r.marks_obtained,
            r.percentage,
            r.grade,
            "Absent" if r.is_absent else ("Pass" if r.is_pass else "Fail"),
            r.remarks,
        ])

    return response
