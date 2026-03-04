from django.contrib import admin
from .models import FeeType, FeeStructure, StudentFee, Payment


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("fee_type", "course", "semester", "amount")
    list_filter = ("fee_type", "course")
    search_fields = ("fee_type__name", "course__name")


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ("student", "semester", "total_amount", "paid_amount", "balance_display", "is_paid", "due_date")
    list_filter = ("is_paid", "semester")
    search_fields = ("student__user__username", "student__roll_number")
    raw_id_fields = ("student",)

    @admin.display(description="Balance")
    def balance_display(self, obj):
        return f"₹{obj.balance}"


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("receipt_number", "payment_date")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "student_fee", "amount", "method", "payment_date")
    list_filter = ("method", "payment_date")
    search_fields = ("receipt_number",)
    readonly_fields = ("receipt_number",)
