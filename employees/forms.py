from django import forms
from django.contrib.auth import get_user_model
from .models import Employee, EmploymentHistory, Qualification, Certification, Publication, EventSeminar, MagicLink, Deployment

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
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'employee_type', 'entity_type',
            'ministry', 'agency', 'government_department', 'district',
            'cadre_category', 'position', 'job_rank', 'reporting_to',
            'work_location', 'date_joined_position', 'date_joined_ministry',
            'contract_end_date', 'roles',
        ]
        widgets = {
            'date_joined_position': forms.DateInput(attrs={**W, 'type': 'date'}),
            'date_joined_ministry': forms.DateInput(attrs={**W, 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'roles': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select) and name not in ('roles',):
                field.widget.attrs.update(WS)
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.SelectMultiple, forms.Select)):
                field.widget.attrs.update(W)


class EmployeeCreateForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=W))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=W))
    email = forms.EmailField(widget=forms.EmailInput(attrs=W))
    employee_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs=W))
    password = forms.CharField(widget=forms.PasswordInput(attrs=W), initial='ChangeMe@2024')


class EmploymentHistoryForm(forms.ModelForm):
    # Make position_title a dropdown from existing positions
    position_title = forms.CharField(
        widget=forms.Select(attrs=WS),
        required=True,
    )

    class Meta:
        model = EmploymentHistory
        fields = ['position_title', 'entity_type', 'entity_name', 'cadre_category',
                  'job_rank', 'start_date', 'end_date', 'is_current', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={**W, 'type': 'date'}),
            'notes': forms.Textarea(attrs={**W, 'rows': 3}),
            'entity_type': forms.Select(attrs=WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Position, CadreCategory, JobRank
        # Populate position choices
        positions = Position.objects.filter(is_active=True).values_list('name', flat=True).distinct()
        pos_choices = [('', '-- Select Position --')] + [(p, p) for p in positions]
        self.fields['position_title'].widget.choices = pos_choices
        # Make cadre_category a dropdown
        categories = CadreCategory.objects.filter(is_active=True).values_list('name', flat=True)
        cat_choices = [('', '-- Select Cadre Category --')] + [(c, c) for c in categories]
        self.fields['cadre_category'].widget = forms.Select(attrs=WS, choices=cat_choices)
        # Make job_rank a dropdown
        ranks = JobRank.objects.filter(is_active=True).values_list('name', flat=True).distinct()
        rank_choices = [('', '-- Select Job Rank --')] + [(r, r) for r in ranks]
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
    class Meta:
        model = Deployment
        fields = ['transfer_type', 'from_entity_type', 'from_entity_name', 'from_position',
                  'from_cadre_category', 'to_entity_type', 'to_entity_name', 'to_position',
                  'to_cadre_category', 'status', 'effective_date',
                  'end_date', 'reason', 'notes', 'reference_number']
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

        # Make to_position a select from positions
        positions = Position.objects.filter(is_active=True)
        pos_choices = [('', '-- Select Position --')] + [(p.name, p.name) for p in positions]
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
