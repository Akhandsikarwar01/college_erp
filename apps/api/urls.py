"""
API URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'students', views.StudentProfileViewSet, basename='student')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'leaves', views.LeaveApplicationViewSet, basename='leave')

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
