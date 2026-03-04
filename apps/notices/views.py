"""
Notices & Events views — CRUD for notices, notice board, events.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notice, NoticeCategory, Event


@login_required
def notice_list(request):
    """Notice board — filtered by user's role."""
    user = request.user
    notices = Notice.objects.select_related("category", "posted_by").filter(
        Q(target_role="ALL") | Q(target_role=user.role)
    )
    categories = NoticeCategory.objects.all()

    # Optional category filter
    cat_id = request.GET.get("category")
    if cat_id:
        notices = notices.filter(category_id=cat_id)

    return render(request, "notices/notice_list.html", {
        "notices": notices,
        "categories": categories,
        "selected_category": cat_id,
    })


@login_required
def notice_detail(request, notice_id):
    notice = get_object_or_404(
        Notice.objects.select_related("category", "posted_by"),
        pk=notice_id,
    )
    return render(request, "notices/notice_detail.html", {"notice": notice})


@login_required
def create_notice(request):
    if not (request.user.is_erp_manager or request.user.is_teacher):
        messages.error(request, "Access denied.")
        return redirect("notice_list")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        category_id = request.POST.get("category") or None
        target_role = request.POST.get("target_role", "ALL")
        is_pinned = request.POST.get("is_pinned") == "on"
        attachment = request.FILES.get("attachment")

        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            notice = Notice.objects.create(
                title=title,
                content=content,
                category_id=category_id,
                posted_by=request.user,
                target_role=target_role,
                is_pinned=is_pinned,
            )
            if attachment:
                notice.attachment = attachment
                notice.save()
            messages.success(request, "Notice published.")
            return redirect("notice_list")

    categories = NoticeCategory.objects.all()
    return render(request, "notices/create_notice.html", {"categories": categories})


@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    if not (request.user.is_erp_manager or notice.posted_by == request.user):
        messages.error(request, "Access denied.")
        return redirect("notice_list")

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted.")
    return redirect("notice_list")


# ──────────────────────────────────────────────────────────────────────
# EVENTS
# ──────────────────────────────────────────────────────────────────────

@login_required
def event_list(request):
    events = Event.objects.select_related("organizer").all()
    return render(request, "notices/event_list.html", {"events": events})


@login_required
def create_event(request):
    if not (request.user.is_erp_manager or request.user.is_teacher):
        messages.error(request, "Access denied.")
        return redirect("event_list")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        date = request.POST.get("date")
        end_date = request.POST.get("end_date") or None
        venue = request.POST.get("venue", "").strip()

        if not title or not date:
            messages.error(request, "Title and date are required.")
        else:
            Event.objects.create(
                title=title, description=description,
                date=date, end_date=end_date,
                venue=venue, organizer=request.user,
            )
            messages.success(request, "Event created.")
            return redirect("event_list")

    return render(request, "notices/create_event.html")
