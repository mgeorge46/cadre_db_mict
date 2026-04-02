from django.contrib import admin
from .models import Scheme, SchemeView, SchemeSignature


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'reference_number', 'is_published', 'views_count', 'signatures_count', 'created_at']
    list_filter = ['is_published', 'requires_signature']
    search_fields = ['title', 'reference_number']


admin.site.register(SchemeView)
admin.site.register(SchemeSignature)
