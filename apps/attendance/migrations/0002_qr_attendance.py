"""
Migration: Replace old AttendanceSession/AttendanceRecord with QR-based models.

Run AFTER creating this file:
  python manage.py migrate attendance

If you have existing attendance data, back up db.sqlite3 first.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0001_initial"),
        ("faculty", "0001_initial"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        # Drop old constraint that may conflict
        migrations.RunSQL(
            "DROP TABLE IF EXISTS attendance_attendancerecord;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS attendance_attendancesession;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.CreateModel(
            name="AttendanceSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date",       models.DateField()),
                ("is_active",  models.BooleanField(default=True)),
                ("is_locked",  models.BooleanField(default=False)),
                ("teacher_assignment", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sessions",
                    to="faculty.teacherassignment",
                )),
            ],
            options={
                "ordering": ["-date", "-created_at"],
            },
        ),

        migrations.AddConstraint(
            model_name="attendancesession",
            constraint=models.UniqueConstraint(
                fields=["teacher_assignment", "date"],
                name="unique_session_per_assignment_per_day",
            ),
        ),

        migrations.AddIndex(
            model_name="attendancesession",
            index=models.Index(fields=["date", "is_active"], name="att_session_date_idx"),
        ),

        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at",  models.DateTimeField(auto_now_add=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
                ("is_present",  models.BooleanField(default=True)),
                ("marked_at",   models.DateTimeField(default=django.utils.timezone.now)),
                ("session", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="records",
                    to="attendance.attendancesession",
                )),
                ("student", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="attendance_records",
                    to="accounts.studentprofile",
                )),
            ],
            options={
                "ordering": ["student__roll_number"],
            },
        ),

        migrations.AddConstraint(
            model_name="attendancerecord",
            constraint=models.UniqueConstraint(
                fields=["session", "student"],
                name="unique_attendance_per_session",
            ),
        ),

        migrations.AddIndex(
            model_name="attendancerecord",
            index=models.Index(fields=["marked_at"], name="att_record_marked_idx"),
        ),
    ]
