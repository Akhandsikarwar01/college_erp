from django.urls import path
from . import views

urlpatterns = [
    path("",                        views.notice_list,    name="notice_list"),
    path("create/",                 views.create_notice,  name="create_notice"),
    path("<int:notice_id>/",        views.notice_detail,  name="notice_detail"),
    path("<int:notice_id>/delete/", views.delete_notice,  name="delete_notice"),
    path("events/",                 views.event_list,     name="event_list"),
    path("events/create/",         views.create_event,   name="create_event"),
]
