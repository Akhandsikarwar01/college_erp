"""
Academics AJAX endpoints — cascading dropdowns for forms.
All endpoints require login to prevent data leakage.
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Program, Course, Class, Section


def _json_qs(qs):
    return JsonResponse(list(qs), safe=False)


@login_required
def get_programs(request):
    dept_id = request.GET.get("department_id")
    if not dept_id:
        return JsonResponse([], safe=False)
    qs = Program.objects.filter(department_id=dept_id).values("id", "name").order_by("name")
    return _json_qs(qs)


@login_required
def get_courses(request):
    prog_id = request.GET.get("program_id")
    if not prog_id:
        return JsonResponse([], safe=False)
    qs = Course.objects.filter(program_id=prog_id).values("id", "name").order_by("name")
    return _json_qs(qs)


@login_required
def get_classes(request):
    course_id = request.GET.get("course_id")
    if not course_id:
        return JsonResponse([], safe=False)
    qs = Class.objects.filter(course_id=course_id).values("id", "name").order_by("name")
    return _json_qs(qs)


@login_required
def get_sections(request):
    class_id = request.GET.get("class_id")
    if not class_id:
        return JsonResponse([], safe=False)
    qs = Section.objects.filter(class_obj_id=class_id).values("id", "name").order_by("name")
    return _json_qs(qs)
