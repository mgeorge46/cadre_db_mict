from django.urls import path
from . import views

app_name = 'inquiries'

urlpatterns = [
    path('', views.inquiry_list, name='list'),
    path('create/', views.inquiry_create, name='create'),
    path('<int:pk>/', views.inquiry_detail, name='detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
