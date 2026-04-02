from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("users/", views.user_list_view, name="user_list"),
    path("users/create/", views.user_create_view, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit_view, name="user_edit"),
    path("users/<int:pk>/change-password/", views.admin_change_password_view, name="admin_change_password"),
    path("users/<int:pk>/delete/", views.user_delete_view, name="user_delete"),
]
