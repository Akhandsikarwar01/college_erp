"""
API URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api import views

# Create router for viewsets
router = DefaultRouter()

# Account & Profile endpoints
router.register(r'students', views.StudentProfileViewSet, basename='student')
router.register(r'teachers', views.TeacherViewSet, basename='teacher')

# Attendance endpoints
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

# Leave endpoints
router.register(r'leaves', views.LeaveApplicationViewSet, basename='leave')

# Academic endpoints
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'semesters', views.SemesterViewSet, basename='semester')
router.register(r'courses', views.CourseViewSet, basename='course')

# Timetable endpoints
router.register(r'time-slots', views.TimeSlotViewSet, basename='time-slot')
router.register(r'timetable', views.TimetableViewSet, basename='timetable')

# Fee endpoints
router.register(r'fee-types', views.FeeTypeViewSet, basename='fee-type')
router.register(r'fee-structures', views.FeeStructureViewSet, basename='fee-structure')
router.register(r'student-fees', views.StudentFeeViewSet, basename='student-fee')
router.register(r'payments', views.PaymentViewSet, basename='payment')

# Examination endpoints
router.register(r'exams', views.ExamViewSet, basename='exam')
router.register(r'exam-schedules', views.ExamScheduleViewSet, basename='exam-schedule')
router.register(r'results', views.StudentResultViewSet, basename='result')

# Faculty endpoints
router.register(r'teacher-assignments', views.TeacherAssignmentViewSet, basename='teacher-assignment')

# Notice endpoints
router.register(r'notices', views.NoticeViewSet, basename='notice')
router.register(r'events', views.EventViewSet, basename='event')

app_name = 'api'

urlpatterns = [
    # API info
    path('', views.api_info, name='info'),
    
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Dashboard
    path('dashboard/', views.dashboard_api, name='dashboard'),
    
    # Router endpoints
    path('', include(router.urls)),
]
