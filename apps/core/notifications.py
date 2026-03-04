"""
Email notification system for parent portal
Sends automated alerts for fees, attendance, and leave applications
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from apps.accounts.models import ParentProfile, StudentProfile
from apps.attendance.models import AttendanceRecord
from apps.fees.models import StudentFee
from apps.leave.models import LeaveApplication


class ParentNotificationService:
    """Service to send notifications to parents"""

    @staticmethod
    def send_fee_reminder(student_profile):
        """Send fee payment reminder to parent"""
        try:
            parent_profile = ParentProfile.objects.get(students=student_profile)
            pending_fees = StudentFee.objects.filter(
                student=student_profile, status='pending'
            )
            
            if not pending_fees.exists():
                return False

            total_pending = sum(f.pending_amount for f in pending_fees)
            
            portal_url = getattr(settings, "PARENT_PORTAL_URL", None) or f"{getattr(settings, 'BASE_URL', '')}/parent/"
            context = {
                'parent_name': parent_profile.user.first_name,
                'student_name': student_profile.user.full_name,
                'total_pending': total_pending,
                'fees': pending_fees,
                'school_name': 'College ERP',
                'portal_url': portal_url,
            }
            
            html_message = render_to_string(
                'emails/fee_reminder.html',
                context
            )
            text_message = strip_tags(html_message)
            
            send_mail(
                subject=f'Fee Payment Reminder - {student_profile.user.full_name}',
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent_profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except ParentProfile.DoesNotExist:
            return False

    @staticmethod
    def send_attendance_alert(student_profile, threshold=75):
        """Send alert if attendance drops below threshold"""
        try:
            parent_profile = ParentProfile.objects.get(students=student_profile)
            
            # Calculate attendance percentage
            total_classes = AttendanceRecord.objects.filter(
                student=student_profile
            ).count()
            
            if total_classes == 0:
                return False
            
            present_classes = AttendanceRecord.objects.filter(
                student=student_profile,
                status='present'
            ).count()
            
            attendance_pct = (present_classes / total_classes) * 100
            
            if attendance_pct >= threshold:
                return False  # Attendance is good
            
            portal_url = getattr(settings, "PARENT_PORTAL_URL", None) or f"{getattr(settings, 'BASE_URL', '')}/parent/"
            context = {
                'parent_name': parent_profile.user.first_name,
                'student_name': student_profile.user.full_name,
                'attendance_pct': round(attendance_pct, 2),
                'threshold': threshold,
                'present': present_classes,
                'total': total_classes,
                'portal_url': portal_url,
            }
            
            html_message = render_to_string(
                'emails/attendance_alert.html',
                context
            )
            text_message = strip_tags(html_message)
            
            send_mail(
                subject=f'Attendance Alert - {student_profile.user.full_name}',
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent_profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except ParentProfile.DoesNotExist:
            return False

    @staticmethod
    def send_leave_status_update(leave_application):
        """Notify parent when leave is approved/rejected"""
        try:
            student = leave_application.student
            parent_profile = ParentProfile.objects.get(students=student)
            
            portal_url = getattr(settings, "PARENT_PORTAL_URL", None) or f"{getattr(settings, 'BASE_URL', '')}/parent/"
            context = {
                'parent_name': parent_profile.user.first_name,
                'student_name': student.user.full_name,
                'leave_type': leave_application.leave_type.name,
                'status': leave_application.status,
                'start_date': leave_application.start_date,
                'end_date': leave_application.end_date,
                'remarks': leave_application.remarks or 'N/A',
                'portal_url': portal_url,
            }
            
            html_message = render_to_string(
                'emails/leave_status_update.html',
                context
            )
            text_message = strip_tags(html_message)
            
            send_mail(
                subject=f'Leave Application {leave_application.status.upper()} - {student.user.full_name}',
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent_profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except ParentProfile.DoesNotExist:
            return False

    @staticmethod
    def send_batch_notifications():
        """Send all pending notifications (designed for scheduled task)"""
        results = {
            'fee_reminders': 0,
            'attendance_alerts': 0,
        }
        
        # Send fee reminders for pending fees
        pending_fee_students = StudentFee.objects.filter(
            status='pending'
        ).values_list('student', flat=True).distinct()
        
        for student_id in pending_fee_students:
            student = StudentProfile.objects.get(id=student_id)
            if ParentNotificationService.send_fee_reminder(student):
                results['fee_reminders'] += 1
        
        # Send attendance alerts
        for student in StudentProfile.objects.all():
            if ParentNotificationService.send_attendance_alert(student):
                results['attendance_alerts'] += 1
        
        return results
