from django.contrib import admin
from .models import Inquiry, InquiryResponse, InquiryAttachment


class InquiryResponseInline(admin.TabularInline):
    model = InquiryResponse
    extra = 0


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'submitted_by', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['reference_number', 'title']
    inlines = [InquiryResponseInline]
