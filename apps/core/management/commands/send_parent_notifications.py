"""
Django management command to send parent notifications
Usage: python manage.py send_parent_notifications [--type fee|attendance]
"""

from django.core.management.base import BaseCommand
from apps.core.notifications import ParentNotificationService


class Command(BaseCommand):
    help = 'Send automated notifications to parents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'fee', 'attendance'],
            help='Type of notifications to send',
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        
        if notification_type == 'all':
            self.stdout.write(self.style.SUCCESS('📧 Sending all notifications...'))
            results = ParentNotificationService.send_batch_notifications()
            
            self.stdout.write(self.style.SUCCESS(
                f"✅ Fee Reminders Sent: {results['fee_reminders']}"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"✅ Attendance Alerts Sent: {results['attendance_alerts']}"
            ))
        
        self.stdout.write(self.style.SUCCESS('✅ Notification command completed!'))
