from django.urls import path
from .views import get_programs, get_courses, get_classes, get_sections

urlpatterns = [
    path("get-programs/",  get_programs,  name="get_programs"),
    path("get-courses/",   get_courses,   name="get_courses"),
    path("get-classes/",   get_classes,   name="get_classes"),
    path("get-sections/",  get_sections,  name="get_sections"),
]
