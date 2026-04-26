from django import forms
from django.contrib.auth import get_user_model
from .models import (Employee, EmploymentHistory, Qualification, Certification,
                     Publication, EventSeminar, MagicLink, Deployment,
                     ONBOARDING_STATUS_CHOICES, ONBOARDING_STATUS_EMPLOYEE_CHOICES,
                     VERIFICATION_STATUS_CHOICES)

User = get_user_model()
W = {'class': 'form-control'}
WS = {'class': 'form-select'}


class EmployeeBioForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'title', 'date_of_birth', 'gender', 'nationality', 'national_id',
            'passport_number', 'tin_number', 'nssf_number', 'phone_primary',
            'phone_secondary', 'personal_email', 'profile_photo', 'physical_address',
            'district_of_origin', 'district_of_residence', 'marital_status',
            'religion', 'blood_type', 'has_disability', 'disability_description',
            'next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone',
            'next_of_kin_email', 'next_of_kin_address',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={**W, 'type': 'date'}),
            'physical_address': forms.Textarea(attrs={**W, 'rows': 3}),
            'disability_description': forms.Textarea(attrs={**W, 'rows': 2}),
            'next_of_kin_address': forms.Textarea(attrs={**W, 'rows': 2}),
            'district_of_origin': forms.Select(attrs=WS),
            'district_of_residence': forms.Select(attrs=WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select,)) and name not in ('district_of_origin', 'district_of_residence'):
                field.widget.attrs.update(WS)
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput, forms.Select, forms.Textarea, forms.DateInput)):
                field.widget.attrs.update(W)

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            today = date.today()
            age = (today - dob).days // 365
            if age < 18:
                raise forms.ValidationError("Employee must be at least 18 years old.")
        return dob


class EmployeeWorkForm(forms.ModelForm):
    # ─────────────────────────────────────────────────────────────────────────
    # UI RENAME NOTE (maintainers):
    #   Model field "position"  → displayed in UI as "Speciality"
    #   Model field "job_rank"  → displayed in UI as "Position"
    #   Model field "date_joined_position" → "Date Joined Speciality" in UI
    #   The model/field names are unchanged — only labels differ.
    # ─────────────────────────────────────────────────────────────────────────
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'employee_type', 'entity_type',
            'ministry', 'agency', 'government_department', 'district',
            'cadre_category', 'position', 'job_rank', 'reporting_to',
            'work_location', 'date_joined_position', 'date_joined_ministry',
            'contract_end_date', 'roles', 'onboarding_status',
        ]
        labels = {
            'position': 'Speciality',               # UI rename: model field stays "position"
            'job_rank': 'Position',                 # UI rename: model field stays "job_rank"
            'date_joined_position': 'Date Joined Speciality',  # follows position rename
            'onboarding_status': 'Parenting Status',  # UI rename: model field stays "onboarding_status"
        }
        widgets = {
            'date_joined_position': forms.DateInput(attrs={**W, 'type': 'date'}),
            'date_joined_ministry': forms.DateInput(attrs={**W, 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'roles': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop optional 'user' kwarg so we can filter choices per role
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select) and name not in ('roles',):
                field.widget.attrs.update(WS)
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.SelectMultiple, forms.Select)):
                field.widget.attrs.update(W)
        # Hide "Not Set" from employees (admins & IT admins see all choices)
        if user and not (getattr(user, 'is_admin', False) or getattr(user, 'is_it_admin', False) or getattr(user, 'is_superuser', False)):
            self.fields['onboarding_status'].choices = ONBOARDING_STATUS_EMPLOYEE_CHOICES


class EmployeeCreateForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=W))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=W))
    email = forms.EmailField(widget=forms.EmailInput(attrs=W))
    employee_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs=W))
    password = forms.CharField(widget=forms.PasswordInput(attrs=W), initial='ChangeMe@2024')


class EmploymentHistoryForm(forms.ModelForm):
    # ─────────────────────────────────────────────────────────────────────────
    # UI RENAME NOTE (maintainers):
    #   "position_title" field → displayed as "Speciality Title" in UI
    #   "job_rank" field       → displayed as "Position" in UI
    #   Model/field names are unchanged.
    # ─────────────────────────────────────────────────────────────────────────

    # Make position_title a dropdown from existing positions (model: Position → UI: Speciality)
    position_title = forms.CharField(
        label='Speciality Title',   # UI rename: underlying data stores position name
        widget=forms.Select(attrs=WS),
        required=True,
    )

    class Meta:
        model = EmploymentHistory
        fields = ['position_title', 'entity_type', 'entity_name', 'cadre_category',
                  'job_rank', 'start_date', 'end_date', 'is_current', 'notes']
        labels = {
            'job_rank': 'Position',  # UI rename: model field stays "job_rank"
        }
        widgets = {
            'start_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'notes': forms.Textarea(attrs={**W, 'rows': 3}),
            'entity_type': forms.Select(attrs=WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Position, CadreCategory, JobRank
        # Populate speciality choices (model: Position, UI label: Speciality)
        positions = Position.objects.filter(is_active=True).values_list('name', flat=True).distinct()
        pos_choices = [('', '-- Select Speciality --')] + [(p, p) for p in positions]
        self.fields['position_title'].widget.choices = pos_choices
        # Make cadre_category a dropdown
        categories = CadreCategory.objects.filter(is_active=True).values_list('name', flat=True)
        cat_choices = [('', '-- Select Cadre Category --')] + [(c, c) for c in categories]
        self.fields['cadre_category'].widget = forms.Select(attrs=WS, choices=cat_choices)
        # Make job_rank a dropdown (model: JobRank, UI label: Position)
        ranks = JobRank.objects.filter(is_active=True).values_list('name', flat=True).distinct()
        rank_choices = [('', '-- Select Position --')] + [(r, r) for r in ranks]
        self.fields['job_rank'].widget = forms.Select(attrs=WS, choices=rank_choices)
        # Make entity_name a select (will be populated by JS)
        self.fields['entity_name'].widget = forms.Select(attrs=WS, choices=[('', '-- Select Entity --')])

        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Select, forms.Textarea, forms.DateInput)):
                field.widget.attrs.update(W)

    def clean_start_date(self):
        from datetime import date
        start = self.cleaned_data.get('start_date')
        if start and start > date.today():
            raise forms.ValidationError("Start date cannot be in the future.")
        return start

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("End date cannot be before the start date.")
        return cleaned


class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = ['qualification_type', 'institution', 'field_of_study', 'start_date', 'end_date', 'grade', 'document']
        widgets = {
            'qualification_type': forms.Select(attrs=WS),
            'start_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.FileInput, forms.DateInput)):
                field.widget.attrs.update(W)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError("Start date cannot be after the end date.")
        return cleaned


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_body', 'date_attained', 'has_expiry', 'expiry_date', 'credential_id', 'document']
        widgets = {
            'date_attained': forms.DateInput(attrs={**W, 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={**W, 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput, forms.DateInput)):
                field.widget.attrs.update(W)


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'journal_or_publisher', 'date_published', 'url', 'description', 'co_authors']
        widgets = {
            'date_published': forms.DateInput(attrs={**W, 'type': 'date'}),
            'description': forms.Textarea(attrs={**W, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput)):
                field.widget.attrs.update(W)


class EventSeminarForm(forms.ModelForm):
    class Meta:
        model = EventSeminar
        fields = ['name', 'organizer', 'location', 'date_attended', 'duration_days', 'certificate_obtained', 'document', 'notes']
        widgets = {
            'date_attended': forms.DateInput(attrs={**W, 'type': 'date'}),
            'notes': forms.Textarea(attrs={**W, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput, forms.Textarea, forms.DateInput)):
                field.widget.attrs.update(W)


class DeploymentForm(forms.ModelForm):
    # ─────────────────────────────────────────────────────────────────────────
    # UI RENAME NOTE (maintainers):
    #   "from_position" / "to_position" fields → displayed as "Speciality" in UI
    #   Model field names stay as "from_position" / "to_position".
    # ─────────────────────────────────────────────────────────────────────────
    class Meta:
        model = Deployment
        fields = ['transfer_type', 'from_entity_type', 'from_entity_name', 'from_position',
                  'from_cadre_category', 'to_entity_type', 'to_entity_name', 'to_position',
                  'to_cadre_category', 'status', 'effective_date',
                  'end_date', 'reason', 'notes', 'reference_number']
        labels = {
            'from_position': 'Speciality',   # UI rename
            'to_position': 'Speciality',     # UI rename
        }
        widgets = {
            'effective_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'reason': forms.TextInput(attrs=W),
            'notes': forms.Textarea(attrs={**W, 'rows': 3}),
            'reference_number': forms.TextInput(attrs=W),
            'from_entity_type': forms.Select(attrs={**WS, 'disabled': 'disabled'}),
            'to_entity_type': forms.Select(attrs=WS),
            'transfer_type': forms.Select(attrs=WS),
            'status': forms.Select(attrs=WS),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        from core.models import Position, CadreCategory

        # Make FROM fields read-only
        for fname in ['from_entity_type', 'from_entity_name', 'from_position', 'from_cadre_category']:
            self.fields[fname].widget.attrs['readonly'] = True
            self.fields[fname].widget.attrs['tabindex'] = '-1'
            self.fields[fname].required = False
            if fname != 'from_entity_type':
                self.fields[fname].widget = forms.TextInput(attrs={**W, 'readonly': 'readonly', 'tabindex': '-1', 'style': 'background:#f1f5f9;'})

        # Make to_position a select from positions (model: Position, UI label: Speciality)
        positions = Position.objects.filter(is_active=True)
        pos_choices = [('', '-- Select Speciality --')] + [(p.name, p.name) for p in positions]
        self.fields['to_position'].widget = forms.Select(attrs=WS, choices=pos_choices)

        # Make to_cadre_category a select
        categories = CadreCategory.objects.filter(is_active=True)
        cat_choices = [('', '-- Select Cadre Category --')] + [(c.name, c.name) for c in categories]
        self.fields['to_cadre_category'].widget = forms.Select(attrs=WS, choices=cat_choices)

        # Make to_entity_name a select (populated by JS based on to_entity_type)
        self.fields['to_entity_name'].widget = forms.Select(attrs=WS, choices=[('', '-- Select Entity --')])

        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.Textarea, forms.DateInput)):
                if 'readonly' not in field.widget.attrs:
                    field.widget.attrs.update(W)


class MagicLinkForm(forms.Form):
    SECTION_CHOICES = [
        ('bio', 'Bio Data'),
        ('work', 'Work Information'),
        ('qualifications', 'Qualifications'),
        ('certifications', 'Certifications'),
        ('publications', 'Publications'),
        ('events', 'Events & Seminars'),
    ]
    duration_hours = forms.IntegerField(min_value=1, max_value=168, initial=24,
                                        widget=forms.NumberInput(attrs=W))
    sections = forms.MultipleChoiceField(
        choices=SECTION_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        initial=['bio', 'work'],
        required=False
    )


class VerificationForm(forms.ModelForm):
    """Admin-only form to set verification statuses for each profile section."""
    class Meta:
        model = Employee
        fields = [
            'bio_verification_status', 'bio_verification_note',
            'work_verification_status', 'work_verification_note',
            'qual_verification_status', 'qual_verification_note',
            'cert_verification_status', 'cert_verification_note',
            'pub_events_verification_status', 'pub_events_verification_note',
            'overall_verification_status', 'overall_verification_note',
        ]
        labels = {
            'bio_verification_status': 'Bio Data Status',
            'bio_verification_note': 'Bio Rejection Reason (visible to employee)',
            'work_verification_status': 'Work Info Status',
            'work_verification_note': 'Work Rejection Reason (visible to employee)',
            'qual_verification_status': 'Qualifications Status',
            'qual_verification_note': 'Qualifications Rejection Reason',
            'cert_verification_status': 'Certifications Status',
            'cert_verification_note': 'Certifications Rejection Reason',
            'pub_events_verification_status': 'Publications & Events Status',
            'pub_events_verification_note': 'Publications & Events Rejection Reason',
            'overall_verification_status': 'Overall Profile Status',
            'overall_verification_note': 'Overall Rejection Reason',
        }
        widgets = {
            'bio_verification_status': forms.Select(attrs=WS),
            'work_verification_status': forms.Select(attrs=WS),
            'qual_verification_status': forms.Select(attrs=WS),
            'cert_verification_status': forms.Select(attrs=WS),
            'pub_events_verification_status': forms.Select(attrs=WS),
            'overall_verification_status': forms.Select(attrs=WS),
            'bio_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
            'work_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
            'qual_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
            'cert_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
            'pub_events_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
            'overall_verification_note': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Reason for returning (shown to employee)'}),
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={**W, 'placeholder': 'Enter your registered email'})
    )


class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label='New Password', min_length=8,
        widget=forms.PasswordInput(attrs={**W, 'placeholder': 'At least 8 characters'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={**W, 'placeholder': 'Repeat new password'})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned
