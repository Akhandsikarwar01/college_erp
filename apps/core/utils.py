"""
Utility functions and helpers for the ERP system
"""

from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from functools import wraps
from datetime import datetime, timedelta
import csv
from io import StringIO
from django.http import HttpResponse


# ──────────────────────────────────────────────────────────────────────────────
# PERMISSION DECORATORS
# ──────────────────────────────────────────────────────────────────────────────

def student_required(view_func):
    """Decorator to restrict view to students only"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_student:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def teacher_required(view_func):
    """Decorator to restrict view to teachers only"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_teacher:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def erp_manager_required(view_func):
    """Decorator to restrict view to ERP managers only"""
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_erp_manager:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def ajax_request(view_func):
    """Decorator to handle AJAX requests and return JSON"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        try:
            response = view_func(request, *args, **kwargs)
            if isinstance(response, dict):
                return JsonResponse(response)
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return wrapped_view


# ──────────────────────────────────────────────────────────────────────────────
# EXPORT UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def export_to_csv(queryset, fields, filename):
    """Export queryset to CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow(fields)
    
    # Write data
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field, '')
            if callable(value):
                value = value()
            row.append(value)
        writer.writerow(row)
    
    return response


def list_to_csv_response(data, fields, filename):
    """Convert list of dictionaries to CSV response"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.DictWriter(response, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
    
    return response


# ──────────────────────────────────────────────────────────────────────────────
# VALIDATION UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def validate_phone_number(phone):
    """Validate phone number"""
    if not phone:
        return True
    return bool(__import__('re').match(r'^[0-9]{10}$', phone))


def get_academic_year(date=None):
    """Get academic year from date"""
    if not date:
        date = datetime.now().date()
    year = date.year
    if date.month < 6:  # Before June
        return f"{year - 1}-{year}"
    return f"{year}-{year + 1}"


def get_semester_from_date(date=None):
    """Get semester (odd/even) from date"""
    if not date:
        date = datetime.now().date()
    month = date.month
    if month in [6, 7, 8, 9, 10, 11]:  # June to November
        return "ODD"
    return "EVEN"


# ──────────────────────────────────────────────────────────────────────────────
# PAGINATION UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def paginate_queryset(queryset, page=1, per_page=20):
    """Paginate queryset"""
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page)


# ──────────────────────────────────────────────────────────────────────────────
# SEARCH UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def search_users(query, role=None):
    """Search users by username, email, or full name"""
    from apps.accounts.models import CustomUser
    from django.db.models import Q
    
    queryset = CustomUser.objects.all()
    if role:
        queryset = queryset.filter(role=role)
    
    return queryset.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )


def search_students(query):
    """Search students by admission number, enrollment number, or name"""
    from apps.accounts.models import StudentProfile
    from django.db.models import Q
    
    return StudentProfile.objects.filter(
        Q(user__username__icontains=query) |
        Q(admission_number__icontains=query) |
        Q(enrollment_number__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    )


# ──────────────────────────────────────────────────────────────────────────────
# NOTIFICATION UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def send_email_notification(recipient_email, subject, message, html=False):
    """Send email notification"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        if html:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [recipient_email])
            msg.attach_alternative(message, "text/html")
            msg.send()
        else:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# CALCULATION UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def calculate_gpa(marks_list, max_marks=100):
    """Calculate GPA from marks"""
    if not marks_list:
        return 0
    percentage = (sum(marks_list) / (len(marks_list) * max_marks)) * 100
    
    # Simple GPA calculation (can be customized)
    if percentage >= 90:
        return 4.0
    elif percentage >= 80:
        return 3.5
    elif percentage >= 70:
        return 3.0
    elif percentage >= 60:
        return 2.5
    elif percentage >= 50:
        return 2.0
    return 1.0


def calculate_attendance_percentage(total_classes, present_classes):
    """Calculate attendance percentage"""
    if total_classes == 0:
        return 0
    return round((present_classes / total_classes) * 100, 2)


# ──────────────────────────────────────────────────────────────────────────────
# DATE UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def get_date_range(start_date, end_date):
    """Get all dates in a range"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def get_working_days(start_date, end_date):
    """Get number of working days (excluding weekends)"""
    count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday to Friday
            count += 1
        current += timedelta(days=1)
    return count


def is_business_day(date):
    """Check if date is a business day"""
    return date.weekday() < 5


def get_financial_year(date=None):
    """Get financial year"""
    if not date:
        date = datetime.now().date()
    year = date.year
    if date.month < 4:  # Before April
        return f"{year - 1}-{year}"
    return f"{year}-{year + 1}"
