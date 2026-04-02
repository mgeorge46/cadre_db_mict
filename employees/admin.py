from django.contrib import admin
from .models import Employee, EmploymentHistory, Qualification, Certification, Publication, EventSeminar, MagicLink


class EmploymentHistoryInline(admin.TabularInline):
    model = EmploymentHistory
    extra = 0


class QualificationInline(admin.TabularInline):
    model = Qualification
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'get_full_name', 'entity_type', 'cadre_category', 'position', 'is_active', 'profile_completion']
    list_filter = ['entity_type', 'cadre_category', 'employee_type', 'is_active']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'user__email']
    inlines = [EmploymentHistoryInline, QualificationInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(EmploymentHistory)
class EmploymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'position_title', 'entity_name', 'start_date', 'end_date']


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'qualification_type', 'institution', 'end_date']


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'name', 'issuing_body', 'date_attained', 'expiry_date']


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ['employee', 'token', 'is_used', 'expires_at', 'created_at']
