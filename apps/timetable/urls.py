from django.urls import path
from . import views

urlpatterns = [
    path("",             views.my_timetable,     name="my_timetable"),
    path("manage/",      views.manage_timetable, name="manage_timetable"),
    path("calendar/",    views.academic_calendar, name="academic_calendar"),
]
