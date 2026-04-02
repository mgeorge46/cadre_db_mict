from django.utils import timezone
from django.db.models import Q


def notifications(request):
    """Provide notification counts and recent items to all templates."""
    if not request.user.is_authenticated:
        return {}

    today = timezone.now().date()
    # Active (non-expired) published announcements
    active_ann_qs = None
    unread_count = 0
    recent_unread = []

    try:
        from announcements.models import Announcement, AnnouncementRead

        active_ann_qs = Announcement.objects.filter(
            is_published=True
        ).filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=today))

        employee = getattr(request.user, 'employee_profile', None)
        if employee:
            # Announcements not yet read by this employee
            read_ids = AnnouncementRead.objects.filter(
                employee=employee
            ).values_list('announcement_id', flat=True)
            unread_anns = active_ann_qs.exclude(id__in=read_ids).order_by('-created_at')
            unread_count = unread_anns.count()
            recent_unread = list(unread_anns[:5])
        else:
            # Admin without employee profile: show all recent active announcements
            unread_count = active_ann_qs.count()
            recent_unread = list(active_ann_qs.order_by('-created_at')[:5])
    except Exception:
        pass

    return {
        'notification_count': unread_count,
        'recent_notifications': recent_unread,
    }
