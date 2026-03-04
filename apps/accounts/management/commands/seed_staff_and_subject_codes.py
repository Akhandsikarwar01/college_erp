from __future__ import annotations

import random
from typing import Tuple

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academics.models import Department, Subject
from apps.accounts.models import CustomUser, DeanProfile, Role, TeacherProfile


FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan", "Shaurya",
    "Ananya", "Diya", "Saanvi", "Aadhya", "Myra", "Aarohi", "Anika", "Ira", "Kavya", "Riya",
    "Rahul", "Amit", "Vikram", "Suresh", "Rohit", "Nikhil", "Karan", "Manish", "Deepak", "Anil",
    "Pooja", "Neha", "Priya", "Sneha", "Shreya", "Nisha", "Aisha", "Meera", "Swati", "Ishita",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Yadav", "Mishra", "Joshi", "Mehta",
    "Agarwal", "Jain", "Nair", "Iyer", "Reddy", "Chauhan", "Saxena", "Bansal", "Pandey", "Tiwari",
    "Kulkarni", "Pillai", "Kapoor", "Bhatia", "Chatterjee", "Mukherjee", "Sinha", "Tripathi", "Thakur", "Dubey",
]


class Command(BaseCommand):
    help = "Assign subject codes, create one dean per department, and create department-wise teachers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--teachers",
            type=int,
            default=1000,
            help="Target total number of teachers in system (default: 1000)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="Teacher@123",
            help="Default password for created dean/teacher users",
        )
        parser.add_argument(
            "--force-subject-codes",
            action="store_true",
            help="Regenerate codes for all subjects (default: only fill missing/invalid)",
        )

    def _unique_user_fields(self, base_username: str, email_prefix: str, mobile_seed: int) -> Tuple[str, str, str]:
        username = base_username
        suffix = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        email = f"{email_prefix}@collegeerp.local"
        email_suffix = 1
        while CustomUser.objects.filter(email=email).exists():
            email = f"{email_prefix}{email_suffix}@collegeerp.local"
            email_suffix += 1

        mobile = str(7000000000 + mobile_seed)[-10:]
        while CustomUser.objects.filter(mobile_number=mobile).exists():
            mobile_seed += 1
            mobile = str(7000000000 + mobile_seed)[-10:]

        return username, email, mobile

    def _subject_code_for(self, subject: Subject, sequence: int) -> str:
        dept_code = subject.semester.course.program.department.code.upper().replace(" ", "")[:6]
        sem = subject.semester.number
        base = f"{dept_code}{sem:02d}{sequence:03d}"
        return base[:20]

    def handle(self, *args, **options):
        target_teachers = max(0, int(options["teachers"]))
        default_password = options["password"]
        force_subject_codes = options["force_subject_codes"]

        rng = random.Random(2026)

        with transaction.atomic():
            self.stdout.write(self.style.HTTP_INFO("Assigning subject codes..."))
            subjects = Subject.objects.select_related(
                "semester__course__program__department"
            ).order_by(
                "semester__course__program__department__code",
                "semester__course__name",
                "semester__number",
                "id",
            )

            updated_codes = 0
            used_codes = set(Subject.objects.exclude(code="").values_list("code", flat=True))
            for idx, subject in enumerate(subjects, start=1):
                must_update = force_subject_codes or not subject.code
                if not must_update:
                    continue

                sequence = idx
                code = self._subject_code_for(subject, sequence)
                while code in used_codes or Subject.objects.exclude(pk=subject.pk).filter(code=code).exists():
                    sequence += 1
                    code = self._subject_code_for(subject, sequence)

                subject.code = code
                subject.save(update_fields=["code"])
                used_codes.add(code)
                updated_codes += 1

            self.stdout.write(self.style.SUCCESS(f"Subject codes updated: {updated_codes}"))

            self.stdout.write(self.style.HTTP_INFO("Creating deans (one per department)..."))
            departments = list(Department.objects.order_by("code"))
            deans_created = 0
            for dept_idx, department in enumerate(departments, start=1):
                if DeanProfile.objects.filter(department=department).exists():
                    continue

                first_name = FIRST_NAMES[dept_idx % len(FIRST_NAMES)]
                last_name = LAST_NAMES[(dept_idx * 3) % len(LAST_NAMES)]

                username, email, mobile = self._unique_user_fields(
                    base_username=f"dean_{department.code.lower()}",
                    email_prefix=f"dean.{department.code.lower()}",
                    mobile_seed=dept_idx,
                )

                dean_user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=default_password,
                    first_name=first_name,
                    last_name=last_name,
                    mobile_number=mobile,
                    role=Role.DEAN,
                    is_approved=True,
                    is_verified=True,
                )

                DeanProfile.objects.create(
                    user=dean_user,
                    department=department,
                    employee_id=f"D{department.code[:4].upper()}{dept_idx:03d}"[:20],
                )
                deans_created += 1

            self.stdout.write(self.style.SUCCESS(f"Deans created: {deans_created}"))

            self.stdout.write(self.style.HTTP_INFO("Creating department-wise teachers..."))
            current_teachers = TeacherProfile.objects.count()
            to_create = max(0, target_teachers - current_teachers)

            teachers_created = 0
            for index in range(1, to_create + 1):
                department = departments[(current_teachers + index - 1) % len(departments)]
                first_name = rng.choice(FIRST_NAMES)
                last_name = rng.choice(LAST_NAMES)

                username, email, mobile = self._unique_user_fields(
                    base_username=f"t_{department.code.lower()}_{current_teachers + index:04d}",
                    email_prefix=f"teacher.{department.code.lower()}.{current_teachers + index:04d}",
                    mobile_seed=100000 + current_teachers + index,
                )

                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=default_password,
                    first_name=first_name,
                    last_name=last_name,
                    mobile_number=mobile,
                    role=Role.TEACHER,
                    is_approved=True,
                    is_verified=True,
                )

                TeacherProfile.objects.create(
                    user=user,
                    employee_id=f"T{2026}{current_teachers + index:04d}"[:20],
                    department=department,
                )
                teachers_created += 1

            self.stdout.write(self.style.SUCCESS(f"Teachers created: {teachers_created}"))
            self.stdout.write(self.style.SUCCESS(f"Total teachers now: {TeacherProfile.objects.count()}"))
            self.stdout.write(self.style.SUCCESS("Done ✅"))
