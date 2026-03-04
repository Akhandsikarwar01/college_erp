from django.urls import path
from . import views

urlpatterns = [
    path("",                                views.exam_list,         name="exam_list"),
    path("create/",                         views.create_exam,       name="create_exam"),
    path("<int:exam_id>/",                  views.exam_detail,       name="exam_detail"),
    path("<int:exam_id>/schedule/add/",     views.add_schedule,      name="add_exam_schedule"),
    path("<int:exam_id>/toggle-publish/",   views.toggle_publish,    name="toggle_publish_exam"),
    path("schedule/<int:schedule_id>/results/",       views.enter_results,     name="enter_results"),
    path("schedule/<int:schedule_id>/results/export/", views.export_results_csv, name="export_results_csv"),
    path("my-results/",                     views.my_results,        name="my_results"),
]
