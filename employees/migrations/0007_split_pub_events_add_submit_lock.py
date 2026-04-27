from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0006_alter_employee_onboarding_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Split pub_events into pub + events
        migrations.AddField(
            model_name='employee',
            name='pub_verification_status',
            field=models.CharField(
                choices=[('pending', 'Pending Review'), ('verified', 'Verified'), ('returned', 'Returned to Employee')],
                default='pending', max_length=20, verbose_name='Publications Verification'),
        ),
        migrations.AddField(
            model_name='employee',
            name='pub_verification_note',
            field=models.TextField(blank=True, verbose_name='Publications Rejection Reason'),
        ),
        migrations.AddField(
            model_name='employee',
            name='events_verification_status',
            field=models.CharField(
                choices=[('pending', 'Pending Review'), ('verified', 'Verified'), ('returned', 'Returned to Employee')],
                default='pending', max_length=20, verbose_name='Events & Seminars Verification'),
        ),
        migrations.AddField(
            model_name='employee',
            name='events_verification_note',
            field=models.TextField(blank=True, verbose_name='Events & Seminars Rejection Reason'),
        ),
        migrations.RemoveField(model_name='employee', name='pub_events_verification_status'),
        migrations.RemoveField(model_name='employee', name='pub_events_verification_note'),

        # Submit for verification flags
        migrations.AddField(model_name='employee', name='bio_submitted',
            field=models.BooleanField(default=False, verbose_name='Bio Submitted for Verification')),
        migrations.AddField(model_name='employee', name='work_submitted',
            field=models.BooleanField(default=False, verbose_name='Work Submitted for Verification')),
        migrations.AddField(model_name='employee', name='qual_submitted',
            field=models.BooleanField(default=False, verbose_name='Qualifications Submitted for Verification')),
        migrations.AddField(model_name='employee', name='cert_submitted',
            field=models.BooleanField(default=False, verbose_name='Certifications Submitted for Verification')),
        migrations.AddField(model_name='employee', name='pub_submitted',
            field=models.BooleanField(default=False, verbose_name='Publications Submitted for Verification')),
        migrations.AddField(model_name='employee', name='events_submitted',
            field=models.BooleanField(default=False, verbose_name='Events Submitted for Verification')),

        # Per-section lock flags
        migrations.AddField(model_name='employee', name='bio_locked',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='work_locked',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='qual_locked',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='cert_locked',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='pub_locked',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='employee', name='events_locked',
            field=models.BooleanField(default=False)),
    ]
