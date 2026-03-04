"""
DRF Serializers for API endpoints
"""
from rest_framework import serializers
from apps.accounts.models import CustomUser, StudentProfile, TeacherProfile, DeanProfile
from apps.academics.models import Section, Department, Program, Course, Class, Subject, Semester
from apps.attendance.models import AttendanceRecord, AttendanceSession
from apps.leave.models import LeaveApplication
from apps.fees.models import FeeStructure, FeeType, StudentFee, Payment
from apps.timetable.models import TimeSlot, TimetableEntry
from apps.faculty.models import TeacherAssignment
from apps.examinations.models import Exam, ExamSchedule, StudentResult
from apps.notices.models import Notice, Event


class UserSerializer(serializers.ModelSerializer):
    """Basic user information"""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'role', 'role_display', 'mobile_number'
        ]
        read_only_fields = ['id', 'username']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class SectionSerializer(serializers.ModelSerializer):
    """Section details"""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    course_name = serializers.CharField(source='class_obj.course.name', read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'class_name', 'course_name']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Complete student profile with personal and academic details"""
    user = UserSerializer(read_only=True)
    section_details = SectionSerializer(source='section', read_only=True)
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'user', 'section', 'section_details', 'roll_number',
            'admission_number', 'application_number', 'enrollment_number',
            'date_of_birth', 'gender', 'blood_group',
            'father_name', 'mother_name', 'guardian_phone',
            'address_line_1', 'address_line_2', 'city', 'state', 'pincode',
            'department_name'
        ]
    
    def get_department_name(self, obj):
        if obj.section and obj.section.class_obj and obj.section.class_obj.course:
            if hasattr(obj.section.class_obj.course, 'program'):
                if hasattr(obj.section.class_obj.course.program, 'department'):
                    return obj.section.class_obj.course.program.department.name
        return None


class AttendanceSessionSerializer(serializers.ModelSerializer):
    """Attendance session info — via teacher assignment"""
    subject_name = serializers.CharField(source='teacher_assignment.subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    subject = serializers.IntegerField(source='teacher_assignment.subject.id', read_only=True)
    
    class Meta:
        model = AttendanceSession
        fields = ['id', 'date', 'subject', 'subject_name', 'teacher_name']
    
    def get_teacher_name(self, obj):
        if obj.teacher_assignment and obj.teacher_assignment.teacher:
            return obj.teacher_assignment.teacher.user.get_full_name()
        return None


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Student attendance record"""
    session_details = AttendanceSessionSerializer(source='session', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'session', 'session_details', 'student', 'is_present', 'status_display', 'marked_at']
    
    def get_status_display(self, obj):
        return "Present" if obj.is_present else "Absent"


class StudentAttendanceSummarySerializer(serializers.Serializer):
    """Attendance statistics summary"""
    total_sessions = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    percentage = serializers.FloatField()


class LeaveApplicationSerializer(serializers.ModelSerializer):
    """Leave application details"""
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'applicant', 'applicant_name', 
            'leave_type', 'leave_type_name', 'start_date', 'end_date', 'days',
            'reason', 'status', 'status_display', 'reviewed_by', 'reviewer_name',
            'review_remarks', 'reviewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'applicant']
    
    def get_reviewer_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None
    
    def get_days(self, obj):
        return obj.days


class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    """Create leave application (student/parent use)"""
    days = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'days']
    
    def get_days(self, obj):
        return obj.days
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data
