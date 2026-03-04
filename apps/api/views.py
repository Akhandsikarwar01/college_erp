"""
API Views for student/parent portal and mobile app
"""
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import StudentProfile, TeacherProfile
from apps.academics.models import Department, Subject, Course, Semester, Section
from apps.attendance.models import AttendanceRecord, AttendanceSession
from apps.leave.models import LeaveApplication
from apps.fees.models import FeeStructure, StudentFee, Payment, FeeType
from apps.timetable.models import TimeSlot, TimetableEntry
from apps.faculty.models import TeacherAssignment
from apps.examinations.models import Exam, ExamSchedule, StudentResult
from apps.notices.models import Notice, Event
from apps.api.serializers import (
    UserSerializer, StudentProfileSerializer, AttendanceRecordSerializer,
    StudentAttendanceSummarySerializer, LeaveApplicationSerializer,
    LeaveApplicationCreateSerializer, AttendanceSessionSerializer,
    DepartmentSerializer, SubjectSerializer, CourseSerializer, ClassSerializer,
    TimeSlotSerializer, TimetableEntrySerializer, FeeTypeSerializer,
    FeeStructureSerializer, StudentFeeSerializer, PaymentSerializer,
    ExamSerializer, ExamScheduleSerializer, StudentResultSerializer,
    TeacherProfileSerializer, TeacherAssignmentSerializer,
    NoticeSerializer, EventSerializer, SemesterSerializer
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
            },
            'academics': {
                'departments': '/api/departments/',
                'subjects': '/api/subjects/',
                'courses': '/api/courses/',
                'semesters': '/api/semesters/',
            },
            'timetable': {
                'time_slots': '/api/time-slots/',
                'entries': '/api/timetable/',
                'my_timetable': '/api/timetable/my-timetable/',
            },
            'fees': {
                'fee_types': '/api/fee-types/',
                'fee_structures': '/api/fee-structures/',
                'student_fees': '/api/student-fees/',
                'student_fees_my': '/api/student-fees/my-fees/',
                'payments': '/api/payments/',
            },
            'examinations': {
                'exams': '/api/exams/',
                'exam_schedules': '/api/exam-schedules/',
                'my_schedules': '/api/exam-schedules/my-schedules/',
                'results': '/api/results/',
                'my_results': '/api/results/my-results/',
            },
            'faculty': {
                'teachers': '/api/teachers/',
                'assignments': '/api/teacher-assignments/',
            },
            'notices': {
                'notices': '/api/notices/',
                'events': '/api/events/',
            }
        }
    })


# ============= ACADEMIC VIEWSETS =============

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Department information - read-only"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """Subject information"""
    queryset = Subject.objects.select_related('semester', 'semester__course').all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_semester(self, request):
        """Get subjects for a specific semester"""
        semester_id = request.query_params.get('semester_id')
        if semester_id:
            subjects = Subject.objects.filter(semester_id=semester_id)
            serializer = self.get_serializer(subjects, many=True)
            return Response(serializer.data)
        return Response({'error': 'semester_id required'}, status=status.HTTP_400_BAD_REQUEST)


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    """Semester information with subjects"""
    queryset = Semester.objects.prefetch_related('subjects').all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Course/Program information"""
    queryset = Course.objects.select_related('program', 'program__department').prefetch_related('semesters', 'semesters__subjects').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get courses for a specific department"""
        dept_id = request.query_params.get('department_id')
        if dept_id:
            courses = Course.objects.filter(program__department_id=dept_id).select_related('program')
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': 'department_id required'}, status=status.HTTP_400_BAD_REQUEST)


# ============= TIMETABLE VIEWSETS =============

class TimeSlotViewSet(viewsets.ReadOnlyModelViewSet):
    """Time period definitions"""
    queryset = TimeSlot.objects.all().order_by('slot_number')
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]


class TimetableViewSet(viewsets.ReadOnlyModelViewSet):
    """Timetable entries"""
    queryset = TimetableEntry.objects.select_related(
        'time_slot', 'section', 'teacher_assignment',
        'teacher_assignment__teacher', 'teacher_assignment__subject'
    ).all()
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_timetable(self, request):
        """Get timetable for student's section"""
        user = request.user
        if not user.is_student:
            return Response(
                {'error': 'Only students can access this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student = StudentProfile.objects.get(user=user)
            entries = TimetableEntry.objects.filter(
                section=student.section
            ).select_related('time_slot', 'teacher_assignment', 'teacher_assignment__subject').order_by('day', 'time_slot__slot_number')
            
            serializer = self.get_serializer(entries, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get timetable for a specific section"""
        section_id = request.query_params.get('section_id')
        if section_id:
            entries = TimetableEntry.objects.filter(section_id=section_id).select_related(
                'time_slot', 'teacher_assignment', 'teacher_assignment__subject'
            ).order_by('day', 'time_slot__slot_number')
            serializer = self.get_serializer(entries, many=True)
            return Response(serializer.data)
        return Response({'error': 'section_id required'}, status=status.HTTP_400_BAD_REQUEST)


# ============= FEE VIEWSETS =============

class FeeTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Fee types"""
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer
    permission_classes = [IsAuthenticated]


class FeeStructureViewSet(viewsets.ReadOnlyModelViewSet):
    """Fee structures"""
    queryset = FeeStructure.objects.select_related('fee_type', 'course', 'semester').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """Get fee structures for a course"""
        course_id = request.query_params.get('course_id')
        if course_id:
            structures = FeeStructure.objects.filter(course_id=course_id).select_related('fee_type', 'semester')
            serializer = self.get_serializer(structures, many=True)
            return Response(serializer.data)
        return Response({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)


class StudentFeeViewSet(viewsets.ReadOnlyModelViewSet):
    """Student fee records"""
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            try:
                student = StudentProfile.objects.get(user=user)
                return StudentFee.objects.filter(
                    student=student
                ).select_related('student', 'semester').order_by('-created_at')
            except StudentProfile.DoesNotExist:
                return StudentFee.objects.none()
        return StudentFee.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_fees(self, request):
        """Get my fee records"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get fee summary"""
        queryset = self.get_queryset()
        total = queryset.aggregate(total=Count('id'), paid=Count('id', filter=Q(is_paid=True)))
        total_amount = sum(sf.total_amount for sf in queryset)
        paid_amount = sum(sf.paid_amount for sf in queryset)
        
        return Response({
            'total_records': total['total'],
            'paid_records': total['paid'],
            'total_liability': str(total_amount),
            'total_paid': str(paid_amount),
            'pending': str(total_amount - paid_amount)
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Payment records"""
    queryset = Payment.objects.select_related('student_fee', 'student_fee__student').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            try:
                student = StudentProfile.objects.get(user=user)
                return Payment.objects.filter(
                    student_fee__student=student
                ).select_related('student_fee').order_by('-payment_date')
            except StudentProfile.DoesNotExist:
                return Payment.objects.none()
        return super().get_queryset()


# ============= EXAMINATION VIEWSETS =============

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """Exam information"""
    queryset = Exam.objects.select_related('exam_type').all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class ExamScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exam schedules"""
    queryset = ExamSchedule.objects.select_related('exam', 'subject').all()
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_schedules(self, request):
        """Get exam schedules for my subjects"""
        user = request.user
        if not user.is_student:
            return Response({'error': 'Only students can access this'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            student = StudentProfile.objects.get(user=user)
            # Get all sections and their subjects
            schedules = ExamSchedule.objects.filter(
                subject__semester__course__classes__sections=student.section
            ).select_related('exam', 'subject').distinct().order_by('exam_date')
            
            serializer = self.get_serializer(schedules, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentResultViewSet(viewsets.ReadOnlyModelViewSet):
    """Student examination results"""
    serializer_class = StudentResultSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            try:
                student = StudentProfile.objects.get(user=user)
                return StudentResult.objects.filter(
                    student=student
                ).select_related('exam_schedule', 'exam_schedule__exam', 'exam_schedule__subject').order_by('-exam_schedule__exam_date')
            except StudentProfile.DoesNotExist:
                return StudentResult.objects.none()
        return StudentResult.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        """Get my exam results"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get results summary"""
        queryset = self.get_queryset()
        results = list(queryset)
        
        if not results:
            return Response({'message': 'No results found'})
        
        total_marks = sum(r.marks_obtained for r in results)
        total_possible = sum(r.exam_schedule.exam.total_marks for r in results if r.exam_schedule and r.exam_schedule.exam)
        avg_percentage = (total_marks / total_possible * 100) if total_possible > 0 else 0
        
        return Response({
            'total_exams': len(results),
            'total_marks': total_marks,
            'average_percentage': round(avg_percentage, 2),
            'results_count': len(results)
        })


# ============= FACULTY VIEWSETS =============

class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    """Teacher information"""
    queryset = TeacherProfile.objects.select_related('user', 'department').all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get teachers for a department"""
        dept_id = request.query_params.get('department_id')
        if dept_id:
            teachers = TeacherProfile.objects.filter(department_id=dept_id).select_related('user')
            serializer = self.get_serializer(teachers, many=True)
            return Response(serializer.data)
        return Response({'error': 'department_id required'}, status=status.HTTP_400_BAD_REQUEST)


class TeacherAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Teacher subject assignments"""
    queryset = TeacherAssignment.objects.select_related(
        'teacher', 'teacher__user', 'subject', 'section'
    ).all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """Get teachers for a subject"""
        subject_id = request.query_params.get('subject_id')
        if subject_id:
            assignments = TeacherAssignment.objects.filter(subject_id=subject_id).select_related(
                'teacher', 'teacher__user', 'section'
            )
            serializer = self.get_serializer(assignments, many=True)
            return Response(serializer.data)
        return Response({'error': 'subject_id required'}, status=status.HTTP_400_BAD_REQUEST)


# ============= NOTICE VIEWSETS =============

class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """Notices and announcements"""
    queryset = Notice.objects.select_related('posted_by').order_by('-created_at')
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Events"""
    queryset = Event.objects.select_related('organizer').order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        from datetime import datetime
        upcoming = Event.objects.filter(
            date__gte=datetime.now().date()
        ).select_related('organizer').order_by('date')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
