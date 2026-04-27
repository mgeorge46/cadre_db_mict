from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Inquiry, InquiryResponse, InquiryAttachment, InquiryCategory
from .forms import InquiryForm, InquiryResponseForm, InquiryCategoryForm


@login_required
def inquiry_list(request):
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if is_admin:
        qs = Inquiry.objects.select_related('submitted_by__user', 'assigned_to').all()
        # Admin filters
        status_f = request.GET.get('status', '')
        priority_f = request.GET.get('priority', '')
        if status_f:
            qs = qs.filter(status=status_f)
        if priority_f:
            qs = qs.filter(priority=priority_f)
    else:
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'You do not have an employee profile.')
            return redirect('dashboard:index')
        qs = Inquiry.objects.filter(submitted_by=request.user.employee_profile)

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(reference_number__icontains=search))

    per_page = request.GET.get('per_page', '50')
    try:
        per_page = int(per_page)
        if per_page not in (20, 50, 100):
            per_page = 50
    except (ValueError, TypeError):
        per_page = 50

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inquiries/inquiry_list.html', {
        'page_obj': page_obj, 'is_admin': is_admin, 'page_title': 'Inquiries',
        'breadcrumbs': [('Inquiries', None)],
        'status_choices': Inquiry._meta.get_field('status').choices,
        'priority_choices': Inquiry._meta.get_field('priority').choices,
        'current_status': request.GET.get('status', ''),
        'current_priority': request.GET.get('priority', ''),
        'search': search,
        'per_page': per_page,
    })


@login_required
def inquiry_detail(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    # Permission check
    if not is_admin:
        if not hasattr(request.user, 'employee_profile') or inquiry.submitted_by != request.user.employee_profile:
            messages.error(request, 'Access denied.')
            return redirect('inquiries:list')

    response_form = InquiryResponseForm(request.POST or None)
    if request.method == 'POST' and 'respond' in request.POST:
        if response_form.is_valid():
            resp = response_form.save(commit=False)
            resp.inquiry = inquiry
            resp.responded_by = request.user
            if not is_admin:
                resp.is_internal = False
            resp.save()
            messages.success(request, 'Response added.')
            return redirect('inquiries:detail', pk=pk)

    if request.method == 'POST' and 'update_status' in request.POST and is_admin:
        new_status = request.POST.get('status')
        if new_status in dict(Inquiry._meta.get_field('status').choices):
            inquiry.status = new_status
            if new_status == 'resolved':
                inquiry.resolved_at = timezone.now()
            elif new_status == 'closed':
                inquiry.closed_at = timezone.now()
            inquiry.save()
            messages.success(request, f'Status updated to {inquiry.get_status_display()}.')
            return redirect('inquiries:detail', pk=pk)

    if request.method == 'POST' and 'assign' in request.POST and is_admin:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        assignee_id = request.POST.get('assignee')
        try:
            assignee = User.objects.get(pk=assignee_id)
            inquiry.assigned_to = assignee
            inquiry.save()
            messages.success(request, f'Assigned to {assignee.get_full_name()}.')
        except User.DoesNotExist:
            pass
        return redirect('inquiries:detail', pk=pk)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    responses = inquiry.responses.all()
    if not is_admin:
        responses = responses.filter(is_internal=False)

    return render(request, 'inquiries/inquiry_detail.html', {
        'inquiry': inquiry, 'response_form': response_form, 'is_admin': is_admin,
        'responses': responses, 'page_title': f'Inquiry: {inquiry.reference_number}',
        'breadcrumbs': [('Inquiries', 'inquiries:list'), (inquiry.reference_number, None)],
        'status_choices': Inquiry._meta.get_field('status').choices,
        'admin_users': User.objects.filter(Q(is_admin=True) | Q(is_it_admin=True) | Q(is_superuser=True)) if is_admin else [],
    })


@login_required
def inquiry_create(request):
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    employee = getattr(request.user, 'employee_profile', None)
    if not employee and not is_admin:
        messages.error(request, 'You need an employee profile to submit inquiries. Please contact your administrator.')
        return redirect('dashboard:index')

    form = InquiryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        inq = form.save(commit=False)
        if employee:
            inq.submitted_by = employee
        else:
            # Admin without employee profile: find or create a placeholder
            # Try to find any employee, otherwise redirect with helpful message
            from employees.models import Employee as EmpModel
            first_emp = EmpModel.objects.first()
            if not first_emp:
                messages.error(request, 'No employee profiles exist yet. Please create an employee profile first.')
                return redirect('employees:create')
            inq.submitted_by = first_emp
            messages.warning(request, 'Inquiry submitted. Note: Create your employee profile to submit inquiries under your name.')
        inq.save()
        messages.success(request, f'Inquiry submitted. Reference: {inq.reference_number}')
        return redirect('inquiries:detail', pk=inq.pk)
    return render(request, 'inquiries/inquiry_form.html', {
        'form': form, 'page_title': 'Submit Inquiry',
        'breadcrumbs': [('Inquiries', 'inquiries:list'), ('Submit New', None)]
    })


# ── Inquiry Category Management (admin only) ─────────────────────────────────
def _is_admin(request):
    return request.user.is_authenticated and (
        request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    )


@login_required
def category_list(request):
    if not _is_admin(request):
        messages.error(request, 'Access denied.')
        return redirect('inquiries:list')
    categories = InquiryCategory.objects.all()
    form = InquiryCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category added.')
        return redirect('inquiries:category_list')
    return render(request, 'inquiries/category_list.html', {
        'categories': categories, 'form': form,
        'page_title': 'Inquiry Categories',
        'breadcrumbs': [('Inquiries', 'inquiries:list'), ('Categories', None)],
    })


@login_required
def category_delete(request, pk):
    if not _is_admin(request):
        messages.error(request, 'Access denied.')
        return redirect('inquiries:list')
    cat = get_object_or_404(InquiryCategory, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
    return redirect('inquiries:category_list')
