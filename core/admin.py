from django.contrib import admin
from .models import (Ministry, Agency, GovernmentDepartment, District,
                     EmployeeType, CadreCategory, Position, Role, JobRank, SystemSettings)


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']


@admin.register(GovernmentDepartment)
class GovernmentDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'is_active']
    list_filter = ['region']
    search_fields = ['name']


@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']


@admin.register(CadreCategory)
class CadreCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'cadre_category', 'is_active']
    list_filter = ['cadre_category']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_active']
    list_filter = ['position']


@admin.register(JobRank)
class JobRankAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'cadre_category', 'entity_type', 'level', 'is_active']
    list_filter = ['entity_type', 'cadre_category']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()
