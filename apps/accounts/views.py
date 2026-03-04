"""
Account management views: login, OTP verification, and internal account provisioning.
"""

import csv
from io import TextIOWrapper

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import render, redirect

from apps.accounts.models import CustomUser, StudentProfile, TeacherProfile, Role, OTP
from apps.academics.models import Department, Section
from apps.faculty.models import TeacherMaster

User = get_user_model()

REQUIRED_CSV_HEADERS = {"username", "password", "roll_number", "admission_number", "enrollment_number"}


# ──────────────────────────────────────────────────────────────────────────────
# SIGNUP
# ──────────────────────────────────────────────────────────────────────────────

def signup_view(request):
    messages.error(
        request,
        "Public signup is disabled. Student accounts are created by Admission Team and teacher accounts by ERP Manager."
    )
    return redirect("login")


# ──────────────────────────────────────────────────────────────────────────────
# VERIFY OTP
# ──────────────────────────────────────────────────────────────────────────────

def verify_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("login")

    if request.method == "POST":
        entered = request.POST.get("otp", "").strip()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("login")

        otp_obj = OTP.objects.filter(user=user).order_by("-created_at").first()

        if not otp_obj:
            messages.error(request, "OTP not found. Please sign in again.")
            return redirect("login")

        if otp_obj.is_expired():
            messages.error(request, "OTP expired. Please sign in again.")
            return redirect("login")

        if otp_obj.code != entered:
            messages.error(request, "Incorrect OTP. Please try again.")
            return render(request, "accounts/verify_otp.html")

        user.is_verified = True
        user.is_active   = True
        user.save()

        del request.session["pending_user_id"]
        messages.success(request, "Email verified! Your account is pending admin approval.")
        return redirect("login")

    return render(request, "accounts/verify_otp.html")


# ──────────────────────────────────────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password   = request.POST.get("password", "")

        username = identifier
        if identifier.isdigit() and len(identifier) == 10:
            user_obj = User.objects.filter(mobile_number=identifier).first()
            if user_obj:
                username = user_obj.username
            else:
                messages.error(request, "No account with that mobile number.")
                return render(request, "accounts/login.html")

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid credentials.")
            return render(request, "accounts/login.html")

        if not user.is_superuser:
            if not user.is_verified:
                request.session["pending_user_id"] = user.id
                messages.warning(request, "Please verify your email first.")
                return redirect("verify_otp")

            if not user.is_approved:
                messages.warning(
                    request,
                    "Your account is pending approval from the ERP Manager."
                )
                return render(request, "accounts/login.html")

        login(request, user)
        return redirect("dashboard")

    return render(request, "accounts/login.html")


# ──────────────────────────────────────────────────────────────────────────────
# IMPORT STUDENTS CSV  (ERP Manager only)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def import_students_csv(request):
    if not (request.user.is_erp_manager or request.user.is_admission_team):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        csv_file   = request.FILES.get("csv_file")
        section_id = request.POST.get("section")

        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("import_students")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are accepted.")
            return redirect("import_students")

        section = Section.objects.filter(id=section_id).first()
        if not section:
            messages.error(request, "Invalid section selected.")
            return redirect("import_students")

        decoded = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader  = csv.DictReader(decoded)
        headers = {h.strip().lower() for h in (reader.fieldnames or [])}

        if not REQUIRED_CSV_HEADERS.issubset(headers):
            messages.error(
                request,
                f"CSV must contain: {', '.join(REQUIRED_CSV_HEADERS)}"
            )
            return redirect("import_students")

        created = skipped = 0
        try:
            with transaction.atomic():
                for row in reader:
                    uname = row.get("username", "").strip().lower()
                    pwd   = row.get("password", "").strip()
                    roll  = row.get("roll_number", "").strip()
                    adm   = row.get("admission_number", "").strip()
                    enr   = row.get("enrollment_number", "").strip()

                    if not all([uname, pwd, roll, adm, enr]):
                        skipped += 1
                        continue

                    if User.objects.filter(username=uname).exists():
                        skipped += 1
                        continue

                    u = User.objects.create_user(
                        username=uname, password=pwd,
                        role=Role.STUDENT,
                        is_verified=True, is_approved=True, is_active=True,
                    )
                    StudentProfile.objects.create(
                        user=u, section=section,
                        roll_number=roll,
                        admission_number=adm,
                        application_number=f"APP-{adm}",
                        enrollment_number=enr,
                    )
                    created += 1

            messages.success(request, f"Import complete: {created} created, {skipped} skipped.")
        except Exception as exc:
            messages.error(request, f"Import failed: {exc}")

        return redirect("import_students")

    departments = Department.objects.prefetch_related(
        "programs__courses__classes__sections"
    )
    return render(request, "accounts/import_students.html", {"departments": departments})


@login_required
def create_student_account(request):
    if not (request.user.is_erp_manager or request.user.is_admission_team):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        mobile = request.POST.get("mobile", "").strip()
        section_id = request.POST.get("section")
        admission_number = request.POST.get("admission_number", "").strip()
        application_number = request.POST.get("application_number", "").strip()
        enrollment_number = request.POST.get("enrollment_number", "").strip()
        roll_number = request.POST.get("roll_number", "").strip()
        username = request.POST.get("username", "").strip().lower() or admission_number.lower()
        password = request.POST.get("password", "").strip() or f"{admission_number[-6:]}@123"

        father_name = request.POST.get("father_name", "").strip()
        mother_name = request.POST.get("mother_name", "").strip()
        date_of_birth = request.POST.get("date_of_birth") or None
        gender = request.POST.get("gender", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()
        address_line_1 = request.POST.get("address_line_1", "").strip()
        address_line_2 = request.POST.get("address_line_2", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        guardian_phone = request.POST.get("guardian_phone", "").strip()

        if not all([first_name, last_name, email, section_id, admission_number, enrollment_number, roll_number]):
            messages.error(request, "Required fields missing.")
            return redirect("create_student_account")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("create_student_account")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("create_student_account")

        if StudentProfile.objects.filter(admission_number=admission_number).exists():
            messages.error(request, "Admission number already exists.")
            return redirect("create_student_account")

        if StudentProfile.objects.filter(enrollment_number=enrollment_number).exists():
            messages.error(request, "Enrollment number already exists.")
            return redirect("create_student_account")

        section = Section.objects.filter(id=section_id).first()
        if not section:
            messages.error(request, "Invalid section selected.")
            return redirect("create_student_account")

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile_number=mobile,
                role=Role.STUDENT,
                is_verified=True,
                is_approved=True,
                is_active=True,
            )

            StudentProfile.objects.create(
                user=user,
                section=section,
                admission_number=admission_number,
                application_number=application_number or f"APP-{admission_number}",
                enrollment_number=enrollment_number,
                roll_number=roll_number,
                father_name=father_name,
                mother_name=mother_name,
                date_of_birth=date_of_birth,
                gender=gender,
                blood_group=blood_group,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                pincode=pincode,
                guardian_phone=guardian_phone,
            )

        messages.success(request, f"Student account created. Username: {username}, Password: {password}")
        return redirect("create_student_account")

    departments = Department.objects.prefetch_related("programs__courses__classes__sections")
    return render(request, "accounts/create_student_account.html", {"departments": departments})


@login_required
def create_teacher_account(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        mobile = request.POST.get("mobile", "").strip()
        employee_id = request.POST.get("employee_id", "").strip()
        username = request.POST.get("username", "").strip().upper() or employee_id.upper()
        password = request.POST.get("password", "").strip() or "teacher123"

        if not all([first_name, last_name, email, employee_id, username]):
            messages.error(request, "Required fields missing.")
            return redirect("create_teacher_account")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("create_teacher_account")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("create_teacher_account")

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile_number=mobile,
                role=Role.TEACHER,
                is_verified=True,
                is_approved=True,
                is_active=True,
            )
            TeacherProfile.objects.create(user=user, employee_id=employee_id)

        messages.success(request, f"Teacher account created. Username: {username}, Password: {password}")
        return redirect("create_teacher_account")

    return render(request, "accounts/create_teacher_account.html")


@login_required
def create_admission_user(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        mobile = request.POST.get("mobile", "").strip()
        username = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "").strip() or "admission123"

        if not all([first_name, last_name, email, username]):
            messages.error(request, "Required fields missing.")
            return redirect("create_admission_user")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("create_admission_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("create_admission_user")

        User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile,
            role=Role.ADMISSION_TEAM,
            is_verified=True,
            is_approved=True,
            is_active=True,
        )

        messages.success(request, f"Admission Team user created. Username: {username}, Password: {password}")
        return redirect("create_admission_user")

    return render(request, "accounts/create_admission_user.html")
