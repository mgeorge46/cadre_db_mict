from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_type', models.CharField(choices=[('transfer', 'Transfer'), ('deployment', 'Deployment'), ('secondment', 'Secondment'), ('attachment', 'Attachment')], default='transfer', max_length=20)),
                ('from_entity_type', models.CharField(blank=True, choices=[('ministry', 'Ministry'), ('agency', 'Agency'), ('department', 'Government Department'), ('local_govt', 'Local Government')], max_length=20)),
                ('from_entity_name', models.CharField(blank=True, max_length=200)),
                ('from_position', models.CharField(blank=True, max_length=200)),
                ('to_entity_type', models.CharField(choices=[('ministry', 'Ministry'), ('agency', 'Agency'), ('department', 'Government Department'), ('local_govt', 'Local Government')], max_length=20)),
                ('to_entity_name', models.CharField(max_length=200)),
                ('to_position', models.CharField(blank=True, max_length=200)),
                ('effective_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('reason', models.CharField(blank=True, max_length=500)),
                ('notes', models.TextField(blank=True)),
                ('reference_number', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deployments_created', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deployments', to='employees.employee')),
            ],
            options={
                'ordering': ['-effective_date'],
            },
        ),
    ]
