"""
Library views — book catalog, issue/return, student book history.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, BookCategory, BookIssue


@login_required
def book_catalog(request):
    books = Book.objects.select_related("category").all()

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        books = books.filter(title__icontains=q) | books.filter(author__icontains=q)

    # Category filter
    cat_id = request.GET.get("category")
    if cat_id:
        books = books.filter(category_id=cat_id)

    categories = BookCategory.objects.all()

    return render(request, "library/book_catalog.html", {
        "books": books,
        "categories": categories,
        "search_query": q,
        "selected_category": cat_id,
    })


@login_required
def issue_book(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("book_catalog")

    if request.method == "POST":
        book_id = request.POST.get("book")
        borrower_id = request.POST.get("borrower")
        days = int(request.POST.get("days", 14))

        if not all([book_id, borrower_id]):
            messages.error(request, "Book and borrower are required.")
        else:
            book = get_object_or_404(Book, pk=book_id)
            if not book.is_available:
                messages.error(request, "No copies available.")
            else:
                from apps.accounts.models import CustomUser
                borrower = get_object_or_404(CustomUser, pk=borrower_id)

                issue_date = timezone.now().date()
                BookIssue.objects.create(
                    book=book,
                    borrower=borrower,
                    issue_date=issue_date,
                    due_date=issue_date + timedelta(days=days),
                )
                book.available_copies -= 1
                book.save(update_fields=["available_copies"])
                messages.success(request, f"'{book.title}' issued to {borrower.full_name}.")
                return redirect("book_catalog")

    from apps.accounts.models import CustomUser
    books = Book.objects.filter(available_copies__gt=0).order_by("title")
    users = CustomUser.objects.filter(is_active=True).order_by("username")

    return render(request, "library/issue_book.html", {
        "books": books,
        "users": users,
    })


@login_required
def return_book(request, issue_id):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("book_catalog")

    issue = get_object_or_404(BookIssue.objects.select_related("book"), pk=issue_id)

    if request.method == "POST":
        issue.return_date = timezone.now().date()
        issue.status = "RETURNED"

        # Calculate fine: ₹5 per day overdue
        if issue.return_date > issue.due_date:
            overdue_days = (issue.return_date - issue.due_date).days
            issue.fine_amount = Decimal(overdue_days * 5)

        issue.save()

        # Restore book availability
        issue.book.available_copies += 1
        issue.book.save(update_fields=["available_copies"])

        msg = f"'{issue.book.title}' returned."
        if issue.fine_amount > 0:
            msg += f" Fine: ₹{issue.fine_amount}"
        messages.success(request, msg)

    return redirect("issued_books")


@login_required
def issued_books(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("book_catalog")

    issues = BookIssue.objects.filter(
        status="ISSUED"
    ).select_related("book", "borrower").order_by("-issue_date")

    overdue = [i for i in issues if i.is_overdue]

    return render(request, "library/issued_books.html", {
        "issues": issues,
        "overdue_count": len(overdue),
    })


@login_required
def my_books(request):
    issues = BookIssue.objects.filter(
        borrower=request.user
    ).select_related("book").order_by("-issue_date")

    return render(request, "library/my_books.html", {
        "issues": issues,
    })


@login_required
def add_book(request):
    if not request.user.is_erp_manager:
        messages.error(request, "Access denied.")
        return redirect("book_catalog")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        category_id = request.POST.get("category") or None
        publisher = request.POST.get("publisher", "").strip()
        copies = int(request.POST.get("total_copies", 1))

        if not title or not author:
            messages.error(request, "Title and author are required.")
        else:
            Book.objects.create(
                title=title, author=author, isbn=isbn,
                category_id=category_id, publisher=publisher,
                total_copies=copies, available_copies=copies,
            )
            messages.success(request, f"'{title}' added to library.")
            return redirect("book_catalog")

    categories = BookCategory.objects.all()
    return render(request, "library/add_book.html", {"categories": categories})
