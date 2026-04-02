from django.contrib import admin
from .models import Announcement, AnnouncementRead


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'published_at', 'expiry_date', 'reads_count']
    list_filter = ['is_published', 'filter_type']
    search_fields = ['title']


admin.site.register(AnnouncementRead)
