from django.urls import path
from . import views

urlpatterns = [
    path("",                       views.book_catalog,  name="book_catalog"),
    path("add/",                   views.add_book,      name="add_book"),
    path("issue/",                 views.issue_book,    name="issue_book"),
    path("issued/",                views.issued_books,  name="issued_books"),
    path("<int:issue_id>/return/", views.return_book,   name="return_book"),
    path("my-books/",             views.my_books,      name="my_books"),
]
