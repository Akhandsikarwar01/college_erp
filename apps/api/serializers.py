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


# ============= ACADEMIC SERIALIZERS =============

class DepartmentSerializer(serializers.ModelSerializer):
    """Department information"""
    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'description']


class SubjectSerializer(serializers.ModelSerializer):
    """Subject/Course information"""
    semester_number = serializers.IntegerField(source='semester.number', read_only=True)
    course_name = serializers.CharField(source='semester.course.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'description', 'semester_number', 'course_name']


class SemesterSerializer(serializers.ModelSerializer):
    """Semester information"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Semester
        fields = ['id', 'number', 'course_name', 'subjects']


class CourseSerializer(serializers.ModelSerializer):
    """Course/Program information"""
    program_name = serializers.CharField(source='program.name', read_only=True)
    department_name = serializers.CharField(source='program.department.name', read_only=True)
    semesters = SemesterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'program_name', 'department_name', 'semesters']


class ClassSerializer(serializers.ModelSerializer):
    """Class information"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'course_name', 'course']


# ============= TIMETABLE SERIALIZERS =============

class TimeSlotSerializer(serializers.ModelSerializer):
    """Time period definition"""
    class Meta:
        model = TimeSlot
        fields = ['id', 'slot_number', 'start_time', 'end_time', 'label', 'is_break']


class TimetableEntrySerializer(serializers.ModelSerializer):
    """Single timetable entry"""
    day_name = serializers.SerializerMethodField()
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)
    subject_name = serializers.CharField(source='teacher_assignment.subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher_assignment.teacher.user.full_name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    
    class Meta:
        model = TimetableEntry
        fields = ['id', 'day', 'day_name', 'time_slot_details', 'section_name', 'subject_name', 'teacher_name']
    
    def get_day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return days[obj.day] if obj.day < len(days) else 'Unknown'


# ============= FEE SERIALIZERS =============

class FeeTypeSerializer(serializers.ModelSerializer):
    """Fee type information"""
    class Meta:
        model = FeeType
        fields = ['id', 'name']


class FeeStructureSerializer(serializers.ModelSerializer):
    """Fee structure for a course semester"""
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    semester_number = serializers.IntegerField(source='semester.number', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'fee_type_name', 'course_name', 'semester_number', 'amount']


class StudentFeeSerializer(serializers.ModelSerializer):
    """Student fee record"""
    semester_number = serializers.IntegerField(source='semester.number', read_only=True)
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentFee
        fields = [
            'id', 'semester_number', 'student_name', 'total_amount', 'paid_amount',
            'due_date', 'is_paid', 'status'
        ]
    
    def get_status(self, obj):
        if obj.is_paid:
            return 'Paid'
        elif obj.paid_amount > 0:
            return 'Partial'
        return 'Unpaid'


class PaymentSerializer(serializers.ModelSerializer):
    """Payment record"""
    student_name = serializers.CharField(source='student_fee.student.user.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'student_name', 'amount', 'payment_method', 'transaction_id', 'payment_date']


# ============= EXAMINATION SERIALIZERS =============

class ExamSerializer(serializers.ModelSerializer):
    """Exam information"""
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type_name', 'total_marks', 'description']


class ExamScheduleSerializer(serializers.ModelSerializer):
    """Exam schedule for a subject"""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    
    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'exam_name', 'subject_name', 'subject_code', 
            'exam_date', 'start_time', 'end_time', 'duration_minutes'
        ]


class StudentResultSerializer(serializers.ModelSerializer):
    """Student exam result"""
    exam_name = serializers.CharField(source='exam_schedule.exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam_schedule.subject.name', read_only=True)
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    percentage = serializers.SerializerMethodField()
    grade = serializers.CharField(read_only=True)
    
    class Meta:
        model = StudentResult
        fields = [
            'id', 'exam_name', 'subject_name', 'student_name',
            'marks_obtained', 'percentage', 'grade', 'remarks'
        ]
    
    def get_percentage(self, obj):
        if obj.exam_schedule and obj.exam_schedule.exam:
            total = obj.exam_schedule.exam.total_marks
            return round((obj.marks_obtained / total * 100) if total > 0 else 0, 2)
        return 0


# ============= TEACHER SERIALIZERS =============

class TeacherProfileSerializer(serializers.ModelSerializer):
    """Teacher profile information"""
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'department_name', 'qualification', 'specialization', 'experience_years']


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """Teacher assignment to subject section"""
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    course_name = serializers.CharField(source='section.class_obj.course.name', read_only=True)
    
    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'teacher_name', 'subject_name', 'subject_code',
            'section_name', 'course_name'
        ]


# ============= NOTICE SERIALIZERS =============

class NoticeSerializer(serializers.ModelSerializer):
    """Notice/Announcement"""
    category_name = serializers.CharField(source='category.name', read_only=True) if hasattr(Notice, 'category') else None
    posted_by = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'category_name', 'posted_by', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Event information"""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'end_date', 'venue', 'organizer_name', 'created_at']
