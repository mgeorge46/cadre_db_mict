from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Scheme, SchemeView, SchemeSignature
from .forms import SchemeForm


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


@login_required
def scheme_list(request):
    if request.user.is_admin or request.user.is_it_admin or request.user.is_superuser:
        qs = Scheme.objects.all()
    else:
        qs = Scheme.objects.filter(is_published=True)

    per_page = request.GET.get('per_page', '50')
    try:
        per_page = int(per_page)
        if per_page not in (20, 50, 100):
            per_page = 50
    except (ValueError, TypeError):
        per_page = 50

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'schemes/scheme_list.html', {
        'page_obj': page_obj, 'page_title': 'Schemes',
        'breadcrumbs': [('Schemes', None)],
        'per_page': per_page,
    })


@login_required
def scheme_detail(request, pk):
    scheme = get_object_or_404(Scheme, pk=pk)
    if not scheme.is_published and not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, 'This scheme is not yet published.')
        return redirect('schemes:list')

    employee = None
    has_viewed = False
    has_signed = False
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        sv, created = SchemeView.objects.get_or_create(scheme=scheme, employee=employee)
        has_viewed = True
        has_signed = SchemeSignature.objects.filter(scheme=scheme, employee=employee).exists()

    if request.method == 'POST' and 'sign' in request.POST:
        if employee and not has_signed:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            SchemeSignature.objects.create(scheme=scheme, employee=employee, ip_address=ip)
            messages.success(request, 'You have signed this scheme.')
            return redirect('schemes:detail', pk=pk)

    context = {
        'scheme': scheme, 'employee': employee, 'has_viewed': has_viewed,
        'has_signed': has_signed, 'page_title': scheme.title,
        'breadcrumbs': [('Schemes', 'schemes:list'), (scheme.title, None)],
    }
    if request.user.is_admin or request.user.is_it_admin or request.user.is_superuser:
        context['scheme_views'] = scheme.views.select_related('employee__user').all()
        context['scheme_signatures'] = scheme.signatures.select_related('employee__user').all()
    return render(request, 'schemes/scheme_detail.html', context)


@admin_required
def scheme_create(request):
    form = SchemeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        scheme = form.save(commit=False)
        scheme.created_by = request.user
        if scheme.is_published and not scheme.published_at:
            scheme.published_at = timezone.now()
        scheme.save()
        messages.success(request, 'Scheme created successfully.')
        return redirect('schemes:detail', pk=scheme.pk)
    return render(request, 'schemes/scheme_form.html', {
        'form': form, 'page_title': 'Create Scheme', 'action': 'Create',
        'breadcrumbs': [('Schemes', 'schemes:list'), ('Create', None)]
    })


@admin_required
def scheme_edit(request, pk):
    scheme = get_object_or_404(Scheme, pk=pk)
    form = SchemeForm(request.POST or None, request.FILES or None, instance=scheme)
    if request.method == 'POST' and form.is_valid():
        s = form.save(commit=False)
        if s.is_published and not s.published_at:
            s.published_at = timezone.now()
        s.save()
        messages.success(request, 'Scheme updated.')
        return redirect('schemes:detail', pk=scheme.pk)
    return render(request, 'schemes/scheme_form.html', {
        'form': form, 'scheme': scheme, 'page_title': 'Edit Scheme', 'action': 'Update',
        'breadcrumbs': [('Schemes', 'schemes:list'), (scheme.title, 'schemes:detail'), ('Edit', None)]
    })


@admin_required
def scheme_delete(request, pk):
    scheme = get_object_or_404(Scheme, pk=pk)
    if request.method == 'POST':
        scheme.delete()
        messages.success(request, 'Scheme deleted.')
    return redirect('schemes:list')
