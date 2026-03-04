from django.contrib import admin
from .models import NoticeCategory, Notice, Event


@admin.register(NoticeCategory)
class NoticeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "posted_by", "target_role", "is_pinned", "created_at")
    list_filter = ("target_role", "is_pinned", "category")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "end_date", "venue", "organizer")
    list_filter = ("date",)
    search_fields = ("title", "venue")
    date_hierarchy = "date"
