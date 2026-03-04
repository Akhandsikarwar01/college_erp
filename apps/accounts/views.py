"""
Account management views: signup (student/teacher), login, OTP, CSV import.
"""

import csv
from io import TextIOWrapper

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
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
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        first_name        = request.POST.get("first_name", "").strip()
        last_name         = request.POST.get("last_name", "").strip()
        role              = request.POST.get("role", "").strip()
        username          = request.POST.get("username", "").strip().lower()
        mobile            = request.POST.get("mobile", "").strip()
        email             = request.POST.get("email", "").strip().lower()
        password          = request.POST.get("password", "")
        # Student-only
        admission_number  = request.POST.get("admission_number", "").strip()
        enrollment_number = request.POST.get("enrollment_number", "").strip()

        # ── Basic validation ──────────────────────────────────────────────────
        base_fields = [first_name, last_name, role, username, mobile, email, password]
        if not all(base_fields):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/signup.html", {"post": request.POST})

        if role == Role.STUDENT and not (admission_number and enrollment_number):
            messages.error(request, "Admission number and enrollment number are required.")
            return render(request, "accounts/signup.html", {"post": request.POST})

        # ── Clean stale unverified accounts ──────────────────────────────────
        User.objects.filter(mobile_number=mobile, is_verified=False).delete()
        User.objects.filter(email=email, is_verified=False).delete()

        if User.objects.filter(mobile_number=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, "accounts/signup.html", {"post": request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "accounts/signup.html", {"post": request.POST})

        # ── Role-specific checks ──────────────────────────────────────────────
        teacher_master = None
        if role == Role.TEACHER:
            teacher_master = TeacherMaster.objects.filter(
                teacher_code=username, is_registered=False
            ).first()
            if not teacher_master:
                messages.error(request, "Invalid or already-used teacher code.")
                return render(request, "accounts/signup.html", {"post": request.POST})

        elif role == Role.STUDENT:
            # Check uniqueness of admission/enrollment numbers
            if StudentProfile.objects.filter(admission_number=admission_number).exists():
                messages.error(request, "Admission number already registered.")
                return render(request, "accounts/signup.html", {"post": request.POST})
            if StudentProfile.objects.filter(enrollment_number=enrollment_number).exists():
                messages.error(request, "Enrollment number already registered.")
                return render(request, "accounts/signup.html", {"post": request.POST})

        else:
            messages.error(request, "Invalid role selected.")
            return render(request, "accounts/signup.html", {"post": request.POST})

        # ── Create user ───────────────────────────────────────────────────────
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    mobile_number=mobile,
                    email=email,
                    role=role,
                    is_active=False,
                    is_verified=False,
                    is_approved=False,
                )

                if role == Role.TEACHER:
                    teacher_master.is_registered = True
                    teacher_master.save()
                    TeacherProfile.objects.create(
                        user=user,
                        employee_id=username,
                    )

                # Student profile is completed after admin assigns a section.
                # We store admission/enrollment numbers on the session for now,
                # and attach them during the admin approval / profile-setup flow.
                if role == Role.STUDENT:
                    # Store in session until admin approves & assigns section
                    request.session["pending_admission"]  = admission_number
                    request.session["pending_enrollment"] = enrollment_number

                otp_code = OTP.generate_otp()
                OTP.objects.create(user=user, code=otp_code)

                send_mail(
                    subject="Your College ERP Verification OTP",
                    message=(
                        f"Hello {first_name},\n\n"
                        f"Your OTP for College ERP is: {otp_code}\n\n"
                        "This OTP expires in 5 minutes.\n\n"
                        "If you did not register, please ignore this email."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

                request.session["pending_user_id"] = user.id
                messages.success(request, "OTP sent to your email.")
                return redirect("verify_otp")

        except Exception as exc:
            messages.error(request, f"Registration failed: {exc}")
            return render(request, "accounts/signup.html", {"post": request.POST})

    return render(request, "accounts/signup.html")


# ──────────────────────────────────────────────────────────────────────────────
# VERIFY OTP
# ──────────────────────────────────────────────────────────────────────────────

def verify_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("signup")

    if request.method == "POST":
        entered = request.POST.get("otp", "").strip()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("signup")

        otp_obj = OTP.objects.filter(user=user).order_by("-created_at").first()

        if not otp_obj:
            messages.error(request, "OTP not found. Please register again.")
            return redirect("signup")

        if otp_obj.is_expired():
            messages.error(request, "OTP expired. Please register again.")
            return redirect("signup")

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
    if not (request.user.is_erp_manager):
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
