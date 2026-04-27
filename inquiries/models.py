from django.db import models


class InquiryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Inquiry Categories'

    def __str__(self):
        return self.name


STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('pending_info', 'Pending Information'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class Inquiry(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    description = models.TextField()
    submitted_by = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='submitted_inquiries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_inquiries')
    category = models.ForeignKey(InquiryCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='inquiries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f"[{self.reference_number}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import datetime
            prefix = f"INQ-{datetime.datetime.now().strftime('%Y%m')}-"
            last = Inquiry.objects.filter(reference_number__startswith=prefix).count() + 1
            self.reference_number = f"{prefix}{last:04d}"
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        mapping = {
            'open': 'danger', 'in_progress': 'primary',
            'pending_info': 'warning', 'resolved': 'success', 'closed': 'secondary'
        }
        return mapping.get(self.status, 'secondary')

    @property
    def priority_badge_class(self):
        mapping = {'low': 'success', 'medium': 'info', 'high': 'warning', 'urgent': 'danger'}
        return mapping.get(self.priority, 'secondary')


class InquiryResponse(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='responses')
    responded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response by {self.responded_by} on {self.inquiry}"


class InquiryAttachment(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='inquiry_attachments/')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.inquiry}"
