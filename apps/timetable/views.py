"""
Timetable views — weekly schedule for students/teachers, management for ERP manager.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.academics.models import Section
from apps.faculty.models import TeacherAssignment

from .models import TimeSlot, TimetableEntry, AcademicCalendar, DAY_CHOICES


# ──────────────────────────────────────────────────────────────────────────────
# STUDENT / TEACHER TIMETABLE VIEW
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def my_timetable(request):
    user = request.user
    entries = TimetableEntry.objects.none()
    title = "My Timetable"

    if user.is_student and hasattr(user, "student_profile"):
        section = user.student_profile.section
        entries = TimetableEntry.objects.filter(
            section=section
        ).select_related(
            "time_slot", "teacher_assignment__subject",
            "teacher_assignment__teacher__user"
        )
        title = f"Timetable — {section.name}"

    elif user.is_teacher and hasattr(user, "teacher_profile"):
        entries = TimetableEntry.objects.filter(
            teacher_assignment__teacher=user.teacher_profile
        ).select_related(
            "time_slot", "section__class_obj__course",
            "teacher_assignment__subject"
        )
        title = "My Teaching Schedule"

    elif user.is_erp_manager:
        entries = TimetableEntry.objects.all().select_related(
            "time_slot", "section__class_obj__course",
            "teacher_assignment__subject",
            "teacher_assignment__teacher__user"
        )
        title = "All Timetables"

    # Build grid: rows = time slots, columns = days
    slots = TimeSlot.objects.all().order_by("slot_number")
    days = DAY_CHOICES

    grid = []
    for slot in slots:
        row = {"slot": slot, "cells": []}
        for day_num, day_name in days:
            entry = entries.filter(day=day_num, time_slot=slot).first()
            row["cells"].append({
                "day": day_name,
                "day_num": day_num,
                "entry": entry,
            })
        grid.append(row)

    return render(request, "timetable/timetable_grid.html", {
        "title": title,
        "grid": grid,
        "days": days,
        "slots": slots,
    })


# ──────────────────────────────────────────────────────────────────────────────
# MANAGE TIMETABLE (ERP Manager)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def manage_timetable(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        day = request.POST.get("day")
        slot_id = request.POST.get("time_slot")
        section_id = request.POST.get("section")
        assignment_id = request.POST.get("teacher_assignment")

        if not all([day, slot_id, section_id, assignment_id]):
            messages.error(request, "All fields are required.")
        else:
            try:
                TimetableEntry.objects.update_or_create(
                    day=day,
                    time_slot_id=slot_id,
                    section_id=section_id,
                    defaults={"teacher_assignment_id": assignment_id},
                )
                messages.success(request, "Timetable entry saved.")
                return redirect("manage_timetable")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    slots = TimeSlot.objects.filter(is_break=False).order_by("slot_number")
    sections = Section.objects.select_related("class_obj__course").all()
    assignments = TeacherAssignment.objects.select_related(
        "teacher__user", "subject", "section"
    ).all()

    return render(request, "timetable/manage_timetable.html", {
        "days": DAY_CHOICES,
        "slots": slots,
        "sections": sections,
        "assignments": assignments,
    })


# ──────────────────────────────────────────────────────────────────────────────
# ACADEMIC CALENDAR
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def academic_calendar(request):
    events = AcademicCalendar.objects.all().order_by("date")

    if request.user.is_erp_manager and request.method == "POST":
        title = request.POST.get("title", "").strip()
        date = request.POST.get("date")
        end_date = request.POST.get("end_date") or None
        cal_type = request.POST.get("calendar_type", "HOLIDAY")
        desc = request.POST.get("description", "").strip()

        if title and date:
            AcademicCalendar.objects.create(
                title=title, date=date, end_date=end_date,
                calendar_type=cal_type, description=desc,
            )
            messages.success(request, f"'{title}' added to calendar.")
            return redirect("academic_calendar")
        else:
            messages.error(request, "Title and date are required.")

    return render(request, "timetable/academic_calendar.html", {
        "events": events,
    })
