from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import LoginForm, UserPasswordChangeForm, UserCreateForm, UserEditForm, AdminPasswordChangeForm

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "dashboard:index")
            return redirect(next_url)
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"page_title": "My Profile"})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:profile")
    return render(request, "accounts/change_password.html", {"form": form, "page_title": "Change Password"})


@login_required
def user_list_view(request):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    qs = User.objects.all().order_by("first_name", "last_name")
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    per_page = request.GET.get('per_page', '50')
    try:
        per_page = int(per_page)
        if per_page not in (20, 50, 100):
            per_page = 50
    except (ValueError, TypeError):
        per_page = 50
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "accounts/user_list.html", {
        "users": page_obj, "page_obj": page_obj, "search": search,
        "per_page": per_page, "page_title": "User Management"
    })


@login_required
def user_create_view(request):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    form = UserCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.get_full_name()} created successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "page_title": "Create User", "action": "Create"})


@login_required
def user_edit_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user_obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {
        "form": form, "page_title": "Edit User", "action": "Update", "user_obj": user_obj
    })


@login_required
def admin_change_password_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    form = AdminPasswordChangeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user_obj.set_password(form.cleaned_data['new_password1'])
            user_obj.save()
            messages.success(request, f"Password for {user_obj.get_full_name()} changed successfully.")
            return redirect("accounts:user_list")
    return render(request, "accounts/change_password_for_user.html", {
        "form": form,
        "user_obj": user_obj,
        "page_title": f"Change Password: {user_obj.get_full_name()}"
    })


@login_required
def user_delete_view(request, pk):
    if not (request.user.is_admin or request.user.is_it_admin or request.user.is_superuser):
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("accounts:user_list")
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only superusers can delete superuser accounts.")
        return redirect("accounts:user_list")
    if request.method == "POST":
        name = user_obj.get_full_name()
        user_obj.delete()
        messages.success(request, f"User {name} deleted successfully.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_confirm_delete.html", {
        "user_obj": user_obj,
        "page_title": f"Delete User: {user_obj.get_full_name()}"
    })
