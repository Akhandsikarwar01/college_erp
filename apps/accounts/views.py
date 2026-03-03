import csv
from io import TextIOWrapper
import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from apps.accounts.models import CustomUser, StudentProfile, Role, OTP
from apps.academics.models import Department, Section
from apps.faculty.models import TeacherMaster


User = get_user_model()

REQUIRED_HEADERS = {"username", "password", "roll_number"}


# ======================================================
# IMPORT STUDENTS CSV
# ======================================================
@login_required
def import_students_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        section_id = request.POST.get("section")

        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("import_students")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Invalid file type.")
            return redirect("import_students")

        section = Section.objects.filter(id=section_id).first()
        if not section:
            messages.error(request, "Invalid section selected.")
            return redirect("import_students")

        decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.DictReader(decoded_file)

        headers = {h.strip().lower() for h in reader.fieldnames}

        if not REQUIRED_HEADERS.issubset(headers):
            messages.error(
                request,
                "CSV must contain: username, password, roll_number"
            )
            return redirect("import_students")

        created_count = 0

        try:
            with transaction.atomic():
                for row in reader:
                    username = row.get("username", "").strip().lower()
                    password = row.get("password", "").strip()
                    roll = row.get("roll_number", "").strip()

                    if not username or not password or not roll:
                        continue

                    if User.objects.filter(username=username).exists():
                        continue

                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        role=Role.STUDENT,
                        is_verified=True,
                        is_approved=True,
                        is_active=True
                    )

                    StudentProfile.objects.create(
                        user=user,
                        section=section,
                        roll_number=roll
                    )

                    created_count += 1

            messages.success(request, f"{created_count} students imported.")
        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")

        return redirect("import_students")

    departments = Department.objects.all()
    return render(request, "accounts/import_students.html", {"departments": departments})


# ======================================================
# SIGNUP
# ======================================================
def signup_view(request):
    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        role = request.POST.get("role")
        username = request.POST.get("username", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")

        # Duplicate checks
        existing_user = User.objects.filter(mobile_number=mobile).first()

        if existing_user:
            if not existing_user.is_verified:
                existing_user.delete()
            else:
                messages.error(request, "Mobile already registered.")
                return redirect("signup")

        existing_email_user = User.objects.filter(email=email).first()

        if existing_email_user:
            if not existing_email_user.is_verified:
                existing_email_user.delete()
            else:
                messages.error(request, "Email already registered.")
                return redirect("signup")

        # -------------------------
        # TEACHER SIGNUP
        # -------------------------
        if role == Role.TEACHER:

            teacher = TeacherMaster.objects.filter(
                teacher_code=username,
                is_registered=False
            ).first()

            if not teacher:
                messages.error(request, "Invalid or used teacher code.")
                return redirect("signup")

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile,
                email=email,
                role=Role.TEACHER,
                is_active=False,
                is_verified=False,
                is_approved=False
            )

            teacher.is_registered = True
            teacher.save()

        # -------------------------
        # STUDENT SIGNUP
        # -------------------------
        elif role == Role.STUDENT:

            user = User.objects.create_user(
                username=username.lower(),
                password=password,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile,
                email=email,
                role=Role.STUDENT,
                is_active=False,
                is_verified=False,
                is_approved=False
            )

        else:
            messages.error(request, "Invalid role selected.")
            return redirect("signup")

        # -------------------------
        # OTP GENERATION
        # -------------------------
        otp_code = OTP.generate_otp()

        OTP.objects.create(
            user=user,
            code=otp_code
        )

        send_mail(
            "Your ERP OTP",
            f"Your OTP is {otp_code}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        request.session["user_id"] = user.id

        return redirect("verify_otp")

    return render(request, "accounts/signup.html")


# ======================================================
# LOGIN
# ======================================================
def login_view(request):
    if request.method == "POST":

        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password")

        username = None

        # Mobile login
        if identifier.isdigit() and len(identifier) == 10:
            user_obj = User.objects.filter(mobile_number=identifier).first()
            if user_obj:
                username = user_obj.username
        else:
            username = identifier

        if not username:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

        # Skip OTP + approval for superuser
        if not user.is_superuser:

            if not user.is_verified:
                messages.error(request, "Please verify OTP first.")
                return redirect("login")

            if not user.is_approved:
                messages.error(request, "Awaiting ERP approval.")
                return redirect("login")

        login(request, user)
        return redirect("dashboard")

    return render(request, "accounts/login.html")


# ======================================================
# VERIFY OTP
# ======================================================
def verify_otp(request):
    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        user_id = request.session.get("user_id")

        if not user_id:
            messages.error(request, "Session expired.")
            return redirect("signup")

        user = User.objects.get(id=user_id)
        otp_obj = OTP.objects.filter(user=user).last()

        if not otp_obj:
            messages.error(request, "OTP not found.")
            return redirect("signup")

        if otp_obj.is_expired():
            messages.error(request, "OTP expired.")
            return redirect("signup")

        if otp_obj.code == entered_otp:
            user.is_verified = True
            user.is_active = True
            user.save()

            messages.success(request, "Email verified. Wait for approval.")
            return redirect("login")

        messages.error(request, "Invalid OTP.")

    return render(request, "accounts/verify_otp.html")