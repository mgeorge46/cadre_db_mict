from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import json
from .models import Announcement, AnnouncementRead
from .forms import AnnouncementForm


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_entity_json():
    """Return entity lists as JSON for the announcement form."""
    from core.models import Ministry, Agency, GovernmentDepartment, District
    return {
        'ministries_json': json.dumps(list(Ministry.objects.filter(is_active=True).values('id', 'name'))),
        'agencies_json': json.dumps(list(Agency.objects.filter(is_active=True).values('id', 'name'))),
        'departments_json': json.dumps(list(GovernmentDepartment.objects.filter(is_active=True).values('id', 'name'))),
        'districts_json': json.dumps(list(District.objects.filter(is_active=True).values('id', 'name'))),
    }


@login_required
def announcement_list(request):
    today = timezone.now().date()
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if is_admin:
        qs = Announcement.objects.all()
    else:
        # Employees only see published, non-expired announcements
        qs = Announcement.objects.filter(is_published=True).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gte=today)
        )
    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'announcements/announcement_list.html', {
        'page_obj': page_obj, 'page_title': 'Announcements',
        'breadcrumbs': [('Announcements', None)],
        'is_admin': is_admin,
    })


@login_required
def announcement_detail(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if not ann.is_published and not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, 'This announcement is not yet published.')
        return redirect('announcements:list')

    employee = None
    read_record = None
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        read_record, _ = AnnouncementRead.objects.get_or_create(announcement=ann, employee=employee)

    if request.method == 'POST' and 'acknowledge' in request.POST and employee:
        if read_record and not read_record.acknowledged:
            read_record.acknowledged = True
            read_record.acknowledged_at = timezone.now()
            read_record.save()
            messages.success(request, 'Announcement acknowledged.')
            return redirect('announcements:detail', pk=pk)

    context = {
        'ann': ann, 'employee': employee, 'read_record': read_record,
        'page_title': ann.title,
        'breadcrumbs': [('Announcements', 'announcements:list'), (ann.title, None)]
    }
    if request.user.is_admin or request.user.is_it_admin or request.user.is_superuser:
        context['reads'] = ann.reads.select_related('employee__user').all()
    return render(request, 'announcements/announcement_detail.html', context)


@admin_required
def announcement_create(request):
    from core.models import Position
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann = form.save(commit=False)
        ann.created_by = request.user
        # Capture targeting fields from POST
        ann.target_entity_type = request.POST.get('target_entity_type', '')
        entity_id = request.POST.get('target_entity_id', '')
        if entity_id:
            ann.target_entity_ids = [int(entity_id)]
        position_id = request.POST.get('target_position_id', '')
        if position_id:
            ann.target_position_ids = [int(position_id)]
        if ann.is_published and not ann.published_at:
            ann.published_at = timezone.now()
        ann.save()
        messages.success(request, 'Announcement created successfully.')
        return redirect('announcements:detail', pk=ann.pk)
    ctx = {'form': form, 'page_title': 'Create Announcement', 'action': 'Create',
           'breadcrumbs': [('Announcements', 'announcements:list'), ('Create', None)],
           'positions': Position.objects.filter(is_active=True).select_related('cadre_category')}
    ctx.update(_get_entity_json())
    return render(request, 'announcements/announcement_form.html', ctx)


@admin_required
def announcement_edit(request, pk):
    from core.models import Position
    ann = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=ann)
    if request.method == 'POST' and form.is_valid():
        a = form.save(commit=False)
        a.target_entity_type = request.POST.get('target_entity_type', '')
        entity_id = request.POST.get('target_entity_id', '')
        if entity_id:
            a.target_entity_ids = [int(entity_id)]
        position_id = request.POST.get('target_position_id', '')
        if position_id:
            a.target_position_ids = [int(position_id)]
        if a.is_published and not a.published_at:
            a.published_at = timezone.now()
        a.save()
        messages.success(request, 'Announcement updated.')
        return redirect('announcements:detail', pk=ann.pk)
    ctx = {'form': form, 'ann': ann, 'page_title': 'Edit Announcement', 'action': 'Update',
           'breadcrumbs': [('Announcements', 'announcements:list'), (ann.title, 'announcements:detail'), ('Edit', None)],
           'positions': Position.objects.filter(is_active=True).select_related('cadre_category')}
    ctx.update(_get_entity_json())
    return render(request, 'announcements/announcement_form.html', ctx)


@admin_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('announcements:list')
