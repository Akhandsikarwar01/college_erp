"""
API Views for student/parent portal and mobile app
"""
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import StudentProfile
from apps.attendance.models import AttendanceRecord, AttendanceSession
from apps.leave.models import LeaveApplication
from apps.api.serializers import (
    UserSerializer, StudentProfileSerializer, AttendanceRecordSerializer,
    StudentAttendanceSummarySerializer, LeaveApplicationSerializer,
    LeaveApplicationCreateSerializer, AttendanceSessionSerializer
)
from apps.api.permissions import IsStudentOrParent, IsStudent


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Student profile endpoint - read-only access for students/parents
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsStudentOrParent]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return StudentProfile.objects.filter(user=user).select_related(
                'user', 'section', 'section__class_id', 
                'section__class_id__course', 'section__class_id__course__program'
            )
        # For parents (future): filter by linked students
        return StudentProfile.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's student profile"""
        try:
            profile = StudentProfile.objects.select_related(
                'user', 'section', 'section__class_id',
                'section__class_id__course', 'section__class_id__course__program'
            ).get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Attendance records for students/parents
    """
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsStudentOrParent]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return AttendanceRecord.objects.filter(
                    student=student_profile
                ).select_related('session', 'session__subject', 'session__teacher').order_by('-session__date')
            except StudentProfile.DoesNotExist:
                return AttendanceRecord.objects.none()
        return AttendanceRecord.objects.none()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get attendance summary statistics"""
        user = request.user
        if not user.is_student:
            return Response(
                {'error': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student_profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        records = AttendanceRecord.objects.filter(student=student_profile)
        
        total = records.count()
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        late = records.filter(status='late').count()
        
        percentage = (present / total * 100) if total > 0 else 0.0
        
        data = {
            'total_sessions': total,
            'present_count': present,
            'absent_count': absent,
            'late_count': late,
            'percentage': round(percentage, 2)
        }
        
        serializer = StudentAttendanceSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """Get attendance breakdown by subject"""
        user = request.user
        if not user.is_student:
            return Response(
                {'error': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student_profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Group by subject
        from django.db.models import Count, Case, When, IntegerField
        
        subject_stats = AttendanceRecord.objects.filter(
            student=student_profile
        ).values(
            'session__subject__name'
        ).annotate(
            total=Count('id'),
            present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
            absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
            late=Count(Case(When(status='late', then=1), output_field=IntegerField())),
        )
        
        # Calculate percentage for each subject
        for stat in subject_stats:
            stat['percentage'] = round((stat['present'] / stat['total'] * 100) if stat['total'] > 0 else 0.0, 2)
        
        return Response(subject_stats)


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    """
    Leave applications for students
    - Students can view their own applications and create new ones
    - Read-only for parents (future)
    """
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveApplicationCreateSerializer
        return LeaveApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return LeaveApplication.objects.filter(
                    student=student_profile
                ).select_related(
                    'student', 'student__user', 'leave_type', 'reviewer'
                ).order_by('-created_at')
            except StudentProfile.DoesNotExist:
                return LeaveApplication.objects.none()
        return LeaveApplication.objects.none()
    
    def perform_create(self, serializer):
        student_profile = StudentProfile.objects.get(user=self.request.user)
        serializer.save(student=student_profile, status='pending')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending leave applications"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    """
    Dashboard summary for mobile app/portal
    """
    user = request.user
    
    if not user.is_student:
        return Response(
            {'error': 'Only students can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_profile = StudentProfile.objects.select_related(
            'user', 'section', 'section__class_id'
        ).get(user=user)
    except StudentProfile.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Attendance summary
    attendance_records = AttendanceRecord.objects.filter(student=student_profile)
    total_attendance = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0.0
    
    # Leave applications
    pending_leaves = LeaveApplication.objects.filter(
        student=student_profile, status='pending'
    ).count()
    
    # Recent attendance (last 10 records)
    recent_attendance = AttendanceRecord.objects.filter(
        student=student_profile
    ).select_related('session', 'session__subject').order_by('-session__date')[:10]
    
    data = {
        'student': StudentProfileSerializer(student_profile).data,
        'attendance': {
            'total_sessions': total_attendance,
            'present_count': present_count,
            'percentage': round(attendance_percentage, 2)
        },
        'leaves': {
            'pending_count': pending_leaves
        },
        'recent_attendance': AttendanceRecordSerializer(recent_attendance, many=True).data
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    API information endpoint
    """
    return Response({
        'name': 'College ERP API',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'login': '/api/auth/login/',
                'refresh': '/api/auth/refresh/',
            },
            'student': {
                'profile': '/api/students/me/',
                'attendance': '/api/attendance/',
                'attendance_summary': '/api/attendance/summary/',
                'attendance_by_subject': '/api/attendance/by_subject/',
                'leave_applications': '/api/leaves/',
                'dashboard': '/api/dashboard/',
            }
        }
    })
