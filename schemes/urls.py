from django.urls import path
from . import views

app_name = 'schemes'

urlpatterns = [
    path('', views.scheme_list, name='list'),
    path('create/', views.scheme_create, name='create'),
    path('<int:pk>/', views.scheme_detail, name='detail'),
    path('<int:pk>/edit/', views.scheme_edit, name='edit'),
    path('<int:pk>/delete/', views.scheme_delete, name='delete'),
]
