from django import forms
from .models import (Ministry, Agency, GovernmentDepartment, District,
                     EmployeeType, CadreCategory, Position, Role, JobRank, SystemSettings)

WIDGET_ATTRS = {'class': 'form-control'}
CHECK_ATTRS = {'class': 'form-check-input'}


def text_field(**kwargs):
    return forms.CharField(widget=forms.TextInput(attrs=WIDGET_ATTRS), **kwargs)


def textarea_field(**kwargs):
    return forms.CharField(widget=forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}), required=False, **kwargs)


class MinistryForm(forms.ModelForm):
    class Meta:
        model = Ministry
        fields = ['name', 'code', 'description', 'address', 'phone', 'email', 'website', 'is_active']
        widgets = {f: forms.TextInput(attrs=WIDGET_ATTRS) for f in ['name', 'code', 'address', 'phone']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs['class'] = 'form-control'


class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ['name', 'code', 'description', 'address', 'phone', 'email', 'website', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class GovernmentDepartmentForm(forms.ModelForm):
    class Meta:
        model = GovernmentDepartment
        fields = ['name', 'code', 'description', 'address', 'phone', 'email', 'website', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name', 'region', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'region': forms.Select(attrs=WIDGET_ATTRS),
        }


class EmployeeTypeForm(forms.ModelForm):
    class Meta:
        model = EmployeeType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }


class CadreCategoryForm(forms.ModelForm):
    class Meta:
        model = CadreCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'cadre_category', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'cadre_category': forms.Select(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'position', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'position': forms.Select(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }


class JobRankForm(forms.ModelForm):
    # ─────────────────────────────────────────────────────────────────────────
    # UI RENAME NOTE (maintainers):
    #   The database model is called "JobRank" and the field is "job_rank".
    #   In the UI this is now displayed as "Position".
    #   The "code" field is displayed in the UI as "Scale".
    #   Do NOT rename the model/field — only these form labels and templates use
    #   the new terminology.
    # ─────────────────────────────────────────────────────────────────────────
    class Meta:
        model = JobRank
        fields = ['name', 'code', 'cadre_category', 'entity_type', 'description', 'level', 'is_active']
        labels = {
            'code': 'Scale',        # UI label only — model field remains "code"
        }
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'code': forms.TextInput(attrs=WIDGET_ATTRS),
            'cadre_category': forms.Select(attrs=WIDGET_ATTRS),
            'entity_type': forms.Select(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
            'level': forms.NumberInput(attrs=WIDGET_ATTRS),
        }


class SystemSettingsForm(forms.ModelForm):
    # ── Bio Data fields ──────────────────────────────────────────────────────
    BIO_FIELD_CHOICES = [
        ('profile_photo', 'Profile Photo'),
        ('title', 'Title (Mr/Mrs/Dr)'),
        ('gender', 'Gender'),
        ('date_of_birth', 'Date of Birth'),
        ('nationality', 'Nationality'),
        ('phone_primary', 'Primary Phone'),
        ('phone_secondary', 'Secondary Phone'),
        ('personal_email', 'Personal Email'),
        ('physical_address', 'Physical Address'),
        ('district_of_origin', 'District of Origin'),
        ('district_of_residence', 'District of Residence'),
        ('marital_status', 'Marital Status'),
        ('religion', 'Religion'),
        ('blood_type', 'Blood Type'),
        ('has_disability', 'Disability Status'),
        ('next_of_kin_name', 'Next of Kin Name'),
        ('next_of_kin_phone', 'Next of Kin Phone'),
        ('next_of_kin_relationship', 'Next of Kin Relationship'),
        ('emergency_contact_name', 'Emergency Contact Name'),
        ('emergency_contact_phone', 'Emergency Contact Phone'),
        ('national_id', 'National ID'),
        ('passport_number', 'Passport Number'),
        ('nssf_number', 'NSSF Number'),
        ('tin_number', 'TIN Number'),
    ]
    # ── Work Information fields ───────────────────────────────────────────────
    WORK_FIELD_CHOICES = [
        ('employee_number', 'Employee Number'),
        ('employee_type', 'Employee Type'),
        ('entity_type', 'Entity Type'),
        ('cadre_category', 'Cadre Category'),
        ('position', 'Speciality'),
        ('job_rank', 'Position / Job Rank'),
        ('roles', 'Assigned Roles'),
        ('work_location', 'Work Location'),
        ('date_joined_position', 'Date Joined Speciality'),
        ('date_joined_ministry', 'Date Joined Ministry/Entity'),
        ('contract_end_date', 'Contract End Date'),
        ('reporting_to', 'Reporting To'),
        ('profile_completion', 'Profile Completion %'),
    ]
    # ── Sections (tab-level access) ──────────────────────────────────────────
    SECTION_CHOICES = [
        ('career_history', 'Career History'),
        ('deployment_history', 'Deployment History'),
        ('qualifications', 'Qualifications'),
        ('certifications', 'Certifications'),
        ('publications', 'Publications'),
        ('events', 'Events & Seminars'),
    ]

    DIRECTORY_FIELD_CHOICES = BIO_FIELD_CHOICES + WORK_FIELD_CHOICES + SECTION_CHOICES

    directory_visible_fields = forms.MultipleChoiceField(
        choices=DIRECTORY_FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Visible Fields in Employee Directory',
        help_text='Select which fields non-admin employees can see when viewing the directory.'
    )

    class Meta:
        model = SystemSettings
        fields = ['system_name', 'email_host', 'email_port', 'email_use_tls',
                  'email_host_user', 'email_host_password', 'email_from_name',
                  'magic_link_default_duration', 'allow_employee_profile_edit',
                  'allow_employees_view_directory', 'announcement_default_duration',
                  'directory_visible_fields']
        widgets = {
            'email_host_password': forms.PasswordInput(attrs={**WIDGET_ATTRS, 'render_value': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.PasswordInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs['class'] = 'form-control'
        if self.instance.pk:
            self.fields['directory_visible_fields'].initial = self.instance.directory_visible_fields or []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.directory_visible_fields = self.cleaned_data.get('directory_visible_fields', [])
        if commit:
            instance.save()
        return instance
