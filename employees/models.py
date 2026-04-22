import uuid
from django.db import models
from django.utils import timezone

ENTITY_TYPE_CHOICES = [
    ('ministry', 'Ministry'),
    ('agency', 'Agency'),
    ('department', 'Government Department'),
    ('local_govt', 'Local Government'),
]

GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
MARITAL_CHOICES = [
    ('single', 'Single'), ('married', 'Married'),
    ('divorced', 'Divorced'), ('widowed', 'Widowed')
]
BLOOD_TYPE_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
]
TITLE_CHOICES = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')]


class Employee(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='employee_profile')
    employee_number = models.CharField(max_length=50, unique=True)

    # Bio Data
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, default='Ugandan')
    national_id = models.CharField(max_length=50, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    tin_number = models.CharField(max_length=50, blank=True)
    nssf_number = models.CharField(max_length=50, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    profile_photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    physical_address = models.TextField(blank=True)
    district_of_origin = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL, related_name='origin_employees')
    district_of_residence = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL, related_name='residence_employees')
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True)
    has_disability = models.BooleanField(default=False)
    disability_description = models.TextField(blank=True)

    # Next of Kin
    next_of_kin_name = models.CharField(max_length=200, blank=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    next_of_kin_email = models.EmailField(blank=True)
    next_of_kin_address = models.TextField(blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)

    # Work Information
    # ─────────────────────────────────────────────────────────────────────────
    # UI RENAME NOTE (maintainers):
    #   Field "position"  (→ core.Position)  is labelled "Speciality" in the UI.
    #   Field "job_rank"  (→ core.JobRank)   is labelled "Position"   in the UI.
    #   Field "date_joined_position"         is "Date Joined Speciality" in the UI.
    #   DO NOT rename these fields — it would require a migration and break queries.
    #   Only form labels, template headings and view page-titles use the new terms.
    # ─────────────────────────────────────────────────────────────────────────
    employee_type = models.ForeignKey('core.EmployeeType', null=True, blank=True, on_delete=models.SET_NULL)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, blank=True)
    ministry = models.ForeignKey('core.Ministry', null=True, blank=True, on_delete=models.SET_NULL)
    agency = models.ForeignKey('core.Agency', null=True, blank=True, on_delete=models.SET_NULL)
    government_department = models.ForeignKey('core.GovernmentDepartment', null=True, blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL, related_name='deployed_employees')
    cadre_category = models.ForeignKey('core.CadreCategory', null=True, blank=True, on_delete=models.SET_NULL)
    position = models.ForeignKey('core.Position', null=True, blank=True, on_delete=models.SET_NULL)   # UI: "Speciality"
    job_rank = models.ForeignKey('core.JobRank', null=True, blank=True, on_delete=models.SET_NULL)    # UI: "Position"
    reporting_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='direct_reports')
    work_location = models.CharField(max_length=300, blank=True)
    date_joined_position = models.DateField(null=True, blank=True)
    date_joined_ministry = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    roles = models.ManyToManyField('core.Role', blank=True)

    # System Fields
    profile_completion = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL, related_name='employees_created')

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_number})"

    def get_entity_name(self):
        if self.entity_type == 'ministry' and self.ministry:
            return self.ministry.name
        elif self.entity_type == 'agency' and self.agency:
            return self.agency.name
        elif self.entity_type == 'department' and self.government_department:
            return self.government_department.name
        elif self.entity_type == 'local_govt' and self.district:
            return self.district.name
        return 'N/A'

    def calculate_profile_completion(self):
        fields_to_check = [
            'title', 'date_of_birth', 'gender', 'national_id', 'phone_primary',
            'physical_address', 'district_of_origin', 'district_of_residence',
            'marital_status', 'next_of_kin_name', 'next_of_kin_phone',
            'emergency_contact_name', 'emergency_contact_phone',
            'employee_type', 'entity_type', 'cadre_category', 'position', 'job_rank',
            'date_joined_position', 'date_joined_ministry', 'work_location',
        ]
        filled = 0
        for field in fields_to_check:
            val = getattr(self, field)
            if val is not None and val != '':
                filled += 1
        if self.profile_photo:
            filled += 1
            fields_to_check.append('profile_photo')
        # Only check related managers if instance is already saved
        if self.pk:
            if self.qualifications.exists():
                filled += 1
                fields_to_check.append('qualifications')
        total = len(fields_to_check)
        return int((filled / total) * 100) if total > 0 else 0

    def save(self, *args, **kwargs):
        self.profile_completion = self.calculate_profile_completion()
        super().save(*args, **kwargs)


class EmploymentHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employment_history')
    position_title = models.CharField(max_length=200)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    entity_name = models.CharField(max_length=200)
    cadre_category = models.CharField(max_length=200, blank=True)
    job_rank = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.position_title} at {self.entity_name}"


QUAL_TYPES = [
    ('phd', 'PhD/Doctorate'),
    ('masters', 'Masters Degree'),
    ('pgdip', 'Postgraduate Diploma'),
    ('degree', "Bachelor's Degree"),
    ('diploma', 'Diploma'),
    ('certificate', 'Certificate'),
    ('alevel', 'A-Level'),
    ('olevel', 'O-Level'),
    ('primary', 'Primary'),
]


class Qualification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='qualifications')
    qualification_type = models.CharField(max_length=20, choices=QUAL_TYPES)
    institution = models.CharField(max_length=300)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    document = models.FileField(upload_to='qualifications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.get_qualification_type_display()} - {self.institution}"


class Certification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=300)
    issuing_body = models.CharField(max_length=300)
    date_attained = models.DateField()
    has_expiry = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=200, blank=True)
    document = models.FileField(upload_to='certifications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_attained']

    def __str__(self):
        return f"{self.name} - {self.employee}"

    @property
    def is_expired(self):
        if self.has_expiry and self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False


class Publication(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=500)
    journal_or_publisher = models.CharField(max_length=300, blank=True)
    date_published = models.DateField()
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    co_authors = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_published']

    def __str__(self):
        return self.title


class EventSeminar(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=300)
    organizer = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=300, blank=True)
    date_attended = models.DateField()
    duration_days = models.IntegerField(default=1)
    certificate_obtained = models.BooleanField(default=False)
    document = models.FileField(upload_to='events/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_attended']

    def __str__(self):
        return f"{self.name} - {self.employee}"


TRANSFER_TYPE_CHOICES = [
    ('transfer', 'Transfer'),
    ('deployment', 'Deployment'),
    ('secondment', 'Secondment'),
    ('attachment', 'Attachment'),
]

DEPLOYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


class Deployment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='deployments')
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, default='transfer')
    from_entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, blank=True)
    from_entity_name = models.CharField(max_length=200, blank=True)
    from_position = models.CharField(max_length=200, blank=True)
    from_cadre_category = models.CharField(max_length=200, blank=True)
    to_entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    to_entity_name = models.CharField(max_length=200)
    to_position = models.CharField(max_length=200, blank=True)
    to_cadre_category = models.CharField(max_length=200, blank=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DEPLOYMENT_STATUS_CHOICES, default='pending')
    reason = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL, related_name='deployments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    # Audit fields for status changes
    status_changed_by = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='deployment_status_changes')
    status_changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.get_transfer_type_display()}: {self.employee} → {self.to_entity_name}"


class MagicLink(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='magic_links')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    sections = models.JSONField(default=list)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Magic Link for {self.employee} - {'Used' if self.is_used else 'Active'}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class BulkMagicLink(models.Model):
    FILTER_CHOICES = [('all', 'All'), ('entity', 'By Entity'), ('position', 'By Position')]
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    filter_type = models.CharField(max_length=20, choices=FILTER_CHOICES)
    entity_type = models.CharField(max_length=20, blank=True)
    entity_id = models.IntegerField(null=True, blank=True)
    position_id = models.IntegerField(null=True, blank=True)
    duration_hours = models.IntegerField(default=24)
    sections = models.JSONField(default=list)
    sent_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bulk Magic Link: {self.name} ({self.sent_count} sent)"
