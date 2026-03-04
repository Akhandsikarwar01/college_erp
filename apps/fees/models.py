"""
Fees & Finance models.

FeeType → FeeStructure (per course/semester)
StudentFee → Payment
"""

import uuid
from django.db import models
from apps.core.models import TimeStampedModel
from apps.academics.models import Course, Semester
from apps.accounts.models import StudentProfile


class FeeType(TimeStampedModel):
    """Tuition, Lab, Library, Exam, Hostel, etc."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FeeStructure(TimeStampedModel):
    """Amount for a fee type per course/semester."""
    fee_type = models.ForeignKey(
        FeeType, on_delete=models.CASCADE, related_name="structures"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="fee_structures"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="fee_structures"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("fee_type", "course", "semester")
        ordering = ["course", "semester__number", "fee_type"]

    def __str__(self):
        return f"{self.fee_type.name} — {self.course.name} Sem {self.semester.number}: ₹{self.amount}"


class StudentFee(TimeStampedModel):
    """Generated fee for a student for a semester."""
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="fees"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="student_fees"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "semester")
        ordering = ["-created_at"]

    @property
    def balance(self):
        return self.total_amount - self.paid_amount

    @property
    def status(self):
        if self.is_paid:
            return "Paid"
        if self.paid_amount > 0:
            return "Partial"
        return "Unpaid"

    def __str__(self):
        return f"{self.student.user.full_name} – Sem {self.semester.number}: ₹{self.total_amount}"


PAYMENT_METHODS = [
    ("CASH", "Cash"),
    ("ONLINE", "Online Transfer"),
    ("UPI", "UPI"),
    ("CHEQUE", "Cheque"),
    ("DD", "Demand Draft"),
]


class Payment(TimeStampedModel):
    """Individual payment record."""
    student_fee = models.ForeignKey(
        StudentFee, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="CASH")
    receipt_number = models.CharField(
        max_length=50, unique=True, blank=True
    )
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-payment_date"]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        # Update parent StudentFee
        fee = self.student_fee
        fee.paid_amount = sum(
            p.amount for p in fee.payments.all()
        )
        fee.is_paid = fee.paid_amount >= fee.total_amount
        fee.save(update_fields=["paid_amount", "is_paid"])

    def __str__(self):
        return f"{self.receipt_number} — ₹{self.amount}"
