from django.db import models


FILTER_CHOICES = [
    ('all', 'All Employees'),
    ('entity_type', 'By Entity Type'),
    ('entity', 'Specific Entity'),
    ('position', 'By Position'),
]


class Announcement(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    filter_type = models.CharField(max_length=20, choices=FILTER_CHOICES, default='all')
    target_entity_type = models.CharField(max_length=20, blank=True)
    target_entity_ids = models.JSONField(default=list)
    target_position_ids = models.JSONField(default=list)
    send_email = models.BooleanField(default=True)
    requires_acknowledgment = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def reads_count(self):
        return self.reads.count()

    @property
    def acknowledged_count(self):
        return self.reads.filter(acknowledged=True).count()


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['announcement', 'employee']

    def __str__(self):
        return f"{self.employee} read {self.announcement}"
