from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    # Ministries
    path('ministries/', views.ministry_list, name='ministry_list'),
    path('ministries/create/', views.ministry_create, name='ministry_create'),
    path('ministries/<int:pk>/edit/', views.ministry_edit, name='ministry_edit'),
    path('ministries/<int:pk>/delete/', views.ministry_delete, name='ministry_delete'),
    # Agencies
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/create/', views.agency_create, name='agency_create'),
    path('agencies/<int:pk>/edit/', views.agency_edit, name='agency_edit'),
    path('agencies/<int:pk>/delete/', views.agency_delete, name='agency_delete'),
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    # Districts
    path('districts/', views.district_list, name='district_list'),
    path('districts/create/', views.district_create, name='district_create'),
    path('districts/<int:pk>/edit/', views.district_edit, name='district_edit'),
    path('districts/<int:pk>/delete/', views.district_delete, name='district_delete'),
    # Cadre
    path('cadre/', views.cadre_category_list, name='cadre_category_list'),
    path('cadre/create/', views.cadre_category_create, name='cadre_category_create'),
    path('cadre/<int:pk>/edit/', views.cadre_category_edit, name='cadre_category_edit'),
    path('cadre/<int:pk>/delete/', views.cadre_category_delete, name='cadre_category_delete'),
    # Positions
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    # Job Ranks
    path('job-ranks/', views.job_rank_list, name='job_rank_list'),
    path('job-ranks/create/', views.job_rank_create, name='job_rank_create'),
    path('job-ranks/<int:pk>/edit/', views.job_rank_edit, name='job_rank_edit'),
    path('job-ranks/<int:pk>/delete/', views.job_rank_delete, name='job_rank_delete'),
    # Employee Types
    path('employee-types/', views.employee_type_list, name='employee_type_list'),
    path('employee-types/create/', views.employee_type_create, name='employee_type_create'),
    path('employee-types/<int:pk>/edit/', views.employee_type_edit, name='employee_type_edit'),
    path('employee-types/<int:pk>/delete/', views.employee_type_delete, name='employee_type_delete'),
    # AJAX
    path('ajax/positions/', views.get_positions, name='ajax_positions'),
    path('ajax/roles/', views.get_roles, name='ajax_roles'),
    path('ajax/entities/', views.get_entities, name='ajax_entities'),
]
