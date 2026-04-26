from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
import csv
import io

from .models import (Employee, EmploymentHistory, Qualification, Certification,
                     Publication, EventSeminar, MagicLink, BulkMagicLink, Deployment,
                     ONBOARDING_STATUS_CHOICES)
from .forms import (EmployeeBioForm, EmployeeWorkForm, EmployeeCreateForm,
                    EmploymentHistoryForm, QualificationForm, CertificationForm,
                    PublicationForm, EventSeminarForm, MagicLinkForm, DeploymentForm,
                    VerificationForm)
from core.models import Ministry, Agency, GovernmentDepartment, District, CadreCategory, Position, JobRank, SystemSettings
# ─────────────────────────────────────────────────────────────────────────────
# UI RENAME NOTE (maintainers):
#   "Position" model / "position" field  → displayed as "Speciality" in the UI
#   "JobRank"  model / "job_rank" field  → displayed as "Position"   in the UI
#   "JobRank.code" field                 → displayed as "Scale"       in the UI
#   All underlying field/model names remain unchanged to avoid migrations.
# ─────────────────────────────────────────────────────────────────────────────

User = get_user_model()


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
def employee_list(request):
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    qs = Employee.objects.select_related(
        'user', 'cadre_category', 'position', 'job_rank', 'employee_type',
        'ministry', 'agency', 'government_department', 'district'
    ).filter(is_active=True)

    # Visibility control: non-admins can only see their own record unless directory is enabled
    if not is_admin:
        settings = SystemSettings.get_settings()
        if not settings.allow_employees_view_directory:
            if hasattr(request.user, 'employee_profile'):
                qs = qs.filter(user=request.user)
            else:
                qs = qs.none()

    # Filters
    search = request.GET.get('search', '')
    entity_type = request.GET.get('entity_type', '')
    cadre_cat = request.GET.get('cadre_category', '')
    position_id = request.GET.get('position', '')
    job_rank_id = request.GET.get('job_rank', '')
    emp_type = request.GET.get('employee_type', '')
    view_mode = request.GET.get('view', 'tile')

    if search:
        qs = qs.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_number__icontains=search) |
            Q(user__email__icontains=search)
        )
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if cadre_cat:
        qs = qs.filter(cadre_category_id=cadre_cat)
    if position_id:
        qs = qs.filter(position_id=position_id)
    if job_rank_id:
        qs = qs.filter(job_rank_id=job_rank_id)
    if emp_type:
        qs = qs.filter(employee_type_id=emp_type)

    per_page = request.GET.get('per_page', '50')
    try:
        per_page = int(per_page)
        if per_page not in (20, 50, 100):
            per_page = 50
    except (ValueError, TypeError):
        per_page = 50
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'view_mode': view_mode,
        'search': search,
        'entity_type': entity_type,
        'cadre_cat': cadre_cat,
        'cadre_categories': CadreCategory.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'job_ranks': JobRank.objects.filter(is_active=True),
        'page_title': 'Employees',
        'breadcrumbs': [('Employees', None)],
        'total_count': qs.count(),
        'per_page': per_page,
    }
    from core.models import EmployeeType
    context['employee_types'] = EmployeeType.objects.filter(is_active=True)
    return render(request, 'employees/employee_list.html', context)


@admin_required
def employee_import_template(request):
    """Download a CSV template for employee import."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_import_template.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'first_name', 'last_name', 'email', 'employee_number', 'title',
        'gender', 'phone_primary', 'national_id', 'date_of_birth',
        'entity_type', 'entity_name', 'cadre_category', 'position',
        'job_rank', 'employee_type', 'date_joined_ministry', 'work_location'
    ])
    # Sample row
    writer.writerow([
        'John', 'Doe', 'john.doe@moict.go.ug', 'EMP-001', 'Mr',
        'M', '+256700000000', 'CM12345678ABCDE', '1990-01-15',
        'ministry', 'Ministry of ICT and National Guidance', 'IT Officer',
        'Systems Administrator', 'Principal IT Officer', 'Permanent',
        '2020-06-01', 'Kampala'
    ])
    return response


@admin_required
def employee_import(request):
    """Import employees from CSV file."""
    if request.method != 'POST':
        return render(request, 'employees/employee_import.html', {
            'page_title': 'Import Employees',
            'breadcrumbs': [('Employees', 'employees:list'), ('Import', None)]
        })

    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        messages.error(request, 'Please select a CSV file.')
        return redirect('employees:import')

    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Please upload a CSV file (.csv extension).')
        return redirect('employees:import')

    try:
        decoded = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))
    except Exception as e:
        messages.error(request, f'Error reading CSV file: {e}')
        return redirect('employees:import')

    from core.models import EmployeeType
    created_count = 0
    skipped_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        email = row.get('email', '').strip()
        emp_number = row.get('employee_number', '').strip()

        if not all([first_name, last_name, email, emp_number]):
            errors.append(f'Row {row_num}: Missing required field (first_name, last_name, email, or employee_number)')
            skipped_count += 1
            continue

        # Check for duplicates
        if User.objects.filter(email=email).exists():
            errors.append(f'Row {row_num}: Email "{email}" already exists')
            skipped_count += 1
            continue
        if Employee.objects.filter(employee_number=emp_number).exists():
            errors.append(f'Row {row_num}: Employee number "{emp_number}" already exists')
            skipped_count += 1
            continue

        try:
            # Create user
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                email=email, username=username,
                first_name=first_name, last_name=last_name,
                password='changeme2024'
            )
            user.is_employee = True
            user.save()

            # Create employee
            emp = Employee(user=user, employee_number=emp_number, created_by=request.user)

            # Optional fields
            emp.title = row.get('title', '').strip()
            emp.gender = row.get('gender', '').strip()
            emp.phone_primary = row.get('phone_primary', '').strip()
            emp.national_id = row.get('national_id', '').strip()
            emp.work_location = row.get('work_location', '').strip()

            # Date fields
            dob = row.get('date_of_birth', '').strip()
            if dob:
                try:
                    from datetime import date
                    emp.date_of_birth = date.fromisoformat(dob)
                except ValueError:
                    pass
            djm = row.get('date_joined_ministry', '').strip()
            if djm:
                try:
                    from datetime import date
                    emp.date_joined_ministry = date.fromisoformat(djm)
                except ValueError:
                    pass

            # Entity type and entity
            entity_type = row.get('entity_type', '').strip().lower()
            entity_name = row.get('entity_name', '').strip()
            if entity_type and entity_name:
                emp.entity_type = entity_type
                if entity_type == 'ministry':
                    emp.ministry = Ministry.objects.filter(name__iexact=entity_name).first()
                elif entity_type == 'agency':
                    emp.agency = Agency.objects.filter(name__iexact=entity_name).first()
                elif entity_type == 'department':
                    emp.government_department = GovernmentDepartment.objects.filter(name__iexact=entity_name).first()
                elif entity_type == 'local_govt':
                    emp.district = District.objects.filter(name__iexact=entity_name).first()

            # Lookup FK fields
            cadre_name = row.get('cadre_category', '').strip()
            if cadre_name:
                emp.cadre_category = CadreCategory.objects.filter(name__iexact=cadre_name).first()

            pos_name = row.get('position', '').strip()
            if pos_name:
                emp.position = Position.objects.filter(name__iexact=pos_name).first()

            rank_name = row.get('job_rank', '').strip()
            if rank_name:
                emp.job_rank = JobRank.objects.filter(name__iexact=rank_name).first()

            emp_type = row.get('employee_type', '').strip()
            if emp_type:
                emp.employee_type = EmployeeType.objects.filter(name__iexact=emp_type).first()

            emp.save()
            emp.calculate_profile_completion()
            emp.save(update_fields=['profile_completion'])
            created_count += 1

        except Exception as e:
            errors.append(f'Row {row_num}: Error creating employee - {e}')
            skipped_count += 1

    if created_count:
        messages.success(request, f'Successfully imported {created_count} employee(s).')
    if skipped_count:
        messages.warning(request, f'Skipped {skipped_count} row(s) with errors.')
    if errors:
        # Store first 20 errors in session for display
        request.session['import_errors'] = errors[:20]

    return redirect('employees:import_result')


@admin_required
def employee_import_result(request):
    errors = request.session.pop('import_errors', [])
    return render(request, 'employees/employee_import_result.html', {
        'errors': errors,
        'page_title': 'Import Results',
        'breadcrumbs': [('Employees', 'employees:list'), ('Import Results', None)]
    })


@login_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    is_own_profile = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp

    # Permission check
    if not is_admin and not is_own_profile:
        settings_obj = SystemSettings.get_settings()
        if not settings_obj.allow_employees_view_directory:
            messages.error(request, 'Access denied. You can only view your own profile.')
            return redirect('employees:list')

    # Data breach protection: when employee views another employee's profile,
    # only expose the fields the admin has whitelisted in System Settings → directory_visible_fields
    viewing_another_as_employee = not is_admin and not is_own_profile
    visible_fields = set()  # empty set means "show everything" (admin / own profile)
    if viewing_another_as_employee:
        settings_obj = SystemSettings.get_settings()
        visible_fields = set(settings_obj.directory_visible_fields or [])

    tab = request.GET.get('tab', 'bio')
    # Verification summary for own-profile accordion
    verification_summary = [
        ('Bio Data', emp.bio_verification_status, emp.bio_verification_note),
        ('Work Information', emp.work_verification_status, emp.work_verification_note),
        ('Qualifications', emp.qual_verification_status, emp.qual_verification_note),
        ('Certifications', emp.cert_verification_status, emp.cert_verification_note),
        ('Publications & Events', emp.pub_events_verification_status, emp.pub_events_verification_note),
        ('Overall Profile', emp.overall_verification_status, emp.overall_verification_note),
    ]

    context = {
        'emp': emp,
        'tab': tab,
        'is_admin': is_admin,
        'is_own_profile': is_own_profile,
        'viewing_another_as_employee': viewing_another_as_employee,
        'visible_fields': visible_fields,  # empty = no restriction (admin/own)
        'page_title': emp.user.get_full_name(),
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), None)],
        'employment_history': emp.employment_history.all(),
        'qualifications': emp.qualifications.all(),
        'certifications': emp.certifications.all(),
        'publications': emp.publications.all(),
        'events': emp.events.all(),
        'magic_links': emp.magic_links.order_by('-created_at')[:10] if is_admin else [],
        'deployments': emp.deployments.all(),
        'verification_form': VerificationForm(instance=emp) if is_admin else None,
        'verification_summary': verification_summary,
    }
    return render(request, 'employees/employee_detail.html', context)


@admin_required
def employee_create(request):
    form = EmployeeCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        # Create user
        username = cd['email'].split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user = User.objects.create_user(
            email=cd['email'],
            username=username,
            first_name=cd['first_name'],
            last_name=cd['last_name'],
            password=cd['password']
        )
        emp = Employee.objects.create(
            user=user,
            employee_number=cd['employee_number'],
            created_by=request.user
        )
        messages.success(request, f'Employee {user.get_full_name()} created successfully.')
        return redirect('employees:detail', pk=emp.pk)
    return render(request, 'employees/employee_create.html', {
        'form': form, 'page_title': 'Add Employee',
        'breadcrumbs': [('Employees', 'employees:list'), ('Add Employee', None)]
    })


@login_required
def employee_edit_bio(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    _check_edit_permission(request, emp)
    form = EmployeeBioForm(request.POST or None, request.FILES or None, instance=emp)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Bio data updated successfully.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/employee_edit_bio.html', {
        'form': form, 'emp': emp, 'page_title': 'Edit Bio Data',
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), 'employees:detail'), ('Edit Bio', None)]
    })


@login_required
def employee_edit_work(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    _check_edit_permission(request, emp)
    # Capture all old values for change tracking
    old_position = emp.position
    old_cadre_category = emp.cadre_category
    old_job_rank = emp.job_rank
    old_entity_type = emp.entity_type
    old_entity = emp.get_entity_name()
    form = EmployeeWorkForm(request.POST or None, instance=emp, user=request.user)
    if request.method == 'POST' and form.is_valid():
        emp_updated = form.save(commit=False)
        new_position = form.cleaned_data.get('position')
        new_cadre_category = form.cleaned_data.get('cadre_category')
        new_job_rank = form.cleaned_data.get('job_rank')
        new_entity_type = form.cleaned_data.get('entity_type', '')

        # Compute new entity name from form data
        new_ministry = form.cleaned_data.get('ministry')
        new_agency = form.cleaned_data.get('agency')
        new_department = form.cleaned_data.get('government_department')
        new_district = form.cleaned_data.get('district')
        if new_entity_type == 'ministry' and new_ministry:
            new_entity_name = new_ministry.name
        elif new_entity_type == 'agency' and new_agency:
            new_entity_name = new_agency.name
        elif new_entity_type == 'department' and new_department:
            new_entity_name = new_department.name
        elif new_entity_type == 'local_govt' and new_district:
            new_entity_name = new_district.name
        else:
            new_entity_name = old_entity

        # Check if any tracked field changed
        position_changed = old_position != new_position
        cadre_changed = old_cadre_category != new_cadre_category
        rank_changed = old_job_rank != new_job_rank
        entity_changed = old_entity != new_entity_name or old_entity_type != new_entity_type

        if position_changed or cadre_changed or rank_changed or entity_changed:
            # Mark existing current history as previous
            EmploymentHistory.objects.filter(employee=emp, is_current=True).update(
                is_current=False, end_date=timezone.now().date()
            )
            # Create new current history entry
            changes = []
            if position_changed:
                changes.append(f"Position: {old_position} -> {new_position}")
            if cadre_changed:
                changes.append(f"Cadre: {old_cadre_category} -> {new_cadre_category}")
            if rank_changed:
                changes.append(f"Rank: {old_job_rank} -> {new_job_rank}")
            if entity_changed:
                changes.append(f"Entity: {old_entity} -> {new_entity_name}")

            EmploymentHistory.objects.create(
                employee=emp,
                position_title=new_position.name if new_position else (old_position.name if old_position else ''),
                entity_type=new_entity_type or emp.entity_type or '',
                entity_name=new_entity_name,
                cadre_category=new_cadre_category.name if new_cadre_category else '',
                job_rank=new_job_rank.name if new_job_rank else '',
                start_date=form.cleaned_data.get('date_joined_position') or timezone.now().date(),
                is_current=True,
                notes=f'Auto-tracked: {"; ".join(changes)}'
            )
        emp_updated.save()
        form.save_m2m()
        messages.success(request, 'Work information updated.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/employee_edit_work.html', {
        'form': form, 'emp': emp, 'page_title': 'Edit Work Information',
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), 'employees:detail'), ('Edit Work', None)],
        'ministries': Ministry.objects.filter(is_active=True),
        'agencies': Agency.objects.filter(is_active=True),
        'departments': GovernmentDepartment.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True),
    })


def _check_edit_permission(request, emp):
    settings_obj = SystemSettings.get_settings()
    is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin and not (is_own and settings_obj.allow_employee_profile_edit):
        messages.error(request, 'You do not have permission to edit this profile.')
        from django.shortcuts import redirect as _redirect
        raise PermissionError()


# Employment History
@login_required
def employment_history_add(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    form = EmploymentHistoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        if obj.is_current:
            EmploymentHistory.objects.filter(employee=emp, is_current=True).update(is_current=False)
        obj.save()
        messages.success(request, 'Employment history added.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/history_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Employment History',
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), 'employees:detail'), ('Add History', None)]
    })


@login_required
def employment_history_edit(request, pk, history_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(EmploymentHistory, pk=history_pk, employee=emp)
    form = EmploymentHistoryForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Employment history updated.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/history_form.html', {
        'form': form, 'emp': emp, 'obj': obj, 'page_title': 'Edit Employment History'
    })


@login_required
def employment_history_delete(request, pk, history_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(EmploymentHistory, pk=history_pk, employee=emp)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Employment history deleted.')
    return redirect('employees:detail', pk=pk)


# Qualifications
@login_required
def qualification_add(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    # Only admins or the employee themselves (if self-edit enabled) may add
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
    settings_obj = SystemSettings.get_settings()
    if not is_admin and not (is_own and settings_obj.allow_employee_profile_edit):
        messages.error(request, 'You do not have permission to add qualifications.')
        return redirect('employees:detail', pk=pk)
    form = QualificationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        messages.success(request, 'Qualification added.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/item_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Qualification', 'item_type': 'Qualification'
    })


@login_required
def qualification_edit(request, pk, item_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(Qualification, pk=item_pk, employee=emp)
    form = QualificationForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Qualification updated.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/item_form.html', {
        'form': form, 'emp': emp, 'obj': obj, 'page_title': 'Edit Qualification', 'item_type': 'Qualification'
    })


@login_required
def qualification_delete(request, pk, item_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(Qualification, pk=item_pk, employee=emp)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
        settings_obj = SystemSettings.get_settings()
        if not (is_own and settings_obj.allow_employee_profile_edit):
            messages.error(request, 'You do not have permission to delete this qualification.')
            return redirect('employees:detail', pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Qualification deleted.')
    return redirect('employees:detail', pk=pk)


# Certifications
@login_required
def certification_add(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
    settings_obj = SystemSettings.get_settings()
    if not is_admin and not (is_own and settings_obj.allow_employee_profile_edit):
        messages.error(request, 'You do not have permission to add certifications.')
        return redirect('employees:detail', pk=pk)
    form = CertificationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        messages.success(request, 'Certification added.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/item_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Certification', 'item_type': 'Certification'
    })


@login_required
def certification_delete(request, pk, item_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(Certification, pk=item_pk, employee=emp)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
        settings_obj = SystemSettings.get_settings()
        if not (is_own and settings_obj.allow_employee_profile_edit):
            messages.error(request, 'You do not have permission to delete this certification.')
            return redirect('employees:detail', pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Certification deleted.')
    return redirect('employees:detail', pk=pk)


# Publications
@login_required
def publication_add(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
    settings_obj = SystemSettings.get_settings()
    if not is_admin and not (is_own and settings_obj.allow_employee_profile_edit):
        messages.error(request, 'You do not have permission to add publications.')
        return redirect('employees:detail', pk=pk)
    form = PublicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        messages.success(request, 'Publication added.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/item_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Publication', 'item_type': 'Publication'
    })


@login_required
def publication_delete(request, pk, item_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(Publication, pk=item_pk, employee=emp)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
        settings_obj = SystemSettings.get_settings()
        if not (is_own and settings_obj.allow_employee_profile_edit):
            messages.error(request, 'You do not have permission to delete this publication.')
            return redirect('employees:detail', pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Publication deleted.')
    return redirect('employees:detail', pk=pk)


# Events
@login_required
def event_add(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
    settings_obj = SystemSettings.get_settings()
    if not is_admin and not (is_own and settings_obj.allow_employee_profile_edit):
        messages.error(request, 'You do not have permission to add events.')
        return redirect('employees:detail', pk=pk)
    form = EventSeminarForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        messages.success(request, 'Event/Seminar added.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/item_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Event/Seminar', 'item_type': 'Event/Seminar'
    })


@login_required
def event_delete(request, pk, item_pk):
    emp = get_object_or_404(Employee, pk=pk)
    obj = get_object_or_404(EventSeminar, pk=item_pk, employee=emp)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        is_own = hasattr(request.user, 'employee_profile') and request.user.employee_profile == emp
        settings_obj = SystemSettings.get_settings()
        if not (is_own and settings_obj.allow_employee_profile_edit):
            messages.error(request, 'You do not have permission to delete this event.')
            return redirect('employees:detail', pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Event deleted.')
    return redirect('employees:detail', pk=pk)


# ── Bulk Magic Link ──────────────────────────────────────────────────────────
@admin_required
def bulk_magic_link(request):
    """Send profile-update magic links to a filtered set of employees."""
    from core.models import CadreCategory, Position, JobRank
    from employees.models import ONBOARDING_STATUS_CHOICES

    # Build filtered queryset from GET params (preview) or POST params (send)
    params = request.POST if request.method == 'POST' else request.GET
    qs = Employee.objects.select_related('user', 'cadre_category', 'position', 'job_rank').filter(is_active=True)

    onboarding_status = params.get('onboarding_status', '')
    completion_lt = params.get('completion_lt', '')
    entity_type = params.get('entity_type', '')
    cadre_cat = params.get('cadre_category', '')
    position_id = params.get('position', '')
    job_rank_id = params.get('job_rank', '')

    if onboarding_status:
        qs = qs.filter(onboarding_status=onboarding_status)
    if completion_lt:
        try:
            qs = qs.filter(profile_completion__lt=int(completion_lt))
        except ValueError:
            pass
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if cadre_cat:
        qs = qs.filter(cadre_category_id=cadre_cat)
    if position_id:
        qs = qs.filter(position_id=position_id)
    if job_rank_id:
        qs = qs.filter(job_rank_id=job_rank_id)

    if request.method == 'POST' and params.get('action') == 'send':
        sys_settings = SystemSettings.get_settings()
        duration = int(params.get('duration_hours', sys_settings.magic_link_default_duration or 48))
        sections = params.getlist('sections') or ['bio', 'work']
        expires_at = timezone.now() + timedelta(hours=duration)
        created_links = []
        for emp in qs:
            ml = MagicLink.objects.create(
                employee=emp, expires_at=expires_at,
                created_by=request.user, sections=sections
            )
            link = request.build_absolute_uri(f'/employees/magic/{ml.token}/')
            created_links.append({'emp': emp, 'link': link, 'token': ml.token})
        messages.success(request, f'Magic links created for {len(created_links)} employee(s).')
        return render(request, 'employees/bulk_magic_link_sent.html', {
            'created_links': created_links,
            'page_title': 'Bulk Magic Links Sent',
        })

    context = {
        'matched_count': qs.count(),
        'preview_employees': qs[:10],
        'onboarding_status_choices': ONBOARDING_STATUS_CHOICES,
        'cadre_categories': CadreCategory.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'job_ranks': JobRank.objects.filter(is_active=True),
        # current filter values
        'sel_onboarding': onboarding_status,
        'sel_completion_lt': completion_lt,
        'sel_entity_type': entity_type,
        'sel_cadre_cat': cadre_cat,
        'sel_position': position_id,
        'sel_job_rank': job_rank_id,
        'page_title': 'Bulk Magic Link',
        'breadcrumbs': [('Employees', 'employees:list'), ('Bulk Magic Link', None)],
    }
    return render(request, 'employees/bulk_magic_link.html', context)


# Magic Links
@admin_required
def send_magic_link(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    sys_settings = SystemSettings.get_settings()
    form = MagicLinkForm(request.POST or None, initial={'duration_hours': sys_settings.magic_link_default_duration})
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        expires_at = timezone.now() + timedelta(hours=cd['duration_hours'])
        ml = MagicLink.objects.create(
            employee=emp,
            expires_at=expires_at,
            created_by=request.user,
            sections=cd['sections']
        )
        # Build link
        link = request.build_absolute_uri(f'/employees/magic/{ml.token}/')
        messages.success(request, f'Magic link created. Share this link: {link}')
        # TODO: send via email
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/magic_link_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Send Magic Link',
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), 'employees:detail'), ('Magic Link', None)]
    })


def magic_link_update(request, token):
    ml = get_object_or_404(MagicLink, token=token)
    if not ml.is_valid:
        return render(request, 'employees/magic_link_expired.html', {'ml': ml})
    emp = ml.employee
    sections = ml.sections or []

    if request.method == 'POST':
        section = request.POST.get('section_submit', '')
        saved = False
        error_form = None

        if section == 'bio' and 'bio' in sections:
            f = EmployeeBioForm(request.POST, request.FILES, instance=emp)
            if f.is_valid():
                f.save()
                saved = True
                messages.success(request, 'Bio data saved successfully.')
            else:
                error_form = 'bio'
        elif section == 'work' and 'work' in sections:
            f = EmployeeWorkForm(request.POST, instance=emp, user=emp.user)
            if f.is_valid():
                f.save()
                saved = True
                messages.success(request, 'Work information saved successfully.')
            else:
                error_form = 'work'
        elif section == 'qualifications' and 'qualifications' in sections:
            f = QualificationForm(request.POST, request.FILES)
            if f.is_valid():
                q = f.save(commit=False)
                q.employee = emp
                q.save()
                emp.save()  # recalculate profile completion
                saved = True
                messages.success(request, 'Qualification added successfully.')
            else:
                error_form = 'qualifications'
        elif section == 'certifications' and 'certifications' in sections:
            f = CertificationForm(request.POST, request.FILES)
            if f.is_valid():
                c = f.save(commit=False)
                c.employee = emp
                c.save()
                saved = True
                messages.success(request, 'Certification added successfully.')
            else:
                error_form = 'certifications'
        elif section == 'publications' and 'publications' in sections:
            f = PublicationForm(request.POST)
            if f.is_valid():
                p = f.save(commit=False)
                p.employee = emp
                p.save()
                saved = True
                messages.success(request, 'Publication added successfully.')
            else:
                error_form = 'publications'
        elif section == 'events' and 'events' in sections:
            f = EventSeminarForm(request.POST, request.FILES)
            if f.is_valid():
                e = f.save(commit=False)
                e.employee = emp
                e.save()
                saved = True
                messages.success(request, 'Event/Seminar added successfully.')
            else:
                error_form = 'events'

        if saved:
            return redirect('employees:magic_link_update', token=token)

    # Build fresh forms for GET (or after save redirect)
    context = {
        'ml': ml,
        'emp': emp,
        'sections': sections,
        'bio_form': EmployeeBioForm(instance=emp) if 'bio' in sections else None,
        'work_form': EmployeeWorkForm(instance=emp, user=emp.user) if 'work' in sections else None,
        'qual_form': QualificationForm() if 'qualifications' in sections else None,
        'cert_form': CertificationForm() if 'certifications' in sections else None,
        'pub_form': PublicationForm() if 'publications' in sections else None,
        'event_form': EventSeminarForm() if 'events' in sections else None,
        'qualifications': emp.qualifications.all(),
        'certifications': emp.certifications.all(),
        'publications': emp.publications.all(),
        'events': emp.events.all(),
    }
    return render(request, 'employees/magic_link_update.html', context)


# ── Verification Views (admin-only) ──────────────────────────────────────────
@admin_required
def save_verification(request, pk):
    """Save verification statuses for one employee (POST only)."""
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = VerificationForm(request.POST, instance=emp)
        if form.is_valid():
            v = form.save(commit=False)
            v.verification_updated_at = timezone.now()
            v.verification_updated_by = request.user
            v.save()
            messages.success(request, f'Verification status updated for {emp.user.get_full_name()}.')
        else:
            messages.error(request, 'Please correct the errors in the verification form.')
    return redirect(f"{request.build_absolute_uri('/employees/' + str(pk) + '/')}?tab=verification")


@admin_required
def verification_dashboard(request):
    """Dashboard showing all employees' verification statuses with bulk verify."""
    from django.db.models import Q, Count

    qs = Employee.objects.select_related('user', 'cadre_category', 'position').filter(is_active=True)

    # Filters
    status_filter = request.GET.get('status_filter', '')
    entity_type = request.GET.get('entity_type', '')
    cadre_cat = request.GET.get('cadre_category', '')

    if status_filter == 'fully_verified':
        qs = qs.filter(overall_verification_status='verified')
    elif status_filter == 'pending':
        qs = qs.filter(overall_verification_status='pending')
    elif status_filter == 'returned':
        qs = qs.filter(overall_verification_status='returned')
    elif status_filter == 'any_returned':
        qs = qs.filter(
            Q(bio_verification_status='returned') |
            Q(work_verification_status='returned') |
            Q(qual_verification_status='returned') |
            Q(cert_verification_status='returned') |
            Q(pub_events_verification_status='returned')
        )

    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if cadre_cat:
        qs = qs.filter(cadre_category_id=cadre_cat)

    # Bulk verify action
    if request.method == 'POST':
        action = request.POST.get('bulk_action', '')
        sections = request.POST.getlist('bulk_sections')
        emp_ids = request.POST.getlist('emp_ids')
        target_status = request.POST.get('target_status', 'verified')

        if emp_ids:
            target_qs = Employee.objects.filter(pk__in=emp_ids)
        else:
            target_qs = qs

        update_kwargs = {
            'verification_updated_at': timezone.now(),
            'verification_updated_by': request.user,
        }
        if not sections or 'all' in sections:
            sections = ['bio', 'work', 'qual', 'cert', 'pub_events', 'overall']

        section_map = {
            'bio': 'bio_verification_status',
            'work': 'work_verification_status',
            'qual': 'qual_verification_status',
            'cert': 'cert_verification_status',
            'pub_events': 'pub_events_verification_status',
            'overall': 'overall_verification_status',
        }
        for sec in sections:
            if sec in section_map:
                update_kwargs[section_map[sec]] = target_status

        count = target_qs.update(**update_kwargs)
        messages.success(request, f'Updated verification for {count} employee(s).')
        return redirect('employees:verification_dashboard')

    # Summary stats
    total = Employee.objects.filter(is_active=True).count()
    fully_verified = Employee.objects.filter(is_active=True, overall_verification_status='verified').count()
    pending = Employee.objects.filter(is_active=True, overall_verification_status='pending').count()
    returned = Employee.objects.filter(is_active=True, overall_verification_status='returned').count()

    # Per entity summary
    entity_summary = (
        Employee.objects.filter(is_active=True)
        .values('entity_type')
        .annotate(
            total=Count('id'),
            verified_count=Count('id', filter=Q(overall_verification_status='verified')),
        )
        .order_by('entity_type')
    )
    entity_display = dict(Employee._meta.get_field('entity_type').choices)
    for e in entity_summary:
        e['entity_label'] = entity_display.get(e['entity_type'], e['entity_type'] or 'N/A')

    per_page = 50
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    from core.models import CadreCategory as CC
    context = {
        'page_title': 'Verification Status',
        'breadcrumbs': [('Employees', 'employees:list'), ('Verification Status', None)],
        'page_obj': page_obj,
        'total': total,
        'fully_verified': fully_verified,
        'pending': pending,
        'returned': returned,
        'entity_summary': entity_summary,
        'cadre_categories': CC.objects.filter(is_active=True),
        'status_filter': status_filter,
        'entity_type': entity_type,
        'cadre_cat': cadre_cat,
    }
    return render(request, 'employees/verification_dashboard.html', context)


@login_required
def employee_deactivate(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('employees:list')
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        emp.is_active = False
        emp.save()
        emp.user.is_active = False
        emp.user.save()
        messages.success(request, f'{emp.user.get_full_name()} has been deactivated.')
    return redirect('employees:list')


# Deployments
@login_required
def deployment_add(request, pk):
    from django.urls import reverse
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        messages.error(request, 'Access denied.')
        return redirect('employees:detail', pk=pk)
    # Pre-populate from_entity from current employee data
    initial = {}
    if emp.entity_type:
        initial['from_entity_type'] = emp.entity_type
        initial['from_entity_name'] = emp.get_entity_name()
    if emp.position:
        initial['from_position'] = emp.position.name
    if emp.cadre_category:
        initial['from_cadre_category'] = emp.cadre_category.name
    form = DeploymentForm(request.POST or None, initial=initial, employee=emp)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.created_by = request.user
        # Ensure FROM fields are saved even though they're read-only
        obj.from_entity_type = emp.entity_type or ''
        obj.from_entity_name = emp.get_entity_name()
        obj.from_position = emp.position.name if emp.position else ''
        obj.from_cadre_category = emp.cadre_category.name if emp.cadre_category else ''
        obj.status_changed_by = request.user
        obj.status_changed_at = timezone.now()
        obj.save()
        messages.success(request, 'Deployment/Transfer record added.')
        return redirect(reverse('employees:detail', kwargs={'pk': pk}) + '?tab=deployments')
    return render(request, 'employees/deployment_form.html', {
        'form': form, 'emp': emp, 'page_title': 'Add Deployment/Transfer',
        'breadcrumbs': [('Employees', 'employees:list'), (emp.user.get_full_name(), 'employees:detail'), ('Add Deployment', None)]
    })


@login_required
def deployment_edit(request, pk, dep_pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        messages.error(request, 'Access denied.')
        return redirect('employees:detail', pk=pk)
    obj = get_object_or_404(Deployment, pk=dep_pk, employee=emp)
    old_status = obj.status
    form = DeploymentForm(request.POST or None, instance=obj, employee=emp)
    if request.method == 'POST' and form.is_valid():
        dep = form.save(commit=False)
        # Ensure FROM fields persist
        dep.from_entity_type = obj.from_entity_type
        dep.from_entity_name = obj.from_entity_name
        dep.from_position = obj.from_position
        dep.from_cadre_category = obj.from_cadre_category
        # Track status change
        if dep.status != old_status:
            dep.status_changed_by = request.user
            dep.status_changed_at = timezone.now()
        dep.save()
        messages.success(request, 'Deployment record updated.')
        return redirect('employees:detail', pk=pk)
    return render(request, 'employees/deployment_form.html', {
        'form': form, 'emp': emp, 'obj': obj, 'page_title': 'Edit Deployment/Transfer'
    })


@login_required
def deployment_delete(request, pk, dep_pk):
    emp = get_object_or_404(Employee, pk=pk)
    is_admin = request.user.is_admin or request.user.is_it_admin or request.user.is_superuser
    if not is_admin:
        messages.error(request, 'Access denied.')
        return redirect('employees:detail', pk=pk)
    obj = get_object_or_404(Deployment, pk=dep_pk, employee=emp)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deployment record deleted.')
    return redirect('employees:detail', pk=pk)
