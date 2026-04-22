from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import (Ministry, Agency, GovernmentDepartment, District,
                     EmployeeType, CadreCategory, Position, Role, JobRank, SystemSettings)
# ─────────────────────────────────────────────────────────────────────────────
# UI RENAME NOTE (maintainers):
#   Position  model  → labelled "Speciality" in the UI (url: /core/positions/)
#   JobRank   model  → labelled "Position"   in the UI (url: /core/job-ranks/)
#   JobRank.code     → labelled "Scale"       in the UI
#   Field/model names are unchanged — only page titles and form labels differ.
# ─────────────────────────────────────────────────────────────────────────────
from .forms import (MinistryForm, AgencyForm, GovernmentDepartmentForm, DistrictForm,
                    EmployeeTypeForm, CadreCategoryForm, PositionForm, RoleForm,
                    JobRankForm, SystemSettingsForm)


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_per_page(request, default=50):
    try:
        pp = int(request.GET.get('per_page', default))
        return pp if pp in (20, 50, 100) else default
    except (ValueError, TypeError):
        return default


@login_required
def settings_view(request):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:index')
    settings_obj = SystemSettings.get_settings()
    form = SystemSettingsForm(request.POST or None, instance=settings_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'System settings saved successfully.')
        return redirect('core:settings')
    return render(request, 'core/settings.html', {
        'form': form, 'page_title': 'System Settings',
        'breadcrumbs': [('Settings', None), ('System Settings', None)]
    })


@admin_required
def ministry_list(request):
    items = Ministry.objects.all().order_by('name')
    return render(request, 'core/entity_list.html', {
        'items': items, 'entity_type': 'Ministry', 'entity_plural': 'Ministries',
        'create_url': 'core:ministry_create', 'edit_url': 'core:ministry_edit',
        'delete_url': 'core:ministry_delete', 'page_title': 'Ministries',
        'breadcrumbs': [('Settings', None), ('Entities', None), ('Ministries', None)]
    })


@admin_required
def ministry_create(request):
    form = MinistryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ministry created successfully.')
        return redirect('core:ministry_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Ministry', 'action': 'Create',
        'back_url': 'core:ministry_list', 'page_title': 'Add Ministry',
        'breadcrumbs': [('Settings', None), ('Ministries', 'core:ministry_list'), ('Add', None)]
    })


@admin_required
def ministry_edit(request, pk):
    obj = get_object_or_404(Ministry, pk=pk)
    form = MinistryForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ministry updated.')
        return redirect('core:ministry_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Ministry', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:ministry_list', 'page_title': 'Edit Ministry',
        'breadcrumbs': [('Settings', None), ('Ministries', 'core:ministry_list'), ('Edit', None)]
    })


@admin_required
def ministry_delete(request, pk):
    obj = get_object_or_404(Ministry, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(ministry=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it has employees assigned.')
            return redirect('core:ministry_list')
        obj.delete()
        messages.success(request, 'Ministry deleted.')
    return redirect('core:ministry_list')


@admin_required
def agency_list(request):
    items = Agency.objects.all().order_by('name')
    return render(request, 'core/entity_list.html', {
        'items': items, 'entity_type': 'Agency', 'entity_plural': 'Agencies',
        'create_url': 'core:agency_create', 'edit_url': 'core:agency_edit',
        'delete_url': 'core:agency_delete', 'page_title': 'Agencies',
        'breadcrumbs': [('Settings', None), ('Entities', None), ('Agencies', None)]
    })


@admin_required
def agency_create(request):
    form = AgencyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agency created successfully.')
        return redirect('core:agency_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Agency', 'action': 'Create',
        'back_url': 'core:agency_list', 'page_title': 'Add Agency',
        'breadcrumbs': [('Settings', None), ('Agencies', 'core:agency_list'), ('Add', None)]
    })


@admin_required
def agency_edit(request, pk):
    obj = get_object_or_404(Agency, pk=pk)
    form = AgencyForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Agency updated.')
        return redirect('core:agency_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Agency', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:agency_list', 'page_title': 'Edit Agency',
        'breadcrumbs': [('Settings', None), ('Agencies', 'core:agency_list'), ('Edit', None)]
    })


@admin_required
def agency_delete(request, pk):
    obj = get_object_or_404(Agency, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(agency=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it has employees assigned.')
            return redirect('core:agency_list')
        obj.delete()
        messages.success(request, 'Agency deleted.')
    return redirect('core:agency_list')


@admin_required
def department_list(request):
    items = GovernmentDepartment.objects.all().order_by('name')
    return render(request, 'core/entity_list.html', {
        'items': items, 'entity_type': 'Department', 'entity_plural': 'Government Departments',
        'create_url': 'core:department_create', 'edit_url': 'core:department_edit',
        'delete_url': 'core:department_delete', 'page_title': 'Government Departments',
        'breadcrumbs': [('Settings', None), ('Entities', None), ('Departments', None)]
    })


@admin_required
def department_create(request):
    form = GovernmentDepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Department created successfully.')
        return redirect('core:department_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Government Department', 'action': 'Create',
        'back_url': 'core:department_list', 'page_title': 'Add Department'
    })


@admin_required
def department_edit(request, pk):
    obj = get_object_or_404(GovernmentDepartment, pk=pk)
    form = GovernmentDepartmentForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Department updated.')
        return redirect('core:department_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Government Department', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:department_list', 'page_title': 'Edit Department'
    })


@admin_required
def department_delete(request, pk):
    obj = get_object_or_404(GovernmentDepartment, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(government_department=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it has employees assigned.')
            return redirect('core:department_list')
        obj.delete()
        messages.success(request, 'Department deleted.')
    return redirect('core:department_list')


@admin_required
def district_list(request):
    items = District.objects.all().order_by('region', 'name')
    return render(request, 'core/district_list.html', {
        'items': items, 'page_title': 'Districts / Local Government',
        'breadcrumbs': [('Settings', None), ('Entities', None), ('Districts', None)]
    })


@admin_required
def district_create(request):
    form = DistrictForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'District created successfully.')
        return redirect('core:district_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'District', 'action': 'Create',
        'back_url': 'core:district_list', 'page_title': 'Add District'
    })


@admin_required
def district_edit(request, pk):
    obj = get_object_or_404(District, pk=pk)
    form = DistrictForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'District updated.')
        return redirect('core:district_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'District', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:district_list', 'page_title': 'Edit District'
    })


@admin_required
def district_delete(request, pk):
    obj = get_object_or_404(District, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(district=obj).exists() or Employee.objects.filter(district_of_origin=obj).exists() or Employee.objects.filter(district_of_residence=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it is referenced by employees.')
            return redirect('core:district_list')
        obj.delete()
        messages.success(request, 'District deleted.')
    return redirect('core:district_list')


@admin_required
def cadre_category_list(request):
    qs = CadreCategory.objects.annotate(pos_count=Count('positions')).all()
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    per_page = _get_per_page(request)
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/cadre_list.html', {
        'page_obj': page_obj, 'search': search, 'per_page': per_page,
        'page_title': 'Cadre Categories',
        'breadcrumbs': [('Settings', None), ('Cadre Management', None), ('Categories', None)]
    })


@admin_required
def cadre_category_create(request):
    form = CadreCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cadre category created.')
        return redirect('core:cadre_category_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Cadre Category', 'action': 'Create',
        'back_url': 'core:cadre_category_list', 'page_title': 'Add Cadre Category'
    })


@admin_required
def cadre_category_edit(request, pk):
    obj = get_object_or_404(CadreCategory, pk=pk)
    form = CadreCategoryForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cadre category updated.')
        return redirect('core:cadre_category_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Cadre Category', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:cadre_category_list', 'page_title': 'Edit Cadre Category'
    })


@admin_required
def cadre_category_delete(request, pk):
    obj = get_object_or_404(CadreCategory, pk=pk)
    if request.method == 'POST':
        if obj.positions.exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it has positions assigned. Delete all positions first.')
            return redirect('core:cadre_category_list')
        obj.delete()
        messages.success(request, 'Cadre category deleted.')
    return redirect('core:cadre_category_list')


@admin_required
def position_list(request):
    qs = Position.objects.select_related('cadre_category').annotate(role_count=Count('roles')).all()
    search = request.GET.get('search', '')
    cat_filter = request.GET.get('category', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if cat_filter:
        qs = qs.filter(cadre_category_id=cat_filter)
    # CSV export
    if request.GET.get('export') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="specialities.csv"'
        writer = csv.writer(response)
        writer.writerow(['Speciality Name', 'Category', 'Description', 'Roles Count', 'Status'])
        for p in qs:
            writer.writerow([p.name, p.cadre_category.name, p.description or '', p.role_count, 'Active' if p.is_active else 'Inactive'])
        return response
    per_page = _get_per_page(request)
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/position_list.html', {
        'page_obj': page_obj, 'search': search, 'per_page': per_page,
        'categories': CadreCategory.objects.filter(is_active=True),
        'cat_filter': cat_filter,
        'page_title': 'Specialities',
        'breadcrumbs': [('Settings', None), ('Cadre Management', None), ('Specialities', None)]
    })


@admin_required
def role_list(request):
    qs = Role.objects.select_related('position__cadre_category').all()
    search = request.GET.get('search', '')
    pos_filter = request.GET.get('position', '')
    cat_filter = request.GET.get('category', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if pos_filter:
        qs = qs.filter(position_id=pos_filter)
    if cat_filter:
        qs = qs.filter(position__cadre_category_id=cat_filter)
    # CSV export
    if request.GET.get('export') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="roles.csv"'
        writer = csv.writer(response)
        writer.writerow(['Role Name', 'Position', 'Category', 'Description', 'Status'])
        for r in qs:
            writer.writerow([r.name, r.position.name, r.position.cadre_category.name, r.description or '', 'Active' if r.is_active else 'Inactive'])
        return response
    per_page = _get_per_page(request)
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/role_list.html', {
        'page_obj': page_obj, 'search': search, 'per_page': per_page,
        'categories': CadreCategory.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'cat_filter': cat_filter, 'pos_filter': pos_filter,
        'page_title': 'Roles',
        'breadcrumbs': [('Settings', None), ('Cadre Management', None), ('Roles', None)]
    })


@admin_required
def position_create(request):
    form = PositionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Speciality created.')
        return redirect('core:position_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Speciality', 'action': 'Create',
        'back_url': 'core:position_list', 'page_title': 'Add Speciality'
    })


@admin_required
def position_edit(request, pk):
    obj = get_object_or_404(Position, pk=pk)
    form = PositionForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Speciality updated.')
        return redirect('core:position_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Speciality', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:position_list', 'page_title': 'Edit Speciality'
    })


@admin_required
def position_delete(request, pk):
    obj = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        if obj.roles.exists():
            messages.error(request, f'Cannot delete speciality "{obj.name}" — it has roles assigned. Delete all roles first.')
            return redirect('core:position_list')
        obj.delete()
        messages.success(request, 'Speciality deleted.')
    return redirect('core:position_list')


@admin_required
def role_create(request):
    form = RoleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Role created.')
        return redirect('core:role_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Role', 'action': 'Create',
        'back_url': 'core:role_list', 'page_title': 'Add Role'
    })


@admin_required
def role_edit(request, pk):
    obj = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Role updated.')
        return redirect('core:role_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Role', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:role_list', 'page_title': 'Edit Role'
    })


@admin_required
def role_delete(request, pk):
    obj = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(roles=obj).exists():
            messages.error(request, f'Cannot delete role "{obj.name}" — it is assigned to employees.')
            return redirect('core:role_list')
        obj.delete()
        messages.success(request, 'Role deleted.')
    return redirect('core:role_list')


@admin_required
def job_rank_list(request):
    qs = JobRank.objects.select_related('cadre_category').all()
    search = request.GET.get('search', '')
    cat_filter = request.GET.get('category', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
    if cat_filter:
        qs = qs.filter(cadre_category_id=cat_filter)
    # CSV export
    if request.GET.get('export') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="positions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Position Name', 'Scale (Code)', 'Category', 'Entity Type', 'Level', 'Status'])
        for item in qs:
            writer.writerow([item.name, item.code, item.cadre_category.name if item.cadre_category else 'All',
                             item.get_entity_type_display(), item.level, 'Active' if item.is_active else 'Inactive'])
        return response
    per_page = _get_per_page(request)
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/job_rank_list.html', {
        'page_obj': page_obj, 'search': search, 'per_page': per_page,
        'categories': CadreCategory.objects.filter(is_active=True),
        'cat_filter': cat_filter,
        'page_title': 'Positions',
        'breadcrumbs': [('Settings', None), ('Positions', None)]
    })


@admin_required
def job_rank_create(request):
    form = JobRankForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Position created.')
        return redirect('core:job_rank_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Position', 'action': 'Create',
        'back_url': 'core:job_rank_list', 'page_title': 'Add Position'
    })


@admin_required
def job_rank_edit(request, pk):
    obj = get_object_or_404(JobRank, pk=pk)
    form = JobRankForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Position updated.')
        return redirect('core:job_rank_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Position', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:job_rank_list', 'page_title': 'Edit Position'
    })


@admin_required
def job_rank_delete(request, pk):
    obj = get_object_or_404(JobRank, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(job_rank=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it is assigned to employees.')
            return redirect('core:job_rank_list')
        obj.delete()
        messages.success(request, 'Position deleted.')
    return redirect('core:job_rank_list')


@admin_required
def employee_type_list(request):
    items = EmployeeType.objects.all()
    return render(request, 'core/employee_type_list.html', {
        'items': items, 'page_title': 'Employee Types',
        'breadcrumbs': [('Settings', None), ('Employee Types', None)]
    })


@admin_required
def employee_type_create(request):
    form = EmployeeTypeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Employee type created.')
        return redirect('core:employee_type_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Employee Type', 'action': 'Create',
        'back_url': 'core:employee_type_list', 'page_title': 'Add Employee Type'
    })


@admin_required
def employee_type_edit(request, pk):
    obj = get_object_or_404(EmployeeType, pk=pk)
    form = EmployeeTypeForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Employee type updated.')
        return redirect('core:employee_type_list')
    return render(request, 'core/entity_form.html', {
        'form': form, 'entity_type': 'Employee Type', 'action': 'Edit', 'obj': obj,
        'back_url': 'core:employee_type_list', 'page_title': 'Edit Employee Type'
    })


@admin_required
def employee_type_delete(request, pk):
    obj = get_object_or_404(EmployeeType, pk=pk)
    if request.method == 'POST':
        from employees.models import Employee
        if Employee.objects.filter(employee_type=obj).exists():
            messages.error(request, f'Cannot delete "{obj.name}" — it is assigned to employees.')
            return redirect('core:employee_type_list')
        obj.delete()
        messages.success(request, 'Employee type deleted.')
    return redirect('core:employee_type_list')


def get_positions(request):
    cadre_id = request.GET.get('cadre_id')
    positions = Position.objects.filter(cadre_category_id=cadre_id, is_active=True).values('id', 'name')
    return JsonResponse({'positions': list(positions)})


def get_roles(request):
    position_id = request.GET.get('position_id')
    roles = Role.objects.filter(position_id=position_id, is_active=True).values('id', 'name')
    return JsonResponse({'roles': list(roles)})


def get_entities(request):
    """AJAX endpoint returning entity names filtered by entity_type."""
    entity_type = request.GET.get('entity_type', '')
    entities = []
    if entity_type == 'ministry':
        entities = list(Ministry.objects.filter(is_active=True).values('id', 'name'))
    elif entity_type == 'agency':
        entities = list(Agency.objects.filter(is_active=True).values('id', 'name'))
    elif entity_type == 'department':
        entities = list(GovernmentDepartment.objects.filter(is_active=True).values('id', 'name'))
    elif entity_type == 'local_govt':
        entities = list(District.objects.filter(is_active=True).values('id', 'name'))
    return JsonResponse({'entities': entities})


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)
