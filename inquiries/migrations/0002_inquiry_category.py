from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inquiries', '0001_initial'),
    ]

    operations = [
        # 1. Create the new InquiryCategory model
        migrations.CreateModel(
            name='InquiryCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name'], 'verbose_name_plural': 'Inquiry Categories'},
        ),
        # 2. Drop the old varchar category column (cannot be cast to bigint)
        migrations.RemoveField(
            model_name='inquiry',
            name='category',
        ),
        # 3. Add the new FK column (category_id)
        migrations.AddField(
            model_name='inquiry',
            name='category',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='inquiries',
                to='inquiries.inquirycategory',
            ),
        ),
    ]
