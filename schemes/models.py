from django.db import models


class Scheme(models.Model):
    title = models.CharField(max_length=300)
    reference_number = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    document = models.FileField(upload_to='schemes/', null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    requires_signature = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def views_count(self):
        return self.views.count()

    @property
    def signatures_count(self):
        return self.signatures.count()


class SchemeView(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='views')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['scheme', 'employee']

    def __str__(self):
        return f"{self.employee} viewed {self.scheme}"


class SchemeSignature(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='signatures')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        unique_together = ['scheme', 'employee']

    def __str__(self):
        return f"{self.employee} signed {self.scheme}"
