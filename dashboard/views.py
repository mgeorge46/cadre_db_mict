from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
import json

from employees.models import Employee
from core.models import Ministry, Agency, GovernmentDepartment, District, CadreCategory
from inquiries.models import Inquiry
from announcements.models import Announcement, AnnouncementRead
from schemes.models import Scheme


@login_required
def dashboard_index(request):
    today = timezone.now()
    today_date = today.date()
    first_of_month = today.replace(day=1, hour=0, minute=0, second=0)

    # Stats cards
    total_employees = Employee.objects.filter(is_active=True).count()
    total_entities = (
        Ministry.objects.filter(is_active=True).count() +
        Agency.objects.filter(is_active=True).count() +
        GovernmentDepartment.objects.filter(is_active=True).count() +
        District.objects.filter(is_active=True).count()
    )
    complete_profiles = Employee.objects.filter(is_active=True, profile_completion__gte=80).count()
    inquiries_this_month = Inquiry.objects.filter(created_at__gte=first_of_month).count()
    closed_inquiries_this_month = Inquiry.objects.filter(
        closed_at__gte=first_of_month, status='closed'
    ).count()
    # Only count non-expired published announcements this month
    active_ann_qs = Announcement.objects.filter(
        is_published=True,
        created_at__gte=first_of_month
    ).filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=today_date))
    announcements_this_month = active_ann_qs.count()
    announcement_reads_month = AnnouncementRead.objects.filter(read_at__gte=first_of_month).count()

    # Charts data
    # Employees by entity type
    entity_data = {}
    for et_code, et_label in [('ministry', 'Ministries'), ('agency', 'Agencies'),
                               ('department', 'Departments'), ('local_govt', 'Local Gov.')]:
        entity_data[et_label] = Employee.objects.filter(entity_type=et_code, is_active=True).count()

    # Employees by cadre category
    cadre_data = list(
        Employee.objects.filter(is_active=True)
        .values('cadre_category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # Profile completion distribution
    completion_ranges = [
        ('0-20%', Employee.objects.filter(is_active=True, profile_completion__lt=20).count()),
        ('20-40%', Employee.objects.filter(is_active=True, profile_completion__gte=20, profile_completion__lt=40).count()),
        ('40-60%', Employee.objects.filter(is_active=True, profile_completion__gte=40, profile_completion__lt=60).count()),
        ('60-80%', Employee.objects.filter(is_active=True, profile_completion__gte=60, profile_completion__lt=80).count()),
        ('80-100%', Employee.objects.filter(is_active=True, profile_completion__gte=80).count()),
    ]

    # Recent inquiries
    recent_inquiries = Inquiry.objects.select_related('submitted_by__user').order_by('-created_at')[:5]
    # Recent announcements
    recent_announcements = Announcement.objects.filter(is_published=True).order_by('-published_at')[:5]

    # Open inquiries by status
    inquiry_status_data = list(
        Inquiry.objects.values('status').annotate(count=Count('id'))
    )

    context = {
        'page_title': 'Dashboard',
        'total_employees': total_employees,
        'total_entities': total_entities,
        'complete_profiles': complete_profiles,
        'inquiries_this_month': inquiries_this_month,
        'closed_inquiries_this_month': closed_inquiries_this_month,
        'announcements_this_month': announcements_this_month,
        'announcement_reads_month': announcement_reads_month,
        'entity_chart_labels': json.dumps(list(entity_data.keys())),
        'entity_chart_data': json.dumps(list(entity_data.values())),
        'cadre_chart_labels': json.dumps([d['cadre_category__name'] or 'Unassigned' for d in cadre_data]),
        'cadre_chart_data': json.dumps([d['count'] for d in cadre_data]),
        'completion_labels': json.dumps([r[0] for r in completion_ranges]),
        'completion_data': json.dumps([r[1] for r in completion_ranges]),
        'recent_inquiries': recent_inquiries,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def global_search(request):
    q = request.GET.get('q', '').strip()
    employees = []
    inquiries = []
    schemes = []

    if q:
        from django.db.models import Q
        employees = Employee.objects.select_related(
            'user', 'cadre_category', 'position', 'job_rank', 'ministry', 'agency',
            'government_department', 'district'
        ).filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(employee_number__icontains=q) |
            Q(user__email__icontains=q) |
            Q(phone_primary__icontains=q) |
            Q(national_id__icontains=q),
            is_active=True
        )[:50]

        inquiries = Inquiry.objects.select_related('submitted_by__user', 'assigned_to').filter(
            Q(title__icontains=q) |
            Q(reference_number__icontains=q) |
            Q(description__icontains=q) |
            Q(category__icontains=q)
        )[:50]

        schemes = Scheme.objects.filter(
            Q(title__icontains=q) |
            Q(reference_number__icontains=q) |
            Q(content__icontains=q)
        )[:50]

    return render(request, 'dashboard/search_results.html', {
        'q': q,
        'employees': employees,
        'inquiries': inquiries,
        'schemes': schemes,
        'page_title': f'Search Results for "{q}"' if q else 'Search',
        'breadcrumbs': [('Dashboard', 'dashboard:index'), ('Search', None)],
    })
