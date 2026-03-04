from django.contrib import admin
from .models import BookCategory, Book, BookIssue


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "total_copies", "available_copies")
    list_filter = ("category",)
    search_fields = ("title", "author", "isbn")


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower", "issue_date", "due_date", "return_date", "status", "fine_amount")
    list_filter = ("status",)
    search_fields = ("book__title", "borrower__username")
    date_hierarchy = "issue_date"
