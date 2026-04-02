from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_allow_employees_view_directory'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='directory_visible_fields',
            field=models.JSONField(blank=True, default=list, help_text='Fields visible to employees when browsing the employee directory'),
        ),
    ]
