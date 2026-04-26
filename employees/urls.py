from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('import/', views.employee_import, name='import'),
    path('bulk-magic-link/', views.bulk_magic_link, name='bulk_magic_link'),
    path('verification/', views.verification_dashboard, name='verification_dashboard'),
    path('import/template/', views.employee_import_template, name='import_template'),
    path('import/result/', views.employee_import_result, name='import_result'),
    path('create/', views.employee_create, name='create'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('<int:pk>/verify/', views.save_verification, name='save_verification'),
    path('<int:pk>/edit/bio/', views.employee_edit_bio, name='edit_bio'),
    path('<int:pk>/edit/work/', views.employee_edit_work, name='edit_work'),
    path('<int:pk>/deactivate/', views.employee_deactivate, name='deactivate'),
    # Employment History
    path('<int:pk>/history/add/', views.employment_history_add, name='history_add'),
    path('<int:pk>/history/<int:history_pk>/edit/', views.employment_history_edit, name='history_edit'),
    path('<int:pk>/history/<int:history_pk>/delete/', views.employment_history_delete, name='history_delete'),
    # Qualifications
    path('<int:pk>/qualifications/add/', views.qualification_add, name='qualification_add'),
    path('<int:pk>/qualifications/<int:item_pk>/edit/', views.qualification_edit, name='qualification_edit'),
    path('<int:pk>/qualifications/<int:item_pk>/delete/', views.qualification_delete, name='qualification_delete'),
    # Certifications
    path('<int:pk>/certifications/add/', views.certification_add, name='certification_add'),
    path('<int:pk>/certifications/<int:item_pk>/delete/', views.certification_delete, name='certification_delete'),
    # Publications
    path('<int:pk>/publications/add/', views.publication_add, name='publication_add'),
    path('<int:pk>/publications/<int:item_pk>/delete/', views.publication_delete, name='publication_delete'),
    # Events
    path('<int:pk>/events/add/', views.event_add, name='event_add'),
    path('<int:pk>/events/<int:item_pk>/delete/', views.event_delete, name='event_delete'),
    # Magic Links
    path('<int:pk>/magic-link/', views.send_magic_link, name='magic_link'),
    path('magic/<uuid:token>/', views.magic_link_update, name='magic_link_update'),
    # Deployments
    path('<int:pk>/deployments/add/', views.deployment_add, name='deployment_add'),
    path('<int:pk>/deployments/<int:dep_pk>/edit/', views.deployment_edit, name='deployment_edit'),
    path('<int:pk>/deployments/<int:dep_pk>/delete/', views.deployment_delete, name='deployment_delete'),
]
