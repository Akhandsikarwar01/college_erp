from django.http import JsonResponse
from .models import Program, Course, Class, Section


def get_programs(request):
    department_id = request.GET.get("department_id")
    programs = Program.objects.filter(department_id=department_id)
    data = [{"id": p.id, "name": p.name} for p in programs]
    return JsonResponse(data, safe=False)


def get_courses(request):
    program_id = request.GET.get("program_id")
    courses = Course.objects.filter(program_id=program_id)
    data = [{"id": c.id, "name": c.name} for c in courses]
    return JsonResponse(data, safe=False)


def get_classes(request):
    course_id = request.GET.get("course_id")
    classes = Class.objects.filter(course_id=course_id)
    data = [{"id": c.id, "name": c.name} for c in classes]
    return JsonResponse(data, safe=False)


def get_sections(request):
    class_id = request.GET.get("class_id")
    sections = Section.objects.filter(class_obj_id=class_id)
    data = [{"id": s.id, "name": s.name} for s in sections]
    return JsonResponse(data, safe=False)