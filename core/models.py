from django.db import models


class Ministry(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Ministries'
        ordering = ['name']

    def __str__(self):
        return self.name


class Agency(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Agencies'
        ordering = ['name']

    def __str__(self):
        return self.name


class GovernmentDepartment(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


REGION_CHOICES = [
    ('Central', 'Central'),
    ('Eastern', 'Eastern'),
    ('Western', 'Western'),
    ('Northern', 'Northern'),
]


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region})"


class EmployeeType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CadreCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Cadre Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=200)
    cadre_category = models.ForeignKey(CadreCategory, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.cadre_category})"


class Role(models.Model):
    name = models.CharField(max_length=200)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='roles')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.position})"


ENTITY_CHOICES = [
    ('ministry', 'Ministry'),
    ('agency', 'Agency'),
    ('department', 'Department'),
    ('local_govt', 'Local Government'),
    ('all', 'All'),
]


class JobRank(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    cadre_category = models.ForeignKey(CadreCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='job_ranks')
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES, default='all')
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SystemSettings(models.Model):
    email_host = models.CharField(max_length=200, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.EmailField(blank=True)
    email_host_password = models.CharField(max_length=200, blank=True)
    email_from_name = models.CharField(max_length=100, default='Ministry of ICT')
    system_name = models.CharField(max_length=200, default='IT Cadre Tracking Database')
    magic_link_default_duration = models.IntegerField(default=24)
    allow_employee_profile_edit = models.BooleanField(default=False)
    allow_employees_view_directory = models.BooleanField(default=False)
    directory_visible_fields = models.JSONField(
        default=list,
        blank=True,
        help_text='Fields visible to employees when browsing the employee directory'
    )
    announcement_default_duration = models.IntegerField(default=30)

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return 'System Settings'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
